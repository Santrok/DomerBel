const getElementSelectOblast = document.getElementById("select_oblast")
getElementSelectOblast.addEventListener("change", showCity)
const getElementSelectCategory0 = document.getElementById("select_category_0")
const categorySelect = document.querySelector(".category_select")
categorySelect.addEventListener("change", showCategory)
let regionStatus = document.getElementById("select_oblast").value
let statusCategory0 = document.getElementById("select_category_0")
    ? document.getElementById("select_category_0").value
    : ""
let statusCategory1 = document.getElementById("select_category_1")
    ? document.getElementById("select_category_1").value
    : ""
let statusCategory2 = document.getElementById("select_category_2")
    ? document.getElementById("select_category_2").value
    : ""
let statusCategory3 = document.getElementById("select_category_3")
    ? document.getElementById("select_category_3").value
    : ""
const informationList = document.querySelector(".additional_information")
informationList.addEventListener("change", showAdditionalInformationTwo)
let statusElementTwo = document.querySelector(
    ".information_item.information_item_two"
)
    ? document.querySelector(".information_item.information_item_two").dataset
        .element
    : ""

document.getElementById("select_category_0").addEventListener("change", () => {
    informationList.innerHTML = ""
    document.querySelector(".category_level_1")?.remove()
    document.querySelector(".category_level_2")?.remove()
    document.querySelector(".category_level_3")?.remove()
    statusCategory1 = ""
    statusCategory2 = ""
    statusCategory3 = ""
})

document.getElementById("select_category_1")?.addEventListener("change", () => {
    informationList.innerHTML = ""
    document.querySelector(".category_level_2")?.remove()
    document.querySelector(".category_level_3")?.remove()
    statusCategory2 = ""
    statusCategory3 = ""
})

document.getElementById("select_category_2")?.addEventListener("change", () => {
    informationList.innerHTML = ""
    document.querySelector(".category_level_3")?.remove()
    statusCategory3 = ""
})


function showCity(event) {
    if (event.target.value !== regionStatus) {
        regionStatus = event.target.value
        if (event.target.value !== "0") {
            fetch(`${window.location.protocol}//${window.location.host}/api/v1/get_city_list/${event.target.value}`)
                .then((response) => response.json())
                .then((data) => {
                    if (document.querySelector(".city")) {
                        document.getElementById("select_city").innerHTML = ` 
                    <option value="">---------</option>
                    ${data.map(
                            (elem) =>
                                `<option value="${elem.id}">${elem.area}</option>`
                        )}`
                    } else {
                        let region = document.createElement("p")
                        region.classList.add("city")

                        region.innerHTML = `
                <select class="input_field" id="select_city" name="region">
                        <option value="">---------</option>
                    ${data.map(
                            (elem) =>
                                `<option value="${elem.id}">${elem.area}</option>`
                        )}
                    </select>
                `
                        event.target.parentElement.parentElement.append(region)
                    }
                })
        } else if (event.target.value === "0") {
            if (document.querySelector(".city")) {
                document.querySelector(".city").remove()
            }
        }
    }
}

