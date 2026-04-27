(function () {
  function resizeAdminModal(modal) {
    if (!modal) return;

    const iframe = modal.querySelector("iframe");
    if (!iframe) return;

    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const targetHeight = Math.max(360, viewportHeight - 140);

    iframe.style.height = `${targetHeight}px`;
  }

  document.addEventListener("shown.bs.modal", function (event) {
    resizeAdminModal(event.target);
  });

  window.addEventListener("resize", function () {
    document.querySelectorAll(".modal.show").forEach(function (modal) {
      resizeAdminModal(modal);
    });
  });
})();