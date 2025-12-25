// Lista de imágenes reales
const images = [
    "/static/packing/img/ar1.jpg",
    "/static/packing/img/ar2.jpg",
    "/static/packing/img/ar3.jpg",
];

let index = 0;
const bg = document.querySelector(".bg-slideshow");

function changeBackground() {
    bg.style.backgroundImage = `url(${images[index]})`;
    index = (index + 1) % images.length;
}

// Inicializa
changeBackground();

// Cambia cada 6 segundos
setInterval(changeBackground, 6000);
