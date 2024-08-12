const notificationClose = document.querySelector('.modals__notification-close')
const notificationSignIn = document.querySelector('.modals__notification-signIn')

notificationClose.addEventListener('click', () => {
    document.querySelector('.modals').classList.remove('modal__active')
    document.querySelector('.modals__notification').classList.remove('modal__active')
    document.querySelector('.modals__notification').classList.remove('modals__active-resetPassword')
})

notificationSignIn.addEventListener('click', () => {
    document.querySelector('.modals__notification').classList.remove('modal__active')
    document.querySelector('.modals__login').classList.add('modal__active')
})