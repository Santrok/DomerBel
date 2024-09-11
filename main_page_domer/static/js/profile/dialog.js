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
document.getElementById("id_message_send_input").focus()
document.getElementById("id_message_send_input").onkeyup = function (e) {
    if (e.keyCode == 13) {
        document.getElementById("id_message_send_button").click()
    }
}
document.getElementById("id_message_send_button").onclick = function (e) {
    let messageInput = document.getElementById("id_message_send_input").value
    let date = new Date()
    chatSocket.send(JSON.stringify({message: messageInput, userId: userId, time:`${date.getHours()}:${date.getMinutes()}`}))
}
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data)
    let messageItem = document.createElement("div")
    let messageText = document.createElement("p")
    let messageTime = document.createElement("p")
    messageItem.classList.add("message__item")
    messageItem.classList.add(userId === data.userId ? "message-self" : "message-any")
    messageText.classList.add("message__item-text")
    messageText.innerHTML = data.message
    messageTime.classList.add("message__item-time")
    messageTime.innerHTML = data.time
    messageItem.append(messageText)
    messageItem.append(messageTime)
    document.getElementById("id_message_send_input").value = ""
    document.getElementById("id_chat_item_container").append(messageItem)
    lastMessageScroll(messageItem)
}


const chatMessageBlock = document.getElementById("id_message_send_input")

chatMessageBlock.oninput = (e) => {
    if (e.currentTarget.value.length > 0) {
        document.getElementById("id_message_send_button").disabled = false
    } else {
        document.getElementById("id_message_send_button").disabled = true
    }
}