document.addEventListener("DOMContentLoaded", function () {
    var modalElement = document.getElementById('orderModal');
    if (modalElement) {
        var modal = new bootstrap.Modal(modalElement);
        
        // Инициализация модального окна
        modalElement.addEventListener('show.bs.modal', function (event) {
            console.log("Модальное окно открыто");
        });

        modalElement.addEventListener('hide.bs.modal', function (event) {
            console.log("Модальное окно закрыто");
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const generateQrButton = document.getElementById('generateQrButton');

    if (generateQrButton) {
        generateQrButton.addEventListener('click', function () {
            const clientEmail = document.getElementById('clientEmail').value;
            const clientPhone = document.getElementById('clientPhone').value;
            const clientName = document.getElementById('clientName').value;
            const description = document.getElementById('description').value;
            const serviceId = generateQrButton.getAttribute('data-service-id');

            // Проверка заполненности полей
            if (!clientEmail || !clientPhone || !clientName || !description || !serviceId) {
                alert('Все поля должны быть заполнены.');
                return;
            }

            // Получение CSRF токена из cookies
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }

            const csrftoken = getCookie('csrftoken');

            // Отправка POST запроса на создание заявки
            fetch('/service/create_request/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    client_email: clientEmail,
                    client_phone: clientPhone,
                    client_name: clientName,
                    service_id: serviceId,
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
                if (data.status === 'success') {
                    alert(data.message);
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
    }
});

function checkVerificationStatus(serviceRequestId, interval) {
    fetch(`/service/request_status/${serviceRequestId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при проверке статуса заявки');
            }
            return response.json();
        })
        .then(data => {
            if (data.is_verified) {
                // Закрываем форму и показываем окно подтверждения
                document.getElementById('serviceModal').style.display = 'none';
                document.getElementById('confirmationModal').style.display = 'block';

                // Останавливаем интервал проверки статуса
                clearInterval(interval);
            }
        })
        .catch(error => {
            console.error('Ошибка при проверке статуса заявки:', error);
        });
}