document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.querySelector(".menu-toggle");
    const menuContainer = document.querySelector(".menu-container");

    if (menuToggle && menuContainer) {
        menuToggle.addEventListener("click", function (event) {
            menuContainer.classList.toggle("expanded");
            event.stopPropagation(); // Предотвращает закрытие при клике на кнопку
        });

        // Закрытие меню при клике вне его
        document.addEventListener("click", function (event) {
            if (!menuToggle.contains(event.target) && !menuContainer.contains(event.target)) {
                menuContainer.classList.remove("expanded");
            }
        });

        // Предотвращает закрытие при клике внутри меню
        menuContainer.addEventListener("click", function (event) {
            event.stopPropagation();
        });
    }
});
