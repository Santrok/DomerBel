const modalsBlock = document.querySelector('.modals');
const modalLogin = document.querySelector('.modals__login');
const loginBtn = document.querySelector('.header__up-user');

modalsBlock.addEventListener('click', (event) => {    
    if(event.target === modalsBlock){
        const activeList = [...document.querySelectorAll('.modal__active'), ...document.querySelectorAll('.modals__active-grid')];
        for(let i of activeList) {
            i.classList.remove('modal__active') || i.classList.remove("modals__active-grid");
            const fieldError = [...document.querySelectorAll('.modals__signIn-error'), ...document.querySelectorAll(".modals__fields-error"), ...document.querySelectorAll('.paid__form-error')]
            fieldError.forEach(item => {
                if (item.classList.contains('paid__form-error')){
                    item.classList.remove("paid__form-error")
                }
                else {
                    item.remove()
                }
            })
            if (i.tagName === 'FORM') {
                i.reset()
            }
        }
        document.body.style.overflow = 'auto';
    } 
})

document.addEventListener("keyup", (event) => {    
    const activeList = [...document.querySelectorAll('.modal__active'), ...document.querySelectorAll('.modals__active-grid')];
    if (event.code === "Escape") {
        for(let i of activeList) {
            i.classList.remove('modal__active') || i.classList.remove("modals__active-grid");
            if (i.tagName === 'FORM') {
                i.reset()
                document.querySelectorAll(".modals__signIn-error").forEach(item => item.remove())
                document.querySelectorAll(".modals__fields-error").forEach(item => item.classList.remove("modals__fields-error"))
                document.querySelectorAll(".paid__form-error").forEach(item => item.classList.remove("paid__form-error"))
            }
        }
        document.body.style.overflow = 'auto';  
    }
    if(event.code === "Enter") {
        const form = activeList.find(item => item.tagName === "FORM")
        const submitBtn = form?.querySelector(".submit__btn")
        submitBtn.click()
    }
})

loginBtn?.addEventListener('click', () => {
    document.body.style.overflow = 'hidden';
    modalsBlock.classList.add('modal__active');
    modalLogin.classList.add('modal__active');
})
