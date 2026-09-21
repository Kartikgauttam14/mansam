(function (root) {
  function route(message, step, saved = {}) {
    const text = String(message).trim().toLowerCase().replace(/[٠-٩]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d));
    // Information questions must not become preferences, even when they mention a note or size.
    const question = /^(what|which|how|why|where|when|do you|does|is|are|can you explain|tell me about)\b/.test(text) || /^(ما |ماذا|كيف|هل |أين|اين|متى|اشرح)/.test(text) || /[?؟]/.test(text)
      || /\b(compare|price|delivery|shipping|stock|notes in|notes of|notes on|similar|like this|category|list)\b|قارن|السعر|توصيل|شحن|مشابه/.test(text);
    if (question) return { kind: "question", patch: {}, next: step };
    const patch = {};
    if (/\b(gift|present|wife|husband|girlfriend|boyfriend)\b|هدية|هديه|زوجتي|زوجي/.test(text)) patch.purpose = "gift";
    if (/\b(myself|for me)\b|لنفسي/.test(text)) patch.purpose = "self";
    if (/\bunisex\b|للجنسين/.test(text)) patch.gender = "unisex";
    else if (/\b(woman|women|female|lady|wife|girlfriend|mother|sister)\b|امرأة|امراه|نساء|نسائي|زوجتي/.test(text)) patch.gender = "female";
    else if (/\b(man|men|male|gentleman|husband|boyfriend|father|brother)\b|لرجل|رجال|رجالي|زوجي/.test(text)) patch.gender = "male";
    if (/\b(daily|everyday|office|work)\b|يومي/.test(text)) patch.usage = "daily";
    else if (/\b(occasion|wedding|party|evening|birthday)\b|مناسبة|مناسبه|زفاف|حفلة/.test(text)) patch.usage = "occasion";
    const size = text.match(/\b(\d+)\s*(?:ml\b|مل)/) || (step === "size" ? text.match(/^(\d+)$/) : null);
    if (size) patch.sizeMl = Number(size[1]);
    if (/\b(oud|rose|musk|floral|woody|fresh|citrus|vanilla|amber|jasmine|sandalwood)\b|عود|ورد|مسك|زهري|منعش|فانيليا|عنبر|ياسمين/.test(text)) patch.notes = message;
    const merged = { ...saved, ...patch };
    const changed = Object.keys(patch).length > 0;
    if (!changed) return { kind: "question", patch, next: step };
    const next = !merged.gender ? "gender" : !merged.usage ? "usage" : !merged.notes ? 3 : !merged.sizeMl ? "size" : "complete";
    return { kind: next === "complete" ? "recommend" : "answer", patch, next };
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { route };
  else root.MansamConversationRouter = { route };
})(typeof window !== "undefined" ? window : globalThis);
