document.addEventListener("DOMContentLoaded", function () {
  const sliders = document.querySelectorAll("[data-featured-slider]");

  sliders.forEach(function (root) {
    const viewport = root.querySelector(".featured-products__viewport");
    const track = root.querySelector(".featured-products__track");
    const cards = Array.from(root.querySelectorAll(".featured-product-card"));

    if (!viewport || !track || cards.length === 0) return;

    let currentIndex = 0;
    let autoTimer = null;

    function getVisibleCount() {
      if (window.innerWidth <= 520) return 2;
      if (window.innerWidth <= 1100) return 3;
      return 5;
    }

    function getCardWidthWithGap() {
      const firstCard = cards[0];
      if (!firstCard) return 0;

      const cardWidth = firstCard.getBoundingClientRect().width;
      const styles = window.getComputedStyle(track);
      const gap = parseFloat(styles.columnGap || styles.gap || 0);

      return cardWidth + gap;
    }

    function getMaxIndex() {
      const visibleCount = getVisibleCount();
      return Math.max(0, cards.length - visibleCount);
    }

    function updateSlider() {
      const maxIndex = getMaxIndex();

      if (currentIndex > maxIndex) {
        currentIndex = 0;
      }

      const step = getCardWidthWithGap();
      const moveX = currentIndex * step;

      track.style.transform = `translateX(${moveX}px)`;
    }

    function nextSlide() {
      const maxIndex = getMaxIndex();

      if (currentIndex >= maxIndex) {
        currentIndex = 0;
      } else {
        currentIndex += 1;
      }

      updateSlider();
    }

    function startAutoPlay() {
      stopAutoPlay();

      if (cards.length <= getVisibleCount()) return;

      autoTimer = setInterval(nextSlide, 2600);
    }

    function stopAutoPlay() {
      if (autoTimer) {
        clearInterval(autoTimer);
        autoTimer = null;
      }
    }

    root.addEventListener("mouseenter", stopAutoPlay);
    root.addEventListener("mouseleave", startAutoPlay);
    root.addEventListener("touchstart", stopAutoPlay, { passive: true });
    root.addEventListener("touchend", startAutoPlay, { passive: true });

    window.addEventListener("resize", function () {
      currentIndex = 0;
      updateSlider();
      startAutoPlay();
    });

    updateSlider();
    startAutoPlay();
  });
});