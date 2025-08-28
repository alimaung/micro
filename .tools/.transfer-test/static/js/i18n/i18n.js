/**
 * Internationalization (i18n) handler for Transfer Tool
 */

// Available languages with flag country codes
const availableLanguages = {
    'en': {
        name: 'English',
        flagCode: 'us'  // US flag for English
    },
    'de': {
        name: 'Deutsch',
        flagCode: 'de'  // German flag
    }
};

// Default language
let currentLanguage = 'en';

// Translation data gets loaded from language files
let translations = {};

/**
 * Initialize i18n system
 */
function initI18n() {
    // Get saved language preference or use browser language
    const savedLang = localStorage.getItem('language');
    
    if (savedLang && availableLanguages[savedLang]) {
        currentLanguage = savedLang;
    } else {
        // Try to use browser language if available
        const browserLang = navigator.language.split('-')[0];
        if (availableLanguages[browserLang]) {
            currentLanguage = browserLang;
        }
    }
    
    // Set initial translations
    if (currentLanguage === 'en' && translations_en) {
        translations = translations_en;
    } else if (currentLanguage === 'de' && translations_de) {
        translations = translations_de;
    } else {
        // Fallback to English if current language not available
        translations = translations_en;
        currentLanguage = 'en';
    }
    
    // Update UI language indicator
    updateLanguageIndicator();
    
    // Apply translations to the page
    translatePage();
}

/**
 * Update the language indicator in UI
 */
function updateLanguageIndicator() {
    const langToggle = document.getElementById('lang-toggle');
    const langFlag = document.getElementById('lang-flag');
    
    if (langToggle && langFlag) {
        // Get the flag code for the current language
        const flagCode = availableLanguages[currentLanguage].flagCode;
        
        // Update the flag image
        langFlag.src = `https://flagcdn.com/20x15/${flagCode}.png`;
        langFlag.srcset = `https://flagcdn.com/40x30/${flagCode}.png 2x, https://flagcdn.com/60x45/${flagCode}.png 3x`;
        langFlag.alt = currentLanguage.toUpperCase();
    }
}

/**
 * Change the current language
 * @param {string} langCode - Language code to switch to
 */
function changeLanguage(langCode) {
    if (!availableLanguages[langCode]) {
        console.error(`Language ${langCode} is not available`);
        return;
    }
    
    currentLanguage = langCode;
    localStorage.setItem('language', langCode);
    
    // Set translations based on language
    if (langCode === 'en' && translations_en) {
        translations = translations_en;
    } else if (langCode === 'de' && translations_de) {
        translations = translations_de;
    }
    
    // Update UI language indicator
    updateLanguageIndicator();
    
    // Apply translations to the page
    translatePage();
}

/**
 * Get translation for a key
 * @param {string} key - Translation key
 * @returns {string} - Translated text or key if translation not found
 */
function __(key) {
    return translations[key] || key;
}

/**
 * Apply translations to all elements with data-i18n attribute
 */
function translatePage() {
    // Find all elements with data-i18n attribute
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        
        // Check if we have a translation for this key
        if (translations[key]) {
            // Handle different element types
            if (element.tagName === 'INPUT' && element.type === 'text') {
                // For input elements, update placeholder
                if (element.getAttribute('data-i18n-attr') === 'placeholder') {
                    element.placeholder = translations[key];
                } else {
                    element.value = translations[key];
                }
            } else {
                // For most elements, update text content
                element.textContent = translations[key];
            }
        }
    });
    
    // Handle elements with data-i18n-html attribute (for HTML content)
    const htmlElements = document.querySelectorAll('[data-i18n-html]');
    
    htmlElements.forEach(element => {
        const key = element.getAttribute('data-i18n-html');
        
        if (translations[key]) {
            element.innerHTML = translations[key];
        }
    });
}

/**
 * Cycle through available languages
 */
function cycleLanguage() {
    const langKeys = Object.keys(availableLanguages);
    const currentIndex = langKeys.indexOf(currentLanguage);
    const nextIndex = (currentIndex + 1) % langKeys.length;
    
    changeLanguage(langKeys[nextIndex]);
}

// Export functions for use in main.js
window.i18n = {
    init: initI18n,
    translatePage: translatePage,
    changeLanguage: changeLanguage,
    cycleLanguage: cycleLanguage,
    __: __
}; 