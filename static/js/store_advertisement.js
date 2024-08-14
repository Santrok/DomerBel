const favorite = document.querySelector(".store_ads_list")
const fLink = document.querySelector('.favorites')
const favoritesHref = fLink.getAttribute('href')
const fNumber = document.querySelector('.favorites__quantity')

set_favorites_list()

fLink.onmouseover = function(e) {
    fNumber.style.color = 'red'
}

fLink.onmouseout = function(e) {
    fNumber.style.color = '#307792'
}

if (favorite){
    favorite.onclick = function(event){
        let target = event.target;
        if (target.className === "favorite_img"){
            if (target.getAttribute("src") === "/static/img/favorite.png"){
                target.src = "/static/img/favorite_yes.png";
                pushInFavoriteList(event.target.getAttribute('id'))
            }
            else {
                target.src = "/static/img/favorite.png";
                deleteInFavoriteList(event.target.getAttribute('id'))
            }
        }
    }
}


function pushInFavoriteList(id){
    const user = getCookie('user_auth')
    const favorites = localStorage.getItem(`${user}favorites`)
    let list = []
    if (favorites){
        list = JSON.parse(favorites)
        list.push(id)
        setStarsInHeader(list)
        localStorage.setItem(`${user}favorites`, JSON.stringify(list))
    } else {
        list.push(id)
        setStarsInHeader(list)
        localStorage.setItem(`${user}favorites`, JSON.stringify(list))
    }
}

function deleteInFavoriteList(id){
    const user = getCookie('user_auth')
    const favorites = localStorage.getItem(`${user}favorites`)
    if (favorites){
        list = JSON.parse(favorites)
        for (let i = 0; i < list.length; i++){
            if (list[i] == id){
                list.splice(i, 1)
                break
            }
        }
        setStarsInHeader(list)
        localStorage.setItem(`${user}favorites`, JSON.stringify(list))
    }
}

function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));

    return matches ? decodeURIComponent(matches[1]) : undefined;
}

function set_favorites_list(){
    
    const favorites = document.querySelectorAll('.favorite_img')
    
    if (favorites){
        const user = getCookie('user_auth')
        const favorite = localStorage.getItem(`${user}favorites`)
        if (favorite) {
            const list = JSON.parse(favorite)
            if (list){
                setStarsInHeader(list)
                for (let i = 0; i < favorites.length; i++){
                    for (let j = 0; j < list.length; j++){
                        if (favorites[i].getAttribute("id") == list[j]){
                            favorites[i].src = "/static/img/favorite_yes.png"
                            break
                        }
                    }
                }
            }
        }
    }
}

function setStarsInHeader(list){
    const favorites = document.querySelector('.favorites')
    const fNum = document.querySelector('.favorites__quantity')
    if (list.length){
        fNum.innerText = `[${list.length}]`
        favorites.className = 'favorites active'
        favorites.href = `${favoritesHref}?list=${JSON.stringify(list)}`
    } else {
        fNum.innerText = `[]`
        favorites.className = 'favorites'
        favorites.href = `${favoritesHref}?list=[]`
    }
}
