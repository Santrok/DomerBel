const modalsBlock = document.querySelector('.modals');
const modalLogin = document.querySelector('.modals__login');
const loginBtn = document.querySelector('.header__up-user');

modalsBlock.addEventListener('click', (event) => {    
    if(event.target === modalsBlock){
        modalsBlock.classList.remove('modal__active');
        for(let i of modalsBlock.children) {
            i.classList.remove('modal__active') || i.classList.remove("modals__active-grid");
           
            const fieldErorr = document.querySelectorAll('.modals__signIn-error')
            fieldErorr.forEach(item => item.remove())
        }
        document.body.style.overflow = 'auto';
    } 
})

document.addEventListener("keyup", (event) => {    
    if (event.code === "Escape") {
        modalsBlock.classList.remove('modal__active');
        for(let i of modalsBlock.children) {
            i.classList.remove('modal__active') || i.classList.remove("modals__active-grid");
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
