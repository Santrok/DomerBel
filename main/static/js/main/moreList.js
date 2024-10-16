const mooreBtn = document.querySelector(".modal__more")
const closeMoore = document.querySelector(".modals__more-close")

mooreBtn.addEventListener('click', () => {
  document.querySelector('.modals').classList.add('modal__active')
  document.querySelector('.modals__more').classList.add('modals__active-grid')
})

closeMoore.addEventListener('click', () => {
  document.querySelector('.modals').classList.remove('modal__active')
  document.querySelector('.modals__more').classList.remove('modals__active-grid')
})