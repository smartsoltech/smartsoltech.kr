// service-request.js

document.addEventListener("DOMContentLoaded", function () {
    // Открытие модального окна
    const openModalBtn = document.getElementById('openModalBtn');
    const serviceModal = document.getElementById('serviceModal');
    const generateQrButton = document.getElementById('generateQrButton');

    if (openModalBtn && serviceModal) {
        openModalBtn.addEventListener('click', function (event) {
            event.preventDefault();
            // Логирование значения serviceId при открытии модального окна
            const serviceId = openModalBtn.getAttribute('data-service-id');
            console.log("Service ID при открытии модального окна:", serviceId);
            
            // Проверяем, если serviceId отсутствует
            if (!serviceId) {
                alert("Идентификатор услуги не найден. Обновите страницу и попробуйте снова.");
                return;
            }

            // Сохраняем serviceId для дальнейшего использования
            generateQrButton.dataset.serviceId = serviceId;

            // Показываем модальное окно
            serviceModal.classList.add('show');
            serviceModal.style.display = 'block';
        });
    } else {
        console.error('Не удалось найти элемент с id openModalBtn или serviceModal.');
    }

    // Закрытие модального окна
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

    // Обработчик кнопки "Создать заявку"
    if (generateQrButton) {
        generateQrButton.addEventListener('click', function () {
            // Получение значений полей
            const clientEmail = document.getElementById('clientEmail').value.trim();
            const clientPhone = document.getElementById('clientPhone').value.trim();
            const clientName = document.getElementById('clientName').value.trim();
            const description = document.getElementById('description').value.trim();

            // Получаем serviceId из кнопки открытия модального окна
            const serviceId = generateQrButton.dataset.serviceId;

            // Логируем для проверки значения serviceId перед отправкой
            console.log("Service ID перед отправкой запроса:", serviceId);

            // Проверка заполненности полей
            if (!clientEmail || !clientPhone || !clientName || !description || !serviceId) {
                let errorMessage = 'Пожалуйста, заполните все поля формы перед продолжением.\n';
                if (!serviceId) {
                    errorMessage += 'Идентификатор услуги не найден. Обновите страницу и попробуйте снова.\n';
                }
                alert(errorMessage);
                return;
            }

            // Отправка POST запроса на создание заявки
            fetch(`/service/generate_qr_code/${serviceId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken  // Используем глобально инициализированный CSRF токен
                },
                body: JSON.stringify({
                    client_email: clientEmail,
                    client_phone: clientPhone,
                    client_name: clientName,
                    description: description
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка при создании заявки');
                }
                return response.json();
            })
            .then(data => {
                if (data.qr_code_url) {
                    // Обновляем src изображения QR-кода и показываем его
                    const qrCodeImg = document.getElementById('qrCodeImg');
                    if (qrCodeImg) {
                        qrCodeImg.src = data.qr_code_url;
                        qrCodeImg.style.display = 'block';
                    }

                    // Начинаем проверку статуса заявки
                    const interval = setInterval(() => {
                        checkVerificationStatus(data.service_request_id, interval);
                    }, 5000);
                } else if (data.status === 'existing_request') {
                    alert(data.message);
                } else {
                    alert('Неизвестная ошибка. Пожалуйста, попробуйте снова.');
                }
            })
            .catch(error => {
                console.error('Ошибка при создании заявки:', error);
            });
        });
    } else {
        console.error('Не удалось найти элемент с id generateQrButton.');
    }
});
