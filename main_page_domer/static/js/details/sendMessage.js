const sendMessageBtn = document.querySelectorAll(".details__advertisement-send-message")
const blockModals = document.querySelector(".modals")
const sendMessageModal = document.querySelector(".send__message")
const sendMessageFormBtn = document.querySelector(".send__message button")
const isAuthenticated = document.querySelector(".details__advertisement-add-favorites")

sendMessageBtn.forEach(item => item.addEventListener("click", () => {
  if(isAuthenticated.dataset.id) {
    blockModals.classList.add("modal__active")
    sendMessageModal.classList.add("modal__active")
  } else {
    modal.classList.add("modal__active")
    modalLogin.classList.add("modal__active")
  }
}) 
)

sendMessageFormBtn.addEventListener("click", sendMessage)

function sendMessage() {
  const data = new FormData(sendMessageModal)
  data.append("advertisement", isAuthenticated.dataset.id)
  fetch(`${window.location.protocol}//${window.location.host}/api/v1/create_chat/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: data
  })
}