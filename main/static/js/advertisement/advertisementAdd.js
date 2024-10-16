const sortTypeItem = document.querySelectorAll('.sort__type-list-item');
const advertisementList = document.querySelector('.advertisement__list');
const sortedOutput = document.querySelectorAll('.sorted__output-list-item');
const sortedBy = document.querySelectorAll('.sorted__by-list-item div')

if(!localStorage.getItem("sortType")) {
    localStorage.setItem("sortType", "default__item")
}

const type = ['second__item','default__item']
function setSortIcon() {
    sortTypeItem.forEach(item => {
        item.style.opacity = '1'
    })
    sortTypeItem[type.findIndex(i => i == localStorage.getItem("sortType"))].style.opacity = '0.5'
}

setSortIcon()

function setClassAdvertisementList() {
    advertisementList.classList.add(localStorage.getItem("sortType"))
}

setClassAdvertisementList()

sortTypeItem.forEach(item => {
    item.addEventListener('click', (e) => {
        localStorage.setItem("sortType", type[Array.from(e.currentTarget.parentElement.children).findIndex(i => i == e.currentTarget)])
        advertisementList.classList.remove(advertisementList.classList[1])
        advertisementList.classList.add(localStorage.getItem("sortType"))
        setSortIcon()
    })
})


function getCookie(name) {
    const cookie = document.cookie.split(';')
    for(let i of cookie) {
        const [cookieName, cookieValue] = i.trim().split('=');
        if(cookieName == name) {
            return cookieValue
        }
    }
}

const sortedType = ['30', '60', '90'];
function setSortedOutput(sort) {1
    sortedOutput[sortedType.findIndex(i => i == sort)].style.opacity = '1'
}

setSortedOutput(getCookie('sort'))

const sortBy = ['search_boost_date', 'price']
function setSortBy(sort) {
    if(sort === '-search_boost_date') {
        sortedBy[0].style.transform = 'rotate(0deg)'
    }else if (sort === '-price') {
        sortedBy[1].style.transform = 'rotate(0deg)' 
    }else {
        sortedBy[sortBy.findIndex(i => i == sort)].style.transform = 'rotate(180deg)' 
    }
}

setSortBy(getCookie('sorted_by'))
