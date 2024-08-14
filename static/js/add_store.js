let region_opened = document.querySelector(".region_opened");
    region_opened.addEventListener('click', show_city);
let get_element_select_city = document.querySelector("#select_city");
let region_hidden = document.querySelector(".region_hidden")


function show_city(event){
    if (event.target.value !== "0"){
        fetch(`${localStorage.getItem("url")}/api/v1/add_store/city/${event.target.value}`)
            .then((response) => response.json())
            .then(data => {
                region_hidden.style.display = "flex";
                get_element_select_city.innerHTML = `<option value="0">---------</option>`
                get_element_select_city.innerHTML += data.map((elem)=>`<option value=${elem.id}>${elem.area}</option>`)
            })
    }
    else {
        get_element_select_city.innerHTML += "";
        region_hidden.style.display = "none";
    }
}

let get_category = document.querySelector("#select_category");
fetch(`${localStorage.getItem("url")}/api/v1/add_store/categories/`)
    .then((response) => response.json())
    .then((data) => {
        get_category.innerHTML += data.map((category) => {
            if (category.level === 0) {
                return `<option value=${category.id} style="font-weight: 600;" disabled>${category.title}</option>`;
            } else {
                return `<option value=${category.id} style="padding-left: 15px;">${category.title}</option>`;
            }
        })
    })