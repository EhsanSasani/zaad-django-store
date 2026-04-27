document.addEventListener("DOMContentLoaded", function () {
  const slides = Array.from(document.querySelectorAll(".hero-slide"));
  const dots = Array.from(document.querySelectorAll(".hero-slider__dots button"));
  const prev = document.getElementById("heroPrev");
  const next = document.getElementById("heroNext");

  if (!slides.length) return;

  let current = 0;
  let timer = null;

  function showSlide(index) {
    slides.forEach((slide, i) => slide.classList.toggle("is-active", i === index));
    dots.forEach((dot, i) => dot.classList.toggle("is-active", i === index));
    current = index;
  }

  function nextSlide() {
    showSlide((current + 1) % slides.length);
  }

  function prevSlide() {
    showSlide((current - 1 + slides.length) % slides.length);
  }

  function startAuto() {
    stopAuto();
    timer = setInterval(nextSlide, 5000);
  }

  function stopAuto() {
    if (timer) clearInterval(timer);
  }

  if (next) {
    next.addEventListener("click", function () {
      nextSlide();
      startAuto();
    });
  }

  if (prev) {
    prev.addEventListener("click", function () {
      prevSlide();
      startAuto();
    });
  }

  dots.forEach((dot, index) => {
    dot.addEventListener("click", function () {
      showSlide(index);
      startAuto();
    });
  });

  showSlide(0);
  startAuto();
});