const inputElement = document.getElementById("photo_list");
inputElement.addEventListener("change", handleFiles, false);
let inputElementArray = [];
let mainImg = document.querySelector('.main_img') ? document.querySelector('.main_img') : '';

function handleFiles() {
    const dt = new DataTransfer();
    const fileList = this.files;
    for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        if (!file.type.startsWith("image/")) {
            continue;
        }
        const img = document.createElement("img");
        img.classList.add("img_preview");
        if (i === 0 && !document.querySelector('.main_img')) {
            img.classList.add("main_img");
            mainImg = img
        }
        img.file = file;
        img.setAttribute('name', fileList[i].name)
        img.setAttribute('data-id', i)
        const div = document.createElement("div")
        div.classList.add("photo_img")
        const div2 = document.createElement("div")
        div2.classList.add("delete_img")
        div2.setAttribute('data-name', fileList[i].name)
        div.append(div2)
        div.append(img);
        preview.append(div);

        const reader = new FileReader();
        reader.onload = (function (aImg) {
            return function (event) {
                aImg.src = event.target.result;
            };
        })(img);
        reader.readAsDataURL(file);
    }
    if (inputElementArray.length === 0) {
        inputElementArray = Array.from(inputElement.files)
    }
    else {
        for (let i of Array.from(inputElement.files)) {
            inputElementArray.push(i)
        }
        let z = []
        for (let i of inputElementArray) {
            dt.items.add(i)
        }
        z = dt.files
        inputElement.files = z
    }

}

const preview = document.querySelector('.photo_preview');
preview.addEventListener('click', removeImg);

let deletedImages = []
function removeImg(event) {
    const dt = new DataTransfer();
    let z = []

    let target = event.target
    if (target.classList.contains("delete_img")) {
        target.parentElement.remove()
        if (target.parentElement.children[1].classList.contains("main_img")) {
            if (document.querySelector('.photo_preview').childElementCount !== 0) {
                document.querySelector('.photo_preview').children[0].children[1].classList.add("main_img")
                mainImg = document.querySelector('.photo_preview').children[0].children[1]
            } else {
                mainImg = ''
            }
        }
        if (window.location.href === `http://127.0.0.1:8000/users/personal_account/edit_publication/${document.getElementById('add_adver').dataset.slug}/`) {
            deletedImages.push(target.dataset.name)
        }
        inputElementArray = inputElementArray.filter(file => file.name !== target.dataset.name);
        for (let i of inputElementArray) {
            dt.items.add(i)
        }
        z = dt.files
        inputElement.files = z
    }
    if (target.classList.contains("img_preview")) {
        if (mainImg) {
            mainImg.classList.remove("main_img")
        }
        target.classList.add("main_img")
        mainImg = target
    }
}

const addPublicationButton = document.querySelector(".button_add_publication");
addPublicationButton.addEventListener("click", savePublication);

function savePublication() {
    const form = document.querySelector(".form_add_publication");
    const title = form.querySelector("input[name='title']");
    const announcement = form.querySelector("textarea[name='announcement']");
    const description = form.querySelector("textarea[name='description']");
    const preview_image = form.querySelector("input[name='preview_image']");
    const csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    const dataSlag = form.dataset.slug;

    let data = new FormData(form);
    data.append("main_img", mainImg.name);
    data.append("dataSlag", dataSlag);
    data.append("deletedImages", deletedImages);

    fetch(`http://127.0.0.1:8000/api/v1/edit_publication/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
        },
        body: data,
    })
    .then(response => {
        if (response.ok) {
            document.location.href = 'http://127.0.0.1:8000/users/user_all_publications/';
        }
        return response.json()
    })
    .catch(error => {
        console.error("Error:", error);
    });
}
