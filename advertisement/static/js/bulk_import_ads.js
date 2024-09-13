const answerProcessing = document.querySelector('.answer');
const fileForm = document.getElementById('file_form')
const sendBtn = document.getElementById('send')
sendBtn.addEventListener('click', sendFile)

function getCookie(name) {
    const cookie = document.cookie.split(";");
    for (let i of cookie) {
        const [cookieName, cookieValue] = i.trim().split("=");
        if (cookieName == name) {
            return cookieValue;
        }
    }
}


function getResult(id) {
    fetch(
        `${window.location.protocol}//${window.location.host}/api/v1/get_result_task/${id}`, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            },
            body: JSON.stringify(id),
        }
    )
        .then(response => response.json())
        .then(data => {
            if (data.state != undefined && data.state != 'SUCCESS') {
                console.log(data.state)
                setTimeout(getResult, 3000, id)
            } else if (data.state == 'SUCCESS'){
                const url = data.result.file.slice(1,data.result.file.length+1)
                answerProcessing.innerHTML =`
                <p>При обработке вашего файла некоторые объявления не были сохранены. Чтобы посмотреть объявления с ошибками, скачайте файл по ссылке.</p>
                <a href="${window.location.protocol}//${window.location.host}${url}">Скачать файл</a>`
            }
        })
}


function sendFile() {
    let data = new FormData(fileForm)

    fetch(
        `${window.location.protocol}//${window.location.host}/api/v1/get_bulk_import_of_ads/`, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: data,
        }
    )
        .then(response => response.json())
        .then(data => {
            if (data.task_id != undefined) {
                const id = data.task_id
                getResult(id)
            } else if (data.error != undefined) {
                answerProcessing.innerHTML = `
                <p class="amswer__text">${data.error}</p>`
            }
        })
    fileForm.reset()
}

