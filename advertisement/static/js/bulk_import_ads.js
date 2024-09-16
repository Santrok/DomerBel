// console.log('hi')
// const download_file = document.querySelector('.answer');
// download_file.addEventListener('click', Download);
//
// function Download(event){
//     if (event.target.className == 'download_file'){
//      const a = event.target
// //     a.preventDefault()
//      let xhr = new XMLHttpRequest();
//      xhr.open('GET',a.href)
//      xhr.send()
//      xhr.onloadstart = function(event){
//         console.log('отдано на старте:'+event.loaded)
//         console.log('всего на старте:'+event.total)
//      }
//      xhr.onprogress = function(event){
//         console.log('отдано прогресс:'+event.loaded)
//         console.log('всего прогресс:'+event.total)
//      }
//      xhr.onloaded = function(event){
//          console.log('отдано конец:'+event.loaded)
//          console.log('всего конец:'+event.total)
//      }
//     }
//
//
// }

function getCookie(name) {
  const cookie = document.cookie.split(";");
  for (let i of cookie) {
    const [cookieName, cookieValue] = i.trim().split("=");
    if (cookieName == name) {
      return cookieValue;
    }
  }
}


const fileForm = document.getElementById('file_form')
const sendBtn = document.getElementById('send')
    sendBtn.addEventListener('click', sendFile)

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
            console.log(data)
        })
}

