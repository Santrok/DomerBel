const areaZeroLvl = document.querySelector('.areas_list');
areaZeroLvl.addEventListener('click', event => showCity(event));
const categoryZeroLvl = document.querySelector('.categories_list');
categoryZeroLvl.addEventListener('click', event => showCategory(event));

function showCity(event) {
    if (event.target.parentElement.className == 'area_title item_title' && event.target.parentElement.className != 'icon_copy') {
        getCity(event)
    } else if (event.target.className == 'icon_copy') {
        copy(event)
    }
}


function getCity(event) {
//Функция для выпадающего списка городов в зависимости от региона
    const region = event.target.parentElement;
    const cities = region.nextElementSibling;
    const point = region.querySelector('.pointer')
    point.classList.toggle('pointer__active');
    if (cities.childNodes.length == 0) {
        const regionId = region.id;
        fetch(`${localStorage.getItem("url")}/api/v1/get_city_list/${regionId}`)
            .then((response) => response.json())
            .then((data) => {
                for (let city of data) {
                    cities.innerHTML += `<li class="city_title item_title">
                <p>${city.area}</p>
                <div class="copy">
                <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                </div>
                </li>`
                }
            })
    } else {
        cities.innerHTML = ``;
    }
}


function showCategory(event) {
    if (event.target.parentElement.className == 'category_title item_title' && event.target.className != 'icon_copy') {
        getCategory(event)
    } else if (event.target.parentElement.className == 'subcategory_title item_title' && event.target.className != 'icon_copy') {
        getCategoryTwo(event)
    } else if (event.target.parentElement.className == 'field_title item_title' && event.target.className != 'icon_copy') {
        getElement(event)
    } else if (event.target.parentElement.className == 'element_title item_title' && event.target.className != 'icon_copy') {
        getElementTwo(event)
    } else if (event.target.className == 'icon_copy') {
        copy(event)
    }
}


function getCategory(event) {
//Функция для выпадающего списка субкатегорий в зависимости от категорий категорий
    const category = event.target.parentElement;
    const point = category.querySelector('.pointer')
    point.classList.toggle('pointer__active');
    const check = category.nextElementSibling;
    if (check == null) {
        let subcategoriesList = document.createElement('ol');
        subcategoriesList.className = 'subcategories_list title__list'
        category.after(subcategoriesList)
        const categoryId = category.id;
        // fetch(`${localStorage.getItem("url")}/api/v1/get_subcategory_list/?id=${categoryId}`)
        fetch(`${localStorage.getItem("url")}/api/v1/get_category_list/?id=${categoryId}`)
            .then((response) => response.json())
            .then((data) => {
                for (let subcategory of data) {
                    subcategoriesList.innerHTML += `<li class= "subcategory">
                    <div class="subcategory_title item_title" id=${subcategory.id}>
                        <div class="pointer"></div>
                        <p>${subcategory.title}</p>
                        <div class="copy">
                            <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                        </div>
                    </div>
                    </li>`
                }
            })
    } else {
        check.remove()
    }
}



function getCategoryTwo(event) {
    const category = event.target.parentElement;
    const point = category.querySelector('.pointer')
    point.classList.toggle('pointer__active');
    const check = category.nextElementSibling;
    if (check == null) {
        const categoryId = category.id;
        fetch(`${localStorage.getItem("url")}/api/v1/get_subcategory_list/?id=${categoryId}`)
            .then((response) => response.json())
            .then((data) => {
                if (data.length != 0) {
                    let subcategoriesListTwo = document.createElement('ol');
                    subcategoriesListTwo.className = 'subcategories_list title__list'
                    category.after(subcategoriesListTwo)
                    for (let subcategory of data){
                        if (subcategory.field_set.length == 0) {
                            subcategoriesListTwo.innerHTML += `<li class="subcategory">
                            <div class="subcategory_title item_title" id=${subcategory.id}>
                                <p>${subcategory.title}</p>
                                <div class="copy">
                                    <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                                </div>
                            </div>
                            </li>`
                        } else {
                            subcategoriesListTwo.innerHTML += `<li class= "subcategory">
                            <div class="subcategory_title item_title" id=${subcategory.id}>
                                <div class="pointer"></div>
                                <p>${subcategory.title}</p>
                                <div class="copy">
                                    <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                                </div>
                            </div>
                            </li>`
                        }
                    }
                } else {
                    getField(event, point_chek = 1)
                }
            })
    } else {
        check.remove()
    }
}

