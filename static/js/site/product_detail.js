console.log("Arquivo product_detail.js carregado!");


// gerencia um carrossel de imagens horizontal e
document.addEventListener("DOMContentLoaded", () => {
    const track = document.querySelector(".image-track");
    const images = Array.from(track.children);
    const leftButton = document.querySelector(".arrow-left");
    const rightButton = document.querySelector(".arrow-right");
    const imageWidth = 310; // 300px largura + 10px de gap
    const visibleImages = 4; // Número de imagens visíveis
    let currentIndex = 0;

    const updateTrackPosition = () => {
        track.style.transform = `translateX(-${currentIndex * imageWidth}px)`;
    };

    const updateButtons = () => {
        leftButton.disabled = currentIndex === 0;
        rightButton.disabled = currentIndex >= images.length - visibleImages;
    };

    leftButton.addEventListener("click", () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateTrackPosition();
            updateButtons();
        }
    });

    rightButton.addEventListener("click", () => {
        if (currentIndex < images.length - visibleImages) {
            currentIndex++;
            updateTrackPosition();
            updateButtons();
        }
    });

    // Inicializa o estado dos botões
    updateButtons();
});





