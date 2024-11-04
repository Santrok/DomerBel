const favoriteNoteArr = document.querySelectorAll(".advertisement__list-item-notes")
const blockModals = document.querySelector(".modals")
const cancelBtn = document.querySelector(".cancel__btn")
const noteModal = document.querySelector(".note__modal")
const saveBtn = document.querySelector(".save-note__btn")
saveBtn.addEventListener("click", saveNote)

let targetNote

cancelBtn.addEventListener("click", () => {
    blockModals.classList.remove("modal__active")
    removeModal.classList.remove("modal__active")
})


favoriteNoteArr.forEach((item) =>
    item.addEventListener("click", (event) => {
        blockModals.classList.add("modal__active")
        noteModal.classList.add("modal__active")
        if (event?.currentTarget?.parentElement?.parentElement?.parentElement?.parentElement?.dataset?.id) {
            let advertisementValue = document.querySelector(
                ".note__modal input[name=advertisement]"
            )
            advertisementValue.value = event.currentTarget.parentElement.parentElement.parentElement.parentElement.dataset?.id
        }
        const noteText = document.querySelector(".note__modal textarea[name=note]")
        noteText.focus()
        if (event.currentTarget.textContent !== "Написать заметку...") {
            noteText.value = event.currentTarget.textContent
        }
        targetNote = event.currentTarget
    })
)

function saveNote(event) {
    const noteData = new FormData(noteModal)
    fetch(`${window.location.origin}/api/v1/add_new_notes_for_favorites/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: noteData
    })
        .then((resp) => resp.json())
        .then((data) => {
            // console.log(data)
            if (data.errors) {
                const errors = new Error("error")
                errors.data = data
                throw errors
            }
            targetNote.innerText = noteData.get("note") ? noteData.get("note") : "Написать заметку..."
        })
        .catch((errors) => {
            console.log(errors.data);
            console.log("johan")
            blockModals.classList.remove("modal__active")
            noteModal.classList.remove("modal__active")
            if (errors.data.errors.advertisement) {
                document.querySelector(".modals__notification-success").style.display = 'none'
                document.querySelector(".modals__notification-error").style.display = 'flex'
                document.querySelector(".modals__notification").classList.add("modal__active")
                modal.classList.add("modal__active")
                document.querySelector(".modals__notification-text").innerText =
                    errors.data.errors.advertisement
            }
        })


    blockModals.classList.remove("modal__active")
    noteModal.classList.remove("modal__active")
}