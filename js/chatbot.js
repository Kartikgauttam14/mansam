(function () {
  const config = window.MANSAM_CONFIG || {};
  const endpoint = config.chatEndpoint || "/api/chat";
  const state = { open: false, busy: false, language: null, awaitingName: false, customerName: "", contextProductIds: [], profile: { name: "", preferences: [], productIds: [] }, conversation: [], inputMode: "chat", recognition: null, voiceSession: null, listening: false, speechAudio: null };

  const copy = {
    en: { title: "Mansam Concierge", intro: "Your personal fragrance guide", placeholder: "Describe a note, mood, or occasion", namePlaceholder: "Enter your name", send: "Send", askName: "Welcome to Mansam. May I have your name?", greeting: "Welcome to Mansam, {name} sir! What fragrance can I help you find today?", opening: "Hello. I can help you discover Mansam fragrances from the catalogue.", one: "Which perfume has rose and oud?", two: "I want a fresh daily fragrance.", viewProduct: "View perfume", error: "I could not reach the fragrance guide. Please try again.", chat: "Chat", voice: "Voice", listen: "Listening...", tapToSpeak: "Tap to speak", voicePrompt: "Tell me what you are looking for", voiceHint: "Speak in English or Arabic", thinking: "Finding the right fragrance", available: "Available now", readAloud: "Read answer aloud", clearMemory: "Clear fragrance memory", voiceUnavailable: "Voice input is not available in this browser.", noSpeech: "I did not hear anything. Tap the microphone and try again.", voiceError: "Voice input could not start. Please try again." },
    ar: { title: "مستشار منسَم", intro: "دليلك الشخصي لاكتشاف العطور", placeholder: "اكتب نفحاتك أو مزاجك أو مناسبتك", namePlaceholder: "اكتب اسمك", send: "إرسال", askName: "مرحباً بك في منسَم. ما اسمك؟", greeting: "مرحباً بك في منسَم يا {name} سيدي! ما العطر الذي يمكنني مساعدتك في العثور عليه اليوم؟", opening: "مرحباً. يمكنني مساعدتك في اكتشاف عطور منسَم من الكتالوج.", one: "أي عطر يحتوي على الورد والعود؟", two: "أريد عطراً منعشاً للاستخدام اليومي.", viewProduct: "عرض العطر", error: "تعذر الوصول إلى دليل العطور. حاول مرة أخرى.", chat: "كتابة", voice: "صوت", listen: "جارٍ الاستماع...", tapToSpeak: "اضغط للتحدث", voicePrompt: "أخبرني بما تبحث عنه", voiceHint: "تحدث بالعربية أو الإنجليزية", thinking: "نبحث عن العطر المناسب", available: "متاح الآن", readAloud: "استمع إلى الإجابة", clearMemory: "مسح ذاكرة العطور", voiceUnavailable: "الإدخال الصوتي غير متاح في هذا المتصفح.", noSpeech: "لم أسمع شيئاً. اضغط على الميكروفون وحاول مرة أخرى.", voiceError: "تعذر تشغيل الإدخال الصوتي. حاول مرة أخرى." }
  };

  function language() { return state.language || ((document.documentElement.lang || localStorage.getItem("language") || "en").startsWith("ar") ? "ar" : "en"); }
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
    return (lastRepeatedStart > 0 ? collapsed.slice(lastRepeatedStart) : collapsed).join(" ").trim();
  }

  function rememberTurn(role, text) {
    const value = String(text || "").trim();
    if (!value) return;
    state.conversation.push({ role, text: value });
    state.conversation = state.conversation.slice(-8);
  }

  function loadProfile() {
    try {
      const stored = JSON.parse(localStorage.getItem("mansam-fragrance-memory") || "{}");
      return {
        name: cleanCustomerName(stored.name),
        preferences: Array.isArray(stored.preferences) ? stored.preferences.slice(0, 8) : [],
        productIds: Array.isArray(stored.productIds) ? stored.productIds.slice(0, 3) : [],
      };
    } catch (error) { return { name: "", preferences: [], productIds: [] }; }
  }

  function saveProfile(memory) {
    if (!memory || typeof memory !== "object") return;
    state.profile = {
      name: memory.name ? cleanCustomerName(memory.name) : state.profile.name,
      preferences: Array.isArray(memory.preferences) ? memory.preferences.slice(0, 8) : state.profile.preferences,
      productIds: Array.isArray(memory.productIds) ? memory.productIds.slice(0, 3) : state.profile.productIds,
    };
    state.contextProductIds = state.profile.productIds.slice(0, 3);
    try { localStorage.setItem("mansam-fragrance-memory", JSON.stringify(state.profile)); } catch (error) { /* storage may be unavailable */ }
  }

  function clearMemory() {
    state.profile = { name: "", preferences: [], productIds: [] };
    state.customerName = "";
    state.awaitingName = Boolean(state.language);
    state.contextProductIds = [];
    state.conversation = [];
    try { localStorage.removeItem("mansam-fragrance-memory"); } catch (error) { /* storage may be unavailable */ }
    const messages = document.querySelector(".mansam-chat__messages");
    if (messages) { messages.innerHTML = ""; if (state.awaitingName) addMessage(copy[language()].askName, "assistant", [], true); }
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
    panel.querySelector("[data-chat-title]").textContent = text.title;
    panel.querySelector("[data-chat-intro]").textContent = text.intro;
    panel.querySelector("[data-chat-availability]").textContent = text.available;
    panel.querySelector("[data-chat-input]").placeholder = state.awaitingName ? text.namePlaceholder : text.placeholder;
    panel.querySelector("[data-chat-send]").textContent = text.send;
    panel.querySelector("[data-chat-one]").textContent = text.one;
    panel.querySelector("[data-chat-two]").textContent = text.two;
    panel.querySelector("[data-chat-language-switcher]").value = lang;
    panel.querySelector("[data-chat-mode='chat']").textContent = text.chat;
    panel.querySelector("[data-chat-mode='voice']").textContent = text.voice;
    panel.querySelector("[data-chat-voice-prompt]").textContent = text.voicePrompt;
    panel.querySelector("[data-chat-voice-hint]").textContent = text.voiceHint;
    panel.querySelector("[data-chat-voice-trigger]").setAttribute("aria-label", text.tapToSpeak);
    panel.querySelector("[data-chat-voice-trigger]").title = text.tapToSpeak;
    panel.querySelector("[data-chat-voice-status]").textContent = state.listening ? text.listen : "";
    panel.querySelector("[data-chat-mic]").setAttribute("aria-label", lang === "ar" ? "بدء الإدخال الصوتي" : "Start voice input");
    panel.querySelector(".mansam-chat__close").setAttribute("aria-label", lang === "ar" ? "إغلاق" : "Close");
    panel.querySelector("[data-chat-reset]").setAttribute("aria-label", text.clearMemory);
    panel.querySelector("[data-chat-reset]").title = text.clearMemory;
    const welcome = panel.querySelector(".mansam-chat__message--welcome div");
    if (welcome) welcome.textContent = text.opening;
    launcher.setAttribute("aria-label", text.title);
    launcher.title = text.title;
    if (state.recognition) state.recognition.lang = lang === "ar" ? "ar-SA" : "en-US";
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
    const panel = document.querySelector(".mansam-chat");
    panel.querySelector("[data-chat-language-choice]").hidden = true;
    panel.querySelector("[data-chat-conversation]").hidden = false;
    state.customerName = state.profile.name || "";
    state.awaitingName = !state.customerName;
    refreshLanguage();
    panel.querySelector(".mansam-chat__messages").innerHTML = "";
    const welcomeMessage = state.awaitingName
      ? copy[selectedLanguage].askName
      : copy[selectedLanguage].greeting.replace("{name}", state.customerName);
    addMessage(welcomeMessage, "assistant", [], true);
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
    session.transcript = cleanVoiceTranscript(session.transcript);
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
      if (submit) submitVoiceTranscript(session);
      else session.submitted = true;
    }
    const recognition = state.recognition;
    state.recognition = null;
    state.voiceSession = null;
    if (recognition && state.listening) recognition.stop();
    setListening(false);
  }

  function startRecognition() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) { setListening(false, copy[language()].voiceUnavailable); return; }
    if (state.listening || state.voiceSession || state.recognition) {
      if (state.listening) stopRecognition();
      return;
    }
    stopSpeaking();
    const recognition = new Recognition();
    const session = { transcript: "", finalTranscript: "", interimTranscript: "", submitted: false, cancelled: false, silenceTimer: null };
    state.recognition = recognition;
    state.voiceSession = session;
    const isMobileVoice = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    recognition.lang = language() === "ar" ? "ar-SA" : "en-US";
    // Mobile browsers often emit cumulative interim results; one final utterance is more reliable there.
    recognition.interimResults = !isMobileVoice;
    recognition.continuous = !isMobileVoice;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => {
      if (state.voiceSession !== session || session.cancelled) {
        recognition.stop();
        return;
      }
      setListening(true);
    };
    recognition.onresult = event => {
      if (state.voiceSession !== session || session.cancelled) return;
      let interimTranscript = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = result[0].transcript.trim();
        if (result.isFinal) session.finalTranscript = `${session.finalTranscript} ${transcript}`.trim();
        else interimTranscript = `${interimTranscript} ${transcript}`.trim();
      }
      session.interimTranscript = interimTranscript;
      session.transcript = cleanVoiceTranscript(`${session.finalTranscript} ${session.interimTranscript}`);
      const input = document.querySelector("[data-chat-input]");
      if (input) input.value = session.transcript;
      clearTimeout(session.silenceTimer);
      if (session.transcript) {
        session.silenceTimer = setTimeout(() => submitVoiceTranscript(session), 1800);
      }
    };
    recognition.onerror = event => {
      if (state.voiceSession !== session || session.cancelled) return;
      if (event.error === "aborted") return;
      if (event.error === "no-speech" && session.transcript) {
        submitVoiceTranscript(session);
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
        submitVoiceTranscript(session);
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

  async function requestChat(payload) {
    let lastError;
    for (let attempt = 0; attempt < 2; attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 25000);
      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });
        if (!response.ok) throw new Error(`Chat request failed (${response.status})`);
        return await response.json();
      } catch (error) {
        lastError = error;
        if (attempt === 0) await new Promise(resolve => setTimeout(resolve, 500));
      } finally {
        clearTimeout(timeout);
      }
    }
    throw lastError || new Error("Chat request failed");
  }

  async function send(message, fromVoice = false) {
    const input = document.querySelector("[data-chat-input]");
    const sendButton = document.querySelector("[data-chat-send]");
    const text = cleanVoiceTranscript(fromVoice ? (message || input.value) : (message || input.value).trim());
    if (!text || state.busy) return;
    stopRecognition(false);
    if (state.awaitingName) {
      const name = cleanCustomerName(text);
      if (name.length < 2) {
        addMessage(text, "customer");
        addMessage(copy[language()].askName, "assistant", [], true);
        input.value = "";
        return;
      }
      state.customerName = name;
      state.awaitingName = false;
      state.profile.name = name;
      saveProfile(state.profile);
      input.value = "";
      addMessage(name, "customer");
      const welcomeMessage = copy[language()].greeting.replace("{name}", name);
      addMessage(welcomeMessage, "assistant", [], true);
      if (fromVoice) speakText(welcomeMessage, language());
      refreshLanguage();
      return;
    }
    state.language = detectLanguage(text);
    refreshLanguage();
    state.busy = true;
    input.value = "";
    input.disabled = true;
    sendButton.disabled = true;
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
      if (state.inputMode === "voice") speakText(payload.answer, payload.language || language());
    } catch (error) {
      addMessage(copy[language()].error, "assistant");
      rememberTurn("assistant", copy[language()].error);
      console.error("Mansam chatbot error:", error);
    } finally {
      setThinking(false);
      state.busy = false;
      input.disabled = false;
      sendButton.disabled = false;
      input.focus();
    }
  }

  function mount() {
    if (document.querySelector(".mansam-chat")) return;
    const wrapper = document.createElement("div");
    wrapper.innerHTML = `<button class="mansam-chat-launcher" type="button" aria-expanded="false" aria-label="Mansam Concierge" title="Mansam Concierge"><span class="mansam-chat-launcher__ring" aria-hidden="true"></span><span class="mansam-chat-launcher__mark" aria-hidden="true">M</span><span class="mansam-chat__sr-only">Open Mansam Concierge</span></button><section class="mansam-chat" lang="en" dir="ltr" hidden><div class="mansam-chat__language-choice" data-chat-language-choice><span class="mansam-chat__choice-mark" aria-hidden="true">M</span><p>MANSAM FRAGRANCES</p><strong>Choose your language</strong><span lang="ar" dir="rtl">اختر لغتك</span><div><button type="button" data-chat-language="en">English</button><button type="button" data-chat-language="ar" lang="ar" dir="rtl">العربية</button></div></div><div data-chat-conversation hidden><header class="mansam-chat__header"><div class="mansam-chat__brand"><span class="mansam-chat__header-mark" aria-hidden="true"><img src="logo3.png" alt=""></span><div><strong data-chat-title></strong><span data-chat-intro></span><small><i aria-hidden="true"></i><b data-chat-availability></b></small></div></div><div class="mansam-chat__header-actions"><select data-chat-language-switcher aria-label="Chat language"><option value="en">English</option><option value="ar">العربية</option></select><button class="mansam-chat__reset" data-chat-reset type="button" aria-label="Clear fragrance memory" title="Clear fragrance memory">&#8635;</button><button class="mansam-chat__close" data-chat-close type="button" aria-label="Close" title="Close">&times;</button></div></header><div class="mansam-chat__messages" aria-live="polite"></div><div class="mansam-chat__suggestions"><button type="button" data-chat-one></button><button type="button" data-chat-two></button></div><p class="mansam-chat__voice-status" data-chat-voice-status aria-live="polite"></p><form class="mansam-chat__form"><div class="mansam-chat__mode" role="group" aria-label="Input mode"><button type="button" data-chat-mode="chat" class="is-active"></button><button type="button" data-chat-mode="voice"></button></div><div class="mansam-chat__voice-stage" data-chat-voice-stage hidden><span class="mansam-chat__voice-orbit" aria-hidden="true"></span><button type="button" data-chat-voice-trigger><span aria-hidden="true">&#127908;</span><b data-chat-voice-prompt></b></button><strong data-chat-voice-stage-status></strong><small data-chat-voice-hint></small></div><div class="mansam-chat__composer" data-chat-composer><input data-chat-input type="text" autocomplete="off"><button class="mansam-chat__mic" data-chat-mic type="button" title="Start voice input" aria-label="Start voice input">&#127908;</button><button data-chat-send type="submit"></button></div></form></div></section>`;
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
