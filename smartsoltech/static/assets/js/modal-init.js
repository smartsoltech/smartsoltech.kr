document.addEventListener("DOMContentLoaded", function () {
    // Работа с модальным окном заявки
    var modalElement = document.getElementById('orderModal');
    if (modalElement) {
        var modal = new bootstrap.Modal(modalElement);

        // Инициализация модального окна
        modalElement.addEventListener('show.bs.modal', function () {
            console.log("Модальное окно открыто");
        });

        modalElement.addEventListener('hide.bs.modal', function () {
            console.log("Модальное окно закрыто");
        });
    }

    // Открытие модального окна для заявки на услугу
    const openModalBtn = document.getElementById('openModalBtn');
    const serviceModal = document.getElementById('serviceModal');

    if (openModalBtn && serviceModal) {
        openModalBtn.addEventListener('click', function (event) {
            event.preventDefault();
            const serviceId = openModalBtn.getAttribute('data-service-id');
            console.log("Service ID при открытии модального окна:", serviceId);

            if (!serviceId) {
                alert("Идентификатор услуги не найден. Обновите страницу и попробуйте снова.");
                return;
            }

            generateQrButton.dataset.serviceId = serviceId;

            serviceModal.classList.add('show');
            serviceModal.style.display = 'block';
        });
    }

    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function () {
            if (serviceModal) {
                serviceModal.classList.remove('show');
                setTimeout(() => {
                    serviceModal.style.display = 'none';
                }, 500);
            }
        });
    });
});
