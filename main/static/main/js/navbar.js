document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.querySelector("[data-nav-dropdown]");
  const trigger = document.querySelector("[data-nav-dropdown-trigger]");

  if (!dropdown || !trigger) return;

  trigger.setAttribute("aria-expanded", "false");

  function setDropdownOpen(isOpen) {
    dropdown.classList.toggle("is-open", isOpen);
    trigger.setAttribute("aria-expanded", isOpen ? "true" : "false");
  }

  trigger.addEventListener("click", function (event) {
    event.preventDefault();
    event.stopPropagation();
    setDropdownOpen(!dropdown.classList.contains("is-open"));
  });

  document.addEventListener("click", function (event) {
    if (!dropdown.contains(event.target)) {
      setDropdownOpen(false);
    }
  });

  window.addEventListener("resize", function () {
    setDropdownOpen(false);
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
