const selectAll = document.querySelector(
  ".main__info-advertisement-nav-select-all"
)

selectAll?.addEventListener("click", (event) => {
  let checkboxex = window.location.pathname.includes("my_publications")
    ? document.querySelectorAll(
        ".publications__list-item input[type='checkbox']"
      )
    : document.querySelectorAll(
        '.main__info-advertisement-list-item input[type="checkbox"]'
      )

  checkboxex?.forEach((item) => {
    item.checked = event.target.checked
  })
})
