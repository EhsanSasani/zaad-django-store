(function () {
  const modal = document.querySelector("[data-product-modal]");
  if (!modal) return;

  const modalImage = modal.querySelector("[data-modal-image]");
  const modalType = modal.querySelector("[data-modal-type]");
  const modalTitle = modal.querySelector("[data-modal-title]");
  const modalPrice = modal.querySelector("[data-modal-price]");
  const modalCloseItems = Array.from(document.querySelectorAll("[data-product-modal-close]"));

  const typeLabels = {
    "hand-bouquet": "HAND BOUQUET",
    "box": "BOX",
    "bouquet": "BOUQUET",
    "jarl": "JARL",
    "wedding": "WEDDING",
    "stand": "STAND",
    "plants": "PLANTS",
    "bakery": "BAKERY",
    "gifts": "GIFTS",
    "event": "EVENT",
  };

  function getTypeLabel(value) {
    return typeLabels[value] || value || "COLLECTION";
  }

  function openModal(card) {
    const image = card.querySelector("[data-product-image]");

    const imageSrc = image ? image.getAttribute("src") : "";
    const imageAlt = image ? image.getAttribute("alt") : "";

    const type = getTypeLabel(card.dataset.productType);
    const code = card.dataset.productCode || "";
    const name = card.dataset.productName || "";
    const price = card.dataset.productPrice || "استعلام قیمت";

    if (modalImage) {
      modalImage.src = imageSrc;
      modalImage.alt = imageAlt;
    }

    if (modalType) {
      modalType.textContent = type;
    }

    if (modalTitle) {
      modalTitle.textContent = name || code || "ZAD";
    }

    if (modalPrice) {
      modalPrice.textContent = price;
    }

    modal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = "";

    if (modalImage) {
      modalImage.src = "";
      modalImage.alt = "";
    }
  }

  document.addEventListener("click", function (event) {
    const card = event.target.closest("[data-zad-modal-card]");

    if (card) {
      event.preventDefault();
      openModal(card);
      return;
    }

    if (event.target.closest("[data-product-modal-close]")) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });
})();