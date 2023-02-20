// Theme switcher using a switch id="theme_switcher" with JS

document.addEventListener("DOMContentLoaded", function() {
  const themeSwitcher = document.getElementById("theme_switcher");
  const theme = document.documentElement.getAttribute("data-theme");

  themeSwitcher.checked = theme === 'dark';

  themeSwitcher.addEventListener("change", () => {
    if (themeSwitcher.checked) {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.setAttribute("data-theme", "light");
    }
  });
});
