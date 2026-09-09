const DEFAULT_LANGUAGE = "en";
const LANGUAGE_CODES = {
    en: "002",
    ar: "001"
};

const FALLBACK_TRANSLATIONS = {
    en: {
        "discover_your_perfume": "DISCOVER YOUR PERFUME",
        "dream": "Dream",
        "discover": "Discover",
        "gift": "Gift",
        "describe_your_dream": "Describe your dream",
        "in_a_few_words": "In a few words",
        "dream_placeholder": "e.g. Bold and Confident, Peaceful Life, Luxury Lifestyle",
        "is_it_for": "Is it for ....",
        "for_him": "For Him",
        "for_her": "For Her",
        "discover_your_perfect_perfume": "Discover Your Perfect Perfume",
        "your_dream": "Your Dream",
        "read_more": "Read More",
        "show_less": "Show Less",
        "unlock_your_gift_option": "Unlock Your Gift Option",
        "gift_voucher": "Gift Voucher",
        "complimentary_voucher": "Complimentary 12ml EDP",
        "collect_your_gift": "Collect your GIFT from any of our Boutiques.",
        "unique_reservation": "This gift is uniquely reserved for you.",
        "terms_and_conditions": "T&C apply.",
        "enter_name": "Enter your name",
        "enter_phone": "Enter phone number",
        "enter_email": "Enter your email",
        "collect_gift": "Collect Gift Voucher",
        "close": "close",
        "select_gender_error": "Please select gender",
        "dream_words_error": "Tell us a bit more about your dream so we can reveal your perfect fragrance.",
        "no_dream_provided": "No dream provided",
        "fallback_recommendation_query": "I want a luxury fragrance that reflects my dream",
        "listen_recommendation": "Listen to recommendation",
        "no_emotion_provided": "No emotion provided",
        "name_error": "Name must be at least 3 characters.",
        "phone_error": "Enter valid phone number (7-15 digits).",
        "email_error": "Enter a valid email address.",
        "submitting": "Submitting...",
        "email_exists": "Your email ID already exists.",
        "failed_submit_dream": "Failed to submit dream.",
        "claim_my_gift": "Claim My Gift",
        "no_gift_data": "No gift data found",
        "save_pdf": "Save PDF",
        "save_image": "Save Image",
        "voucher_title": "GIFT VOUCHER",
        "voucher_subtitle": "Your gift is uniquely reserved for you.",
        "voucher_your_dream": "Your Dream:",
        "discovered_perfume": "Discovered Perfume:",
        "by_mansam": "by Mansam",
        "voucher_gift_label": "Gift: Complimentary 12ml EDP",
        "with_mansam_purchase": "with your Mansam purchase",
        "voucher_number": "Voucher Number:",
        "issued_on": "Issued On:",
        "valid_till": "Valid Till:",
        "redeem_note": "Redeem your gift by visiting any Mansam boutique on or before the stated expiry date.",
        "terms_title": "Terms & Conditions:",
        "term_1": "Valid for one-time redemption at Mansam boutiques in KSA & UAE only, with in-person visit before expiry.",
        "term_2": "Gift is non-transferable, not redeemable for cash, subject to availability, may be substituted, and carries no warranty.",
        "term_3": "Customer data is securely held and used only for Mansam communication and promotions in line with applicable data protection laws.",
        "image_generation_failed": "Image generation failed.",
        "pdf_generation_failed": "PDF generation failed."
    },
    ar: {
        "discover_your_perfume": "اكتشف عطرك",
        "dream": "حلم",
        "discover": "اكتشف",
        "gift": "هدية",
        "describe_your_dream": "أخبرنا عن حلمك",
        "in_a_few_words": "في بضع كلمات",
        "dream_placeholder": "مثال: جريء وواثق، حياة هادئة، أسلوب حياة فاخر",
        "is_it_for": "هل هو لـ…",
        "for_him": "للرجال",
        "for_her": "للنساء",
        "discover_your_perfect_perfume": "اكتشف عطرك المثالي",
        "your_dream": "حلمك",
        "read_more": "اقرأ المزيد",
        "show_less": "عرض أقل",
        "unlock_your_gift_option": "افتح خيار هديتك",
        "gift_voucher": "بطاقة هدية",
        "complimentary_voucher": "هدية مجانية عطر بحجم 12 مل",
        "collect_your_gift": "يمكنك استلام هديتك من أي من بوتيكات منسَم.",
        "unique_reservation": "هذه الهدية مخصصة لك حصريًا.",
        "terms_and_conditions": "تخضع هذه العرض للشروط والأحكام.",
        "enter_name": "يرجى إدخال اسمك",
        "enter_phone": "يرجى إدخال رقم هاتفك",
        "enter_email": "يرجى إدخال بريدك الإلكتروني",
        "collect_gift": "عرض بطاقة هديتك",
        "close": "إغلاق",
        "select_gender_error": "يرجى اختيار الفئة",
        "dream_words_error": "أخبرنا أكثر قليلًا عن حلمك لنكشف لك عطرك المثالي.",
        "no_dream_provided": "لم يتم تقديم حلم",
        "fallback_recommendation_query": "أريد عطرًا فاخرًا يعبر عن حلمي",
        "listen_recommendation": "استمع إلى التوصية",
        "no_emotion_provided": "لم يتم تقديم مشاعر",
        "name_error": "يجب ألا يقل الاسم عن 3 أحرف.",
        "phone_error": "يرجى إدخال رقم هاتف صحيح من 7 إلى 15 رقمًا.",
        "email_error": "يرجى إدخال بريد إلكتروني صحيح.",
        "submitting": "جارٍ الإرسال...",
        "email_exists": "هذا البريد الإلكتروني مسجل بالفعل.",
        "failed_submit_dream": "تعذر إرسال الحلم.",
        "claim_my_gift": "احصل على هديتي",
        "no_gift_data": "لا توجد بيانات للهدية",
        "save_pdf": "حفظ PDF",
        "save_image": "حفظ الصورة",
        "voucher_title": "بطاقة هدية",
        "voucher_subtitle": "هذه الهدية مخصصة لك حصريًا.",
        "voucher_your_dream": "حلمك:",
        "discovered_perfume": "العطر المكتشف:",
        "by_mansam": "من منسَم",
        "voucher_gift_label": "الهدية: عطر مجاني بحجم 12 مل",
        "with_mansam_purchase": "مع مشترياتك من منسَم",
        "voucher_number": "رقم البطاقة:",
        "issued_on": "تاريخ الإصدار:",
        "valid_till": "صالحة حتى:",
        "redeem_note": "استلم هديتك بزيارة أي بوتيك منسَم في تاريخ الانتهاء المحدد أو قبله.",
        "terms_title": "الشروط والأحكام:",
        "term_1": "صالحة للاستخدام لمرة واحدة فقط في بوتيكات منسَم داخل المملكة العربية السعودية والإمارات العربية المتحدة، مع ضرورة الحضور الشخصي قبل تاريخ الانتهاء.",
        "term_2": "الهدية غير قابلة للتحويل أو الاستبدال نقدًا، وتخضع للتوفر، وقد يتم استبدالها بمنتج مماثل، ولا تشمل أي ضمان.",
        "term_3": "يتم حفظ بياناتكم بأمان، وتُستخدم فقط لأغراض التواصل والعروض الخاصة بمنسَم وفقًا لأنظمة حماية البيانات المعمول بها.",
        "image_generation_failed": "تعذر إنشاء الصورة.",
        "pdf_generation_failed": "تعذر إنشاء ملف PDF."
    }
};

