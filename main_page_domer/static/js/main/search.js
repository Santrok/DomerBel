const fields = document.querySelector(".fields")
const getCategory = document.querySelector(".main__search-form-item-category")
const parentRegionElement = document.querySelector(".region")
const getRegion = document.querySelector(".main__search-form-item-region")

function getOption(url) {
  fetch(url)
    .then((response) => response.json())
    .then((data) => {      
      if (data.length === 0) return false
      if(window.location.pathname.includes("stores") && fields.children.length >= 1) {
        return
      }
      if (data.some(item => item.spisok !== null && item.spisok !== undefined) && fields.children.length !== 0) {
        data.forEach((item) => {
          if (
            item?.search?.split("|")?.length >= 2 &&
            !item?.spisok?.element_set
          ) {
            createSelectElement(item, item.search.split("|")[0], fields)
            createSelectElement(item, item.search.split("|")[1], fields)
            return
          }
          if (item?.search?.trim() === "") return
          createSelectElement(item, item?.search?.split("|")[0]?.trim(), fields)
        })
        return
      }
      if (data.some(item => item.search === "")) return
      if (Array.isArray(data) && data.some(item=>item.area)) {
        createSelectElement(data, "Любое расположение")
        return
      }
      createSelectElement(data, {id:"", title:"Все разделы"}, fields)
    })
    .catch((error) => {
      console.error(error, "error obj")
    })
}

function getInnerList(data, id) {
  const dataModel = data.spisok.element_set.find((item) => item.id == id)
  if(!dataModel || dataModel?.elementtwo_set.length === 0) {
    
    fields.children[
      Array.from(fields.children).findIndex((item) =>
        item.classList.contains("category__mark")
      )
    ]?.remove()
    return
  }
  dataModel.outer_id = +fields.children[Array.from(fields.children).findIndex(
    (item) => item.dataset.active === "true"
  )].name
  createSelectElement(dataModel, data?.search?.split("|")[1]?.trim(), fields)
}

function createSelectElement(
  data,
  titleObj = {
    id: "",
    title: "Все разделы",
  },
  fields,
  search = true
) {
  const select = document.createElement("select")
  if (Array.isArray(data) && data?.some(item => item.level) && !data.some(item => item.area)) {
    select.setAttribute("name", "category")
    select.dataset.level = data[0]?.level
  }else {
    if(Array.isArray(data) && data?.some(item => item.area)) {
      select.setAttribute("name", "region")
    }
    else {
      select.setAttribute("name", data?.outer_id || data?.id)
    }
  }
  createOptionElement(titleObj, select, Array.isArray(data) && data.some(item=>item.area)?"" : undefined)
  if (data?.spisok && data?.spisok !== null && !data.elementtwo_set) {
    data?.spisok?.element_set?.forEach((item) => {
      createOptionElement(item, select)
    })
    if (
      data?.spisok?.element_set?.some((item) => item?.elementtwo_set && item?.elementtwo_set.length > 0)
    ) {
      select.addEventListener("change", (event) => {
        const id = event.target.options[event.target.selectedIndex].dataset.fetchid
        getInnerList(data, id)
      })
      select.dataset.active = true
    }
  } else if (!data?.spisok && !data?.int_val_list && !data?.elementtwo_set && !data?.some(item => item.area)) {
    data?.forEach((item) => {
      createOptionElement(item, select)
    })
    select.addEventListener("change", (event) =>
      getCategoryFunc(event, getOption)
    )
  } else if (data?.elementtwo_set && data?.elementtwo_set.length > 0) {
    select.classList.add("category__mark")
    data?.elementtwo_set.forEach((item) => {
      createOptionElement(item, select)
    })
    fields.children[
      Array.from(fields.children).findIndex((item) =>
        item.classList.contains("category__mark")
      )
    ]?.remove()
    const actionSelectIndex = Array.from(fields.children).findIndex(
      (item) => item.dataset.active === "true"
    )
    fields.insertBefore(select, fields.children[actionSelectIndex + 1])
    return
  } else if(data?.max_val_interval_date !== 0) {
    for(let i = data.max_val_interval_date; i >= data.min_val_interval_date ; i--){
      createOptionElement(i, select, i)
    }
  } else {
    if (data.search === null || !data.search) {
      fields.children[
        Array.from(fields.children).findIndex((item) =>
          item.classList.contains("category__mark")
        )
      ]?.remove()
      return
    }
    data?.int_val_list?.forEach((item) => {
      createOptionElement(item, select, item)
    })
  }
  if(Array.isArray(data) && data?.some(item => item?.area)) {
    data.forEach(forItem => {
      createOptionElement(forItem, select)
    })
    if(search) {
      parentRegionElement.append(select)
    }else {
      fields.after(select)
    }
    return
  }
  fields.append(select)
}

function createOptionElement(item, parentElement, itemList) {
  const option = document.createElement("option")
  if(parentElement.dataset.level) {
    option.value = item.id
  }else {
    option.value = item.title || item.id || itemList
    }
  option.dataset.fetchid = item.id
  option.textContent = item.title || item.title_ad || item.area || item
  parentElement.append(option)
}

getCategory?.addEventListener("change", (event) => {
  getCategoryFunc(event, getOption)
  fields.innerHTML = ""
})

getRegion?.addEventListener("change", (event) => {
 getCategoryFunc(event, getOption)
})  

function getCategoryFunc(event, func) {
  const id = event.target.options[event.target.selectedIndex].dataset.fetchid
  const filterFields = Array.from(fields.children).filter(
    (item) =>
      !item.dataset.level || item.dataset.level > event.target.dataset.level
  )
  if(event.target.dataset.level && fields.children.length > 1){
    for(let item of filterFields){
      item.remove()
    }
    if(event.target.dataset.level && event.target.value === ""){
      return
    }
  }  
  if(event.target.name === "region") {
    getRegion?.nextElementSibling?.remove()
    if(event.target.value === "" || event.target.value == undefined) {
      return
    }
    func(`http://127.0.0.1:8000/api/v1/get_city_list/${id}`)
    return
  }  
  if(event.target.value === undefined || event.target.value === "") {
    return
  }
  if (!func(`http://127.0.0.1:8000/api/v1/categories_for_search/${id}`)) {
    func(`http://127.0.0.1:8000/api/v1/get_field_list/?id=${id}`)
  }else{
    func(`http://127.0.0.1:8000/api/v1/categories_for_search/${id}`)
  }
}