function getField(event, point_chek = 0) {
//Функция для выпадающего списка полей по субкатегорий
    const subcategory = event.target.parentElement;
    const point = subcategory.querySelector('.pointer')
    if (point != null && point_chek == 0) {
        point.classList.toggle('pointer__active');
    }
    const check = subcategory.nextElementSibling
    if (check == null) {
        let fieldsList = document.createElement('ol');
        fieldsList.className = 'fields_list title__list'
        subcategory.after(fieldsList)
        const subcategoryId = subcategory.id
        fetch(`${localStorage.getItem("url")}/api/v1/get_field_list/?id=${subcategoryId}`)
            .then((response) => response.json())
            .then((data) => {
                for (let field of data) {
                    if (field.spisok !== null) {
                        if (field.title.length == 0) {
                            fieldsList.innerHTML += `<li class="field">
                        <div class="field_title item_title" id=${field.id}>
                            <div class="pointer"></div>
                            <p>${field.title_ad}</p>
                            <div class="copy">
                                <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                            </div>
                        </div>
                        </li>`
                        } else {
                            fieldsList.innerHTML += `<li class="field">
                        <div class="field_title item_title" id=${field.id}>
                            <div class="pointer"></div>
                            <p>${field.title}</p>
                            <div class="copy">
                                <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                            </div>
                        </div>
                        </li>`
                        }
                    } else {
                        fieldsList.innerHTML += `<li class="field">
                        <div class="field_title item_title">
                            <p>${field.title}</p>
                            <div class="copy">
                                <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                            </div>
                        </div>
                        </li>`
                    }
                }
            })
    } else {
        check.remove()
    }
}


function getElement(event) {
    const field = event.target.parentElement
    const point = field.querySelector('.pointer')
    if (point != null) {
        point.classList.toggle('pointer__active');
    }
    const check = field.nextElementSibling
    if (check == null) {
        const fieldId = field.id
        if (fieldId !== "") {
            let elementsList = document.createElement('ol');
            elementsList.className = 'elements_list title__list'
            field.after(elementsList)
            fetch(`${localStorage.getItem("url")}/api/v1/get_element_list/?id=${fieldId}`)
                .then((response) => response.json())
                .then((data) => {
                    for (let element of data) {
                        if (element.elementtwo_set.length != 0) {
                            elementsList.innerHTML += `<li class="element">
                            <div class="element_title item_title" id=${element.id}>
                                <div class="pointer"></div>
                                <p>${element.title}</p>
                                <div class="copy">
                                    <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                                </div>
                            </div>
                        </li>`
                        } else {
                            elementsList.innerHTML += `<li class="element">
                            <div class="element_title item_title" id=${element.id}>
                                <p>${element.title}</p>
                                <div class="copy">
                                    <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                                </div>
                            </div>
                        </li>`
                        }
                    }
                })
        }
    } else {
        check.remove()
    }
}


function getElementTwo(event) {
    const element = event.target.parentElement
    const point = element.querySelector('.pointer')
    if (point != null) {
        point.classList.toggle('pointer__active');
    }
    const check = element.nextElementSibling
    if (check == null) {
        const elementId = element.id
        fetch(`${localStorage.getItem("url")}/api/v1/get_elementtwo_list/?slug=${elementId}`)
            .then((response) => response.json())
            .then((data) => {
                if (data.length != 0){
                    let elementsTwoList = document.createElement('ol');
                    elementsTwoList.className = 'elementstwo_list title__list'
                    element.after(elementsTwoList)
                    for (let elementtwo of data) {
                        elementsTwoList.innerHTML += `<li class="elementtwo">
                        <div class="elementtwo_title item_title" id=${element.id}>
                            <p>${element.title} ${elementtwo.title}</p>
                            <div class="copy">
                                <img class="icon_copy" src="${localStorage.getItem("url")}/media/images/icon_copy.png" alt="${localStorage.getItem("url")}/media/images/icon_copy.png">
                            </div>
                        </div>
                    </li>`
                    }
                }
            })
    } else {
        check.remove()
    }
}


function copy(event) {
    const elementText = event.target.parentElement.parentElement.querySelector('p')
    const text = elementText.textContent
    const copyDiv = event.target
    const defaultText = 'Скопировано'
    navigator.clipboard.writeText(text)
    setTimeout(function () {
        elementText.textContent = defaultText;
        copyDiv.style = "display: none;"
    }, 500)
    setTimeout(function () {
        elementText.textContent = text;
        copyDiv.style = "display: flex;"
    }, 1500)
}



