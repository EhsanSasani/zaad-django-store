document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.querySelector("[data-nav-dropdown]");
  const trigger = document.querySelector("[data-nav-dropdown-trigger]");

  if (!dropdown || !trigger) return;

  trigger.addEventListener("click", function (event) {
    event.stopPropagation();
    dropdown.classList.toggle("is-open");
  });

  document.addEventListener("click", function (event) {
    if (!dropdown.contains(event.target)) {
      dropdown.classList.remove("is-open");
    }
  });

  window.addEventListener("resize", function () {
    dropdown.classList.remove("is-open");
  });
});

document.addEventListener("DOMContentLoaded", function () {

  const header = document.querySelector(".site-header");

  if (!header) return;

  function updateHeader() {
    if (window.scrollY > 80) {
      header.classList.add("is-scrolled");
    } else {
      header.classList.remove("is-scrolled");
    }
  }

  updateHeader();

  window.addEventListener("scroll", updateHeader);
});