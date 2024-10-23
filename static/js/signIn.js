const modal = document.querySelector('.modals');
const signIn = document.querySelector('.modals__signIn');
const signUp = document.querySelector('.modals__login')
const signInBtn = document.querySelector('.modals__login-action').children[1];
const switchToLoginBtn = document.querySelector('.modals__signUp');
const choiceChildren = document.querySelector('.modals__signIn-choice-wrap').children;
const switchTitle = document.querySelector('.modals__signIn-logo-title-wrap').children[1];
const inputFirstName = document.querySelector('.modals__signIn-fields input[name="first_name"]');

signInBtn.addEventListener('click', () => {
    for(let i of modal.children) {
        i.classList.remove('modal__active')
    }
    signIn.classList.add('modal__active')
})


switchToLoginBtn.addEventListener('click', () => {
    for(let i of modal.children) {
        i.classList.remove('modal__active')
    }
    signUp.classList.add('modal__active')
})

localStorage.getItem('physical') ? null : localStorage.setItem('physical', true);

function findEntity(children) {
   return Array.from(children).findIndex(i => {
        return localStorage.getItem('physical') === 'true' ? i.classList.contains('physical') : i.classList.contains('legal')
    })
}
choiceChildren[findEntity(choiceChildren)].classList.add('modals__signIn-choice-active')

function switchEntity(children) {
    localStorage.setItem('physical', !JSON.parse(localStorage.getItem('physical')))
    for(let i of children) {
        i.classList.remove('modals__signIn-choice-active')
    }
    findEntity(choiceChildren)
    choiceChildren[findEntity(choiceChildren)].classList.add('modals__signIn-choice-active')
}

for(let i of choiceChildren) {
    i.addEventListener('click', (e) => {
        if(e.currentTarget.classList.contains('physical') && e.currentTarget.classList.contains('modals__signIn-choice-active')) {
            return
        }else {
            switchEntity(choiceChildren)
            if(JSON.parse(localStorage.getItem('physical')) === true) {
                switchTitle.innerText = 'Физическое лицо'
                inputFirstName.placeholder = 'Контактное лицо'
            }else {
                switchTitle.innerText = 'Юридическое лицо'
                inputFirstName.placeholder = 'Название организации'
            }
        }
    })
}


