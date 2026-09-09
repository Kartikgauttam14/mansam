const express = require("express");
const { PollyClient, SynthesizeSpeechCommand } = require("@aws-sdk/client-polly");

const router = express.Router();

const polly = new PollyClient({
  region: process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION || "me-south-1"
});

async function streamToBuffer(stream) {
  const chunks = [];

  for await (const chunk of stream) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }

  return Buffer.concat(chunks);
}

router.get("/api/tts", async (req, res) => {
  const text = String(req.query.q || "").trim();
  const language = String(req.query.tl || "ar").toLowerCase();

  if (!text) {
    return res.status(400).json({ error: "Missing q text parameter" });
  }

  if (text.length > 1400) {
    return res.status(413).json({ error: "Text is too long for one TTS request" });
  }

  const isArabic = language.startsWith("ar");
  const voiceId = isArabic
    ? process.env.POLLY_ARABIC_VOICE || "Zeina"
    : process.env.POLLY_ENGLISH_VOICE || "Joanna";
  const engine = process.env.POLLY_ENGINE || "standard";

  try {
    const command = new SynthesizeSpeechCommand({
      Text: text,
      OutputFormat: "mp3",
      VoiceId: voiceId,
      Engine: engine
    });

    const response = await polly.send(command);
    const audio = await streamToBuffer(response.AudioStream);

    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Content-Length", audio.length);
    res.setHeader("Cache-Control", "public, max-age=86400");
    return res.status(200).send(audio);
  } catch (error) {
    console.error("Polly TTS failed:", error);
    return res.status(502).json({ error: "TTS request failed" });
  }
});

module.exports = router;