window.currentTranslations = {};

function getSavedLanguage() {
    return localStorage.getItem("language") || DEFAULT_LANGUAGE;
}

function getLanguageCode(lang = getSavedLanguage()) {
    return LANGUAGE_CODES[lang] || LANGUAGE_CODES[DEFAULT_LANGUAGE];
}

function translate(key, fallback = "") {
    const savedLang = getSavedLanguage();
    const fallbackTranslations = FALLBACK_TRANSLATIONS[savedLang] || FALLBACK_TRANSLATIONS[DEFAULT_LANGUAGE];

    return window.currentTranslations[key] || fallbackTranslations[key] || fallback || key;
}

async function loadLanguage(lang = getSavedLanguage()) {
    try {
        let translations = FALLBACK_TRANSLATIONS[lang] || FALLBACK_TRANSLATIONS[DEFAULT_LANGUAGE];

        try {
            const response = await fetch(`lang/${lang}.json`);

            if (response.ok) {
                translations = await response.json();
            }
        } catch (fetchError) {
            // Direct file:// opens cannot fetch local JSON in many browsers.
        }

        window.currentTranslations = translations;

        document.querySelectorAll("[data-i18n]").forEach(element => {
            const key = element.dataset.i18n;

            if (translations[key]) {
                element.textContent = translations[key];
            }
        });

        document.querySelectorAll("[data-i18n-html]").forEach(element => {
            const key = element.dataset.i18nHtml;

            if (translations[key]) {
                element.innerHTML = translations[key];
            }
        });

        document.querySelectorAll("[data-i18n-placeholder]").forEach(element => {
            const key = element.dataset.i18nPlaceholder;

            if (translations[key]) {
                element.placeholder = translations[key];
            }
        });

        document.querySelectorAll("[data-i18n-value]").forEach(element => {
            const key = element.dataset.i18nValue;

            if (translations[key]) {
                element.value = translations[key];
            }
        });

        document.querySelectorAll("[data-i18n-title]").forEach(element => {
            const key = element.dataset.i18nTitle;

            if (translations[key]) {
                element.title = translations[key];
            }
        });

        document.documentElement.lang = lang;
        document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
        document.body.classList.toggle("rtl", lang === "ar");

        document.dispatchEvent(new CustomEvent("languageLoaded", {
            detail: { lang, translations }
        }));
    } catch (error) {
        console.error("Language load error:", error);
    }
}

function syncLanguageSwitcher(lang = getSavedLanguage()) {
    const dropdown = document.getElementById("languageSwitcher");

    if (dropdown) {
        dropdown.value = lang;
    }
}

function changeLanguage(lang) {
    localStorage.setItem("language", lang);
    syncLanguageSwitcher(lang);
    loadLanguage(lang);

    // Reload pages so API-backed content is requested in the selected language.
    setTimeout(() => window.location.reload(), 100);
}

window.getSavedLanguage = getSavedLanguage;
window.getLanguageCode = getLanguageCode;
window.translate = translate;
window.loadLanguage = loadLanguage;
window.changeLanguage = changeLanguage;
window.syncLanguageSwitcher = syncLanguageSwitcher;

function initializeLanguageSwitcher() {
    const savedLang = getSavedLanguage();

    syncLanguageSwitcher(savedLang);
    loadLanguage(savedLang);

    const dropdown = document.getElementById("languageSwitcher");

    if (dropdown && !dropdown.dataset.i18nBound) {
        dropdown.dataset.i18nBound = "true";

        dropdown.addEventListener("change", function () {
            changeLanguage(this.value);
        });
    }
}

document.addEventListener("DOMContentLoaded", initializeLanguageSwitcher);

window.addEventListener("pageshow", () => {
    const savedLang = getSavedLanguage();

    syncLanguageSwitcher(savedLang);
    loadLanguage(savedLang);
});
