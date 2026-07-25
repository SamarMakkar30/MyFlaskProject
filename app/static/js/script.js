document.addEventListener("DOMContentLoaded", () => {
  const flashMessages = document.querySelectorAll("#flash-messages [data-message]");
  const toastRegion = document.getElementById("toast-region");
  const toastIcons = { success: "bi-check-circle-fill", danger: "bi-exclamation-octagon-fill", error: "bi-exclamation-octagon-fill", warning: "bi-exclamation-triangle-fill", info: "bi-info-circle-fill" };
  flashMessages.forEach((message) => {
    const category = message.dataset.category || "info";
    const toast = document.createElement("div");
    toast.className = `toast app-toast toast-${category}`;
    toast.setAttribute("role", "status"); toast.setAttribute("aria-live", "polite");
    toast.innerHTML = `<div class="toast-body"><i class="bi ${toastIcons[category] || toastIcons.info} toast-icon"></i><span></span><button type="button" class="toast-close" data-bs-dismiss="toast" aria-label="Close"><i class="bi bi-x-lg"></i></button></div>`;
    toast.querySelector("span").textContent = message.dataset.message;
    toastRegion.appendChild(toast);
    new bootstrap.Toast(toast, { delay: 4600 }).show();
  });
  document.querySelectorAll(".needs-validation").forEach((form) => form.addEventListener("submit", (event) => { if (!form.checkValidity()) { event.preventDefault(); event.stopPropagation(); } form.classList.add("was-validated"); }));
});
