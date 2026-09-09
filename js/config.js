window.MANSAM_CONFIG = window.MANSAM_CONFIG || {};

window.MANSAM_CONFIG.arabicTtsEndpoint =
  window.MANSAM_CONFIG.arabicTtsEndpoint || "/api/tts";

window.MANSAM_CONFIG.localArabicTtsEndpoint =
  window.MANSAM_CONFIG.localArabicTtsEndpoint || "/api/tts";

window.MANSAM_CONFIG.fileArabicTtsEndpoint =
  window.MANSAM_CONFIG.fileArabicTtsEndpoint || "http://127.0.0.1:5501/api/tts";

// Do not point this at an unofficial third-party browser TTS URL. Such URLs can
// return HTML and be blocked as non-audio by modern browser security policies.
window.MANSAM_CONFIG.arabicTtsFallbackEndpoint =
  window.MANSAM_CONFIG.arabicTtsFallbackEndpoint || "";
