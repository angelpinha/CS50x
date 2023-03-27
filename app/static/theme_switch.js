// Theme switcher using a switch id="theme_switcher" with JS

document.addEventListener("DOMContentLoaded", function() {
  const themeSwitcher = document.getElementById("theme_switcher");
  const storedTheme = localStorage.getItem("theme");
  const theme = storedTheme || document.documentElement.getAttribute("data-theme");

  document.documentElement.setAttribute("data-theme", theme);
  themeSwitcher.checked = theme === "light";

  themeSwitcher.addEventListener("change", () => {
    if (themeSwitcher.checked) {
      document.documentElement.setAttribute("data-theme", "light");
      localStorage.setItem("theme", "light");
    } else {
      document.documentElement.setAttribute("data-theme", "dark");
      localStorage.setItem("theme", "dark");
    }
  });
});
