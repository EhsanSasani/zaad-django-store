(function () {
  window.dataLayer = window.dataLayer || [];

  function pushEvent(eventName, params) {
    var payload = Object.assign({ event: eventName }, params || {});
    window.dataLayer.push(payload);

    if (typeof window.gtag === "function") {
      var gtagParams = Object.assign({}, params || {});
      window.gtag("event", eventName, gtagParams);
    }
  }

  function currentPageType() {
    return document.body && document.body.dataset.pageType ? document.body.dataset.pageType : "home";
  }

  function currentItemId() {
    return document.body && document.body.dataset.itemId ? document.body.dataset.itemId : null;
  }

  function ctaPosition(node) {
    return (node && node.dataset && node.dataset.ctaPosition) || "inline";
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[href]");
    if (!link) {
      return;
    }

    var href = link.getAttribute("href") || "";
    var params = {
      page_type: currentPageType(),
      item_id: currentItemId(),
      cta_position: ctaPosition(link),
    };

    if (href.indexOf("tel:") === 0) {
      pushEvent("click_to_call", params);
      return;
    }

    if (href.indexOf("wa.me") !== -1 || href.indexOf("whatsapp") !== -1) {
      pushEvent("click_whatsapp", params);
    }
  });

  document.addEventListener("submit", function (event) {
    var form = event.target.closest("form[data-track-lead-form]");
    if (!form) {
      return;
    }

    var leadField = form.querySelector('[name="lead_type"]');
    var leadType = leadField && leadField.value ? leadField.value : form.dataset.defaultLeadType || null;

    pushEvent("lead_form_submit", {
      page_type: currentPageType(),
      item_id: currentItemId(),
      cta_position: form.dataset.ctaPosition || "inline",
      lead_type: leadType,
    });
  });

  function toggleOptionalFields(form) {
    var leadType = form.querySelector('[name="lead_type"]');
    var deliveryWindow = form.querySelector('[name="delivery_window"]');
    var eventRow = form.querySelector(".event-only");
    var dateRow = form.querySelector(".date-only");

    if (!leadType || !deliveryWindow) {
      return;
    }

    function refresh() {
      if (eventRow) {
        eventRow.style.display = leadType.value === "event" ? "grid" : "none";
      }
      if (dateRow) {
        dateRow.style.display = deliveryWindow.value === "pick_date" ? "grid" : "none";
      }
    }

    leadType.addEventListener("change", refresh);
    deliveryWindow.addEventListener("change", refresh);
    refresh();
  }

  document.querySelectorAll("form[data-track-lead-form]").forEach(toggleOptionalFields);
})();
