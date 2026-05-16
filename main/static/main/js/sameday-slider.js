document.addEventListener("DOMContentLoaded", function () {
  const slider = document.querySelector("[data-sameday-slider]");
  if (!slider) return;

  let timer = null;

  function getStep() {
    const firstCard = slider.querySelector(".home-sameday-card");
    if (!firstCard) return 0;

    const styles = window.getComputedStyle(slider);
    const gap = parseFloat(styles.columnGap || styles.gap || 0);

    return firstCard.offsetWidth + gap;
  }

  function moveNext() {
    const step = getStep();
    if (!step) return;

    const maxScroll = slider.scrollWidth - slider.clientWidth;
    const nearEnd = slider.scrollLeft + step >= maxScroll - 8;

    if (nearEnd) {
      slider.scrollTo({ left: 0, behavior: "smooth" });
    } else {
      slider.scrollBy({ left: step, behavior: "smooth" });
    }
  }

  function start() {
    stop();
    timer = window.setInterval(moveNext, 2800);
  }

  function stop() {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
  }

  slider.addEventListener("mouseenter", stop);
  slider.addEventListener("mouseleave", start);
  slider.addEventListener("touchstart", stop, { passive: true });
  slider.addEventListener("touchend", start, { passive: true });

  start();
});