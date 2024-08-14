const dropdownBtn = document.querySelector(".details__advertisement-add-share-list-item-drop-btn");
const dropdown = document.querySelector(".details__advertisement-add-share-list-drop");

document.addEventListener("click", drop);


function drop(event) {
    if (event.target === dropdownBtn) {
        dropdown.classList.toggle("details__advertisement-add-share-list-item-drop-btn-active");
        return
      }
      if(event.target === dropdown) return
      dropdown.classList.remove("details__advertisement-add-share-list-item-drop-btn-active");
}