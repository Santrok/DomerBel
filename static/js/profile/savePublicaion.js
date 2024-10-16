const addPublicationButton = document.getElementById("add_publication");
addPublicationButton.addEventListener("click", savePublication)
const preview = document.querySelector('.photo_preview')
preview.addEventListener('click', removeImg)
const inputElement = document.getElementById("photo_list");
inputElement.addEventListener("change", handleFiles, false);
let inputElementArray = []
let mainImg = ""

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
        if (i === 0) {
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
    inputElementArray = Array.from(inputElement.files);
}

function removeImg(event) {
    const dt = new DataTransfer();
    let z = []
    let target = event.target

    if (target.classList.contains("delete_img")) {
        target.parentElement.remove()
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


function savePublication() {
    const form = document.querySelector(".main__info");
    const title = form.querySelector("input[name='title']");
    const announcement = form.querySelector("textarea[name='announcement']");
    const description = form.querySelector("textarea[name='description']");
    const preview_image = form.querySelector("input[name='preview_image']");
    const csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

    let data = new FormData(form);
    data.append("main_img", mainImg.name)

    fetch(`${window.location.protocol}//${window.location.host}/api/v1/save_publication/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
        },
        body: data,
    })
    .then(response => {
        if (response.ok) {
            document.location.href = `${window.location.protocol}//${window.location.host}/users/user_all_publications/`;
        }
        return response.json()
    })
    .then(response => {
    })
    .catch(error => {
        console.error("Error:", error);
    });
}