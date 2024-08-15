const phoneNum = document.querySelector(".details__advertisement-about-list-item-phone")

phoneNum?.addEventListener("click", (event) => {
  if(event.target.textContent === "Показать номер телефона") {
    event.currentTarget.children[0].style.display = "none"
    event.currentTarget.children[1].style.display = "block"
  }
})
