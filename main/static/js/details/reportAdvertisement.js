const reportBtn = document.querySelector(".details__advertisement-add-report")
const requestReportBtn = document.getElementById("reportAdvertisement")
reportBtn.addEventListener("click", () => {
  document.querySelector(".modals").classList.add("modal__active")
  document.querySelector(".modals__report-advertisement").classList.add("modal__active")
})



requestReportBtn.addEventListener("click", () => {
  const form = document.querySelector(".modals__report-advertisement")
  const formData = new FormData(form)
  const id = document.querySelector('.details__advertisement-id').textContent
  formData.append("advertisement", id.split(":")[1])
  // formData.append("recaptcha", formData.get("g-recaptcha-response"));
  fetch(`${window.location.protocol}//${window.location.host}/api/v1/save_complaint/`, {
  method: "POST",
    headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
  body: formData
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
      form.reset()
    }
  })
  .catch((err) => {
    const data = JSON.parse(err.message);
    if (data["recaptcha"]) {
      registrationButton.removeEventListener("click", registration);
    }
    delete data["recaptcha"];
    grecaptcha.reset();
    generatingErrorSField(data, ".modals__report-advertisement");
  });
})


function getCookie(name) {
    const cookie = document.cookie.split(';')
    for(let i of cookie) {
        const [cookieName, cookieValue] = i.trim().split('=');
        if(cookieName == name) {
            return cookieValue
        }
    }
}
