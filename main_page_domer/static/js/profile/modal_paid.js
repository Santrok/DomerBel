const serviceBtn = document.querySelectorAll('.main__info-advertisement-list-item-about-services')
const blockModals1 = document.querySelector(".modals")
const paidModal = document.querySelector(".paid__modal")

serviceBtn.forEach(item => item.addEventListener("click", () => {
            blockModals1.classList.add("modal__active")
            paidModal.classList.add("modal__active")
            let serviceValue = document.querySelector(".paid__modal input[name=advertisement]")
            serviceValue.value = item.dataset.id
        }
    )
)

const paidBtn = document.getElementById('paid_button')
paidBtn.addEventListener('click', sendPaid)

function sendPaid() {
    const data = new FormData(document.getElementById("paid_form"))
    fetch(`${window.location.origin}/paid/api/send_paid/`,
        {
            method: "POST",
            headers: {
                "X-CSRF-Token": getCookie("csrftoken"),
            },
            body: data,
        })
        .then((response) => response.json())
        .then((data) => {
                console.log(data)
                if (data.errors) {
                    const errors = new Error("errors")
                    errors.data = data
                    throw errors
                }
                window.location.href = data.redirect
            }
        )
        .catch((msg) => {
            const errorList = document.querySelector('.paid__modal-errors')
                if (msg.data.errors.services) {
                    if (document.querySelector(".service__error")) {
                    document.querySelector(".service__error").remove()
                }
                    const paidFieldset = document.querySelector('.paid__form')
                    paidFieldset.classList.add('paid__form-error')
                    let serviceError = document.createElement('p')
                    serviceError.classList.add('service__error')
                    serviceError.classList.add('modals__signIn-error')
                    serviceError.innerHTML = msg.data.errors.services
                    errorList.append(serviceError)
                    document.querySelectorAll(".paid__modal input[name=services]").forEach(item => item.oninput = () => {
                            paidFieldset.classList.remove("paid__form-error")
                            document.querySelector('.service__error').remove()
                        }
                    )
                }
                if (msg.data.errors.advertisement) {
                    if (document.querySelector(".adver__error")) {
                    document.querySelector(".adver__error").remove()
                }
                    let advertisementError = document.createElement('p')
                    advertisementError.classList.add('adver__error')
                    advertisementError.classList.add('modals__signIn-error')
                    advertisementError.innerHTML = msg.data.errors.advertisement
                    errorList.append(advertisementError)
                }
            }
        )
}