function showCategory(event) {
    if (
        event.target === getElementSelectCategory0 &&
        event.target.value !== statusCategory0
    ) {
        statusCategory0 = event.target.value
        if (event.target.value !== "") {
            fetch(
                `${window.location.protocol}//${window.location.host}/api/v1/get_category_list/?id=${event.target.value}`
            )
                .then((response) => response.json())
                .then((data) => {
                    informationList.innerHTML = ""
                    let category = document.createElement("div")
                    category.classList.add("category_level_1")
                    category.innerHTML += `
            <select class="input_field select_class_category" name="category" id="select_category_1">
                <option value="">---------</option>
                ${data.map(
                        (elem) => `<option value="${elem.id}">${elem.title}</option>`
                    )}
            </select>

                `
                    event.target.parentElement.parentElement.append(category)
                })
        }
    }
    if (
        event.target === document.getElementById("select_category_1") &&
        event.target.value !== statusCategory1
    ) {
        statusCategory1 = event.target.value
        informationList.innerHTML = ""
        if (event.target.value !== "") {
            fetch(
                `${window.location.protocol}//${window.location.host}/api/v1/get_category_list/?id=${event.target.value}`
            )
                .then((response) => response.json())
                .then((data) => {
                    if (data.length !== 0) {
                        informationList.innerHTML = ""
                        let category = document.createElement("div")
                        category.classList.add("category_level_2")
                        category.innerHTML += `
            <select class="input_field select_class_category" name="category" id="select_category_2">
                <option value="">---------</option>
                ${data.map(
                            (elem) => `<option value="${elem.id}">${elem.title}</option>`
                        )}
            </select>
                `
                        event.target.parentElement.parentElement.append(category)
                        event.target.addEventListener("change", () => {
                            informationList.innerHTML = ""
                            document.querySelector(".category_level_2")?.remove()
                            document.querySelector(".category_level_3")?.remove()
                            statusCategory2 = ""
                            statusCategory3 = ""
                        })
                    } else {
                        show_additional_information(event)
                    }
                })
        }
    }
    if (
        event.target === document.getElementById("select_category_2") &&
        event.target.value !== statusCategory2
    ) {
        statusCategory2 = event.target.value
        informationList.innerHTML = ""
        if (event.target.value !== "") {
            fetch(
                `${window.location.protocol}//${window.location.host}/api/v1/get_category_list/?id=${event.target.value}`
            )
                .then((response) => response.json())

                .then((data) => {
                    if (data.length !== 0) {
                        informationList.innerHTML = ""
                        let category = document.createElement("div")
                        category.classList.add("category_level_3")
                        category.innerHTML += `
            <select class="input_field select_class_category" name="category" id="select_category_3">
                <option value="">---------</option>
                ${data.map(
                            (elem) => `<option value="${elem.id}">${elem.title}</option>`
                        )}
            </select>
                `
                        event.target.parentElement.parentElement.append(category)
                        event.target.addEventListener("change", () => {
                            informationList.innerHTML = ""
                            document.querySelector(".category_level_3")?.remove()
                            statusCategory3 = ""
                        })
                    } else {
                        show_additional_information(event)
                    }
                })
        }
    }
    if (
        event.target === document.getElementById("select_category_3") &&
        event.target.value !== statusCategory3
    ) {
        statusCategory3 = event.target.value
        informationList.innerHTML = ""
        if (event.target.value !== "") {
            show_additional_information(event)
        }
    }
}

