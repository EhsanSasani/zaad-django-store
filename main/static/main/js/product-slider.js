document.addEventListener("DOMContentLoaded", function () {
  const sliders = document.querySelectorAll("[data-slider]");

  sliders.forEach(function (slider) {
    const viewport = slider.querySelector("[data-slider-viewport]");
    const track = slider.querySelector(".product-slider__track");
    const prevBtn = slider.querySelector("[data-slider-prev]");
    const nextBtn = slider.querySelector("[data-slider-next]");
    const slides = slider.querySelectorAll(".product-slider__slide");

    if (!viewport || !track || !slides.length) return;

    let index = 0;
    let startX = 0;
    let currentTranslate = 0;
    let isDragging = false;
    let dragStartTranslate = 0;

    function getPerView() {
      const width = window.innerWidth;
      if (width <= 520) return 1;
      if (width <= 760) return 2;
      if (width <= 1180) return 3;
      return 4;
    }

    function getMaxIndex() {
      const perView = getPerView();
      return Math.max(0, slides.length - perView);
    }

    function getStepSize() {
      const firstSlide = slides[0];
      const slideWidth = firstSlide.getBoundingClientRect().width;
      const trackStyle = window.getComputedStyle(track);
      const gap = parseFloat(trackStyle.columnGap || trackStyle.gap || 0);
      return slideWidth + gap;
    }

    function getOffsetFromIndex(i) {
      return i * getStepSize();
    }

    function applyTranslate(px) {
      track.style.transform = `translateX(-${px}px)`;
      currentTranslate = px;
    }

    function updateButtons() {
      if (prevBtn) prevBtn.disabled = index <= 0;
      if (nextBtn) nextBtn.disabled = index >= getMaxIndex();
    }

    function update() {
      const maxIndex = getMaxIndex();
      if (index > maxIndex) index = maxIndex;
      if (index < 0) index = 0;

      applyTranslate(getOffsetFromIndex(index));
      updateButtons();
    }

    function snapToNearest() {
      const step = getStepSize();
      const nearestIndex = Math.round(currentTranslate / step);
      index = Math.min(getMaxIndex(), Math.max(0, nearestIndex));
      track.classList.remove("no-animate");
      update();
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", function () {
        const perView = getPerView();
        index = Math.max(0, index - perView);
        update();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        const perView = getPerView();
        index = Math.min(getMaxIndex(), index + perView);
        update();
      });
    }

    function onPointerDown(clientX) {
      isDragging = true;
      startX = clientX;
      dragStartTranslate = currentTranslate;
      viewport.classList.add("is-dragging");
      track.classList.add("no-animate");
    }

    function onPointerMove(clientX) {
      if (!isDragging) return;

      const delta = clientX - startX;
      let nextTranslate = dragStartTranslate - delta;

      const minTranslate = 0;
      const maxTranslate = getOffsetFromIndex(getMaxIndex());

      if (nextTranslate < minTranslate) nextTranslate = minTranslate;
      if (nextTranslate > maxTranslate) nextTranslate = maxTranslate;

      applyTranslate(nextTranslate);
    }

    function onPointerUp() {
      if (!isDragging) return;
      isDragging = false;
      viewport.classList.remove("is-dragging");
      snapToNearest();
    }

    viewport.addEventListener("mousedown", function (e) {
      onPointerDown(e.clientX);
    });

    window.addEventListener("mousemove", function (e) {
      onPointerMove(e.clientX);
    });

    window.addEventListener("mouseup", function () {
      onPointerUp();
    });

    viewport.addEventListener(
      "touchstart",
      function (e) {
        if (!e.touches.length) return;
        onPointerDown(e.touches[0].clientX);
      },
      { passive: true }
    );

    viewport.addEventListener(
      "touchmove",
      function (e) {
        if (!e.touches.length) return;
        onPointerMove(e.touches[0].clientX);
      },
      { passive: true }
    );

    viewport.addEventListener("touchend", function () {
      onPointerUp();
    });

    viewport.addEventListener("mouseleave", function () {
      onPointerUp();
    });

    window.addEventListener("resize", function () {
      update();
    });

    update();
  });
});