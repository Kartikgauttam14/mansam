Mansam Perfume Finder - Run Instructions
========================================

Use this folder as a website, not by double-clicking the HTML files.

How to run on Windows
---------------------
1. Open this folder.
2. Double-click run-website.bat.
3. A browser will open at:
   http://127.0.0.1:5501/dream.html
4. Keep the black server window open while testing.

Why this is required
--------------------
Arabic text, language JSON files, API calls, and the Arabic speaker work best
from the local website URL.

The Arabic speaker uses this local endpoint:
http://127.0.0.1:5501/api/tts

That endpoint avoids browser blocking and allows Arabic audio to play.

Angular/AWS note
----------------
For Angular or AWS deployment, do not depend on server.py as a production
server. The speaker reads its production endpoint from js/config.js:

/api/tts

Point that value to an existing backend/API route in your Angular/AWS app.
See ANGULAR-AWS-INTEGRATION.txt for the full workflow.

Requirements
------------
- Python 3 installed.
- Internet connection for recommendation APIs and Arabic TTS audio.

If Python is missing
--------------------
Install Python 3 from:
https://www.python.org/downloads/

If port 5501 is busy
--------------------
Close any other local server using port 5501, then run run-website.bat again.
