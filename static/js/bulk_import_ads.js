console.log('hi')
const download_file = document.querySelector('.answer');
download_file.addEventListener('click', Download);

function Download(event){
    if (event.target.className == 'download_file'){
     const a = event.target
//     a.preventDefault()
     let xhr = new XMLHttpRequest();
     xhr.open('GET',a.href)
     xhr.send()
     xhr.onloadstart = function(event){
        console.log('отдано на старте:'+event.loaded)
        console.log('всего на старте:'+event.total)
     }
     xhr.onprogress = function(event){
        console.log('отдано прогресс:'+event.loaded)
        console.log('всего прогресс:'+event.total)
     }
     xhr.onloaded = function(event){
         console.log('отдано конец:'+event.loaded)
         console.log('всего конец:'+event.total)
     }
    }


}

