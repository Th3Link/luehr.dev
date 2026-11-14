(() => {
    const root = document.documentElement;
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
    // Storage may be unavailable in private or restricted browsing contexts.
    const read = key => {
        try { return localStorage.getItem(key); } catch { return null; }
    };
    const save = (key, value) => {
        try { localStorage.setItem(key, value); } catch { /* Preferences remain session-local. */ }
    };
    let theme = read('theme');
    if (!['light', 'dark'].includes(theme)) theme = null;
    const applyTheme = value => {
        root.dataset.theme = value;
        const button = document.getElementById('theme-toggle');
        if (button) button.setAttribute('aria-pressed', String(value === 'dark'));
    };
    // Runs in the head before the page is painted.
    applyTheme(theme || (systemTheme.matches ? 'dark' : 'light'));
    document.addEventListener('DOMContentLoaded', () => {
        applyTheme(theme || (systemTheme.matches ? 'dark' : 'light'));
        document.getElementById('theme-toggle')?.addEventListener('click', () => {
            theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
            save('theme', theme);
            applyTheme(theme);
        });
        document.querySelectorAll('[data-language]').forEach(anchor => {
            anchor.addEventListener('click', () => save('language', anchor.dataset.language));
        });
        // Explicit language URLs and links are never redirected. Only the general root entry negotiates.
        if (document.body.dataset.autoLanguage === 'true' && ['/', '/index.html'].includes(location.pathname)) {
            const stored = read('language');
            const preferred = (navigator.languages?.[0] || navigator.language || 'en').toLowerCase();
            const language = ['de', 'en'].includes(stored) ? stored : preferred.startsWith('de') ? 'de' : 'en';
            // Following an English link from this site is already an explicit choice.
            let internal = false;
            try { internal = new URL(document.referrer).origin === location.origin; } catch { /* Direct entry. */ }
            if (language === 'de' && !internal) location.replace('/de/' + location.search + location.hash);
        }
    });
    systemTheme.addEventListener('change', event => {
        if (!theme) applyTheme(event.matches ? 'dark' : 'light');
    });
})();
