const modalsBlock = document.querySelector('.modals');
const modalLogin = document.querySelector('.modals__login');
const loginBtn = document.querySelector('.header__up-user');

modalsBlock.addEventListener('click', (event) => {    
    if(event.target === modalsBlock){
        const activeList = [...document.querySelectorAll('.modal__active'), ...document.querySelectorAll('.modals__active-grid')];
        for(let i of activeList) {
            i.classList.remove('modal__active') || i.classList.remove("modals__active-grid");
            const fieldErorr = document.querySelectorAll('.modals__signIn-error')
            fieldErorr.forEach(item => item.remove())
            if (i.tagName === 'FORM') {
                i.reset()
            }
        }
        document.body.style.overflow = 'auto';
    } 
})

document.addEventListener("keyup", (event) => {    
    if (event.code === "Escape") {
        const activeList = [...document.querySelectorAll('.modal__active'), ...document.querySelectorAll('.modals__active-grid')];
        for(let i of activeList) {
            i.classList.remove('modal__active') || i.classList.remove("modals__active-grid");
            if (i.tagName === 'FORM') {
                i.reset()
            }
        }
        document.body.style.overflow = 'auto';  
    }
    // if(event.code === "Enter") {
    //     document.querySelector('.modals .modal__active')?.submit()
    // }
})

loginBtn?.addEventListener('click', () => {
    document.body.style.overflow = 'hidden';
    modalsBlock.classList.add('modal__active');
    modalLogin.classList.add('modal__active');
})
