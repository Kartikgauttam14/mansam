# Deploying the Mansam Chatbot on the Existing AWS Server

This guide explains how to add the Mansam bilingual fragrance chatbot to the
existing AWS website. It does not create a new AWS server.

## What this chatbot needs

The chatbot is already added to the Mansam pages. The browser sends customer
questions to this API on the same domain:

```text
POST /api/chat
```

The API returns English or Arabic answers, perfume recommendations, live
catalogue information, and the suggested product link.

The chatbot supports natural conversation, automatic recipient-gender hints
such as girlfriend/wife or boyfriend/husband, perfume comparisons, perfume
lists, English and Arabic voice input, and read-aloud responses.

The chatbot can remember a small fragrance preference profile during the
customer's browser session and across the Mansam pages. It stores only
fragrance preferences and recent product IDs in browser storage, not the raw
conversation. Customers can clear this memory from the chat header.

There is no need to create a new AWS server. Run the chatbot on the existing
AWS machine and let the existing Nginx website forward `/api/chat` to it.

## Files to upload

Copy these files from this project to the existing server. Example server path:

```text
/opt/mansam-chatbot/
```

Required backend files:

```text
server.py
sync_live_catalog.py
data/product-knowledge.json
data/live-catalog.json
data/live-perfumes.json
data/general-chat-intents.json
general_qa_intents.json
```

Optional when using a Hugging Face Gradio Space:

```text
requirements.txt
```

Required frontend files:

```text
js/chatbot.js
dream.html
discover.html
gift.html
voucher.html
```

Also upload the existing image, font, language, and JavaScript files used by
the Mansam pages. If the main website is Angular, deploy the frontend files in
the current Angular asset folder as usual.

## Step 1: Prepare the server folder

SSH into the existing AWS server and run:

```bash
sudo mkdir -p /opt/mansam-chatbot
sudo chown -R $USER:$USER /opt/mansam-chatbot
```

Upload the required files into `/opt/mansam-chatbot`.

The server needs Python 3. Check it with:

```bash
python3 --version
```

No additional Python packages are required for the built-in local RAG chatbot
or the Hugging Face Router option. If the optional Hugging Face Gradio Space
option is enabled, install its client package:

```bash
cd /opt/mansam-chatbot
python3 -m pip install -r requirements.txt
```

## Step 2: Download the current Mansam product catalogue

Move to the uploaded folder:

```bash
cd /opt/mansam-chatbot
```

For UAT, run:

```bash
export MANSAM_SITE_URL=https://uatuae.mansamworld.com
python3 sync_live_catalog.py
```

For production, replace the UAT URL with the production Mansam URL before
running the command.

This creates or updates `data/live-catalog.json`. It contains the product
names, Arabic and English descriptions, notes, prices, stock status, and
product-page links used by the chatbot.

The same command also creates `data/live-perfumes.json`, a perfume-only list
used to prioritize fragrance recommendations. Do not manually edit these
generated files.

During normal operation, the server starts a background refresh before chat
requests when the catalogue is older than five minutes. The chat reply uses
the last successful catalogue immediately, so customers do not wait for the
website refresh. This interval can be changed with
`MANSAM_LIVE_REFRESH_SECONDS`.

## Step 3: Run the chatbot as a service

### Optional: configure a Hugging Face Gradio Space

Use this only when the chatbot should call the authenticated `/answer` endpoint
of a Gradio Space. Create a private environment file:

```bash
sudo install -m 600 -o root -g root /dev/null /etc/mansam-chatbot.env
sudo nano /etc/mansam-chatbot.env
```

Add the following values. Use a newly created Hugging Face token; do not add it
to frontend files or commit it to the project:

```text
HF_GRADIO_SPACE=https://akhaliq-glm-5-3-flash.hf.space
HF_GRADIO_API_NAME=/answer
HF_GRADIO_TOKEN=hf_your_new_token
HF_TIMEOUT_SECONDS=20
```

If these variables are not configured, the chatbot uses its existing Hugging
Face Router option when `HF_TOKEN` is set, otherwise it uses the built-in local
RAG response. A rejected or unavailable Gradio Space automatically falls back
to the local response.

Create this file on the server:

```text
/etc/systemd/system/mansam-chatbot.service
```

Paste the following content:

