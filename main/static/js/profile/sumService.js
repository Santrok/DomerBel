const paidModalInputChecked = document.querySelectorAll(
  ".paid__modal input[type=checkbox]"
)
const sum = document.querySelector(".paid__form-total span")

console.log(paidModalInputChecked)

paidModalInputChecked.forEach((item) => {
  item.addEventListener("input", (e) => {
    if (e.currentTarget.checked) {
      sum.textContent =
        parseInt(sum.textContent) +
        parseInt(e.currentTarget.dataset.cost) +
        " руб"
      return
    }
    sum.textContent =
      parseInt(sum.textContent) -
      parseInt(e.currentTarget.dataset.cost) +
      " руб"
  })
})
