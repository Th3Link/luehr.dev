const root = document.documentElement;
const button = document.getElementById("theme-toggle");

// System Preference
const systemPref = window.matchMedia("(prefers-color-scheme: dark)");

// Load saved theme
const saved = localStorage.getItem("theme");

function setTheme(theme) {
    if (theme === "light") {
        root.dataset.theme = "latte";
        button.textContent = "☀️";
    } else {
        delete root.dataset.theme;
        button.textContent = "🌙";
    }
    updateGithubCards(theme);
}

// Initial setup
if (saved) {
    setTheme(saved);
} else {
    setTheme(systemPref.matches ? "light" : "dark");
}

// Toggle click
button.addEventListener("click", () => {
    const isLight = root.dataset.theme === "latte";

    const newTheme = isLight ? "dark" : "light";
    localStorage.setItem("theme", newTheme);
    setTheme(newTheme);
});

// React to system changes (optional but nice)
systemPref.addEventListener("change", (e) => {
    if (!localStorage.getItem("theme")) {
        setTheme(e.matches ? "light" : "dark");
    }
});

function updateGithubCards(theme) {
    const stats = document.getElementById("gh-stats");
    const langs = document.getElementById("gh-langs");

    if (!stats && !langs) return;

    const isLight = theme === "light";

    const bg = "00000000";
    const text = isLight ? "4c4f69" : "cdd6f4";
    const title = isLight ? "1e66f5" : "89b4fa";
    const border = isLight ? "ccd0da" : "313244";

    if (stats) {
        stats.src =
            `https://github-stats-extended.vercel.app/api?username=th3link` +
            `&show_icons=true&count_private=true` +
            `&bg_color=${bg}&title_color=${title}&text_color=${text}&icon_color=${title}&border_color=${border}`;
    }

    if (langs) {
        langs.src =
            `https://github-stats-extended.vercel.app/api/top-langs/?username=th3link` +
            `&layout=compact&hide=HTML,PostScript,G-code` +
            `&bg_color=${bg}&title_color=${title}&text_color=${text}&border_color=${border}`;
    }
}