```ini
[Unit]
Description=Mansam Chatbot API
After=network-online.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mansam-chatbot
Environment=MANSAM_HOST=127.0.0.1
Environment=MANSAM_PORT=5501
Environment=MANSAM_OPEN_BROWSER=false
Environment=MANSAM_SITE_URL=https://uatuae.mansamworld.com
Environment=MANSAM_LIVE_REFRESH_SECONDS=300
EnvironmentFile=-/etc/mansam-chatbot.env
ExecStart=/usr/bin/python3 /opt/mansam-chatbot/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Important:

- Change `www-data` if the current web server uses another Linux user.
- Change `MANSAM_SITE_URL` to the production domain when deploying to
  production.
- Keep `MANSAM_HOST=127.0.0.1`. This ensures port `5501` is private and cannot
  be reached directly from the internet.

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mansam-chatbot
sudo systemctl status mansam-chatbot
```

The service should show as `active (running)`.

## Step 4: Add the Nginx API route

Open the existing Nginx configuration for the Mansam domain. Inside the current
`server { ... }` block, add this:

```nginx
location = /api/chat {
    proxy_pass http://127.0.0.1:5501/api/chat;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    client_max_body_size 16k;
}

location = /api/tts {
    proxy_pass http://127.0.0.1:5501/api/tts;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
}
```

If the existing website already has a working `/api/tts` route, keep that
route instead of adding a second one. The public `/api/chat` route must reach
the chatbot service, and `/api/tts` must reach a working Arabic/English TTS
service.

Test and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Step 5: Test before sharing with customers

Test the private chatbot service on the server:

```bash
curl -i -X POST http://127.0.0.1:5501/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"I need a fresh office perfume for men","language":"en"}'
```

Expected result:

- HTTP status `200`
- An `answer` in JSON
- A `productLinks` value containing a Mansam product page URL

Then test the public domain:

```bash
curl -i -X POST https://YOUR_DOMAIN/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"أريد عطراً دافئاً بالعود","language":"ar"}'
```

Also test these chatbot requests:

```text
suggest me
compare Aala Sathi Al Qamar with Hamsa
give me the list of all perfumes for women
I want to buy a perfume for my girlfriend
```

The first request should return a Mansam perfume, the comparison request
should return two products, and the list request should return multiple live
product links.

Finally, open the deployed Mansam page in a browser:

1. Open Chat.
2. Choose English or Arabic.
3. Ask for a perfume recommendation.
4. Ask a follow-up question such as `What are its notes and price?`.
5. Check that `View perfume` or `عرض العطر` opens the correct Mansam product.
6. Select Voice, allow microphone access, and test an English and Arabic
   request. On HTTPS, Chrome or Edge can use browser speech recognition.

## Updating products later

Run these commands whenever products, prices, or availability change:

```bash
cd /opt/mansam-chatbot
export MANSAM_SITE_URL=https://uatuae.mansamworld.com
python3 sync_live_catalog.py
sudo systemctl restart mansam-chatbot
```

Use the production Mansam URL instead of the UAT URL for production.

## If something does not work

Check the chatbot service logs:

```bash
sudo systemctl status mansam-chatbot
sudo journalctl -u mansam-chatbot -n 100 --no-pager
```

Check Nginx:

```bash
sudo nginx -t
```

Common causes:

- `/api/chat` returns `404`: the Nginx route is missing or in the wrong server
  block.
- Chatbot shows an error: the `mansam-chatbot` service is stopped or cannot
  read the files in `/opt/mansam-chatbot`.
- Product information is old: run `sync_live_catalog.py`, then restart the
  service.
- Product links open UAT in production: set `MANSAM_SITE_URL` to the production
  domain, refresh the catalogue, and restart the service.
- Voice does not start: use HTTPS or localhost, allow microphone permission,
  and check that Chrome/Edge speech recognition is available. The speaker
  button needs a working `/api/tts` proxy when no Arabic browser voice exists.
- The browser shows a LocalTunnel warning: LocalTunnel is only for temporary
  testing. Use the AWS domain for customer or senior testing.

## Deployment checklist

Before sharing the AWS URL, confirm:

- `sudo systemctl status mansam-chatbot` shows `active (running)`.
- `sudo nginx -t` succeeds.
- `https://YOUR_DOMAIN/api/chat` returns HTTP `200` for an English request.
- An Arabic request returns Arabic text and does not read only numbers.
- A perfume product link opens the correct product page.
- Microphone permission is allowed on the HTTPS domain.
