const favoritesList = document.querySelectorAll(".advertisement__list-item-about-favorites")

favoritesList.forEach(item => {
  item.addEventListener("click", (event) => {

    if(window.location.pathname.includes("favorites")) {
      event?.currentTarget?.parentElement?.parentElement?.parentElement?.remove()
    }
    if(!event?.currentTarget?.parentElement?.parentElement?.dataset?.id){
      modal.classList.add("modal__active")
      modalLogin.classList.add("modal__active")
      return
    }
    if(!event.currentTarget.classList.contains("advertisement__favorites-active")) {
      event.currentTarget.classList.add("advertisement__favorites-active")
      requestFavorites(`${localStorage.getItem("url")}/api/v1/add_to_favorite/`, event?.currentTarget?.parentElement?.parentElement?.dataset?.id)
    }else {
      event.currentTarget.classList.remove("advertisement__favorites-active")
      requestFavorites(`${localStorage.getItem("url")}/api/v1/delete_from_favorite/`, event?.currentTarget?.parentElement?.parentElement?.dataset?.id)
    }
  })
})


function requestFavorites(url, data_id) {
  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      "id": data_id
    })
  })
  .catch((error) => {
    console.error("Error:", error);
  })

}