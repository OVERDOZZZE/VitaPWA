document.addEventListener('DOMContentLoaded', () => {
    const decreaseButtons = document.querySelectorAll('.btn-decrease');
    const increaseButtons = document.querySelectorAll('.btn-increase');
    const removeButtons = document.querySelectorAll('.btn-remove');

    // Decrease quantity
    decreaseButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const productId = button.dataset.productId;
            const display = button.parentElement.querySelector('.quantity-display');
            let quantity = parseFloat(display.textContent);
            
            quantity = Math.max(quantity - 0.1, 0); // Changed to allow going to 0
            await updateCart(productId, quantity);
        });
    });

    // Increase quantity
    increaseButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const productId = button.dataset.productId;
            const display = button.parentElement.querySelector('.quantity-display');
            let quantity = parseFloat(display.textContent);
            
            quantity += 0.1;
            await updateCart(productId, quantity);
        });
    });

    // Remove item
    removeButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const productId = button.dataset.productId;
            await removeFromCart(productId);
        });
    });

    async function updateCart(productId, quantity) {
        try {
            const response = await fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: `product_id=${productId}&quantity=${quantity.toFixed(1)}`
            });

            if (response.ok) {
                const data = await response.json();
                updateCartDisplay(productId, data.quantity);
                if (data.quantity === 0) {
                    document.querySelector(`tr[data-product-id="${productId}"]`).remove();
                    if (!document.querySelector('.cart-table tbody tr')) {
                        location.reload();
                    }
                }
            }
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    }

    async function removeFromCart(productId) {
        try {
            const response = await fetch('/cart/remove/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: `product_id=${productId}`
            });

            if (response.ok) {
                document.querySelector(`tr[data-product-id="${productId}"]`).remove();
                updateTotal();
                if (!document.querySelector('.cart-table tbody tr')) {
                    location.reload();
                }
            }
        } catch (error) {
            console.error('Error removing item:', error);
        }
    }

    function updateCartDisplay(productId, quantity) {
        const row = document.querySelector(`tr[data-product-id="${productId}"]`);
        if (!row) return;
        
        const display = row.querySelector('.quantity-display');
        const price = parseFloat(row.querySelector('.product-price').dataset.price);
        const itemTotal = row.querySelector('.item-total');

        display.textContent = quantity.toFixed(1);
        itemTotal.textContent = (price * quantity).toFixed(2) + ' ₽';
        updateTotal();
    }

    function updateTotal() {
        const items = document.querySelectorAll('.cart-table tbody tr');
        let total = 0;
        items.forEach(item => {
            total += parseFloat(item.querySelector('.item-total').textContent);
        });
        document.getElementById('cart-total').textContent = total.toFixed(2) + ' ₽';
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});