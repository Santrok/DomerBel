// Категории для поиска магазинов
let category_opened = document.querySelector(".category_opened");
category_opened.addEventListener('click', show_category);

let get_element_select_category1 = document.querySelector("#select_category_1");
let get_element_select_category2 = document.querySelector("#select_category_2");
let get_element_select_category3 = document.querySelector("#select_category_3");
let get_element_select_category4 = document.querySelector("#select_category_4");

let category_hidden = document.querySelector(".category_hidden");
let category_hidden2 = document.querySelector(".category_hidden_2");
let category_hidden3 = document.querySelector(".category_hidden_3");

get_element_select_category2.addEventListener('click', show_category);
get_element_select_category3.addEventListener('click', show_category);

function show_category(event) {
    if (event.target.id === "select_category_1") {
        // Прячем второй, третий и четвёртый селекты
        category_hidden.style.display = "none";
        category_hidden2.style.display = "none";
        category_hidden3.style.display = "none";

        // Очищаем значения второго, третьего и четвёртого селектов
        get_element_select_category2.innerHTML = `<option value="0">Все разделы</option>`;
        get_element_select_category3.innerHTML = `<option value="0">Все разделы</option>`;
        get_element_select_category4.innerHTML = `<option value="0">Все разделы</option>`;

        if (event.target.value !== "0") {
            fetch(`http://127.0.0.1:8000/api/v1/categories_for_search/${event.target.value}`)
                .then((response) => response.json())
                .then((data) => {
                // Показываем второй селект
                category_hidden.style.display = "flex";

                // Заполняем второй селект данными из API
                get_element_select_category2.innerHTML += data.map((elem) => `<option value=${elem.id}>${elem.title}</option>`);
                });
        } else {
            // Скрываем второй и последующие селекты
            category_hidden.style.display = "none";
            category_hidden2.style.display = "none";
            category_hidden3.style.display = "none";
        }
    } else if (event.target.id === "select_category_2") {
        // Прячем третий и четвёртый селект
        category_hidden2.style.display = "none";
        category_hidden3.style.display = "none";

        // Очищаем значения третьего и четвёртого селектов
        get_element_select_category3.innerHTML = `<option value="0">Все разделы</option>`;
        get_element_select_category4.innerHTML = `<option value="0">Все разделы</option>`;

        if (event.target.value !== "0") {
            fetch(`http://127.0.0.1:8000/api/v1/categories_for_search/${event.target.value}`)
                .then((response) => response.json())
                .then((data) => {
                if (data.length > 0) {
                    // Показываем третий селект
                    category_hidden2.style.display = "flex";

                    // Заполняем третий селект данными из API
                    get_element_select_category3.innerHTML += data.map((elem) => `<option value=${elem.id}>${elem.title}</option>`);
                    }
                });
        } else {
            // Скрываем третий и последующий селекты
            category_hidden2.style.display = "none";
            category_hidden3.style.display = "none";
        }
    } else if (event.target.id === "select_category_3") {
        // Очищаем значение четвёртого селекта
        get_element_select_category4.innerHTML = `<option value="0">Все разделы</option>`;

        if (event.target.value !== "0") {
            fetch(`http://127.0.0.1:8000/api/v1/categories_for_search/${event.target.value}`)
                .then((response) => response.json())
                .then((data) => {
                if (data.length > 0) {
                    // Показываем четвёртый селект
                    category_hidden3.style.display = "flex";

                    // Заполняем четвёртый селект данными из API
                    get_element_select_category4.innerHTML += data.map((elem) => `<option value=${elem.id}>${elem.title}</option>`);
                    }
                });
        } else {
            // Скрываем четвёртый селект, если выбрано значение "Все разделы"
            category_hidden3.style.display = "none";
        }
    }
}


// Регионы для поиска магазинов
let location_opened = document.querySelector(".location_opened");
    location_opened.addEventListener('click', show_region);
let get_element_select_region = document.querySelector("#select_region_2");
let location_hidden = document.querySelector(".location_hidden")


function show_region(event){
    if (event.target.value !== "0"){
        fetch(`http://127.0.0.1:8000/api/v1/add_store/city/${event.target.value}`)
            .then((response) => response.json())
            .then(data => {
                location_hidden.style.display = "flex";
                get_element_select_region.innerHTML = `<option value="0">Любое расположение</option>`
                get_element_select_region.innerHTML += data.map((elem)=>`<option value=${elem.id}>${elem.area}</option>`)
            })
    }
    else {
        get_element_select_region.innerHTML += "";
        location_hidden.style.display = "none";
    }
}


// Выделение объявлений в ЛК поштучно либо сразу всех
let select_all = document.getElementById('select_all');
let checkboxes = document.getElementsByName('ads_checkbox');

select_all.addEventListener('change', select_all_ads);

function select_all_ads(event) {
    for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = event.target.checked;
    }
}

for (let i = 0; i < checkboxes.length; i++) {
    checkboxes[i].addEventListener('change', find_unchecked_ads)
}

function find_unchecked_ads(event) {
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked == false) {
            select_all.checked = false;
            break;
        }
        select_all.checked = true;
    }
}