(function () {
  const config = window.MANSAM_CONFIG || {};
  const endpoint = config.chatEndpoint || "/api/chat";
  const STORAGE_KEYS = { profile: "mansam-fragrance-memory", conversation: "mansam-chat-session", language: "mansam-chat-language", speaker: "mansam-chat-speaker" };
  const STORAGE_VERSION = 2;
  const state = { open: false, busy: false, language: null, awaitingName: false, customerName: "", flowStep: 1, contextProductIds: [], profile: { name: "", preferences: [], productIds: [] }, conversation: [], inputMode: "chat", recognition: null, recorder: null, voiceStream: null, voiceSession: null, listening: false, speechAudio: null, speakerEnabled: true };

  const copy = {
    en: { title: "Mansam Concierge", intro: "Your personal fragrance guide", placeholder: "Describe a note, mood, or occasion", namePlaceholder: "Enter your name", send: "Send", askName: "Welcome to Mansam. May I have your name?", greeting: "Welcome to Mansam – House of Fine Fragrances, {name} sir.\n\nThank you for visiting us.\n\nI'm your AI fragrance assistant, working alongside our fragrance specialists to make your experience simple, personal, and memorable.\n\nWith expert knowledge of fine fragrances, we're here to answer your questions, recommend the perfect fragrance for you or your loved ones, and help you discover a scent that truly reflects your personality.\n\nWhenever you're ready, let's begin your fragrance journey.", askBoutique: "I can help you find the right fragrance, or answer anything about scents, prices, or delivery. Have you visited our boutique before, or is this your first time?", askGift: "Allow me to give you an idea of what we have. Would you like the perfume for yourself, or as a gift?", askReturning: "Welcome back to Mansam! Which fragrance did you enjoy previously, or what note are you looking for today?", askNotes: "Do you lean more toward oud, rose, or musk? And which note do you not enjoy?", askOccasionLady: "Wonderful — for a lady, then. Is this for a special occasion, or everyday wear?", askOccasionGentleman: "Wonderful — for a gentleman, then. Is this for a special occasion, or everyday wear?", askOccasionSelf: "Wonderful — for yourself. Is this for a special occasion, or everyday wear?", askSpecialGentleman: "A special occasion for him — a beautiful moment to mark. Sarhan brings bold leather and oud, quiet confidence for the evening. Or Shatha Biladi — powerful oud, deep and noble, for formal gatherings. Which feels closer to him?", askSpecialLady: "A special occasion for her — a beautiful moment to mark. I can guide you toward a graceful floral or warm signature fragrance. Would you prefer something elegant and floral, or rich and sensual?", askEveryday: "For everyday wear, I can keep it easy and versatile. Would you prefer something fresh and clean, or warm and memorable?", btnMyself: "For Myself", btnSomeoneElse: "Someone Else", btnLady: "For a Lady", btnGentleman: "For a Gentleman", btnSpecial: "Special Occasion", btnEveryday: "Everyday Wear", btnFirstTime: "First Time", btnVisitedBefore: "Visited Before", btnForMyself: "For Myself", btnAsGift: "As a Gift", btnOud: "Oud", btnRose: "Rose", btnMusk: "Musk", btnFresh: "Fresh Citrus", one: "Which perfume has rose and oud?", two: "I want a fresh daily fragrance.", viewProduct: "View perfume", error: "I could not reach the fragrance guide. Please try again.", chat: "Chat", voice: "Voice", listen: "Listening...", tapToSpeak: "Tap to speak", voicePrompt: "Tell me what you are looking for", voiceHint: "Speak in English or Arabic", thinking: "Finding the right fragrance", available: "Available now", readAloud: "Read answer aloud", speakerOn: "Turn speaker off", speakerOff: "Turn speaker on", clearMemory: "Clear fragrance memory", voiceUnavailable: "Voice input is not available in this browser.", noSpeech: "I did not hear anything. Tap the microphone and try again.", voiceError: "Voice input could not start. Please try again." },
    ar: { title: "مستشار منسَم", intro: "دليلك الشخصي لاكتشاف العطور", placeholder: "اكتب نفحاتك أو مزاجك أو مناسبتك", namePlaceholder: "اكتب اسمك", send: "إرسال", askName: "مرحباً بك في منسَم. ما اسمك؟", greeting: "مرحباً بك في مانسام – دار العطور الفاخرة، يا {name} سيدي.\n\nشكراً لزيارتك.\n\nأنا مساعدك الذكي من مانسام، وأعمل مع خبراء العطور لدينا لنقدم لك تجربة سهلة، شخصية، ولا تُنسى.\n\nبخبرتنا المتخصصة في عالم العطور، يسعدنا مساعدتك، والإجابة على استفساراتك، وترشيح العطر الأنسب لك أو لمن تحب، حتى تجد عطراً يعبر عن شخصيتك بكل تميز.\n\nوحين تكون جاهزاً، لنبدأ رحلتك العطرية.", askBoutique: "يسعدني مساعدتك في العثور على العطر المناسب أو الإجابة عن النفحات والأسعار والتوصيل. هل زرت متجرنا من قبل أم هذه مرتك الأولى؟", askGift: "اسمح لي أن آخذك في جولة سريعة. هل تبحث عن العطر لنفسك أم كهدية؟", askReturning: "أهلاً بك مجدداً في منسَم! ما هو العطر الذي جربته وأعجبك سابقاً، أو ما هي النفحة التي تبحث عنها اليوم؟", askNotes: "هل تميل أكثر إلى العود، الورد، أم المسك؟ وما هي النفحة التي لا تفضلها؟", askOccasionLady: "رائع — العطر لسيدة. هل هو لمناسبة خاصة أم للاستخدام اليومي؟", askOccasionGentleman: "رائع — العطر لرجل. هل هو لمناسبة خاصة أم للاستخدام اليومي؟", askOccasionSelf: "رائع — العطر لك. هل هو لمناسبة خاصة أم للاستخدام اليومي؟", askSpecialGentleman: "مناسبة خاصة له — لحظة جميلة تستحق التمييز. يمنحك عطر سرحان جلداً وعوداً جريئين بثقة هادئة للمساء. أو شذا بلادي — عود قوي وعميق ونبيل للتجمعات الرسمية. أيهما أقرب إليه؟", askSpecialLady: "مناسبة خاصة لها — لحظة جميلة تستحق التمييز. يمكنني ترشيح عطر زهري أنيق أو توقيع دافئ. هل تفضلين رائحة زهرية راقية أم رائحة غنية وحسية؟", askEveryday: "للاستخدام اليومي، أستطيع أن أرشح لك عطراً عملياً ومتعدد الاستخدامات. هل تفضل رائحة منعشة ونظيفة أم دافئة ولافتة؟", btnMyself: "لنفسي", btnSomeoneElse: "لشخص آخر", btnLady: "لسيدة", btnGentleman: "لرجل", btnSpecial: "مناسبة خاصة", btnEveryday: "استخدام يومي", btnFirstTime: "مرتي الأولى", btnVisitedBefore: "زرتكم من قبل", btnForMyself: "لنفسي", btnAsGift: "كهدية", btnOud: "عود", btnRose: "ورد", btnMusk: "مسك", btnFresh: "حمضيات ومنعش", one: "أي عطر يحتوي على الورد والعود؟", two: "أريد عطراً منعشاً للاستخدام اليومي.", viewProduct: "عرض العطر", error: "تعذر الوصول إلى دليل العطور. حاول مرة أخرى.", chat: "كتابة", voice: "صوت", listen: "جارٍ الاستماع...", tapToSpeak: "اضغط للتحدث", voicePrompt: "أخبرني بما تبحث عنه", voiceHint: "تحدث بالعربية أو الإنجليزية", thinking: "نبحث عن العطر المناسب", available: "متاح الآن", readAloud: "استمع إلى الإجابة", speakerOn: "إيقاف صوت المساعد", speakerOff: "تشغيل صوت المساعد", clearMemory: "مسح ذاكرة العطور", voiceUnavailable: "الإدخال الصوتي غير متاح في هذا المتصفح.", noSpeech: "لم أسمع شيئاً. اضغط على الميكروفون وحاول مرة أخرى.", voiceError: "تعذر تشغيل الإدخال الصوتي. حاول مرة أخرى." }
  };

  function language() { return state.language || ((document.documentElement.lang || localStorage.getItem(STORAGE_KEYS.language) || localStorage.getItem("language") || "en").startsWith("ar") ? "ar" : "en"); }
  function detectLanguage(text) { return /[\u0600-\u06FF]/.test(text || "") ? "ar" : "en"; }
  function escapeHtml(value) { return String(value || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;"); }
  function cleanCustomerName(value) {
    let name = String(value || "").replace(/[.!?,،؛]+$/g, "").replace(/\s+/g, " ").trim();
    name = name.replace(/^(?:hi|hello|hey)(?: there)?[,:\s]+/i, "");
    name = name.replace(/^(?:my name is|i am|i'm|im|this is|call me)\s+/i, "");
    name = name.replace(/^(?:اسمي|أنا|انا|هذا اسمي)\s+/i, "");
    return name.slice(0, 40).trim();
  }

  function cleanVoiceTranscript(value) {
    const text = String(value || "").replace(/\s+/g, " ").trim();
    if (!text) return "";
    const words = text.split(" ");
    const collapsed = [];
    words.forEach(word => {
      if (!word) return;
      if (collapsed.length && collapsed[collapsed.length - 1].toLocaleLowerCase() === word.toLocaleLowerCase()) return;
      collapsed.push(word);
    });
    const starters = [
      ["i"], ["hello"], ["hi"], ["hey"], ["i", "need"], ["i", "want"], ["my", "name"], ["this", "is"], ["call", "me"],
      ["please"], ["can", "you"], ["could", "you"], ["أريد"], ["اريد"], ["أحتاج"], ["احتاج"],
      ["مرحبا"], ["مرحباً"], ["أبحث"], ["ابحث"],
    ];
    let lastRepeatedStart = -1;
    starters.forEach(starter => {
      const positions = [];
      for (let index = 0; index <= collapsed.length - starter.length; index += 1) {
        const matches = starter.every((word, offset) => collapsed[index + offset].toLocaleLowerCase() === word.toLocaleLowerCase());
        if (matches) positions.push(index);
      }
      if (positions.length > 1) lastRepeatedStart = Math.max(lastRepeatedStart, positions[positions.length - 1]);
    });
    const trimmed = lastRepeatedStart > 0 ? collapsed.slice(lastRepeatedStart) : collapsed;
    const deduped = [];
    trimmed.forEach(word => {
      deduped.push(word);
      for (let size = Math.min(12, Math.floor(deduped.length / 2)); size >= 1; size -= 1) {
        const start = deduped.length - size * 2;
        const first = deduped.slice(start, start + size).map(item => item.toLocaleLowerCase());
        const second = deduped.slice(start + size).map(item => item.toLocaleLowerCase());
        if (first.length === size && first.join(" ") === second.join(" ")) {
          deduped.splice(start + size, size);
          break;
        }
      }
    });
    return deduped.join(" ").trim();
  }

  function repairVoiceTranscript(value) {
    const text = cleanVoiceTranscript(value);
    // English ASR can hear "gift" as "iftar" in a short request.
    return text.replace(/\b(i\s+(?:need|want)\s+a)\s+(?:iftar|itter)\b/gi, "$1 gift");
  }

  function rememberTurn(role, text) {
    const value = String(text || "").trim();
    if (!value) return;
    state.conversation.push({ role, text: value });
    state.conversation = state.conversation.slice(-8);
    try { sessionStorage.setItem(STORAGE_KEYS.conversation, JSON.stringify({ version: STORAGE_VERSION, turns: state.conversation })); } catch (error) { /* storage may be unavailable */ }
  }

  function loadProfile() {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEYS.profile) || "{}");
      return {
        name: cleanCustomerName(stored.name),
        preferences: Array.isArray(stored.preferences) ? stored.preferences.slice(0, 8) : [],
        productIds: Array.isArray(stored.productIds) ? stored.productIds.slice(0, 3) : [],
      };
    } catch (error) { return { name: "", preferences: [], productIds: [] }; }
  }

  function loadConversation() {
    try {
      const stored = JSON.parse(sessionStorage.getItem(STORAGE_KEYS.conversation) || "{}");
      const turns = Array.isArray(stored.turns) ? stored.turns : Array.isArray(stored) ? stored : [];
      return turns.filter(turn => turn && (turn.role === "customer" || turn.role === "assistant") && String(turn.text || "").trim())
        .filter(turn => !["Hello. I can help you discover Mansam fragrances from the catalogue.", "مرحباً. يمكنني مساعدتك في اكتشاف عطور منسَم من الكتالوج."].includes(String(turn.text).trim()))
        .map(turn => ({ role: turn.role, text: String(turn.text).trim().slice(0, 1200) })).slice(-8);
    } catch (error) { return []; }
  }

  function saveProfile(memory) {
    if (!memory || typeof memory !== "object") return;
    state.profile = {
      name: memory.name ? cleanCustomerName(memory.name) : state.profile.name,
      preferences: Array.isArray(memory.preferences) ? memory.preferences.slice(0, 8) : state.profile.preferences,
      productIds: Array.isArray(memory.productIds) ? memory.productIds.slice(0, 3) : state.profile.productIds,
    };
    state.contextProductIds = state.profile.productIds.slice(0, 3);
    try { localStorage.setItem(STORAGE_KEYS.profile, JSON.stringify({ version: STORAGE_VERSION, ...state.profile })); } catch (error) { /* storage may be unavailable */ }
  }

  function updateSuggestions() {
    const suggestionsContainer = document.querySelector(".mansam-chat__suggestions");
    if (!suggestionsContainer) return;
    const lang = language();
    const c = copy[lang];
    let buttons = [];

    if (state.awaitingName) {
      buttons = [];
    } else if (state.flowStep === 1) {
      buttons = [
        { text: c.btnFirstTime },
        { text: c.btnVisitedBefore }
      ];
    } else if (state.flowStep === 2) {
      buttons = [
        { text: c.btnForMyself },
        { text: c.btnAsGift }
      ];
    } else if (state.flowStep === 3 || state.flowStep === "2_returning") {
      buttons = [
        { text: c.btnOud },
        { text: c.btnRose },
        { text: c.btnMusk },
        { text: c.btnFresh }
      ];
    } else {
      buttons = [
        { text: lang === "ar" ? "أي عطر يحتوي على الورد والعود؟" : "Which perfume has rose and oud?" },
        { text: lang === "ar" ? "أريد عطراً منعشاً للاستخدام اليومي." : "I want a fresh daily fragrance." }
      ];
    }

    suggestionsContainer.innerHTML = buttons.map(b => `<button type="button" class="mansam-chat__suggestion-chip">${escapeHtml(b.text)}</button>`).join("");
    suggestionsContainer.querySelectorAll("button").forEach(btn => {
      btn.addEventListener("click", () => send(btn.textContent));
    });
  }

  function clearMemory() {
    state.profile = { name: "", preferences: [], productIds: [] };
    state.customerName = "";
    state.awaitingName = false;
    state.flowStep = 1;
    state.contextProductIds = [];
    state.conversation = [];
    try {
      localStorage.removeItem(STORAGE_KEYS.profile);
      sessionStorage.removeItem(STORAGE_KEYS.conversation);
    } catch (error) { /* storage may be unavailable */ }
    const messages = document.querySelector(".mansam-chat__messages");
    if (messages) {
      messages.innerHTML = "";
      if (state.language) {
        addMessage(copy[language()].askBoutique, "assistant", [], true);
        updateSuggestions();
      }
    }
  }

  function safeProductUrl(value) {
    try {
      const url = new URL(String(value));
      return url.protocol === "https:" && url.hostname === "uatuae.mansamworld.com" ? url.href : "";
    } catch (error) { return ""; }
  }

  function cleanSpeechText(text) {
    return String(text || "").replace(/https?:\/\/\S+/gi, "").replace(/\bwww\.\S+/gi, "").replace(/[\*_`#]/g, "").replace(/\s+/g, " ").trim();
  }

  function conversationalSpeechText(text) {
    return cleanSpeechText(text)
      .replace(/\s*:\s*/g, ". ")
      .replace(/\s*[|•·]\s*/g, ". ")
      .replace(/\s*[-–—]\s*/g, ", ")
      .replace(/\.{2,}/g, ".")
      .trim();
  }

  function stopSpeaking() {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    if (state.speechAudio) {
      state.speechAudio.pause();
      state.speechAudio.src = "";
      state.speechAudio = null;
    }
  }

  function preferredVoice(lang) {
    const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    const prefix = lang === "ar" ? "ar" : "en";
    const naturalNames = lang === "ar"
      ? ["hoda", "naayf", "natural", "online", "google", "microsoft"]
      : ["natural", "online", "google", "microsoft", "samantha", "alex", "karen", "daniel"];
    const matching = voices.filter(voice => voice.lang.toLowerCase().startsWith(prefix));
    return matching.sort((first, second) => {
      const score = voice => naturalNames.reduce((total, term, index) =>
        total + (voice.name.toLowerCase().includes(term) ? naturalNames.length - index : 0), 0);
      return score(second) - score(first);
    })[0] || null;
  }

  function speakText(text, requestedLanguage) {
    if (!state.speakerEnabled) return;
    const lang = requestedLanguage || detectLanguage(text);
    const speechText = conversationalSpeechText(text);
    if (!speechText) return;
    stopSpeaking();
    const browserVoice = preferredVoice(lang);
    if (window.speechSynthesis && (browserVoice || lang === "en")) {
      const utterance = new SpeechSynthesisUtterance(speechText);
      utterance.lang = browserVoice ? browserVoice.lang : "en-US";
      if (browserVoice) utterance.voice = browserVoice;
      utterance.rate = lang === "ar" ? 0.86 : 0.92;
      utterance.pitch = lang === "ar" ? 1.02 : 1.04;
      utterance.volume = 0.96;
      window.speechSynthesis.speak(utterance);
      return;
    }
    const ttsEndpoint = config.arabicTtsEndpoint || "/api/tts";
    if (lang === "ar" && ttsEndpoint) {
      const separator = ttsEndpoint.includes("?") ? "&" : "?";
      const audio = new Audio(`${ttsEndpoint}${separator}tl=ar&q=${encodeURIComponent(speechText)}`);
      state.speechAudio = audio;
      audio.play().catch(() => {});
    }
  }

  function addMessage(text, role, sources, isWelcome, productLinks) {
    const messages = document.querySelector(".mansam-chat__messages");
    if (!messages) return;
    const messageLanguage = detectLanguage(text) === "ar" ? "ar" : language();
    const sourceText = (sources || []).map(source => escapeHtml(source.name[messageLanguage] || source.name.en || "")).join(" · ");
    const productLinkText = (productLinks || []).map(product => {
      const url = safeProductUrl(product.url);
      const name = escapeHtml(product.name?.[messageLanguage] || product.name?.en || "");
      return url && name ? `<a class="mansam-chat__product-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer"><span>${escapeHtml(copy[messageLanguage].viewProduct)}</span><strong>${name}</strong><b aria-hidden="true">&rarr;</b></a>` : "";
    }).join("");
    const assistantMark = role === "assistant" ? '<span class="mansam-chat__avatar" aria-hidden="true">M</span>' : "";
    const readAloud = escapeHtml(copy[messageLanguage].readAloud);
    messages.insertAdjacentHTML("beforeend", `<article class="mansam-chat__message mansam-chat__message--${role}${isWelcome ? " mansam-chat__message--welcome" : ""}" aria-label="${role === "assistant" ? "Mansam" : "Customer"}"><div class="mansam-chat__message-row">${assistantMark}<div class="mansam-chat__bubble"><p>${escapeHtml(text)}</p>${productLinkText}${role === "assistant" && !isWelcome ? `<button class="mansam-chat__speak" type="button" title="${readAloud}" aria-label="${readAloud}">&#128266;</button>` : ""}${sourceText ? `<small>${sourceText}</small>` : ""}</div></div></article>`);
    const speakButton = messages.lastElementChild.querySelector(".mansam-chat__speak");
    if (speakButton) speakButton.addEventListener("click", () => speakText(text, messageLanguage));
    messages.scrollTop = messages.scrollHeight;
  }

  function setThinking(visible) {
    const messages = document.querySelector(".mansam-chat__messages");
    if (!messages) return;
    const existing = messages.querySelector(".mansam-chat__thinking");
    if (!visible) { if (existing) existing.remove(); return; }
    if (existing) return;
    messages.insertAdjacentHTML("beforeend", `<div class="mansam-chat__thinking" role="status"><span class="mansam-chat__avatar" aria-hidden="true">M</span><span><i></i><i></i><i></i><em>${escapeHtml(copy[language()].thinking)}</em></span></div>`);
    messages.scrollTop = messages.scrollHeight;
  }

  function refreshLanguage() {
    if (!state.language) return;
    const lang = language();
    const text = copy[lang];
    const panel = document.querySelector(".mansam-chat");
    const launcher = document.querySelector(".mansam-chat-launcher");
    if (!panel || !launcher) return;
    panel.lang = lang;
    panel.dir = lang === "ar" ? "rtl" : "ltr";
    const titleEl = panel.querySelector("[data-chat-title]"); if (titleEl) titleEl.textContent = text.title;
    const introEl = panel.querySelector("[data-chat-intro]"); if (introEl) introEl.textContent = text.intro;
    const availEl = panel.querySelector("[data-chat-availability]"); if (availEl) availEl.textContent = text.available;
    const inputEl = panel.querySelector("[data-chat-input]"); if (inputEl) inputEl.placeholder = state.awaitingName ? text.namePlaceholder : text.placeholder;
    const sendEl = panel.querySelector("[data-chat-send]"); if (sendEl) sendEl.textContent = text.send;
    const oneEl = panel.querySelector("[data-chat-one]"); if (oneEl) oneEl.textContent = text.one;
    const twoEl = panel.querySelector("[data-chat-two]"); if (twoEl) twoEl.textContent = text.two;
    const langSwitchEl = panel.querySelector("[data-chat-language-switcher]"); if (langSwitchEl) langSwitchEl.value = lang;
    const modeChatEl = panel.querySelector("[data-chat-mode='chat']"); if (modeChatEl) modeChatEl.textContent = text.chat;
    const modeVoiceEl = panel.querySelector("[data-chat-mode='voice']"); if (modeVoiceEl) modeVoiceEl.textContent = text.voice;
    const vPromptEl = panel.querySelector("[data-chat-voice-prompt]"); if (vPromptEl) vPromptEl.textContent = text.voicePrompt;
    const vHintEl = panel.querySelector("[data-chat-voice-hint]"); if (vHintEl) vHintEl.textContent = text.voiceHint;
    const vTrigEl = panel.querySelector("[data-chat-voice-trigger]"); if (vTrigEl) { vTrigEl.setAttribute("aria-label", text.tapToSpeak); vTrigEl.title = text.tapToSpeak; }
    const vStatEl = panel.querySelector("[data-chat-voice-status]"); if (vStatEl) vStatEl.textContent = state.listening ? text.listen : "";
    const micEl = panel.querySelector("[data-chat-mic]"); if (micEl) micEl.setAttribute("aria-label", lang === "ar" ? "بدء الإدخال الصوتي" : "Start voice input");
    const closeEl = panel.querySelector(".mansam-chat__close"); if (closeEl) closeEl.setAttribute("aria-label", lang === "ar" ? "إغلاق" : "Close");
    const resetEl = panel.querySelector("[data-chat-reset]"); if (resetEl) { resetEl.setAttribute("aria-label", text.clearMemory); resetEl.title = text.clearMemory; }
    const speakerButton = panel.querySelector("[data-chat-speaker]");
    if (speakerButton) {
      speakerButton.innerHTML = state.speakerEnabled ? "&#128266;" : "&#128263;";
      speakerButton.setAttribute("aria-pressed", String(!state.speakerEnabled));
      speakerButton.setAttribute("aria-label", state.speakerEnabled ? text.speakerOn : text.speakerOff);
      speakerButton.title = state.speakerEnabled ? text.speakerOn : text.speakerOff;
    }
    launcher.setAttribute("aria-label", text.title);
    launcher.title = text.title;
    if (state.recognition) state.recognition.lang = lang === "ar" ? "ar-SA" : "en-US";
    updateSuggestions();
  }

  function setOpen(open) {
    state.open = open;
    const panel = document.querySelector(".mansam-chat");
    const launcher = document.querySelector(".mansam-chat-launcher");
    panel.hidden = !open;
    panel.style.display = open ? "flex" : "none";
    panel.setAttribute("aria-hidden", String(!open));
    launcher.setAttribute("aria-expanded", String(open));
    const launcherLabel = open ? "Close Mansam Concierge" : "Open Mansam Concierge";
    launcher.setAttribute("aria-label", launcherLabel);
    launcher.title = launcherLabel;
    if (!open) stopRecognition();
    if (open) (state.language ? panel.querySelector("[data-chat-input]") : panel.querySelector("[data-chat-language='en']")).focus();
  }

  function chooseLanguage(selectedLanguage) {
    state.language = selectedLanguage;
    try { localStorage.setItem(STORAGE_KEYS.language, selectedLanguage); } catch (error) { /* storage may be unavailable */ }
    const panel = document.querySelector(".mansam-chat");
    panel.querySelector("[data-chat-language-choice]").hidden = true;
    panel.querySelector("[data-chat-conversation]").hidden = false;
    state.customerName = state.profile.name || "";
    state.awaitingName = !state.customerName && !state.conversation.length;
    refreshLanguage();
    panel.querySelector(".mansam-chat__messages").innerHTML = "";
    if (state.conversation.length) {
      state.conversation.forEach(turn => addMessage(turn.text, turn.role, [], false));
    } else {
      state.flowStep = 1;
      addMessage(
        state.awaitingName ? copy[selectedLanguage].askName : `${copy[selectedLanguage].greeting.replace("{name}", state.customerName)}\n\n${copy[selectedLanguage].askBoutique}`,
        "assistant", [], true
      );
    }
    updateSuggestions();
    panel.querySelector("[data-chat-input]").focus();
  }

  function setInputMode(mode) {
    state.inputMode = mode;
    const panel = document.querySelector(".mansam-chat");
    const isVoice = mode === "voice";
    panel.classList.toggle("is-voice-mode", isVoice);
    panel.querySelector("[data-chat-mode='chat']").classList.toggle("is-active", !isVoice);
    panel.querySelector("[data-chat-mode='voice']").classList.toggle("is-active", isVoice);
    panel.querySelector("[data-chat-voice-stage]").hidden = !isVoice;
    panel.querySelector("[data-chat-composer]").hidden = isVoice;
    panel.querySelector("[data-chat-voice-stage-status]").textContent = "";
    if (!isVoice) stopRecognition();
  }

  function toggleSpeaker() {
    state.speakerEnabled = !state.speakerEnabled;
    if (!state.speakerEnabled) stopSpeaking();
    try { localStorage.setItem(STORAGE_KEYS.speaker, state.speakerEnabled ? "on" : "off"); } catch (error) { /* storage may be unavailable */ }
    refreshLanguage();
  }

  function setListening(listening, notice) {
    state.listening = listening;
    const panel = document.querySelector(".mansam-chat");
    if (!panel) return;
    panel.querySelectorAll("[data-chat-mic], [data-chat-voice-trigger]").forEach(button => {
      button.classList.toggle("is-listening", listening);
      button.setAttribute("aria-pressed", String(listening));
    });
    const status = notice || (listening ? copy[language()].listen : "");
    panel.querySelector("[data-chat-voice-status]").textContent = status;
    panel.querySelector("[data-chat-voice-stage-status]").textContent = status;
  }

  function submitVoiceTranscript(session) {
    if (!session || session.submitted) return;
    session.transcript = repairVoiceTranscript(session.transcript);
    if (!session.transcript) return;
    session.submitted = true;
    clearTimeout(session.silenceTimer);
    state.language = detectLanguage(session.transcript);
    refreshLanguage();
    send(session.transcript, true);
  }

  function stopRecognition(submit = true) {
    const session = state.voiceSession;
    if (session) {
      session.cancelled = true;
      clearTimeout(session.silenceTimer);
      clearTimeout(session.endTimer);
      if (submit) submitVoiceTranscript(session);
      else session.submitted = true;
    }
    const recognition = state.recognition;
    const recorder = state.recorder;
    state.recognition = null;
    state.recorder = null;
    state.voiceSession = null;
    if (recognition) {
      try { recognition.stop(); } catch (error) { /* already ended */ }
    }
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
    if (state.voiceStream) {
      state.voiceStream.getTracks().forEach(track => track.stop());
      state.voiceStream = null;
    }
    setListening(false);
  }

  async function startRecorderFallback() {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setListening(false, copy[language()].voiceUnavailable);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const session = { transcript: "", finalTranscript: "", interimTranscript: "", submitted: false, cancelled: false, silenceTimer: null, endTimer: null, chunks: [] };
      state.recorder = recorder;
      state.voiceStream = stream;
      state.voiceSession = session;
      recorder.onstart = () => setListening(true);
      recorder.ondataavailable = event => { if (event.data.size) session.chunks.push(event.data); };
      recorder.onerror = () => setListening(false, copy[language()].voiceError);
      recorder.onstop = async () => {
        if (state.voiceSession !== session || session.cancelled || session.submitted) return;
        state.voiceStream = null;
        stream.getTracks().forEach(track => track.stop());
        setListening(false, copy[language()].thinking);
        try {
          const blob = new Blob(session.chunks, { type: recorder.mimeType || "audio/webm" });
          const urls = resolveApiUrl(config.transcriptionEndpoint || "/api/transcribe");
          let response, lastErr;
          for (const url of urls) {
            try {
              response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": blob.type, "X-Speech-Language": language() },
                body: blob,
              });
              if (response.ok) break;
            } catch (err) { lastErr = err; }
          }
          if (!response || !response.ok) throw lastErr || new Error("Transcription failed");
          const payload = await response.json();
          session.transcript = cleanVoiceTranscript(payload.transcript || "");
          submitVoiceTranscript(session);
        } catch (error) {
          state.recorder = null;
          state.voiceSession = null;
          setListening(false, copy[language()].voiceError);
          console.error("Mansam speech fallback error:", error);
        }
      };
      recorder.start();
    } catch (error) {
      setListening(false, copy[language()].voiceUnavailable);
      console.error("Mansam microphone error:", error);
    }
  }

  function startRecognition() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (state.voiceSession || state.recognition || state.recorder) {
      // The same button is a toggle: click once to listen, click again to
      // submit the current transcript immediately.
      stopRecognition(true);
      return;
    }
    if (!Recognition) { startRecorderFallback(); return; }
    stopSpeaking();
    const recognition = new Recognition();
    const session = { transcript: "", finalTranscript: "", interimTranscript: "", finalSegments: {}, interimSegments: {}, submitted: false, cancelled: false, silenceTimer: null, endTimer: null };
    state.recognition = recognition;
    state.voiceSession = session;
    recognition.lang = language() === "ar" ? "ar-SA" : "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => {
      if (state.voiceSession !== session || session.cancelled) {
        recognition.stop();
        return;
      }
      setListening(true);
    };
    recognition.onspeechstart = () => clearTimeout(session.silenceTimer);
    recognition.onspeechend = () => {
      clearTimeout(session.silenceTimer);
      if (session.transcript) session.silenceTimer = setTimeout(() => submitVoiceTranscript(session), 2000);
    };
    recognition.onresult = event => {
      if (state.voiceSession !== session || session.cancelled) return;
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = result[0].transcript.trim();
        if (result.isFinal) {
          session.finalSegments[index] = transcript;
          delete session.interimSegments[index];
        } else {
          session.interimSegments[index] = transcript;
        }
      }
      session.finalTranscript = Object.keys(session.finalSegments).sort((a, b) => Number(a) - Number(b)).map(index => session.finalSegments[index]).join(" ");
      session.interimTranscript = Object.keys(session.interimSegments).sort((a, b) => Number(a) - Number(b)).map(index => session.interimSegments[index]).join(" ");
      session.transcript = cleanVoiceTranscript(`${session.finalTranscript} ${session.interimTranscript}`);
      const input = document.querySelector("[data-chat-input]");
      if (input) input.value = session.transcript;
      clearTimeout(session.silenceTimer);
    };
    recognition.onerror = event => {
      if (state.voiceSession !== session || session.cancelled) return;
      if (event.error === "aborted") return;
      if (event.error === "no-speech" && session.transcript) {
        submitVoiceTranscript(session);
        return;
      }
      if (["network", "service-not-allowed", "language-not-supported"].includes(event.error)) {
        stopRecognition(false);
        startRecorderFallback();
        return;
      }
      const message = ["not-allowed", "service-not-allowed"].includes(event.error)
        ? copy[language()].voiceUnavailable
        : event.error === "no-speech" ? copy[language()].noSpeech : copy[language()].voiceError;
      setListening(false, message);
    };
    recognition.onend = () => {
      if (state.voiceSession !== session) return;
      if (session.transcript && !session.submitted) {
        clearTimeout(session.endTimer);
        session.endTimer = setTimeout(() => submitVoiceTranscript(session), 2000);
        return;
      }
      state.recognition = null;
      state.voiceSession = null;
      setListening(false);
    };
    try {
      recognition.start();
    } catch (error) {
      setListening(false, copy[language()].voiceError);
    }
  }

  function resolveApiUrl(path) {
    if (!path) return [];
    if (path.startsWith("http://") || path.startsWith("https://")) return [path];
    const bases = [];
    if (config.apiBase) bases.push(config.apiBase);
    if (window.location.origin && window.location.origin !== "null" && window.location.protocol !== "file:") {
      bases.push(window.location.origin);
    }
    bases.push("http://127.0.0.1:5501");
    bases.push("http://localhost:5501");
    bases.push("http://127.0.0.1:8000");
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    return Array.from(new Set(bases.map(b => `${b.replace(/\/+$/, "")}${cleanPath}`).concat([cleanPath])));
  }

  function generateClientFallbackAnswer(payload) {
    const msg = String(payload.message || "").toLowerCase();
    const isAr = payload.language === "ar" || /[\u0600-\u06FF]/.test(msg);
    const lang = isAr ? "ar" : "en";

    if (msg.includes("first time") || msg.includes("first visit") || msg.includes("1st time") || msg.includes("مرتي الأولى") || msg.includes("مرتي الاولى") || msg.includes("أول مرة") || msg.includes("اول مرة")) {
      return {
        language: lang,
        answer: isAr
          ? "أهلاً ومرحباً بك في منسَم! اسمح لي أن آخذك في جولة سريعة. هل تبحث عن العطر لنفسك أم كهدية؟"
          : "Welcome to Mansam Perfumes! Allow me to give you an idea of what we offer. Would you like a fragrance for yourself, or as a gift?",
        sources: [], productLinks: [], productIds: []
      };
    }
    if (msg.includes("visited before") || msg.includes("visited") || msg.includes("زرتكم من قبل") || msg.includes("زرتكم")) {
      return {
        language: lang,
        answer: isAr
          ? "أهلاً بك مجدداً في منسَم! ما هو العطر الذي جربته وأعجبك سابقاً، أو ما هي النفحة التي تبحث عنها اليوم؟"
          : "Welcome back to Mansam! Which fragrance did you enjoy previously, or what notes are you looking for today?",
        sources: [], productLinks: [], productIds: []
      };
    }

    if (msg.includes("expensive") || msg.includes("غالي")) {
      return {
        language: lang,
        answer: isAr
          ? "أفهم وجهة نظرك تماماً. جودة عطورنا تعتمد على زيوت عطرية عالية الجودة ومكونات طبيعية بتركيبة عربية مصنعة في فرنسا وفق معايير IFRA. هل تبحث عن القيمة الحقيقية أم عن مجرد اسم؟"
          : "I completely understand your view. The perfume's quality is built on high-grade essential oils and natural ingredients, in an Arab formulation made in France to IFRA standards. Are you looking for real value, or for a name?",
        sources: [], productLinks: [], productIds: []
      };
    }
    if (msg.includes("last") || msg.includes("hours") || msg.includes("يثبت") || msg.includes("ثبات")) {
      return {
        language: lang,
        answer: isAr
          ? "سؤال مباشر وسأجيبك مباشرة. فوحان العطر يستمر من 6 إلى 8 ساعات، وثباته على الملابس والجلد يمتد حتى 24 ساعة. هل بشرتك جافة أم دهنية؟"
          : "A direct question and I'll answer you directly. The perfume's diffusion lasts 6 to 8 hours, and its lingering presence remains for up to 24 hours. Is your skin dry or oily?",
        sources: [], productLinks: [], productIds: []
      };
    }
    if (msg.includes("sample") || msg.includes("عينة") || msg.includes("سمبل")) {
      return {
        language: lang,
        answer: isAr
          ? "طلب يدعو للاحترام. لدينا برنامج عينات لعملائنا المهتمين. يسعدنا استقبالك في بوتيك منسَم لتجربة العطور بنفسك."
          : "A very reasonable request. We have a sample programme for our customers. You are most welcome to visit our boutique to try the perfumes personally.",
        sources: [], productLinks: [], productIds: []
      };
    }
    if (msg.includes("order") || msg.includes("whatsapp") || msg.includes("واتساب") || msg.includes("طلب")) {
      return {
        language: lang,
        answer: isAr
          ? "يسعدني مساعدتك! هل تود أن أجهز لك الطلب، أم ترغب في أن أرسل لك التفاصيل عبر الواتساب لتفكر فيها براحتك؟"
          : "I would be happy to help! Would you like me to prepare your order, or send the details on WhatsApp so you can review at your own pace?",
        sources: [], productLinks: [], productIds: []
      };
    }

    const perfumes = [
      { nameEn: "Mamlakati", nameAr: "مملكتي", collectionEn: "Qanun (Amber & Spices)", collectionAr: "قانون (عنبر وتوابل)", price: "850 AED", url: "https://uatuae.mansamworld.com" },
      { nameEn: "Shatha Biladi", nameAr: "شذا بلادي", collectionEn: "Oud & Agarwood", collectionAr: "عود وأخشاب", price: "1,150 AED", url: "https://uatuae.mansamworld.com" },
      { nameEn: "Amtaar", nameAr: "أمطار", collectionEn: "Buzuq & Watar", collectionAr: "بزق ووتر", price: "850 AED", url: "https://uatuae.mansamworld.com" },
      { nameEn: "Dehab", nameAr: "ذهب", collectionEn: "Signature Attar", collectionAr: "زيوت وعطور خاصة", price: "1,150 AED", url: "https://uatuae.mansamworld.com" }
    ];

    let chosen = perfumes[0];
    if (msg.includes("oud") || msg.includes("عود") || msg.includes("wood")) chosen = perfumes[1];
    else if (msg.includes("rose") || msg.includes("ورد") || msg.includes("fresh") || msg.includes("منعش")) chosen = perfumes[2];
    else if (msg.includes("gift") || msg.includes("هدية") || msg.includes("attar")) chosen = perfumes[3];

    const name = isAr ? chosen.nameAr : chosen.nameEn;
    const collection = isAr ? chosen.collectionAr : chosen.collectionEn;
    const answer = isAr
      ? `أرشح لك عطر ${name} من مجموعة ${collection}. السعر هو ${chosen.price}. متوفر اليوم.\n\nتخيل نفسك في وقت المغرب، والجو هادئ، وهذه الرائحة الدافئة تحيط بك كالعناق.\n\nالعديد من عملائنا اختاروا هذا العطر وعادوا لاقتنائه مجدداً، وأوصوا به في محيطهم.\n\nهل ترغب في أن أجهز لك الطلب، أم تود اقتراحاً آخر؟`
      : `I recommend ${name} from the ${collection} collection. The price is ${chosen.price}. Available today.\n\nImagine yourself at Maghrib, the air calm, and this warm scent surrounds you like an embrace.\n\nMany of our clients chose this perfume and came back for it a second time, recommending it within their circle.\n\nWould you like me to prepare your order, or would you like another perfume suggestion?`;

    return {
      language: lang,
      answer,
      sources: [{ name: { en: "Mansam Catalogue", ar: "كتالوج منسَم" }, url: chosen.url }],
      productLinks: [{ name: { en: chosen.nameEn, ar: chosen.nameAr }, url: chosen.url }],
      productIds: [chosen.nameEn.toLowerCase()]
    };
  }

  async function requestChat(payload) {
    const urlsToTry = config.chatEndpoint ? [config.chatEndpoint] : resolveApiUrl("/api/chat");
    let lastError;
    for (const url of urlsToTry) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 6000);
      try {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });
        if (response.ok) {
          clearTimeout(timeout);
          return await response.json();
        }
      } catch (error) {
        lastError = error;
      } finally {
        clearTimeout(timeout);
      }
    }
    console.warn("Mansam backend server unreachable. Using intelligent client fallback.", lastError);
    return generateClientFallbackAnswer(payload);
  }

  async function send(message, fromVoice = false) {
    const input = document.querySelector("[data-chat-input]");
    const sendButton = document.querySelector("[data-chat-send]");
    const rawText = (message || input?.value || "").trim();
    const text = fromVoice ? cleanVoiceTranscript(rawText) : rawText;
    if (!text || state.busy) return;
    stopRecognition(false);
    if (!state.awaitingName) state.language = detectLanguage(text);
    refreshLanguage();
    if (input) input.value = "";

    const textLower = text.toLowerCase();

    if (state.awaitingName) {
      const name = cleanCustomerName(text);
      if (!name || /^(hi|hello|hey|مرحبا|مرحباً)$/i.test(name)) {
        const prompt = copy[language()].askName;
        addMessage(prompt, "assistant", [], true);
        if (fromVoice || state.inputMode === "voice") speakText(prompt, language());
        return;
      }
      state.customerName = name;
      state.awaitingName = false;
      saveProfile({ name, preferences: state.profile.preferences, productIds: state.profile.productIds });
      addMessage(text, "customer");
      rememberTurn("customer", text);
      const welcome = copy[language()].greeting.replace("{name}", name);
      const nextQuestion = copy[language()].askBoutique;
      const reply = `${welcome}\n\n${nextQuestion}`;
      addMessage(reply, "assistant", [], true);
      rememberTurn("assistant", reply);
      refreshLanguage();
      if (fromVoice || state.inputMode === "voice") speakText(reply, language());
      updateSuggestions();
      return;
    }

    const isFirstTime = /\b(first time|never visited|new here)\b/.test(textLower) || /مرتي الأولى|اول مرة|أول مرة/.test(textLower);
    const isVisitedBefore = /\b(visited before|been before|returning|came before)\b/.test(textLower) || /زرتكم من قبل|سبق وزرت/.test(textLower);
    const isMyself = /\b(for myself|myself|for me|just for me)\b/.test(textLower) || /لنفسي|لي انا/.test(textLower);
    const isLadyRecipient = /\b(wife|girlfriend|girl|lady|woman|mother|daughter|sister|aunt|her)\b/.test(textLower) || /زوجتي|حبيبتي|لها|امرأة|سيدة/.test(textLower);
    const isGentlemanRecipient = /\b(husband|boyfriend|boy|gentleman|man|father|son|brother|uncle|him)\b/.test(textLower) || /زوجي|حبيبي|له|رجل|سيدي/.test(textLower);
    const isSomeoneElse = /\b(someone else|someone|gift|present|for them|for a friend|friend|cousin|cusion)\b/.test(textLower) || /شخص آخر|شخص|هدية|لهم|صديق|قريب/.test(textLower);
    const isForMyself = isMyself;
    const isAsGift = /\b(as a gift|for a gift|gift)\b/.test(textLower) || /كهدية|هدية/.test(textLower);

    if (state.flowStep === 1 && (isFirstTime || isVisitedBefore)) {
      addMessage(text, "customer");
      rememberTurn("customer", text);
      state.flowStep = isVisitedBefore ? "2_returning" : 2;
      const reply = isVisitedBefore ? copy[language()].askReturning : copy[language()].askGift;
      addMessage(reply, "assistant");
      rememberTurn("assistant", reply);
      if (fromVoice || state.inputMode === "voice") speakText(reply, language());
      updateSuggestions();
      return;
    } else if (state.flowStep === 1 && (isForMyself || isAsGift || isLadyRecipient || isGentlemanRecipient || isSomeoneElse)) {
      addMessage(text, "customer");
      rememberTurn("customer", text);
      if (isForMyself || isLadyRecipient || isGentlemanRecipient) {
        state.flowStep = 3;
        const reply = copy[language()].askNotes;
        addMessage(reply, "assistant");
        rememberTurn("assistant", reply);
        if (fromVoice || state.inputMode === "voice") speakText(reply, language());
        updateSuggestions();
        return;
      }
      state.flowStep = 2;
      const reply = copy[language()].askGift;
      addMessage(reply, "assistant");
      rememberTurn("assistant", reply);
      if (fromVoice || state.inputMode === "voice") speakText(reply, language());
      updateSuggestions();
      return;
    } else if (state.flowStep === 2 && (isForMyself || isAsGift)) {
      addMessage(text, "customer");
      rememberTurn("customer", text);
      state.flowStep = 3;
      const reply = copy[language()].askNotes;
      addMessage(reply, "assistant");
      rememberTurn("assistant", reply);
      if (fromVoice || state.inputMode === "voice") speakText(reply, language());
      updateSuggestions();
      return;
    }

    state.busy = true;
    if (input) input.disabled = true;
    if (sendButton) sendButton.disabled = true;
    const conversation = state.conversation.slice(-8);
    addMessage(text, "customer");
    rememberTurn("customer", text);
    setThinking(true);
    try {
      const payload = await requestChat({ message: text, language: language(), contextProductIds: state.contextProductIds, conversation, profile: state.profile });
      if (payload.language === "ar" || payload.language === "en") { state.language = payload.language; refreshLanguage(); }
      addMessage(payload.answer, "assistant", payload.sources, false, payload.productLinks);
      rememberTurn("assistant", payload.answer);
      if (payload.memory) saveProfile(payload.memory);
      else if (Array.isArray(payload.productIds)) saveProfile({ preferences: state.profile.preferences, productIds: payload.productIds.slice(0, 3) });
      if (fromVoice || state.inputMode === "voice") speakText(payload.answer, payload.language || language());
    } catch (error) {
      addMessage(copy[language()].error, "assistant");
      rememberTurn("assistant", copy[language()].error);
      console.error("Mansam chatbot error:", error);
    } finally {
      setThinking(false);
      state.busy = false;
      if (input) input.disabled = false;
      if (sendButton) sendButton.disabled = false;
      updateSuggestions();
      if (input) input.focus();
    }
  }

  function mount() {
    if (document.querySelector(".mansam-chat")) return;
    const wrapper = document.createElement("div");
    wrapper.innerHTML = `<button class="mansam-chat-launcher" type="button" aria-expanded="false" aria-label="Mansam Concierge" title="Mansam Concierge"><span class="mansam-chat-launcher__ring" aria-hidden="true"></span><span class="mansam-chat-launcher__mark" aria-hidden="true">M</span><span class="mansam-chat__sr-only">Open Mansam Concierge</span></button><section class="mansam-chat" lang="en" dir="ltr" hidden><div class="mansam-chat__language-choice" data-chat-language-choice><span class="mansam-chat__choice-mark" aria-hidden="true">M</span><p>MANSAM FRAGRANCES</p><strong>Choose your language</strong><span lang="ar" dir="rtl">اختر لغتك</span><div><button type="button" data-chat-language="en">English</button><button type="button" data-chat-language="ar" lang="ar" dir="rtl">العربية</button></div></div><div data-chat-conversation hidden><header class="mansam-chat__header"><div class="mansam-chat__brand"><span class="mansam-chat__header-mark" aria-hidden="true"><img src="logo3.png" alt=""></span><div><strong data-chat-title></strong><span data-chat-intro></span><small><i aria-hidden="true"></i><b data-chat-availability></b></small></div></div><div class="mansam-chat__header-actions"><select data-chat-language-switcher aria-label="Chat language"><option value="en">English</option><option value="ar">العربية</option></select><button class="mansam-chat__reset" data-chat-reset type="button" aria-label="Clear fragrance memory" title="Clear fragrance memory">&#8635;</button><button class="mansam-chat__speaker" data-chat-speaker type="button" aria-label="Turn speaker off" title="Turn speaker off" aria-pressed="false">&#128266;</button><button class="mansam-chat__close" data-chat-close type="button" aria-label="Close" title="Close">&times;</button></div></header><div class="mansam-chat__messages" aria-live="polite"></div><div class="mansam-chat__suggestions"><button type="button" data-chat-one></button><button type="button" data-chat-two></button></div><p class="mansam-chat__voice-status" data-chat-voice-status aria-live="polite"></p><form class="mansam-chat__form"><div class="mansam-chat__mode" role="group" aria-label="Input mode"><button type="button" data-chat-mode="chat" class="is-active"></button><button type="button" data-chat-mode="voice"></button></div><div class="mansam-chat__voice-stage" data-chat-voice-stage hidden><span class="mansam-chat__voice-orbit" aria-hidden="true"></span><button type="button" data-chat-voice-trigger><span aria-hidden="true">&#127908;</span><b data-chat-voice-prompt></b></button><strong data-chat-voice-stage-status></strong><small data-chat-voice-hint></small></div><div class="mansam-chat__composer" data-chat-composer><input data-chat-input type="text" autocomplete="off"><button class="mansam-chat__mic" data-chat-mic type="button" title="Start voice input" aria-label="Start voice input">&#127908;</button><button data-chat-send type="submit"></button></div></form></div></section>`;
    document.body.appendChild(wrapper);
    const launcher = document.querySelector(".mansam-chat-launcher");
    const panel = document.querySelector(".mansam-chat");
    launcher.addEventListener("click", () => setOpen(!state.open));
    panel.addEventListener("click", event => {
      if (event.target.closest("[data-chat-close]")) {
        event.preventDefault();
        event.stopPropagation();
        setOpen(false);
      }
    }, true);
    panel.querySelector("[data-chat-reset]").addEventListener("click", clearMemory);
    panel.querySelector("[data-chat-speaker]").addEventListener("click", toggleSpeaker);
    panel.querySelector(".mansam-chat__form").addEventListener("submit", event => { event.preventDefault(); send(); });
    panel.querySelector("[data-chat-input]").addEventListener("keydown", event => { if (event.key === "Enter" && !event.isComposing) { event.preventDefault(); send(); } });
    panel.querySelector("[data-chat-one]").addEventListener("click", event => send(event.currentTarget.textContent));
    panel.querySelector("[data-chat-two]").addEventListener("click", event => send(event.currentTarget.textContent));
    panel.querySelector("[data-chat-mic]").addEventListener("click", startRecognition);
    panel.querySelector("[data-chat-voice-trigger]").addEventListener("click", startRecognition);
    panel.querySelector("[data-chat-mode='chat']").addEventListener("click", () => setInputMode("chat"));
    panel.querySelector("[data-chat-mode='voice']").addEventListener("click", () => setInputMode("voice"));
    panel.querySelector("[data-chat-language-switcher]").addEventListener("change", event => { state.language = event.currentTarget.value; refreshLanguage(); panel.querySelector("[data-chat-input]").focus(); });
    panel.querySelectorAll("[data-chat-language]").forEach(button => button.addEventListener("click", () => chooseLanguage(button.dataset.chatLanguage)));
    state.profile = loadProfile();
    state.conversation = loadConversation();
    try { state.speakerEnabled = localStorage.getItem(STORAGE_KEYS.speaker) !== "off"; } catch (error) { /* storage may be unavailable */ }
    state.customerName = state.profile.name || "";
    state.contextProductIds = state.profile.productIds.slice(0, 3);
  }

  const styles = document.createElement("style");
  styles.textContent = `.mansam-chat-launcher{box-sizing:border-box;position:fixed;right:18px;bottom:18px;z-index:1000;min-width:68px;height:40px;border:1px solid #4c321d;border-radius:7px;background:#4c321d;color:#fff;font:600 13px BentonSans-Regular,Arial,sans-serif;cursor:pointer}.mansam-chat{box-sizing:border-box;position:fixed;right:18px;bottom:68px;z-index:1000;width:min(360px,calc(100vw - 32px));height:min(540px,calc(100vh - 100px));display:flex;flex-direction:column;overflow:hidden;border:1px solid #c39a54;border-radius:8px;background:#fffdf8;box-shadow:0 14px 38px rgba(45,28,12,.2);color:#38291e;font-family:BentonSans-Regular,Arial,sans-serif}.mansam-chat[dir="rtl"]{text-align:right;right:auto;left:18px}.mansam-chat [hidden]{display:none!important}.mansam-chat__language-choice{box-sizing:border-box;display:flex;flex:1;min-height:0;flex-direction:column;align-items:center;justify-content:center;gap:9px;padding:28px;text-align:center}.mansam-chat [data-chat-conversation]{display:flex;flex:1;min-height:0;flex-direction:column}.mansam-chat__language-choice strong{font-size:17px}.mansam-chat__language-choice span{color:#6b5540;font-size:15px}.mansam-chat__language-choice div{display:grid;grid-template-columns:repeat(2,minmax(112px,1fr));width:min(100%,250px);gap:10px;margin-top:10px}.mansam-chat__language-choice button{box-sizing:border-box;width:100%;height:40px;border:1px solid #a87930;border-radius:5px;background:#fffaf0;color:#4c321d;font:600 13px BentonSans-Regular,Arial,sans-serif;cursor:pointer}.mansam-chat__header{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:15px 16px;border-bottom:1px solid #e6d7ba;background:#fbf2df}.mansam-chat__header>div{min-width:0}.mansam-chat__header-actions{display:flex;flex:0 0 auto;align-items:center;gap:7px;direction:ltr}.mansam-chat__header-actions select{box-sizing:border-box;width:86px;height:28px;padding:0 5px;border:1px solid #cbb58c;border-radius:4px;background:#fffdf8;color:#4c321d;font:12px BentonSans-Regular,Arial,sans-serif;cursor:pointer}.mansam-chat__header strong,.mansam-chat__header span{display:block}.mansam-chat__header strong{font-size:15px}.mansam-chat__header span{margin-top:4px;font-size:12px;line-height:1.35;color:#6b5540}.mansam-chat__close{width:28px;height:28px;border:0;background:transparent;color:#4c321d;font-size:23px;line-height:1;cursor:pointer}.mansam-chat__messages{flex:1;min-height:0;overflow:auto;padding:14px;background:#fffdf8}.mansam-chat__message{width:fit-content;max-width:87%;margin:0 0 10px;padding:9px 11px;border-radius:7px;font-size:13px;line-height:1.45;white-space:pre-wrap}.mansam-chat__message--assistant{background:#f3e6cd}.mansam-chat__message--customer{margin-left:auto;background:#4c321d;color:#fff}.mansam-chat[dir="rtl"] .mansam-chat__message--customer{margin-right:auto;margin-left:0}.mansam-chat__message small{display:block;margin-top:6px;color:#7b624a;font-size:10px}.mansam-chat__product-link{display:block;width:fit-content;margin-top:8px;color:#76511d;font-size:12px;font-weight:600;line-height:1.35;text-decoration:underline;text-underline-offset:2px}.mansam-chat__speak{display:block;width:28px;height:25px;margin-top:7px;padding:0;border:1px solid #cbb58c;border-radius:4px;background:#fffdf8;cursor:pointer}.mansam-chat__suggestions{display:flex;gap:7px;overflow:auto;padding:9px 12px;border-top:1px solid #eee2ce}.mansam-chat__suggestions button{flex:0 0 auto;max-width:190px;padding:6px 8px;border:1px solid #d4b98a;border-radius:6px;background:#fffaf0;color:#59402b;font:12px BentonSans-Regular,Arial,sans-serif;cursor:pointer;white-space:normal}.mansam-chat__mode{display:flex;padding:0 12px}.mansam-chat__mode button{flex:1;height:31px;border:1px solid #cbb58c;background:#fffdf8;color:#59402b;font:600 12px BentonSans-Regular,Arial,sans-serif;cursor:pointer}.mansam-chat__mode button:first-child{border-radius:5px 0 0 5px}.mansam-chat__mode button:last-child{border-left:0;border-radius:0 5px 5px 0}.mansam-chat__mode button.is-active{background:#4c321d;color:#fff}.mansam-chat__voice-status{min-height:16px;margin:5px 12px 0;color:#7b624a;font-size:11px}.mansam-chat__form{display:flex;gap:8px;padding:10px 12px 12px;border-top:1px solid #eee2ce}.mansam-chat__form input{min-width:0;flex:1;height:36px;padding:0 10px;border:1px solid #cbb58c;border-radius:5px;background:#fff;color:#38291e;font:13px BentonSans-Regular,Arial,sans-serif}.mansam-chat__form button{min-width:40px;height:36px;border:0;border-radius:5px;background:#b8863b;color:#fff;font:600 12px BentonSans-Regular,Arial,sans-serif;cursor:pointer}.mansam-chat__form [data-chat-send]{min-width:58px}.mansam-chat__form [data-chat-mic].is-listening{background:#4c321d;animation:mansam-chat-pulse 1.2s ease-in-out infinite}.mansam-chat__form input:disabled,.mansam-chat__form button:disabled{cursor:wait;opacity:.65}@keyframes mansam-chat-pulse{50%{transform:scale(1.06)}}@media(max-width:480px){.mansam-chat{right:10px;bottom:62px;width:calc(100vw - 20px);height:min(530px,calc(100vh - 82px)}.mansam-chat[dir="rtl"]{left:10px;right:auto}.mansam-chat-launcher{right:10px;bottom:10px}}`;
  document.head.appendChild(styles);

  const enhancedStyles = document.createElement("style");
  enhancedStyles.textContent = `
    .mansam-chat__sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
    .mansam-chat-launcher{right:24px;bottom:24px;display:grid;place-items:center;min-width:54px;width:54px;height:54px;padding:0;border:1px solid #cfb06c;border-radius:50%;background:#271d18;color:#fff;box-shadow:0 10px 26px rgba(39,29,24,.25);isolation:isolate;transition:transform .18s ease,box-shadow .18s ease}
    .mansam-chat-launcher:hover{transform:translateY(-2px);box-shadow:0 14px 30px rgba(39,29,24,.32)}
    .mansam-chat-launcher:focus-visible,.mansam-chat button:focus-visible,.mansam-chat input:focus-visible,.mansam-chat select:focus-visible{outline:3px solid #6e988b;outline-offset:2px}
    .mansam-chat-launcher__mark,.mansam-chat__choice-mark,.mansam-chat__header-mark,.mansam-chat__avatar{display:grid;place-items:center;font-family:Georgia,"Times New Roman",serif;font-weight:700}
    .mansam-chat-launcher__mark{position:relative;z-index:1;width:30px;height:30px;border:1px solid rgba(255,255,255,.55);border-radius:50%;font-size:16px}
    .mansam-chat-launcher__ring{position:absolute;inset:5px;border:1px solid rgba(222,188,112,.62);border-radius:50%}
    .mansam-chat{right:24px;bottom:90px;width:min(416px,calc(100vw - 40px));height:min(650px,calc(100vh - 120px));border:1px solid #c8ab70;border-radius:10px;background:#fdfaf5;box-shadow:0 24px 58px rgba(39,29,24,.22);color:#30251f;font-family:BentonSans-Regular,Arial,sans-serif}
    .mansam-chat[dir="rtl"]{right:auto;left:24px}
    .mansam-chat__language-choice{gap:8px;padding:36px 28px;background:#fdfaf5}
    .mansam-chat__choice-mark{width:46px;height:46px;margin-bottom:10px;border:1px solid #c8ab70;border-radius:50%;background:#271d18;color:#f8e6b4;font-size:20px}
    .mansam-chat__language-choice p{margin:0;color:#96753d;font-size:10px;font-weight:700;letter-spacing:1.4px}
    .mansam-chat__language-choice strong{font-family:Georgia,"Times New Roman",serif;font-size:26px;font-weight:400;line-height:1.15}
    .mansam-chat__language-choice>span{color:#75655a;font-size:16px}
    .mansam-chat__language-choice div{width:min(100%,276px);gap:8px;margin-top:18px}
    .mansam-chat__language-choice button{height:44px;border:1px solid #bfa376;border-radius:7px;background:#fff;color:#372a22;font-size:13px;transition:background .16s ease,color .16s ease,border-color .16s ease}
    .mansam-chat__language-choice button:hover{border-color:#271d18;background:#271d18;color:#fff}
    .mansam-chat__header{align-items:center;padding:14px 16px;border:0;background:#271d18;color:#fff}
    .mansam-chat__brand{display:flex;align-items:center;gap:10px;min-width:0}
    .mansam-chat__header-mark{display:flex;flex:0 0 auto;align-items:center;width:72px;height:30px;border:0;border-radius:0;color:#f8e6b4;font-size:16px;overflow:hidden}
    .mansam-chat__header-mark img{display:block;width:100%;height:100%;object-fit:contain;object-position:center}
    .mansam-chat__header strong{font-size:14px;line-height:1.1}
    .mansam-chat__header span{margin-top:3px;color:#e2d5c5;font-size:11px;line-height:1.25}
    .mansam-chat__header small{display:flex;align-items:center;gap:5px;margin-top:5px;color:#e3c982;font-size:10px;font-weight:400}
    .mansam-chat__header small i{width:6px;height:6px;border-radius:50%;background:#74af96;box-shadow:0 0 0 3px rgba(116,175,150,.16)}
    .mansam-chat__header small b{font-weight:400}
    .mansam-chat__header-actions{gap:5px}
    .mansam-chat__header-actions select{width:82px;height:30px;border:1px solid rgba(228,205,151,.65);border-radius:6px;background:transparent;color:#fff;font-size:11px}
    .mansam-chat__header-actions option{background:#271d18;color:#fff}
    .mansam-chat__close{width:30px;height:30px;border:1px solid transparent;border-radius:6px;color:#fff;font-size:23px}
    .mansam-chat__close:hover{border-color:rgba(255,255,255,.32);background:rgba(255,255,255,.08)}
    .mansam-chat__reset{width:30px;height:30px;border:1px solid transparent;border-radius:6px;background:transparent;color:#e2d5c5;font-size:18px;line-height:1;cursor:pointer}
    .mansam-chat__reset:hover{border-color:rgba(255,255,255,.32);background:rgba(255,255,255,.08);color:#fff}
    .mansam-chat__speaker{width:30px;height:30px;padding:0;border:1px solid transparent;border-radius:6px;background:transparent;color:#e2d5c5;font-size:15px;line-height:1;cursor:pointer}.mansam-chat__speaker:hover{border-color:rgba(255,255,255,.32);background:rgba(255,255,255,.08);color:#fff}
    .mansam-chat__messages{padding:18px 14px 10px;background:#fdfaf5;scrollbar-color:#c9b292 transparent;scrollbar-width:thin}
    .mansam-chat__message{width:auto;max-width:none;margin:0 0 13px;padding:0;background:transparent;font-size:13px;line-height:1.5;white-space:normal}
    .mansam-chat__message-row{display:flex;align-items:flex-end;gap:8px}
    .mansam-chat__avatar{flex:0 0 auto;width:24px;height:24px;margin-bottom:2px;border:1px solid #c8aa6a;border-radius:50%;background:#271d18;color:#f9e9bd;font-size:11px}
    .mansam-chat__bubble{max-width:calc(100% - 32px);padding:10px 12px;border:1px solid #e2d8cb;border-radius:8px;background:#fff;color:#3a2e27;box-shadow:0 2px 4px rgba(39,29,24,.04)}
    .mansam-chat__bubble p{margin:0;white-space:pre-wrap}
    .mansam-chat__message--welcome .mansam-chat__bubble{border-color:#e6d1a0;background:#fff9e9}
    .mansam-chat__message--customer .mansam-chat__message-row{justify-content:flex-end}
    .mansam-chat__message--customer .mansam-chat__bubble{max-width:84%;border-color:#3c6559;background:#3c6559;color:#fff;box-shadow:none}
    .mansam-chat[dir="rtl"] .mansam-chat__message-row{flex-direction:row-reverse}
    .mansam-chat[dir="rtl"] .mansam-chat__message--customer .mansam-chat__message-row{justify-content:flex-start}
    .mansam-chat__product-link{display:grid;grid-template-columns:1fr auto;gap:1px 10px;width:100%;box-sizing:border-box;margin-top:10px;padding:9px 10px;border:1px solid #cfb783;border-radius:7px;background:#fffaf0;color:#382a20;text-decoration:none}
    .mansam-chat__product-link:hover{border-color:#8e6d32;background:#fff5dd}
    .mansam-chat__product-link span{grid-column:1;color:#97763c;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.55px}
    .mansam-chat__product-link strong{grid-column:1;font-size:12px;line-height:1.3}
    .mansam-chat__product-link b{grid-column:2;grid-row:1 / span 2;align-self:center;color:#6c4e1e;font-size:16px}
    .mansam-chat[dir="rtl"] .mansam-chat__product-link b{transform:rotate(180deg)}
    .mansam-chat__message small{margin-top:7px;color:#88786c;font-size:10px;line-height:1.35}
    .mansam-chat__speak{display:inline-grid;place-items:center;width:29px;height:26px;margin-top:8px;border:1px solid #d7c0a0;border-radius:5px;background:#fff;color:#4a382b;font-size:13px;transition:background .16s ease}
    .mansam-chat__speak:hover{background:#f6ead4}
    .mansam-chat__thinking{display:flex;align-items:flex-end;gap:8px;margin:0 0 13px;color:#796b60;font-size:11px}
    .mansam-chat__thinking>span:last-child{display:flex;align-items:center;gap:4px;padding:9px 10px;border:1px solid #e2d8cb;border-radius:8px;background:#fff}
    .mansam-chat__thinking i{width:5px;height:5px;border-radius:50%;background:#94774e;animation:mansam-chat-dot 1.1s infinite ease-in-out}
    .mansam-chat__thinking i:nth-child(2){animation-delay:.13s}.mansam-chat__thinking i:nth-child(3){animation-delay:.26s}
    .mansam-chat__thinking em{margin-left:4px;font-style:normal}.mansam-chat[dir="rtl"] .mansam-chat__thinking em{margin-right:4px;margin-left:0}
    .mansam-chat__suggestions{gap:7px;padding:9px 14px;border-top:1px solid #ece2d4;background:#fdfaf5}
    .mansam-chat__suggestions button{max-width:230px;padding:7px 10px;border:1px solid #d7c4a0;border-radius:999px;background:#fff;color:#58483b;font-size:11px;line-height:1.25;transition:border-color .16s ease,background .16s ease}
    .mansam-chat__suggestions button:hover{border-color:#7d6250;background:#f8f0e3}
    .mansam-chat__voice-status{min-height:0;margin:0;padding:0 14px;color:#856946;font-size:11px;background:#fdfaf5}
    .mansam-chat__voice-status:not(:empty){padding-bottom:7px}
    .mansam-chat__form{display:block;padding:0;border-top:1px solid #ece2d4;background:#fff}
    .mansam-chat__mode{padding:8px 12px 0}
    .mansam-chat__mode button{height:28px;border-color:#d9c6a5;background:#fffdf9;color:#67554a;font-size:11px}
    .mansam-chat__mode button:first-child{border-radius:6px 0 0 6px}.mansam-chat__mode button:last-child{border-radius:0 6px 6px 0}
    .mansam-chat__mode button.is-active{border-color:#3c6559;background:#3c6559;color:#fff}
    .mansam-chat__composer{display:flex;gap:7px;padding:9px 12px 12px}
    .mansam-chat__form input{height:40px;padding:0 12px;border-color:#d6c8b5;border-radius:7px;background:#fffdf9;color:#30251f;font-size:13px}
    .mansam-chat__form input::placeholder{color:#9b8b80}.mansam-chat__form input:focus{border-color:#5b897a;box-shadow:0 0 0 3px rgba(91,137,122,.14);outline:0}
    .mansam-chat__form button{min-width:40px;height:40px;border-radius:7px;background:#b48a42;font-size:12px}.mansam-chat__form [data-chat-send]{min-width:60px;background:#271d18}
    .mansam-chat__form [data-chat-send]:hover{background:#463126}.mansam-chat__form [data-chat-mic]{background:#6d957f}.mansam-chat__form [data-chat-mic]:hover{background:#547968}
    .mansam-chat__form [data-chat-mic].is-listening{background:#b45f51;animation:mansam-chat-pulse 1.2s ease-in-out infinite}
    @keyframes mansam-chat-dot{0%,80%,100%{transform:translateY(0);opacity:.45}40%{transform:translateY(-3px);opacity:1}}
    @media(max-width:560px){.mansam-chat{right:10px;bottom:76px;width:calc(100vw - 20px);height:min(620px,calc(100vh - 94px));border-radius:9px}.mansam-chat[dir="rtl"]{right:auto;left:10px}.mansam-chat-launcher{right:14px;bottom:14px}.mansam-chat__header{padding:12px 13px}.mansam-chat__header-actions select{width:74px}.mansam-chat__messages{padding:14px 11px 8px}.mansam-chat__suggestions{padding-left:11px;padding-right:11px}.mansam-chat__composer{padding-left:10px;padding-right:10px}.mansam-chat__language-choice{padding:28px 20px}}
  `;
  document.head.appendChild(enhancedStyles);

  const voiceStyles = document.createElement("style");
  voiceStyles.textContent = `
    .mansam-chat__voice-stage{position:relative;display:grid;place-items:center;min-height:172px;overflow:hidden;margin:9px 12px 12px;padding:16px;border:1px solid #d6c296;border-radius:8px;background:#f8f1e4;text-align:center;isolation:isolate}
    .mansam-chat__voice-orbit{position:absolute;width:142px;height:142px;border:1px solid rgba(126,157,140,.38);border-radius:50%;z-index:-1}
    .mansam-chat__voice-orbit:before,.mansam-chat__voice-orbit:after{position:absolute;content:"";border:1px solid rgba(126,157,140,.24);border-radius:50%;inset:-13px}
    .mansam-chat__voice-orbit:after{inset:-28px;border-color:rgba(180,138,66,.18)}
    .mansam-chat__voice-stage button{display:grid;place-items:center;gap:4px;width:104px;height:104px;padding:7px;border:1px solid #385e54;border-radius:50%;background:#3c6559;color:#fff;box-shadow:0 8px 18px rgba(60,101,89,.24);cursor:pointer;transition:transform .16s ease,background .16s ease,box-shadow .16s ease}
    .mansam-chat__voice-stage button:hover{background:#2e5248;transform:translateY(-2px);box-shadow:0 11px 22px rgba(60,101,89,.28)}
    .mansam-chat__voice-stage button>span{font-size:25px;line-height:1}.mansam-chat__voice-stage button b{max-width:74px;font:600 11px/1.2 BentonSans-Regular,Arial,sans-serif}
    .mansam-chat__voice-stage>strong{display:block;min-height:16px;margin-top:10px;color:#4d4034;font-size:12px;font-weight:600}.mansam-chat__voice-stage>small{color:#837366;font-size:10px}
    .mansam-chat__voice-stage button.is-listening{background:#b45f51;border-color:#a74e42;box-shadow:0 0 0 8px rgba(180,95,81,.13),0 8px 18px rgba(180,95,81,.24);animation:mansam-chat-voice-pulse 1.25s ease-in-out infinite}
    .mansam-chat.is-voice-mode .mansam-chat__suggestions{border-bottom:1px solid #ece2d4}.mansam-chat.is-voice-mode .mansam-chat__voice-status{display:none}
    @keyframes mansam-chat-voice-pulse{50%{transform:scale(1.05);box-shadow:0 0 0 14px rgba(180,95,81,.05),0 8px 18px rgba(180,95,81,.22)}}
    @media(max-width:560px){.mansam-chat__voice-stage{min-height:158px;margin:8px 10px 10px}.mansam-chat__voice-stage button{width:96px;height:96px}}
  `;
  document.head.appendChild(voiceStyles);
  document.addEventListener("languageLoaded", refreshLanguage);
  window.addEventListener("pageshow", refreshLanguage);
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", mount) : mount();
})();
