(function () {
  var STORAGE_KEY = "zaad-theme";
  var root = document.documentElement;
  var toggleBtn = document.getElementById("themeToggle");
  var themeText = toggleBtn ? toggleBtn.querySelector(".theme-text") : null;
  var mediaQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      // localStorage may be blocked.
    }
  }

  function getCurrentTheme() {
    var attr = root.getAttribute("data-theme");
    if (attr === "dark" || attr === "light") {
      return attr;
    }

    var stored = getStoredTheme();
    if (stored === "dark" || stored === "light") {
      return stored;
    }

    return mediaQuery && mediaQuery.matches ? "dark" : "light";
  }

  function updateToggleState(theme) {
    if (!toggleBtn) {
      return;
    }

    var isDark = theme === "dark";
    var nextLabel = isDark ? "روشن" : "تیره";

    toggleBtn.setAttribute("aria-pressed", isDark ? "true" : "false");
    toggleBtn.setAttribute("aria-label", "تغییر به حالت " + nextLabel);
    toggleBtn.setAttribute("title", "تغییر به حالت " + nextLabel);

    if (themeText) {
      themeText.textContent = nextLabel;
    }
  }

  function applyTheme(theme) {
    var normalized = theme === "dark" ? "dark" : "light";
    root.setAttribute("data-theme", normalized);
    root.classList.toggle("theme-dark", normalized === "dark");
    updateToggleState(normalized);
  }

  applyTheme(getCurrentTheme());

  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      var nextTheme = getCurrentTheme() === "dark" ? "light" : "dark";
      setStoredTheme(nextTheme);
      applyTheme(nextTheme);
    });
  }

  if (mediaQuery) {
    var handleSystemThemeChange = function (event) {
      var storedTheme = getStoredTheme();
      if (storedTheme === "dark" || storedTheme === "light") {
        return;
      }
      applyTheme(event.matches ? "dark" : "light");
    };

    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", handleSystemThemeChange);
    } else if (typeof mediaQuery.addListener === "function") {
      mediaQuery.addListener(handleSystemThemeChange);
    }
  }
})();
