# Deploying the Mansam Chatbot on Render

This guide deploys the current Mansam chatbot as a Render web service. Render
provides the public HTTPS URL, so no LocalTunnel is needed.

## What will be deployed

- English and Arabic chatbot conversation
- Live Mansam catalogue search
- Perfume recommendations, comparison, and list requests
- Arabic and English TTS endpoint at `/api/tts`
- Voice input from supported browsers
- Verified Mansam product links

## Before starting

The project must be pushed to a GitHub or GitLab repository that your Render
account can access. Do not commit Hugging Face tokens or other secrets.

The Render configuration is already included in:

```text
render.yaml
```

## Step 1: Upload the project to GitHub

Create a private repository and upload the complete project folder, including:

```text
server.py
sync_live_catalog.py
requirements.txt
render.yaml
dream.html
discover.html
gift.html
voucher.html
js/
data/
general_qa_intents.json
```

Do not upload `.env` files or API tokens.

## Step 2: Create the Render service

1. Open [Render](https://render.com) and sign in.
2. Select **New** and choose **Blueprint**.
3. Connect the GitHub or GitLab repository.
4. Select the branch containing `render.yaml`.
5. Review the service name `mansam-chatbot`.
6. Click **Apply**.

Render will automatically run:

```text
pip install -r requirements.txt
python3 server.py
```

The server automatically uses Render's `PORT` value and listens on
`0.0.0.0`, which Render requires.

## Step 3: Add optional Hugging Face settings

The chatbot works with its built-in grounded RAG response without Hugging Face.
If a Hugging Face model should phrase responses, open the Render service,
select **Environment**, add the secret variables, save, and redeploy.

For the Hugging Face Router:

```text
HF_TOKEN=your_new_hugging_face_token
HF_MODEL=Qwen/Qwen3.8-27B:deepinfra
```

For the authenticated Gradio Space instead:

```text
HF_GRADIO_SPACE=https://akhaliq-glm-5-3-flash.hf.space
HF_GRADIO_API_NAME=/answer
HF_GRADIO_TOKEN=your_new_hugging_face_token
```

Use a newly generated token and keep it only in Render's secret environment
variables. Never put it in `render.yaml`, HTML, JavaScript, or GitHub.

## Step 4: Open and test the Render URL

After deployment, Render shows a URL similar to:

```text
https://mansam-chatbot.onrender.com
```

Open:

```text
https://YOUR-RENDER-URL.onrender.com/dream.html
```

Test these messages:

```text
suggest me
I want a perfume for my girlfriend
compare Aala Sathi Al Qamar with Hamsa
give me the list of all perfumes for women
```

Switch to Arabic and test an Arabic perfume question. Select Voice and allow
microphone permission when the browser asks.

Test the API directly if needed:

```bash
curl -i -X POST https://YOUR-RENDER-URL.onrender.com/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"suggest me","language":"en"}'
```

Expected result: HTTP `200` with an `answer` and product links for a perfume
request.

## Important Render notes

- The free Render plan may sleep after inactivity. The first request after
  sleeping can take longer while the service starts.
- Live catalogue refresh runs in the background every five minutes.
- Product data is read from the public Mansam API and cached in the service
  folder.
- The Render URL is suitable for testing. For production, add a custom domain
  in Render and update `MANSAM_SITE_URL` to the production Mansam domain.
- Browser microphone access requires HTTPS. The Render URL already uses HTTPS.

## Troubleshooting

Open the Render service and check **Logs**.

- **Health check failed:** confirm `render.yaml` is in the repository root and
  the service uses `python3 server.py`.
- **Page opens but chat fails:** check that `/api/chat` is served by the same
  Render service and that the browser is using the Render URL, not localhost.
- **Arabic speech does not play:** allow microphone/audio permissions and test
  `/api/tts`; the browser uses an installed Arabic voice when available.
- **Old products appear:** wait for the background refresh or trigger a new
  deployment after running `python3 sync_live_catalog.py` locally.
- **Hugging Face error:** verify the secret token and Space API name. The
  chatbot falls back to its local RAG response if the model is unavailable.
