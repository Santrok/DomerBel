const logoInput = document.getElementById('id_logo_image') || document.getElementById("preview_image_logo_image")
const logoLabel = document.querySelector(".main__info label[for='id_logo_image']") || document.querySelector(".main__info label[for='preview_image_logo_image']")
const closeTag = document.querySelector(".delete_img")
logoInput?.addEventListener('change', (event) => {
  const profileImg = document.querySelectorAll(".photo_img")
  if(profileImg.length >= 1) {
    Array.from(profileImg).forEach((item) => {
      item.remove()
    })
  }
  const file = event.target.files[0];
  const reader = new FileReader();
  reader.readAsDataURL(file)
  reader.onload = (e) => {
    const div = document.createElement('div');
    div.classList.add("photo_img")
    const cross = document.createElement('div');
    cross.classList.add("delete_img");
    const img = document.createElement('img');
    img.src = e.target.result
    div.append(img)
    div.append(cross)
    logoLabel.append(div)
    cross.addEventListener('click', (event) => {
      event.target.parentElement.remove()
      logoInput.value = ""
    })
  }
})
