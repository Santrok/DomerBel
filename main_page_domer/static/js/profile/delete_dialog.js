const crossBtn = document.querySelectorAll('.cross__dialog')
const blockModals = document.querySelector(".modals")
const removeDialogModal = document.querySelector(".remove__dialog")

crossBtn.forEach(item => item.addEventListener("click", () => {

    blockModals.classList.add("modal__active")
    removeDialogModal.classList.add("modal__active")

})
)