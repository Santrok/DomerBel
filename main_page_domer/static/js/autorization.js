const registrationForm = document.getElementById("registration_form");
const registrationButton = document.getElementById("registration_button");
registrationButton.addEventListener("click", registration);
const loginForm = document.getElementById("login_form");
const loginButton = document.getElementById("login_button");
const exitBtn = document.querySelector(".exit")
exitBtn?.addEventListener("click", logout)
loginButton.addEventListener("click", login);
const logoutButton = document.getElementById("logout_button");
logoutButton?.addEventListener("click", logout);
const legal = document.querySelector(".legal");
const physical = document.querySelector(".physical");

function getCookie(name) {
  const cookie = document.cookie.split(";");
  for (let i of cookie) {
    const [cookieName, cookieValue] = i.trim().split("=");
    if (cookieName == name) {
      return cookieValue;
    }
  }
}
/**
 * Sends a registration request to the server.
 *
 * @return {Promise} A promise that resolves with the server response or rejects with an error.
 */

function callbackRecaptcha() {
  registrationButton.addEventListener("click", registration);
}

function expiredCallbackRecaptcha() {
  registrationButton.removeEventListener("click", registration);
}
function registration() {
  const data = new FormData(registrationForm);
  data.append("recaptcha", data.get("g-recaptcha-response"));
  if (legal.classList.contains("modals__signIn-choice-active")) data.append("entity", true);
  fetch(`${window.location.protocol}//${window.location.host}/api/v1/registration_user/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: data,
  })
    .then((resp) => resp.json())
    .then((data) => {
      if (data.errors) {
        throw new Error(JSON.stringify(data.errors));
      }
      if (data.success) {
        const notificationModal = document.querySelector(".modals__notification");
        registrationForm.classList.remove("modal__active");
        notificationModal.classList.add("modal__active");
        const notificationText = document.querySelector(".modals__notification-text");
        notificationText.innerText = data.success;
      }
    })
    .catch((err) => {
      const data = JSON.parse(err.message);
      if (data["recaptcha"]) {
        registrationButton.removeEventListener("click", registration);
      }
      delete data["recaptcha"];
      // reseting recaptcha field
      grecaptcha.reset();
      generatingErrorSField(data, ".modals__signIn");
    });
}
/**
 * Function to generate error messages for input fields based on the provided data.
 *
 * @param {Object} data - An object containing input field names as keys and error messages as values.
 */

function generatingErrorSField(data, fieldForm) {
  console.log(data);
  
  for (let i in data) {
    const field = document.querySelector(`${fieldForm} input[name="${i}"]`);
    if (field.parentElement.parentElement.children.length > 1 && field.parentElement.parentElement.children[0].classList.contains("modals__signIn-error")) field.parentElement.parentElement.children[0].remove();
    const p = document.createElement("p");
    if (data[i] !== "") {
      p.classList.add("modals__signIn-error");
      p.innerText = data[i];
      field.parentElement.parentElement.prepend(p);
    }
    field.classList.add("modals__fields-error")
    /**
     * Removes the first child element of the parent element of the field if it exists,
     * and sets the border color of the field to black.
     *
     * @return {void} This function does not return anything.
     */
    field.oninput = () => {
      if (field.parentElement.parentElement.children.length > 1 && field.parentElement.parentElement.children[0].classList.contains("modals__signIn-error")) field.parentElement.parentElement.children[0].remove();
      field.classList.remove("modals__fields-error")
    };
  }
}

/**
 * Sends a login request to the server and handles the response.
 *
 * @return {Promise} A promise that resolves with the server response or rejects with an error.
 */
function login() {
  let data = new FormData(loginForm);
  fetch(`${window.location.protocol}//${window.location.host}/api/v1/login_user/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: data,
  })
    .then((resp) => {
      if (resp.ok) window.location.reload();
      return resp.json();
    })
    .then((data) => {
      if (data.errors) throw new Error(JSON.stringify(data.errors));
    })
    .catch((err) => {
      const data = JSON.parse(err.message);
      if (data["recaptcha"]) {
        loginButton.removeEventListener("click", registration);
      }
      delete data["recaptcha"];
      generatingErrorSField(data, ".modals__login");
    });
}

/**
 * Logs out the user by sending a POST request to the server's logout API endpoint.
 *
 * @return {Promise<void>} A promise that resolves when the logout is successful and the user is redirected to the homepage.
 */
function logout() {
  fetch(`${window.location.protocol}//${window.location.host}/api/v1/logout/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  }).then((resp) => {
    if (resp.ok) window.location.href=`${window.location.protocol}//${window.location.host}/`;
  });
}
