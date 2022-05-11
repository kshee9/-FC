const togglebtn = document.querySelector('.navbar__togglebtn');
const menu = document.querySelector('.navbar__menu');

togglebtn.addEventListener('click',() => {
  menu.classList.toggle('active');
});