// JavaScript (app.js)
const mobileMenu = document.getElementById("mobile-menu");
const navMenu = document.querySelector(".navbar__menu");

mobileMenu.addEventListener("click", () => {
    // Toggle 'is-active' for the menu and hamburger button
    mobileMenu.classList.toggle("is-active");
    navMenu.classList.toggle("active");
});
