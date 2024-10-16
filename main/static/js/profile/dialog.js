const messagesList = document.getElementById("id_chat_item_container")
messagesList.scrollTo(0, messagesList.scrollHeight)

function lastMessageScroll(b) {
    if (!messagesList) return;

    messagesList.scrollTo({
        top: messagesList.scrollHeight,
        left: 100,
        behavior: "smooth",
    });
}

const userId = document.querySelector(".message__input").dataset.id
const roomName = JSON.parse(document.getElementById("room-name").textContent)
const chatSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/chat/" + roomName + "/"
)
chatSocket.onopen = function (e) {
    console.log("The connection was setup successfully !")
}
chatSocket.onclose = function (e) {
    console.log("Something unexpected happened !")
}
document.querySelector("#id_message_send_input").focus()
document.querySelector("#id_message_send_input").onkeyup = function (e) {
    if (e.keyCode == 13) {
        document.querySelector("#id_message_send_button").click()
    }
}
document.querySelector("#id_message_send_button").onclick = function (e) {
    let messageInput = document.querySelector("#id_message_send_input").value
    chatSocket.send(JSON.stringify({message: messageInput, userId: userId}))
}
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data)
    console.log(data)
    let p = document.createElement("p")
    p.classList.add("message__item")
    p.classList.add(userId === data.userId ? "message-self" : "message-any")
    p.innerHTML = data.message
    document.querySelector("#id_message_send_input").value = ""
    document.querySelector("#id_chat_item_container").append(p)
    lastMessageScroll(p)
}


const chatMessageBlock = document.getElementById("id_message_send_input")

chatMessageBlock.oninput = (e) => {
    if (e.currentTarget.value.length > 0) {
        document.querySelector("#id_message_send_button").disabled = false
    } else {
        document.querySelector("#id_message_send_button").disabled = true
    }
}