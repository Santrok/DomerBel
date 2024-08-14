const show = document.querySelectorAll(".views__show");
const hide = document.querySelectorAll(".views__hide")

show.forEach(item => {
  item.addEventListener("click", (event) => {
    if(event.currentTarget.classList.contains("views__show-active")) {
      event.currentTarget.classList.remove("views__show-active")
      event.currentTarget.parentElement.children[1].classList.add("views__show-active")      
      event.currentTarget.parentElement.parentElement.children[1].setAttribute("type", "text")
    }
  })
})


hide.forEach(item => {
  item.addEventListener("click", (event) => {
    if(event.currentTarget.classList.contains("views__show-active")) {
      event.currentTarget.classList.remove("views__show-active")
      event.currentTarget.parentElement.children[0].classList.add("views__show-active")      
      event.currentTarget.parentElement.parentElement.children[1].setAttribute("type", "password")
    }
  })
})
