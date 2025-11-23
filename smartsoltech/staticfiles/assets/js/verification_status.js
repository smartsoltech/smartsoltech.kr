// verification-status.js

function checkVerificationStatus(serviceRequestId, interval) {
    console.log(`Проверка статуса для заявки с ID: ${serviceRequestId}`); // Лог для проверки

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
                const serviceModal = document.getElementById('serviceModal');
                const confirmationModal = document.getElementById('confirmationModal');

                if (serviceModal) {
                    serviceModal.style.display = 'none';
                }

                if (confirmationModal) {
                    confirmationModal.style.display = 'block';
                }

                // Останавливаем интервал проверки статуса
                clearInterval(interval);
            }
        })
        .catch(error => {
            console.error('Ошибка при проверке статуса заявки:', error);
        });
}

// Делаем функцию доступной глобально
window.checkVerificationStatus = checkVerificationStatus;
