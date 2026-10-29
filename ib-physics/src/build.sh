#!/bin/bash
set -e
S=/tmp/claude-0/-home-user-claude/9e2d4e46-2cc0-541d-86cb-d64606be6587/scratchpad
cd $S/work
rm -rf $S/work/un && cp -r $S/orig/un $S/work/un
python3 pre.py un ch2.txt
python3 restyle.py un out
python3 post.py un ch2.txt out
python3 finish.py un /root/.fonts/orig
python3 compact.py un out
cd un && rm -f ../guide.docx && zip -qXr ../guide.docx '[Content_Types].xml' _rels docProps word
