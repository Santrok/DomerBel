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
    } else if (window.location.pathname.includes("advertisement_details")) {
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
                    document.querySelector(".modals__notification-success").style.display = 'none'
                    document.querySelector(".modals__notification-error").style.display = 'flex'
                }
                document
                    .querySelector(".modals__notification")
                    .classList.add("modal__active")
                modal.classList.add("modal__active")
                document.querySelector(".modals__notification-text").innerText =
                    data.success ? data.success : data.error
                sendMessageModal.classList.remove("modal__active")
            }
        )
    sendMessageModal.reset()
}
