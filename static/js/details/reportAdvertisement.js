const reportBtn = document.querySelector(".details__advertisement-add-report")
const requestReportBtn = document.getElementById("reportAdvertisement")
reportBtn.addEventListener("click", () => {
  document.querySelector(".modals").classList.add("modal__active")
  document.querySelector(".modals__report-advertisement").classList.add("modal__active")
})



requestReportBtn.addEventListener("click", () => {
  const form = new FormData(document.querySelector(".modals__report-advertisement"))
  const id = document.querySelector('.details__advertisement-id').textContent
  form.append("advertisement", id.split(":")[1])
  form.append("recaptcha", form.get("g-recaptcha-response"));
  fetch(`${window.location.protocol}//${window.location.host}/api/v1/save_complaint/`, {
  method: "POST",
  body: form
  })
  .then((resp) => resp.json())
  .then((data) => {
    if (data.errors) {
      throw new Error(JSON.stringify(data.errors));
    }
    if (data.success) {
      const notificationModal = document.querySelector(".modals__notification");
      document.querySelector(".modals__report-advertisement").classList.remove("modal__active");
      notificationModal.classList.add("modal__active");
      const notificationText = document.querySelector(".modals__notification-text");
      notificationText.innerText = data.success;
    }
  })
  .catch((err) => {
    const data = JSON.parse(err.message);
    if (data["recaptcha"]) {
      registrationButton.removeEventListener("click", registration);
    }
    delete data["recaptcha"];
    // reseting recaptcha field
    grecaptcha.reset();
    generatingErrorSField(data, ".modals__signIn");
  });
})
