(function () {
  var root = document.documentElement;
  var toggle = document.getElementById("theme-toggle");

  function applyTheme(theme) {
    var isDark = theme === "dark";
    root.dataset.theme = isDark ? "dark" : "";

    if (!toggle) {
      return;
    }

    toggle.setAttribute("aria-pressed", isDark ? "true" : "false");
    toggle.textContent = isDark ? "Light" : "Dark";
  }

  function getStoredTheme() {
    try {
      return localStorage.getItem("eai-theme");
    } catch (error) {
      return null;
    }
  }

  function storeTheme(theme) {
    try {
      localStorage.setItem("eai-theme", theme);
    } catch (error) {}
  }

  applyTheme(getStoredTheme() === "dark" ? "dark" : "light");

  if (toggle) {
    toggle.addEventListener("click", function () {
      var nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      storeTheme(nextTheme);
      applyTheme(nextTheme);
    });
  }
})();
