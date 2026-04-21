// Делегирование событий - работает всегда
document.body.addEventListener('click', function(e) {
    // Проверяем, кликнули ли по кнопке "В корзину"
    if (e.target.classList.contains('add-to-cart')) {
        e.preventDefault();
        
        const productId = e.target.getAttribute('data-id');
        console.log('Добавляем товар ID:', productId);
        
        // Получаем CSRF токен
        const csrf = document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        // Отправляем запрос
        fetch('/api/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
            },
            body: JSON.stringify({product_id: productId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(' Товар добавлен в корзину!');
            } else {
                alert(' Ошибка добавления');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert(' Ошибка соединения');
        });
    }
});

console.log(' JS загружен, обработчик корзины активен');