function show_additional_information(event) {
    fetch(`${window.location.protocol}//${window.location.host}/api/v1/get_field_list/?id=${event.target.value}`)
        .then((response) => response.json())
        .then((data) => {
            informationList.innerHTML = ""
            for (let i of data) {
                if (
                    i.spisok === null &&
                    i.min_val_interval_date === 0 &&
                    i.title !== "Цена" &&
                    i.title !== "Арендная плата" &&
                    i.title !== "Зарплата" &&
                    i.title !== "Минимальная зарплата"
                ) {
                    informationList.innerHTML += ` 
<div class="additional_information_item-${i.id}">
<div class="additional_information_item item_input">
<div class="information_label label_fields">
${i.title ? i.title : i.title_ad}
</div>
<div class="information_select">
<div class="information_item">
 <input class="information_item-input" id="information_${
                        i.id
                    }" type="text" name="${i.id}">
        </div>
</div>
</div> 
</div>
`
                } else if (i.min_val_interval_date !== 0) {
                    let minValDate = i.min_val_interval_date
                    const dateArray = []
                    dateArray.push(minValDate)
                    while (minValDate !== i.max_val_interval_date) {
                        minValDate = minValDate + 1
                        dateArray.push(minValDate)
                    }
                    if (i.title == "Этаж") {
                        informationList.innerHTML += `
<div class="additional_information_item-${i.id} inner_select">
<div class="additional_information_item item_input">
<div class="information_label label_fields">
Этаж
</div>
<div class="information_select">
<div class="information_item">
            <select class="input_field select_class" id="information_${
                            i.id
                        }" name="${i.id}">
                <option value="">---------</option>
                ${dateArray.map(
                            (elem) => `<option value="${elem}">${elem}</option>`
                        )}
            </select>
        </div>
</div>
</div>
<div class="additional_information_item item_input">
<div class="information_label label_fields">
Этажей в доме
</div>
<div class="information_select">
<div class="information_item">
            <select class="input_field select_class" id="element_two-${
                            i.id
                        }" name="${i.id}">
                <option value="">---------</option>
                ${dateArray.map(
                            (elem) => `<option value=${elem}>${elem}</option>`
                        )}
            </select>
        </div>
</div>
</div>
</div>
                    `
                    } else {
                        informationList.innerHTML += `
<div class="additional_information_item-${i.id} inner_select">
<div class="additional_information_item item_input">
<div class="information_label label_fields">
${i.title ? i.title : i.title_ad}
</div>
<div class="information_select">
<div class="information_item">
            <select class="input_field select_class" id="information_${
                            i.id
                        }" name="${i.id}">
                <option value="">---------</option>
                ${dateArray.map(
                            (elem) => `<option value=${elem}>${elem}</option>`
                        )}
            </select>
        </div>
</div>
</div>
</div>
                    `
                    }
                } else if (
                    i.title === "Цена" ||
                    i.title === "Арендная плата" ||
                    i.title === "Зарплата" ||
                    i.title === "Минимальная зарплата"
                ) {
                    informationList.innerHTML += ` 
<div class="additional_information_item-price">
<div class="additional_information_item item_input">
<div class="information_label label_fields">
${i.title ? i.title : i.title_ad}, руб
</div>
<div class="information_select">
<div class="information_item">
 <input class="information_item-input price" id="information_${
                        i.id
                    }" type="text" name="${i.id}">
 <input class="information_item-input price-hidden" id="information_${
                        i.title
                    }" type="hidden" name="${i.title}">
        </div>
</div>
</div> 
</div>
`
                } else {
                    informationList.innerHTML += `
<div class="additional_information_item-${i.id}">
<div class="additional_information_item item_input">
<div class="information_label label_fields">
${i.title ? i.title : i.title_ad}
</div>
<div class="information_select">
<div class="information_item">
            <select class="input_field select_class select_info" id="information_${
                        i.id
                    }" name="${i.id}">
                <option value="">---------</option>
                ${i.spisok.element_set?.map(
                        (elem) =>
                            `<option value="${elem.title}" data-elementtwo="${elem.id}">${elem.title}</option>`
                    )}
            </select>
        </div>
</div>
</div>
</div>
                    `
                }
            }
        })
}

function showAdditionalInformationTwo(event) {
    if (
        event.target.className === "input_field select_class select_info" &&
        event.target.value !== statusElementTwo
    ) {
        let elementTwo = ""
        for (let i of event.target.children) {
            if (i.value === event.target.value) {
                elementTwo = i.dataset.elementtwo
                break
            }
        }
        if (elementTwo && statusElementTwo !== event.target.value) {
            fetch(
                `${window.location.protocol}//${window.location.host}/api/v1/get_elementtwo_list/?slug=${elementTwo}`
            )
                .then((response) => response.json())
                .then((data) => {
                    if (data.length > 0) {
                        statusElementTwo = event.target.value
                        if (document.querySelector(".information_item_two")) {
                            document.querySelector(".information_item_two").remove()
                        }
                        let elementP = document.createElement("div")
                        elementP.classList.add("information_item")
                        elementP.classList.add("information_item_two")
                        elementP.innerHTML += `
            <select class="input_field select_class select_info_two" id='element_two-${event.target.getAttribute(
                            "name"
                        )}' name="${event.target.getAttribute("name")}">
                <option value="">---------</option>
                ${data.map(
                            (elem) =>
                                `<option value="${elem.title}">${elem.title}</option>`
                        )}
            </select>
                `
                        event.target.parentElement.parentElement.append(elementP)
                    }
                })
        } else if (
            event.target ===
            document.querySelector(".information_item_two").parentElement.children[0]
                .children[0]
        ) {
            if (document.querySelector(".information_item_two")) {
                document.querySelector(".information_item_two").remove()
            }
        }
    }
}

