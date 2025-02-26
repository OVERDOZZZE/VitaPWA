document.addEventListener('DOMContentLoaded', () => {
    const getCookie = name => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        return parts.length === 2 ? parts.pop().split(';').shift() : null;
    };
    const csrftoken = getCookie('csrftoken');

    const updateCartCount = async () => {
        const res = await fetch('/cart/count/');
        const data = await res.json();
        document.getElementById('cart-count').textContent = data.cart_item_count;
    };

    const updateCart = async (productId, quantity, input, card) => {
        if (quantity < 0) quantity = 0;
        const res = await fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `product_id=${productId}&quantity=${quantity}`
        });
        const data = await res.json();

        if (data.quantity > 0) {
            input.value = data.quantity;
            card.querySelector('.quantity-controls').style.display = 'flex';
            card.querySelector('.btn-add').style.display = 'none';
        } else {
            card.querySelector('.quantity-controls').style.display = 'none';
            card.querySelector('.btn-add').style.display = 'block';
        }
        updateCartCount();
    };

    const sessionCart = JSON.parse(document.getElementById('session-cart-data')?.textContent || '{}');
    Object.entries(sessionCart).forEach(([productId, quantity]) => {
        const card = document.querySelector(`.product-card[data-product-id="${productId}"]`);
        if (card) {
            card.querySelector('.btn-add').style.display = 'none';
            const controls = card.querySelector('.quantity-controls');
            controls.style.display = 'flex';
            controls.querySelector('.quantity').value = quantity;
        }
    });

    document.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', async () => {
            const productId = btn.dataset.productId;
            const res = await fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken
                },
                body: `product_id=${productId}`
            });
            const data = await res.json();
            if (data.quantity) {
                const card = btn.closest('.product-card');
                btn.style.display = 'none';
                const controls = card.querySelector('.quantity-controls');
                controls.style.display = 'flex';
                controls.querySelector('.quantity').value = data.quantity;
                updateCartCount();
            }
        });
    });

    document.querySelectorAll('.btn-increment, .btn-decrement').forEach(btn => {
        btn.addEventListener('click', () => {
            const productId = btn.dataset.productId;
            const card = btn.closest('.product-card');
            const type = card.dataset.productType;
            const input = card.querySelector('.quantity');
            const step = type === 'unit' ? 1 : 0.1;
            const value = parseFloat(input.value) + (btn.classList.contains('btn-increment') ? step : -step);
            const newValue = type === 'unit' ? Math.round(value) : Number(value.toFixed(1));
            updateCart(productId, newValue, input, card);
        });
    });

    document.querySelectorAll('.quantity').forEach(input => {
        input.addEventListener('change', () => {
            const productId = input.dataset.productId;
            const card = input.closest('.product-card');
            const type = card.dataset.productType;
            let value = parseFloat(input.value);
            value = type === 'unit' ? Math.round(value) : Number(value.toFixed(1));
            updateCart(productId, value, input, card);
        });
    });

    updateCartCount();
});