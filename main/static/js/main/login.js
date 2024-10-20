const modalLogin = document.querySelector(".modals__login")
const loginBtn = document.querySelector(".header__up-user")
const wrapModal = document.querySelector(".modals")

loginBtn?.addEventListener("click", () => {
  document.body.style.overflow = "hidden"
  wrapModal.classList.add("modal__active")
  modalLogin.classList.add("modal__active")
})