const bearerCompany = document.querySelector(".description_radio")
bearerCompany?.addEventListener("change", bearerCompanyInfo)

function bearerCompanyInfo(event) {
    if (event.target.id === "bearer_company") {
        if (!document.querySelector(".bearer_company_store")) {
            fetch(`${window.location.protocol}//${window.location.host}/api/v1/get_store_for_advertisement/`)
                .then((response) => response.json())
                .then((data) => {
                    const bearerCompanyStore = document.createElement("div")
                    bearerCompanyStore.classList.add("bearer_company_store")
                    bearerCompanyStore.innerHTML = `
                    <div class="store_input item_input">
                        <p class="store_label label_fields">
                        Магазин
                        </p>
                    <div class="store_select">
                        <div class="bearer_store">
                            <select class="input_field" name="store" id="select_store">
                                <option value="">---------</option>
                                ${data.map(
                        (elem) =>
                            `<option value="${elem.id}">${elem.title}</option>`
                    )}
                            </select>
                        </div>
                    </div>
                </div>`
                    const bearerCompanyVendorCode = document.createElement("div")
                    bearerCompanyVendorCode.classList.add("bearer_company_vendor_code")
                    bearerCompanyVendorCode.innerHTML = `
        <div class="vendor_code_input item_input">
                        <p class="vendor_code_label label_fields">Артикул</p>
                        <input type="text" name="article" id="article" class="information_item-input">
                    </div>
        `
                    document
                        .querySelector(".bearer_company_additional_info")
                        .append(bearerCompanyStore)
                    document
                        .querySelector(".bearer_company_additional_info")
                        .append(bearerCompanyVendorCode)
                })
        }
    } else if (event.target.id === "bearer_private_person") {
        document.querySelector(".bearer_company_additional_info").innerHTML = ""
    }
}

const preview = document.querySelector(".photo_preview")
preview.addEventListener("click", removeImg)
const inputElement = document.getElementById("photo_list")
inputElement.addEventListener("change", handleFiles, false)
let inputElementArray = []
let mainImg = document.querySelector(".main_img")
    ? document.querySelector(".main_img")
    : ""
let totalSize = 0
const maxSize = 20971520
const maxFiles = 30
const dt = new DataTransfer(); // Для обновления FileList

function handleFiles() {
    const fileList = this.files; // Получаем загруженные файлы
    let newSize = totalSize; // Текущий общий размер
  
    // Проверка превышения количества файлов
    if (inputElementArray.length + fileList.length > maxFiles) {
      alert(`Вы можете загрузить не более ${maxFiles} файлов.`);
      return;
    }
  
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
  
      // Проверка типа файла (только изображения)
      if (!file.type.startsWith("image/")) {
        continue;
      }
  
      // Проверка общего размера
      newSize += file.size;
      if (newSize > maxSize) {
        alert(
          `Файл "${file.name}" превышает допустимый общий размер (${maxSize / (1024 * 1024)} МБ). Он не будет добавлен.`
        );
        newSize -= file.size;
        console.log(dt.files);
        
        continue;
      }
  
      // Добавление файла в DataTransfer
      dt.items.add(file);
  
      // Создание превью изображения
      const img = document.createElement("img");
      img.classList.add("img_preview");
      if (!mainImg && i === 0) {
        img.classList.add("main_img");
        mainImg = img;
      }
      img.file = file;
      img.setAttribute("name", file.name);
      img.setAttribute("data-id", inputElementArray.length + i);
  
      const div = document.createElement("div");
      div.classList.add("photo_img");
  
      const div2 = document.createElement("div");
      div2.classList.add("delete_img");
      div2.setAttribute("data-name", file.name);
      div.append(div2);
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
  
    // Обновляем inputElementArray и устанавливаем новый FileList
    inputElementArray = Array.from(dt.files);    
    inputElement.files = dt.files;
  
    // Обновляем общий размер файлов
    totalSize = newSize;
}

let deletedImages = []

