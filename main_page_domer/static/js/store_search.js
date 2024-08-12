// Категории для поиска магазинов
let category_opened = document.querySelector(".category_opened");
    category_opened.addEventListener('click', show_category);
let get_element_select_category = document.querySelector("#select_category_2");
let category_hidden = document.querySelector(".category_hidden")


function show_category(event){
    if (event.target.value !== "0"){
        fetch(`http://127.0.0.1:8000/api/v1/categories_for_search/${event.target.value}`)
            .then((response) => response.json())
            .then(data => {
                category_hidden.style.display = "flex";
                get_element_select_category.innerHTML = `<option value="0">Все разделы</option>`
                get_element_select_category.innerHTML += data.map((elem)=>`<option value=${elem.id}>${elem.title}</option>`)
            })
    }
    else {
        get_element_select_category.innerHTML += "";
        category_hidden.style.display = "none";
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