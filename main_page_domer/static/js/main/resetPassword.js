const modalResetPassowrd = document.querySelector(".modals__reset-password");
const backBtn = document.querySelector(".modals__reset-password a");
const resetSubmitPasswordBtn = document.getElementById("resetSubmitBtn");
const resetPasswordBtn = document.querySelector(".modals__login-action").children[0];

resetPasswordBtn.addEventListener("click", () => {
  for (let i of modal.children) {
    i.classList.remove("modal__active");
  }
  modalResetPassowrd.classList.add("modal__active");
});

backBtn.addEventListener("click", () => {
  for (let i of modal.children) {
    i.classList.remove("modal__active");
  }
  signUp.classList.add("modal__active");
});

resetSubmitPasswordBtn.addEventListener("click", requestResetPassword);

function requestResetPassword() {
  const data = new FormData(modalResetPassowrd);
  data.append("recaptcha", data.get("g-recaptcha-response"));
  fetch(`${window.location.protocol}//${window.location.host}/api/v1/password_reset/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: data,
  })
    .then((response) => response.json())
    .then((data) => {
      if(data.errors) throw new Error(JSON.stringify(data.errors));
      if(data.success) {
        modalResetPassowrd.classList.remove("modal__active");
        document.querySelector(".modals__notification").classList.add("modals__active-resetPassword");
        document.querySelector(".modals__notification-text").innerHTML = data.success;
      }
    })
    .catch((error) => {
        const errorMessage = JSON.parse(error.message)
        if (errorMessage["recaptcha"]) {
            resetSubmitPasswordBtn.removeEventListener("click", requestResetPassword);
          }
        if(errorMessage["recaptcha"]) delete errorMessage["recaptcha"];
        grecaptcha.reset(1)
        generatingErrorSField(errorMessage, '.modals__reset-password');
    });
}
