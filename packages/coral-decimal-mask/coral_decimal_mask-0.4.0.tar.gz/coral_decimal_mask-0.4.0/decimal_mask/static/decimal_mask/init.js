{
  document.querySelectorAll("[data-decimal-mask]").forEach(el => {
    new DecimalMask(el, JSON.parse(el.dataset.decimalOptions));
  });
}
