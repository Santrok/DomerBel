const areaZeroLvl = document.querySelector('.areas_list');
areaZeroLvl.addEventListener('click',event => showCity(event));
const categoryZeroLvl = document.querySelector('.categories_list');
categoryZeroLvl.addEventListener('click', event => showCategory(event));

function showCity(event) {
    console.log("start showCity")
    if (event.target.parentElement.className == 'area_title item_title'&& event.target.className != 'copy'){
        getCity(event)
    } else if (event.target.className == 'copy'){
        copy(event)
    }
}

function getCity(event) {
//Функция для выпадающего списка городов в зависимости от региона
    const region = event.target.parentElement;
    const cities = region.nextElementSibling;
    if (cities.childNodes.length == 0){
        const regionId = region.id;
        fetch(`${window.location.protocol}//${window.location.host}/api/v1/add_store/city/${regionId}`)
        .then((response) => response.json())
        .then((data) => {
            for (let city of data){
                cities.innerHTML += `<li class="city_title item_title">
                <p>${city.area}</p>
                <div class="copy"></div>
                </li><br>`
            }
        })
    } else {
        cities.innerHTML = ``;
    }
}


function showCategory(event){
    console.log('START showCategory')
    if (event.target.parentElement.className == 'category_title item_title' && event.target.className != 'copy'){
        getCategory(event)
    } else if (event.target.parentElement.className == 'subcategory_title item_title' && event.target.className != 'copy'){
        getField(event)
    } else if (event.target.parentElement.className == 'field_title item_title' && event.target.className != 'copy'){
        getElement(event)
    } else if (event.target.parentElement.className == 'element_title item_title'&& event.target.className != 'copy'){
        getElementTwo(event)
    }else if (event.target.className == 'copy'){
        copy(event)
    }
}


function getCategory(event) {
//Функция для выпадающего списка субкатегорий в зависимости от категорий категорий
    console.log("show subcategory")
    const category = event.target.parentElement;
    const check = category.nextElementSibling;
    if (check == null){
        let subcategoriesList = document.createElement('ol');
        subcategoriesList.className = 'subcategories_list'
        category.after(subcategoriesList)
        const categoryId = category.id;
        fetch(`${window.location.protocol}//${window.location.host}/api/v1/get_subcategory_list/?id=${categoryId}`)
        .then((response) => response.json())
        .then((data) => {
            for (let subcategory of data){
                if(subcategory.field_set.length == 0 || subcategory.field_set.length == 1 && subcategory.field_set[0].title == 'Цена' ){
                    subcategoriesList.innerHTML += `<li class="subcategory">
                    <div class="subcategory_title item_title" id=${subcategory.id}>
                        <p>${subcategory.title}</p>
                        <div class="copy"></div>
                    </div>
                    </li><br>`
                } else {
                    subcategoriesList.innerHTML += `<li class= "subcategory">
                    <div class="subcategory_title item_title" id=${subcategory.id}>
                        <div class="pointer"></div>
                        <p>${subcategory.title}</p>
                        <div class="copy"></div>
                    </div>
                    </li><br>`
                }
            }
        })
    } else {
        check.remove()
    }
}



function getField(event) {
//Функция для выпадающего списка полей по субкатегорий
    console.log("show field")
    const subcategory = event.target.parentElement;
    const check = subcategory.nextElementSibling
    if (check == null ){
        let fieldsList = document.createElement('ol');
        fieldsList.className = 'fields_list'
        subcategory.after(fieldsList)
        const subcategoryId = subcategory.id
        fetch(`${window.location.protocol}//${window.location.host}/api/v1/get_field_list/?id=${subcategoryId}`)
            .then((response) => response.json())
            .then((data) => {
                for (let field of data){
                    if (field.title != 'Цена'){
                        if (field.spisok !== null){
                            fieldsList.innerHTML += `<li class="field">
                            <div class="field_title item_title" id=${field.id}>
                                <div class="pointer"></div>
                                <p>${field.title}</p>
                                <div class="copy"></div>
                            </div>
                            </li><br>`
                        } else {
                            fieldsList.innerHTML += `<li class="field">
                            <div class="field_title item_title">
                                <p>${field.title}</p>
                                <div class="copy"></div>
                            </div>
                            </li><br>`
                        }
                    }
                }
            })
    } else {
        check.remove()
    }
}



function getElement(event){
    console.log("show element")
    const field = event.target.parentElement
    const check = field.nextElementSibling
    if (check == null){
        const fieldId = field.id
        if (fieldId !== ""){
            let elementsList = document.createElement('ol');
            elementsList.className = 'elements_list'
            field.after(elementsList)
            fetch(`${window.location.protocol}//${window.location.host}/api/v1/get_element_list/?id=${fieldId}`)
            .then((response) => response.json())
            .then((data) => {
                for (let element of data){
                    if (element.elementtwo_set.length !=0){
                        elementsList.innerHTML +=`<li class="element">
                            <div class="element_title item_title" id=${element.id}>
                                <div class="pointer"></div>
                                <p>${element.title}</p>
                                <div class="copy"></div>
                            </div>
                        </li><br>`
                    } else {
                        elementsList.innerHTML +=`<li class="element">
                            <div class="element_title item_title" id=${element.id}>
                                <p>${element.title}</p>
                                <div class="copy"></div>
                            </div>
                        </li><br>`
                    }
                }
            })
        }
    } else {
        check.remove()
    }
}



function getElementTwo(event){
    console.log("show elementTwo")
    const element = event.target.parentElement
    const check = element.nextElementSibling
    if (check == null){
        const elementId = element.id
        const elementTitle = element.querySelector('p').textContent
        let elementsTwoList = document.createElement('ol');
        elementsTwoList.className = 'elementstwo_list'
        element.after(elementsTwoList)
        fetch(`${window.location.protocol}//${window.location.host}/api/v1/get_elementtwo_list/?slug=${elementId}`)
            .then((response) => response.json())
            .then((data) => {
                for(let elementtwo of data){
                elementsTwoList.innerHTML += `<li class="elementtwo">
                    <div class="elementtwo_title item_title" id=${element.id}>
                        <p>${elementTitle} ${elementtwo.title}</p>
                        <div class="copy"></div>
                    </div>
                </li>`
                }
            })
    } else {
        check.remove()
    }
}


function copy(event) {
    const elementText = event.target.parentElement.querySelector('p')
    const text = elementText.textContent
    const copyDiv = event.target
    const defaultText = 'Скопировано'
    navigator.clipboard.writeText(text)
    setTimeout(function(){
        elementText.textContent = defaultText;
        copyDiv.style="display: none;"
    },500)
    setTimeout(function(){
        elementText.textContent = text;
        copyDiv.style="display: flex;"
    },1500)
}



