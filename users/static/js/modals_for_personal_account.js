const popup_pa = document.querySelector(".popup_pa")
const more_button_pa = document.querySelector(".more_button_pa");
const nav_category_list_popup_pa = document.querySelector(".nav_category_list_popup_pa");
const closing_cross_pa = document.querySelectorAll(".closing_cross_pa");




// -> view more for personal account
more_button_pa.addEventListener("click", () => {
    popup_pa.style.display = 'flex';
    more_button_pa.style.display = 'flex';
    nav_category_list_popup_pa.style.display = "grid";
    closing_cross_pa.style.display = "flex";
});

closing_cross_pa.forEach(item => item.addEventListener("click", () => {
    popup_pa.style.display = 'none';
    nav_category_list_popup_pa.style.display = "none";
    closing_cross_pa.style.display = "none";
}));

popup_pa.addEventListener("click", (event) => {
    if (event.target === event.currentTarget) {
        popup_pa.style.display = 'none';
        nav_category_list_popup_pa.style.display = "none";
    }
});