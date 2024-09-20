const answerProcessing = document.querySelector('.answer');
const fileForm = document.getElementById('file_form')
const sendBtn = document.getElementById('send')
const message = document.querySelector('.form__notifications-access')
const tableFile = document.querySelector('.table_with_files info__text')
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
                // console.log(tableFile)
                setTimeout(getResult, 3000, id)
            } else if (data.state == 'SUCCESS'){
                const url = data.result.file.slice(1,data.result.file.length+1)
                answerProcessing.innerHTML =`
                <p class="info__text">При обработке вашего файла некоторые объявления не были сохранены. Чтобы посмотреть объявления с ошибками, скачайте файл
                <a href="${window.location.protocol}//${window.location.host}${url}">по ссылке</a>.</p>`
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
                message.classList.add('access__active')
                getResult(id)
            } else if (data.error != undefined) {
                answerProcessing.innerHTML = `
                <p class="info__text"">${data.error}</p>`
            }
        })
    fileForm.reset()
}

