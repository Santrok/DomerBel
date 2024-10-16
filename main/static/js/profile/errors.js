const errorSelect = document.querySelectorAll('.label__error select')
const errorInput = document.querySelectorAll(".label__error input")
errorSelect.forEach(item => {
  item.addEventListener("change", (event) => {    
    event.target.parentElement.classList.remove('label__error')
    const errorBlock = Array.from(event.target.parentElement.children).find(item => item.classList.contains('form-error'))    
    errorBlock?.remove()
  })
})
errorInput.forEach(item => {
  item.addEventListener("input", (event) => {    
    event.target.parentElement.classList.remove('label__error')
    const errorBlock = Array.from(event.target.parentElement.children).find(item => item.classList.contains('form-error'))    
    errorBlock?.remove()
  })
})