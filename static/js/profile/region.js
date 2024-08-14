const regionSelect = document.querySelector(".main__info select[name='region']")
let regionList = document.querySelectorAll(".main__info select[name='region']")
regionSelect?.addEventListener("change", (event) => {
  if(event.target.value === "") {
    regionList = document.querySelectorAll(".main__info select[name='region']")
    Array.from(regionList).splice(1,regionList.length).forEach(region => region.remove())
    return
  }
  fetch(`${localStorage.getItem("url")}/api/v1/get_city_list/${event.target.value}`)
    .then(resp => resp.json())
    .then(data => {
      regionList = document.querySelectorAll(".main__info select[name='region']")
      if(regionList.length > 1) {        
        Array.from(regionList).splice(1,regionList.length).forEach(region => region.remove())
      }
      createSelectElement(
        data,
        {id: "", title: "Любое расположение"},
        regionSelect,
        false
      )
    })
    .catch(err => console.error(err))
})