function removeImg(event) {
    console.log(event);
    
    if (document.querySelector(".photo_file_error")) {
        document.querySelector(".photo_file_error").remove()
        document.querySelector(".photo_file").classList.remove("input_error")
    }
    const dataTransfer = new DataTransfer()
    let z = []

    let target = event.target
    if (target.classList.contains("delete_img")) {
        target.parentElement.remove()
        if (target.parentElement.children[1].classList.contains("main_img")) {
            if (document.querySelector(".photo_preview").childElementCount !== 0) {
                document
                    .querySelector(".photo_preview")
                    .children[0].children[1].classList.add("main_img")
                mainImg =
                    document.querySelector(".photo_preview").children[0].children[1]
            } else {
                mainImg = ""
            }
        }
        if (
            window.location.href ===
            `${window.location.protocol}//${window.location.host}/advertisement/editing_an_ad/${
                document.getElementById("add_adver").dataset.advertisement
            }/`
        ) {
            deletedImages.push(target.dataset.name)
        }
        inputElementArray = inputElementArray.filter(
            (file) => file.name !== target.dataset.name
        )
        for (let i of inputElementArray) {
            dataTransfer.items.add(i)
        }
        z = dataTransfer.files
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

function pathSend (data) {
    if (window.location.href.includes('editing_an_ad')){
           return fetch(`${window.location.origin}/api/v1/update_advertisement/`,
               {
            method: "PATCH",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: data,
        }
               )
        }
    else if (window.location.href.includes('place_an_ad')) {
        return fetch(`${window.location.origin}/api/v1/save_advertisement/`,
               {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: data,
        }
               )
        }
}

const addAdvForm = document.getElementById("add_adver")
const addAdvButton = document.querySelector(".add_adv")
addAdvButton.addEventListener("click", saveAdvertisement)
const blockModals = document.querySelector(".modals")

function saveAdvertisement() {
    blockModals.classList.add("modal__active")
    if (document.querySelector(".price-hidden")) {
        document.querySelector(".price-hidden").value =
            document.querySelector(".price").value
    }
    let data = new FormData(addAdvForm)
    if (mainImg) {
        data.append("preview_img", mainImg.name)
    } else {
        data.append("preview_img", mainImg)
    }
    if (document.getElementById("add_adver").dataset.advertisement) {
        data.append(
            "advertisement",
            document.getElementById("add_adver").dataset.advertisement
        )
        data.append("deleted_images", deletedImages)
    }
    if (data.has("Цена")) {
        data.append("price", data.get("Цена"))
        data.delete("Цена")
    } else if (data.has("Арендная плата")) {
        data.append("price", data.get("Арендная плата"))
        data.delete("Арендная плата")
    } else if (data.has("Зарплата")) {
        data.append("price", data.get("Зарплата"))
        data.delete("Зарплата")
    } else if (data.has("Минимальная зарплата")) {
        data.append("price", data.get("Минимальная зарплата"))
        data.delete("Минимальная зарплата")
    }
    if (data.getAll("photo").length <= 1 && !data.get("photo").name) {
        data.delete("photo")
    }
    pathSend(data)
        .then((response) => response.json())
        .then((data) => {
            blockModals.classList.remove("modal__active")
            if (data.error || data.error_additional) {
                const error = new Error("error")
                error.data = data
                throw error
            }
            document.querySelector(".create_advertisement").innerHTML = `
        <div class="advertisement_notification-success">
                    <svg width="48.000000" height="48.000000" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                        <desc>
                                Created with Pixso.
                        </desc>
                        <defs>
                            <clipPath id="clip946_10107">
                                <rect id="Checkmark Circle" width="48.000000" height="48.000000" fill="white" fill-opacity="0"/>
                            </clipPath>
                        </defs>
                        <g clip-path="url(#clip946_10107)">
                            <path id="Shape" d="M24 4C35.04 4 44 12.95 44 24C44 35.04 35.04 44 24 44C12.95 44 4 35.04 4 24C4 12.95 12.95 4 24 4ZM32.63 17.61C32.17 17.16 31.45 17.13 30.96 17.52L30.86 17.61L20.75 27.73L17.13 24.11C16.64 23.62 15.85 23.62 15.36 24.11C14.91 24.57 14.87 25.29 15.27 25.78L15.36 25.88L19.86 30.38C20.32 30.83 21.04 30.86 21.53 30.47L21.63 30.38L32.63 19.38C33.12 18.89 33.12 18.1 32.63 17.61Z" fill="#008060" fill-opacity="1.000000" fill-rule="nonzero"/>
                        </g>
                    </svg>
        ${data?.success}
        <a href=${data?.link} class="continue__link submit__btn">${data?.link_text}</a>
    </div>
`
            window.scrollTo(0, 0)
        })
        .catch((msg) => {
            if (msg.data.error.title) {
                if (document.querySelector(".title_error")) {
                    document.querySelector(".title_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("title_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.title} `
                document.querySelector(".title_adver").append(errorText)
                document.getElementById("title_input").classList.add("input_error")
                document.getElementById("title_input").oninput = () => {
                    if (document.querySelector(".title_error")) {
                        document.querySelector(".title_error").remove()
                        document
                            .getElementById("title_input")
                            .classList.remove("input_error")
                    }
                }
            }
            if (msg.data.error.region) {
                if (document.querySelector(".region_error")) {
                    document.querySelector(".region_error").remove()
                }
                const errorText = document.createElement("div")
                errorText.classList.add("region_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.region} `
                document.querySelector(".region").append(errorText)
                if (document.getElementById("select_city")) {
                    document.getElementById("select_city").classList.add("input_error")
                    document.getElementById("select_city").oninput = () => {
                        if (document.querySelector(".region_error")) {
                            document.querySelector(".region_error").remove()
                            document
                                .getElementById("select_city")
                                .classList.remove("input_error")
                        }
                    }
                } else {
                    document.getElementById("select_oblast").classList.add("input_error")
                    document.getElementById("select_oblast").oninput = () => {
                        if (document.querySelector(".region_error")) {
                            document.querySelector(".region_error").remove()
                            document
                                .getElementById("select_oblast")
                                .classList.remove("input_error")
                        }
                    }
                }
            }
            if (msg.data.error.category) {
                if (document.querySelector(".category_error")) {
                    document.querySelector(".category_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("category_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.category} `
                document.querySelector(".category").append(errorText)
                if (document.getElementById("select_category_3")) {
                    document
                        .getElementById("select_category_3")
                        .classList.add("input_error")
                    document.getElementById("select_category_3").oninput = () => {
                        if (document.querySelector(".category_error")) {
                            document.querySelector(".category_error").remove()
                            document
                                .getElementById("select_category_3")
                                .classList.remove("input_error")
                        }
                    }
                } else if (document.getElementById("select_category_2")) {
                    document
                        .getElementById("select_category_2")
                        .classList.add("input_error")
                    document.getElementById("select_category_2").oninput = () => {
                        if (document.querySelector(".category_error")) {
                            document.querySelector(".category_error").remove()
                            document
                                .getElementById("select_category_2")
                                .classList.remove("input_error")
                        }
                    }
                } else if (document.getElementById("select_category_1")) {
                    document
                        .getElementById("select_category_1")
                        .classList.add("input_error")
                    document.getElementById("select_category_1").oninput = () => {
                        if (document.querySelector(".category_error")) {
                            document.querySelector(".category_error").remove()
                            document
                                .getElementById("select_category_1")
                                .classList.remove("input_error")
                        }
                    }
                } else if (document.getElementById("select_category_0")) {
                    document
                        .getElementById("select_category_0")
                        .classList.add("input_error")
                    document.getElementById("select_category_0").oninput = () => {
                        if (document.querySelector(".category_error")) {
                            document.querySelector(".category_error").remove()
                            document
                                .getElementById("select_category_0")
                                .classList.remove("input_error")
                        }
                    }
                }
            }
            if (msg.data.error.description) {
                if (document.querySelector(".description_error")) {
                    document.querySelector(".description_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("description_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.description} `
                document.querySelector(".description").append(errorText)
                document.getElementById("description").classList.add("input_error")
                document.getElementById("description").oninput = () => {
                    if (document.querySelector(".description_error")) {
                        document.querySelector(".description_error").remove()
                        document
                            .getElementById("description")
                            .classList.remove("input_error")
                    }
                }
            }
            if (msg.data.error.bearer) {
                if (document.querySelector(".bearer_error")) {
                    document.querySelector(".bearer_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("bearer_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.bearer} `
                document.querySelector(".bearer").append(errorText)
                for (let i of document.querySelectorAll(".custom_radio")) {
                    i.classList.add("radio_error")
                }
                document.getElementById("bearer_private_person").oninput = () => {
                    if (document.querySelector(".bearer_error")) {
                        document.querySelector(".bearer_error").remove()
                        for (let i of document.querySelectorAll(".custom_radio")) {
                            i.classList.remove("radio_error")
                        }
                    }
                }
                document.getElementById("bearer_company").oninput = () => {
                    if (document.querySelector(".bearer_error")) {
                        document.querySelector(".bearer_error").remove()
                        for (let i of document.querySelectorAll(".custom_radio")) {
                            i.classList.remove("radio_error")
                        }
                    }
                }
            }
            if (msg.data.error.contact_name) {
                if (document.querySelector(".contact_error")) {
                    document.querySelector(".contact_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("contact_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.contact_name} `
                document.querySelector(".contact_information").append(errorText)
                document.getElementById("contact").classList.add("input_error")
                document.getElementById("contact").oninput = () => {
                    if (document.querySelector(".contact_error")) {
                        document.querySelector(".contact_error").remove()
                        document.getElementById("contact").classList.remove("input_error")
                    }
                }
            }
            if (msg.data.error.email) {
                if (document.querySelector(".email_error")) {
                    document.querySelector(".email_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("email_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.email} `
                document.querySelector(".email_information").append(errorText)
                document.getElementById("email").classList.add("input_error")
                document.getElementById("email").oninput = () => {
                    if (document.querySelector(".email_error")) {
                        document.querySelector(".email_error").remove()
                        document.getElementById("email").classList.remove("input_error")
                    }
                }
            }
            if (msg.data.error.phone_num) {
                if (document.querySelector(".phone_error")) {
                    document.querySelector(".phone_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("phone_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.phone_num} `
                document.querySelector(".phone_information").append(errorText)
                document.getElementById("phone").classList.add("input_error")
                document.getElementById("phone").oninput = () => {
                    if (document.querySelector(".phone_error")) {
                        document.querySelector(".phone_error").remove()
                        document.getElementById("phone").classList.remove("input_error")
                    }
                }
            }
            if (msg.data.error.store) {
                if (document.querySelector(".store_error")) {
                    document.querySelector(".store_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("store_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.store} `
                document.querySelector(".bearer_company_store").append(errorText)
                document.getElementById("select_store").classList.add("input_error")
                document.getElementById("select_store").oninput = () => {
                    if (document.querySelector(".store_error")) {
                        document.querySelector(".store_error").remove()
                        document
                            .getElementById("select_store")
                            .classList.remove("input_error")
                    }
                }
            }
            if (msg.data.error.price) {
                if (document.querySelector(".price_error")) {
                    document.querySelector(".price_error").remove()
                }
                const errorText = document.createElement("p")
                errorText.classList.add("price_error")
                errorText.classList.add("error")
                errorText.innerHTML = `${msg.data.error.price} `
                document
                    .querySelector(".additional_information_item-price")
                    .append(errorText)
                document.querySelector(".price").classList.add("input_error")
                document.querySelector(".price").oninput = () => {
                    if (document.querySelector(".price_error")) {
                        document.querySelector(".price_error").remove()
                        document.querySelector(".price").classList.remove("input_error")
                    }
                }
            }
            if (msg.data.error.photo) {
              if (document.querySelector(".photo_file_error")) {
                document.querySelector(".photo_file_error").remove()
              }
              const errorText = document.createElement("p")
              errorText.classList.add("photo_file_error")
              errorText.classList.add("error")
              errorText.innerHTML = `${msg.data.error.photo} `
              document
                .querySelector(".photo_label")
                .append(errorText)
              document.querySelector(".photo_file").classList.add("input_error")
              document.querySelector(".photo_file").oninput = () => {
                if (document.querySelector(".photo_file_error")) {
                  document.querySelector(".photo_file_error").remove()
                  document.querySelector(".photo_file").classList.remove("input_error")
                }
              }
            }
            if (msg.data.error_additional) {
                for (let i of msg.data.error_additional) {
                    if (document.querySelector(`.additional_${i.id}_error`)) {
                        document.querySelector(`.additional_${i.id}_error`).remove()
                    }
                    const errorText = document.createElement("p")
                    errorText.classList.add(`additional_${i.id}_error`)
                    errorText.classList.add("error")
                    errorText.innerHTML = `${i.error} `
                    document
                        .querySelector(`.additional_information_item-${i.id}`)
                        .append(errorText)
                    document
                        .getElementById(`information_${i.id}`)
                        .classList.add("input_error")
                    if (document.getElementById(`element_two-${i.id}`)) {
                        document
                            .getElementById(`element_two-${i.id}`)
                            .classList.add("input_error")
                        document.getElementById(`element_two-${i.id}`).oninput = () => {
                            if (document.querySelector(`.additional_${i.id}_error`)) {
                                document.querySelector(`.additional_${i.id}_error`).remove()
                                document
                                    .getElementById(`information_${i.id}`)
                                    .classList.remove("input_error")
                                document
                                    .getElementById(`element_two-${i.id}`)
                                    .classList.remove("input_error")
                            }
                        }
                    }
                    document.getElementById(`information_${i.id}`).oninput = () => {
                        if (document.querySelector(`.additional_${i.id}_error`)) {
                            document.querySelector(`.additional_${i.id}_error`).remove()
                            document
                                .getElementById(`information_${i.id}`)
                                .classList.remove("input_error")
                            document
                                .getElementById(`element_two-${i.id}`)
                                .classList.remove("input_error")
                        }
                    }
                }
            }
            if (msg.data.error.advertisement_error) {
                document.querySelector(".create_advertisement").innerHTML = `
        <div class="advertisement_notification-success">
                    <svg width="34.833332" height="34.833313" viewBox="0 0 34.8333 34.8333" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                        <defs>
                            <filter id="filter_8_7_dd" x="4.316090" y="8.224854" width="26.510229" height="26.510254" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
                                <feFlood flood-opacity="0" result="BackgroundImageFix"/>
                                <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
                                <feOffset dx="0" dy="4"/>
                                <feGaussianBlur stdDeviation="1.33333"/>
                                <feComposite in2="hardAlpha" operator="out" k2="-1" k3="1"/>
                                <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"/>
                                <feBlend mode="normal" in2="BackgroundImageFix" result="effect_dropShadow_1"/>
                                <feBlend mode="normal" in="SourceGraphic" in2="effect_dropShadow_1" result="shape"/>
                            </filter>
                        </defs>
                        <circle id="circle" cx="17.416666" cy="17.416626" r="16.666666" fill="#FF0000" fill-opacity="1.000000"/>
                        <circle id="circle" cx="17.416666" cy="17.416626" r="16.666666" stroke="#FF0000" stroke-opacity="1.000000" stroke-width="1.500000" stroke-linejoin="round"/>
                        <g filter="url(#filter_8_7_dd)"/>
                        <path id="Линия 1" d="M9.57121 25.48L25.5712 9.47998" stroke="#FFFFFF" stroke-opacity="1.000000" stroke-width="2.500000" stroke-linecap="round"/>
                        <path id="Линия 2" d="M9.57121 9.47998L24.5712 25.48" stroke="#FFFFFF" stroke-opacity="1.000000" stroke-width="2.500000" stroke-linecap="round"/>
                    </svg>
        ${msg.data.error.advertisement_error.text}
        <a href=${msg.data.error.advertisement_error.link} class="continue__link submit__btn">${msg.data.error.advertisement_error.link_text}</a>
    </div>
`
            window.scrollTo(0, 0)
            }
        })
}
