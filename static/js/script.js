document.addEventListener('DOMContentLoaded', function() {
    var cartButton = document.getElementById('cart-button');
    var cartMenu = document.getElementById('cart-menu');

    
    cartButton.addEventListener('click', function(event) {
        event.stopPropagation(); 
        cartMenu.classList.toggle('active'); 
    });

    
    document.addEventListener('click', function(event) {
        var isClickInsideCartMenu = cartMenu.contains(event.target);
        var isClickInsideCartButton = cartButton.contains(event.target);
        if (!isClickInsideCartMenu && !isClickInsideCartButton) {
            cartMenu.classList.remove('active'); 
        }
    });

    
    var xButtons = document.querySelectorAll('.x-button');
    xButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault(); 
            var itemId = button.dataset.itemId;
            removeFromCart(itemId); 
            event.stopPropagation(); 
        });
    });
});


function removeFromCart(itemId) {
    fetch('/remove_from_cart', {
        method: 'POST',
        body: new URLSearchParams({
            'item_id': itemId 
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
