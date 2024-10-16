const crossBtn = document.querySelectorAll('.cross__dialog')
const blockModals = document.querySelector(".modals")
const removeModal = document.querySelector(".remove__modal")
const cancelBtn = document.querySelector('.cancel__btn')
cancelBtn.addEventListener('click', () => {
    blockModals.classList.remove("modal__active")
            removeModal.classList.remove("modal__active")
})
crossBtn.forEach(item => item.addEventListener("click", () => {

            blockModals.classList.add("modal__active")
            removeModal.classList.add("modal__active")
            let removeValue = document.querySelector(".remove__modal input[name=dialog]")
    removeValue.value = item.dataset.id
        }
    )
)