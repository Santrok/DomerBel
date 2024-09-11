const sendMessageBtn = [
  ...document.querySelectorAll(".details__advertisement-send-message"),
  ...document.querySelectorAll(".store__send-email"),
]
const blockModals = document.querySelector(".modals")
const sendMessageModal = document.querySelector(".send__message")
const sendMessageFormBtn = document.querySelector(".send__message button")

sendMessageBtn.forEach((item) =>
  item.addEventListener("click", () => {
    if (item.dataset.id) {
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
  if (window.location.pathname.includes("store")) {
    data.append(
      "store",
      sendMessageBtn.find((item) => item.dataset.id).dataset.id
    )
  }else if (window.location.pathname.includes("advertisement_details")) {
    data.append(
      "advertisement",
      sendMessageBtn.find((item) => item.dataset.id).dataset.id
    )
  }
  data.append(
    "chat_object",
    sendMessageBtn.find((item) => item.dataset.id).dataset.id
  )
  fetch(
    `${window.location.protocol}//${window.location.host}/api/v1/create_chat/`,
    {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: data,
    }
  )
    .then((resp) => resp.json())
    .then((data) => {
        if (data.error) {
            document.querySelector(".modals__notification-success").innerHTML = '<svg width="34.833332" height="34.833313" viewBox="0 0 34.8333 34.8333" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n' +
                '                        <defs>\n' +
                '                            <filter id="filter_8_7_dd" x="4.316090" y="8.224854" width="26.510229" height="26.510254" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">\n' +
                '                                <feFlood flood-opacity="0" result="BackgroundImageFix"/>\n' +
                '                                <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>\n' +
                '                                <feOffset dx="0" dy="4"/>\n' +
                '                                <feGaussianBlur stdDeviation="1.33333"/>\n' +
                '                                <feComposite in2="hardAlpha" operator="out" k2="-1" k3="1"/>\n' +
                '                                <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"/>\n' +
                '                                <feBlend mode="normal" in2="BackgroundImageFix" result="effect_dropShadow_1"/>\n' +
                '                                <feBlend mode="normal" in="SourceGraphic" in2="effect_dropShadow_1" result="shape"/>\n' +
                '                            </filter>\n' +
                '                        </defs>\n' +
                '                        <circle id="circle" cx="17.416666" cy="17.416626" r="16.666666" fill="#FF0000" fill-opacity="1.000000"/>\n' +
                '                        <circle id="circle" cx="17.416666" cy="17.416626" r="16.666666" stroke="#FF0000" stroke-opacity="1.000000" stroke-width="1.500000" stroke-linejoin="round"/>\n' +
                '                        <g filter="url(#filter_8_7_dd)"/>\n' +
                '                        <path id="Линия 1" d="M9.57121 25.48L25.5712 9.47998" stroke="#FFFFFF" stroke-opacity="1.000000" stroke-width="2.500000" stroke-linecap="round"/>\n' +
                '                        <path id="Линия 2" d="M9.57121 9.47998L24.5712 25.48" stroke="#FFFFFF" stroke-opacity="1.000000" stroke-width="2.500000" stroke-linecap="round"/>\n' +
                '                    </svg>\n'
        }
      document
        .querySelector(".modals__notification")
        .classList.add("modal__active")
      modal.classList.add("modal__active")
      document.querySelector(".modals__notification-text").innerText =
        data.success ? data.success : data.error
      sendMessageModal.classList.remove("modal__active")
    })
  sendMessageModal.reset()
}
