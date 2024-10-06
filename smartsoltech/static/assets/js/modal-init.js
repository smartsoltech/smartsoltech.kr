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
