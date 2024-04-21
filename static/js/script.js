document.addEventListener('DOMContentLoaded', function() {
    var cartButton = document.getElementById('cart-button');
    var cartMenu = document.getElementById('cart-menu');

    // Обробник події для відкриття / закриття меню корзини
    cartButton.addEventListener('click', function(event) {
        event.stopPropagation(); // Зупиняємо подальше поширення події, щоб вона не спрацьовувала на document
        cartMenu.classList.toggle('active'); // Перемикаємо клас 'active' для відображення / приховання меню
    });

    // Обробник події для закриття меню при кліку за його межами або на хрестик
    document.addEventListener('click', function(event) {
        var isClickInsideCartMenu = cartMenu.contains(event.target);
        var isClickInsideCartButton = cartButton.contains(event.target);
        if (!isClickInsideCartMenu && !isClickInsideCartButton) {
            cartMenu.classList.remove('active'); // Прибираємо клас 'active', якщо клік був поза меню та кнопкою корзини
        }
    });

    // Додаємо обробник події для кожного хрестика в корзині
    var xButtons = document.querySelectorAll('.x-button');
    xButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Забороняємо відправку форми
            var itemId = button.dataset.itemId;
            removeFromCart(itemId); // Викликаємо функцію видалення елемента з корзини
            event.stopPropagation(); // Зупиняємо подальше поширення події, щоб вона не спрацьовувала на решту обробників
        });
    });
});

// Функція для видалення елемента з корзини
function removeFromCart(itemId) {
    fetch('/remove_from_cart', {
        method: 'POST',
        body: new URLSearchParams({
            'item_id': itemId // Відправляємо ідентифікатор елемента для видалення на сервер
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Item removed successfully');
        } else {
            console.error('Failed to remove item');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
