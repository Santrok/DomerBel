const cross = document.querySelectorAll('.cross');
const modalsBlock = document.querySelector(".modals")


function closeModal(){
  const activeList = [...document.querySelectorAll('.modal__active'), ...document.querySelectorAll('.modals__active-grid')];
      for(let i of activeList) {
          i.classList.remove('modal__active') || i.classList.remove("modals__active-grid");
          const fieldError = [
            ...document.querySelectorAll('.modals__signIn-error'), 
            ...document.querySelectorAll(".modals__fields-error"), 
            ...document.querySelectorAll('.paid__form-error')
          ]
          fieldError.forEach(item => {
              if (
                item.classList.contains('paid__form-error') 
                || item.classList.contains('modals__fields-error')
              ) {
                item.classList.remove("paid__form-error") || item.classList.remove("modals__fields-error")
              }
              else {
                item.remove()
              }
          })
          if (i.tagName === 'FORM') {
              i.reset()
          }
          if(i.classList.contains('paid__modal')) {
            const totalPaidCount = Array.from(i.children).find(item => item.classList.contains('paid__form-total')).children[0]
            totalPaidCount.innerText = "0 руб"
          }
      }
      document.body.style.overflow = 'auto';
}

cross.forEach(item => {
    item.addEventListener('click', () => {
        closeModal()
    })
})




modalsBlock.addEventListener('mousedown', (event) => {    
  if(event.target === modalsBlock){
      closeModal()
  } 
})

document.addEventListener("keyup", (event) => {    
  const activeList = [
    ...document.querySelectorAll('.modal__active'), 
    ...document.querySelectorAll('.modals__active-grid')
  ];
  if (event.code === "Escape") {
      closeModal()
  }
  if(event.code === "Enter") {
      const form = activeList.find(item => item.tagName === "FORM")
      const submitBtn = form?.querySelector(".submit__btn")
      submitBtn.click()
  }
})
