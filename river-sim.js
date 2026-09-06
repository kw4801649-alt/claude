(() => {
  "use strict";

  const canvas = document.getElementById("river");
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;

  // ---------- UI ----------
  const flowSlider = document.getElementById("flow");
  const countSlider = document.getElementById("count");
  const turbSlider = document.getElementById("turbulence");
  const rainCheck = document.getElementById("rain");
  const flowFieldCheck = document.getElementById("flowfield");
  const flowVal = document.getElementById("flow-val");
  const countVal = document.getElementById("count-val");
  const turbVal = document.getElementById("turbulence-val");
  const clearRocksBtn = document.getElementById("clear-rocks");
  const resetBtn = document.getElementById("reset");
  const statFps = document.getElementById("stat-fps");
  const statParticles = document.getElementById("stat-particles");
  const statRocks = document.getElementById("stat-rocks");

  let flowSpeed = Number(flowSlider.value);
  let targetCount = Number(countSlider.value);
  let turbulence = Number(turbSlider.value);

  flowSlider.addEventListener("input", () => {
    flowSpeed = Number(flowSlider.value);
    flowVal.textContent = flowSlider.value;
  });
  countSlider.addEventListener("input", () => {
    targetCount = Number(countSlider.value);
    countVal.textContent = countSlider.value;
  });
  turbSlider.addEventListener("input", () => {
    turbulence = Number(turbSlider.value);
    turbVal.textContent = turbSlider.value;
  });
  flowVal.textContent = flowSlider.value;
  countVal.textContent = countSlider.value;
  turbVal.textContent = turbSlider.value;

  // ---------- River channel geometry ----------
  // Centerline meanders left/right down the canvas; width also varies (narrows are faster, like real rivers).
  const baseWidth = 170;
  const widthAmp = 50;
  const centerX = new Float32Array(H);
  const halfWidth = new Float32Array(H);
  const tangent = new Float32Array(H); // dCenterX/dy, used for local flow direction

  function buildChannel() {
    for (let y = 0; y < H; y++) {
      const cx =
        W / 2 +
        70 * Math.sin(y * 0.007 + 0.6) +
        20 * Math.sin(y * 0.015 + 2.1);
      centerX[y] = cx;
      halfWidth[y] =
        (baseWidth + widthAmp * Math.sin(y * 0.02 + 1.3)) / 2;
    }
    for (let y = 0; y < H; y++) {
      const y0 = Math.max(0, y - 1);
      const y1 = Math.min(H - 1, y + 1);
      tangent[y] = (centerX[y1] - centerX[y0]) / (y1 - y0 || 1);
    }
  }
  buildChannel();

  // ---------- Static riverbed (banks) rendered once ----------
  const bg = document.createElement("canvas");
  bg.width = W;
  bg.height = H;
  const bgCtx = bg.getContext("2d");

  function drawBanks() {
    // land
    bgCtx.fillStyle = "#1a2b1f";
    bgCtx.fillRect(0, 0, W, H);

    // riverbed shape
    bgCtx.beginPath();
    bgCtx.moveTo(centerX[0] - halfWidth[0], 0);
    for (let y = 1; y < H; y++) bgCtx.lineTo(centerX[y] - halfWidth[y], y);
    for (let y = H - 1; y >= 0; y--) bgCtx.lineTo(centerX[y] + halfWidth[y], y);
    bgCtx.closePath();

    const grad = bgCtx.createLinearGradient(0, 0, W, 0);
    grad.addColorStop(0, "#0f3a52");
    grad.addColorStop(0.5, "#12496a");
    grad.addColorStop(1, "#0f3a52");
    bgCtx.fillStyle = grad;
    bgCtx.fill();

    // bank edges (sand/mud rim)
    bgCtx.lineWidth = 4;
    bgCtx.strokeStyle = "rgba(196, 176, 120, 0.35)";
    bgCtx.beginPath();
    bgCtx.moveTo(centerX[0] - halfWidth[0], 0);
    for (let y = 1; y < H; y++) bgCtx.lineTo(centerX[y] - halfWidth[y], y);
    bgCtx.stroke();
    bgCtx.beginPath();
    bgCtx.moveTo(centerX[0] + halfWidth[0], 0);
    for (let y = 1; y < H; y++) bgCtx.lineTo(centerX[y] + halfWidth[y], y);
    bgCtx.stroke();
  }
  drawBanks();

  // ---------- Rocks ----------
  /** @type {{x:number,y:number,r:number}[]} */
  const rocks = [];

  function inChannel(x, y) {
    const row = Math.min(H - 1, Math.max(0, Math.round(y)));
    return Math.abs(x - centerX[row]) < halfWidth[row];
  }

  canvas.addEventListener("click", (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * W;
    const y = ((e.clientY - rect.top) / rect.height) * H;
    if (inChannel(x, y)) {
      rocks.push({ x, y, r: 10 + Math.random() * 14 });
    }
  });

  canvas.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * W;
    const y = ((e.clientY - rect.top) / rect.height) * H;
    let closest = -1;
    let closestDist = Infinity;
    for (let i = 0; i < rocks.length; i++) {
      const d = Math.hypot(rocks[i].x - x, rocks[i].y - y);
      if (d < closestDist) {
        closestDist = d;
        closest = i;
      }
    }
    if (closest >= 0 && closestDist < 40) rocks.splice(closest, 1);
  });

  clearRocksBtn.addEventListener("click", () => {
    rocks.length = 0;
  });

  resetBtn.addEventListener("click", () => {
    rocks.length = 0;
    buildChannel();
    drawBanks();
    particles.length = 0;
    spawnParticles(targetCount);
  });

  // ---------- Particles (water) ----------
  // Lateral position is tracked as `offset` from the centerline (not an
  // absolute x). This decouples a particle's cross-channel wandering from
  // the centerline's own sideways motion as it meanders downstream — trying
  // to track absolute x would require the particle's velocity to constantly
  // "chase" the moving centerline, and any small tracking lag compounds over
  // hundreds of frames into a hard drift toward one bank.
  const REF_WIDTH = baseWidth / 2;

  function spawnOne(p) {
    const row = 0;
    const hw = halfWidth[row] * 0.9;
    p.offset = (Math.random() * 2 - 1) * hw;
    p.voffset = 0;
    p.y = -Math.random() * 30;
    p.vy = flowSpeed * 0.5;
    const x = centerX[row] + p.offset;
    p.px = x;
    p.py = p.y;
  }

  function makeParticle() {
    // Spread the initial fill down the whole river.
    const y = Math.random() * H;
    const row = Math.min(H - 1, Math.max(0, Math.round(y)));
    const hw = halfWidth[row] * 0.9;
    const offset = (Math.random() * 2 - 1) * hw;
    const speed = flowSpeed * (REF_WIDTH / Math.max(20, halfWidth[row]));
    const x = centerX[row] + offset;
    return { offset, voffset: 0, y, vy: speed, px: x, py: y };
  }

  /** @type {Array<{offset:number,voffset:number,y:number,vy:number,px:number,py:number}>} */
  const particles = [];
  function spawnParticles(n) {
    for (let i = 0; i < n; i++) particles.push(makeParticle());
  }
  spawnParticles(targetCount);

  function stepParticle(p, dt) {
    const row = Math.min(H - 1, Math.max(0, Math.round(p.y)));
    const cx = centerX[row];
    const hw = Math.max(20, halfWidth[row]);

    // Continuity-like speed: narrower channel -> faster flow.
    const speed = flowSpeed * (REF_WIDTH / hw);

    // Soft wall: only push back once a particle nears a bank, so the flow
    // fills the whole channel width instead of hugging one edge.
    const norm = p.offset / hw; // -1..1
    const edge = Math.max(0, (Math.abs(norm) - 0.65) / 0.35);
    let tvoffset = -Math.sign(norm) * edge * edge * speed * 0.9;
    let tvy = speed;

    // Rock avoidance: deflect around obstacles (in absolute space).
    const x = cx + p.offset;
    for (let i = 0; i < rocks.length; i++) {
      const r = rocks[i];
      const dx = x - r.x;
      const dy = p.y - r.y;
      const dist = Math.hypot(dx, dy);
      const influence = r.r + 26;
      if (dist < influence) {
        const strength = (1 - dist / influence) * speed * 2.2;
        const nx = dx / (dist || 1);
        const ny = dy / (dist || 1);
        tvoffset += nx * strength;
        tvy += ny * strength * 0.6;
      }
    }

    // Turbulence: baseline lateral mixing (real currents aren't laminar
    // single-file), boosted by the slider and by rain.
    const turb = 0.5 + turbulence * 0.02 + (rainCheck.checked ? 0.6 : 0);
    tvoffset += (Math.random() * 2 - 1) * turb * speed * 0.15;
    tvy += (Math.random() * 2 - 1) * turb * speed * 0.1;

    // Steer velocity toward target (smooths motion, stays stable at high dt).
    const steer = Math.min(1, dt * 6);
    p.voffset += (tvoffset - p.voffset) * steer;
    p.vy += (tvy - p.vy) * steer;

    p.px = cx + p.offset;
    p.py = p.y;
    p.offset += p.voffset * dt;
    p.y += p.vy * dt;

    // Bank collision: clamp inside channel, kill outward velocity.
    const row2 = Math.min(H - 1, Math.max(0, Math.round(p.y)));
    const cx2 = centerX[row2];
    const hw2 = Math.max(20, halfWidth[row2]);
    if (p.offset < -hw2) {
      p.offset = -hw2 + 1;
      p.voffset = Math.abs(p.voffset) * 0.3;
    } else if (p.offset > hw2) {
      p.offset = hw2 - 1;
      p.voffset = -Math.abs(p.voffset) * 0.3;
    }

    // Rock hard collision: don't let particles pass through the core.
    for (let i = 0; i < rocks.length; i++) {
      const r = rocks[i];
      const x2 = cx2 + p.offset;
      const dx = x2 - r.x;
      const dy = p.y - r.y;
      const dist = Math.hypot(dx, dy);
      if (dist < r.r) {
        const nx = dx / (dist || 1);
        const ny = dy / (dist || 1);
        p.offset = r.x + nx * r.r - cx2;
        p.y = r.y + ny * r.r;
      }
    }

    if (p.y > H + 10) {
      spawnOne(p);
    }
  }

  // ---------- Flow field overlay ----------
  function drawFlowField() {
    ctx.strokeStyle = "rgba(255,255,255,0.35)";
    ctx.lineWidth = 1;
    const step = 40;
    for (let y = step / 2; y < H; y += step) {
      const row = Math.min(H - 1, Math.max(0, Math.round(y)));
      const hw = halfWidth[row];
      const cx = centerX[row];
      for (let x = cx - hw + 12; x < cx + hw - 12; x += step) {
        const speed = flowSpeed * (REF_WIDTH / Math.max(20, hw));
        const dx = tangent[row] * speed * 0.6;
        const dy = speed;
        const len = Math.hypot(dx, dy) || 1;
        const scale = 12 / len;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + dx * scale, y + dy * scale);
        ctx.stroke();
      }
    }
  }

  // ---------- Rain ----------
  // Each drop is given a fixed landing point up front (rather than always
  // falling to the bottom of the canvas) so it can splash wherever it
  // actually lands, and only when that point is on the water.
  const raindrops = [];
  function updateRain(dt) {
    if (!rainCheck.checked) return;
    const toSpawn = Math.round(dt * 90);
    for (let i = 0; i < toSpawn; i++) {
      const x = Math.random() * W;
      const landY = Math.random() * H;
      raindrops.push({
        x,
        landY,
        y: landY - (30 + Math.random() * 40),
        speed: 400 + Math.random() * 200,
      });
    }
    for (let i = raindrops.length - 1; i >= 0; i--) {
      const d = raindrops[i];
      d.y += d.speed * dt;
      if (d.y >= d.landY) {
        if (inChannel(d.x, d.landY)) spawnRipple(d.x, d.landY);
        raindrops.splice(i, 1);
        continue;
      }
      ctx.strokeStyle = "rgba(200,220,255,0.5)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(d.x, d.y);
      ctx.lineTo(d.x - 2, d.y - 10);
      ctx.stroke();
    }
  }

  // ---------- Ripples (rain hitting the water) ----------
  const ripples = [];
  function spawnRipple(x, y) {
    ripples.push({
      x,
      y,
      start: performance.now(),
      duration: 650 + Math.random() * 350,
      maxRadius: 12 + Math.random() * 8,
    });
  }

  function drawRipples(now) {
    for (let i = ripples.length - 1; i >= 0; i--) {
      const rp = ripples[i];
      const t = (now - rp.start) / rp.duration;
      if (t >= 1) {
        ripples.splice(i, 1);
        continue;
      }
      // Two staggered rings per splash for a richer, more organic ripple.
      for (const delay of [0, 0.25]) {
        const rt = t - delay;
        if (rt <= 0) continue;
        const rNorm = Math.min(1, rt / (1 - delay));
        const radius = rNorm * rp.maxRadius;
        const alpha = (1 - rNorm) * 0.55;
        ctx.beginPath();
        ctx.strokeStyle = `rgba(225,242,255,${alpha.toFixed(2)})`;
        ctx.lineWidth = 1.3 * (1 - rNorm) + 0.3;
        ctx.arc(rp.x, rp.y, radius, 0, Math.PI * 2);
        ctx.stroke();
      }
      // Tiny bright flash right at impact.
      if (t < 0.15) {
        ctx.fillStyle = `rgba(255,255,255,${(0.5 * (1 - t / 0.15)).toFixed(2)})`;
        ctx.beginPath();
        ctx.arc(rp.x, rp.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  // ---------- Main loop ----------
  let lastTime = performance.now();
  let fpsAccum = 0;
  let fpsFrames = 0;
  let fpsDisplay = 0;

  function frame(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;

    // Gradually adjust particle count toward the slider target.
    if (particles.length < targetCount) {
      const toAdd = Math.min(targetCount - particles.length, 40);
      for (let i = 0; i < toAdd; i++) particles.push(makeParticle());
    } else if (particles.length > targetCount) {
      particles.length = Math.max(targetCount, particles.length - 40);
    }

    for (let i = 0; i < particles.length; i++) stepParticle(particles[i], dt);

    // Redraw static banks, then dynamic layers on top.
    ctx.drawImage(bg, 0, 0);

    if (flowFieldCheck.checked) drawFlowField();

    // Rocks
    for (const r of rocks) {
      const grad = ctx.createRadialGradient(
        r.x - r.r * 0.3,
        r.y - r.r * 0.3,
        1,
        r.x,
        r.y,
        r.r
      );
      grad.addColorStop(0, "#8a8378");
      grad.addColorStop(1, "#4a453e");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "rgba(0,0,0,0.35)";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // Particles: draw as short streaks for a flowing look, plus foam near rocks.
    ctx.lineCap = "round";
    for (const p of particles) {
      const row = Math.min(H - 1, Math.max(0, Math.round(p.y)));
      const x = centerX[row] + p.offset;
      const speedMag = Math.hypot(p.voffset, p.vy);
      const alpha = Math.min(0.85, 0.35 + speedMag / (flowSpeed * 2));
      ctx.strokeStyle = `rgba(210,235,255,${alpha.toFixed(2)})`;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.moveTo(p.px, p.py);
      ctx.lineTo(x, p.y);
      ctx.stroke();
    }

    // Foam around rocks
    ctx.fillStyle = "rgba(255,255,255,0.5)";
    for (const r of rocks) {
      for (let a = 0; a < 10; a++) {
        const ang = (a / 10) * Math.PI * 2 + now * 0.0005;
        const rad = r.r + 4 + Math.sin(now * 0.003 + a) * 2;
        ctx.beginPath();
        ctx.arc(
          r.x + Math.cos(ang) * rad,
          r.y + Math.sin(ang) * rad,
          1,
          0,
          Math.PI * 2
        );
        ctx.fill();
      }
    }

    drawRipples(now);
    updateRain(dt);

    // FPS
    fpsAccum += dt;
    fpsFrames++;
    if (fpsAccum >= 0.5) {
      fpsDisplay = Math.round(fpsFrames / fpsAccum);
      fpsAccum = 0;
      fpsFrames = 0;
      statFps.textContent = String(fpsDisplay);
      statParticles.textContent = String(particles.length);
      statRocks.textContent = String(rocks.length);
    }

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
})();
