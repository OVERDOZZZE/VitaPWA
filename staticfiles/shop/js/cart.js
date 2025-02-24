document.addEventListener('DOMContentLoaded', function() {
    // Функция для получения CSRF-токена из cookie
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

    // Функция для обновления количества уникальных товаров в корзине в header
    function updateCartCount() {
        fetch('/cart/count/')
            .then(response => response.json())
            .then(data => {
                const cartCountElem = document.getElementById('cart-count');
                if (cartCountElem) {
                    cartCountElem.textContent = data.cart_item_count;
                }
            });
    }

    // При загрузке страницы — обновляем состояние элементов управления для добавленных товаров
    const sessionCartElem = document.getElementById('session-cart-data');
    if (sessionCartElem) {
        const sessionCart = JSON.parse(sessionCartElem.textContent);
        for (let productId in sessionCart) {
            const productDiv = document.querySelector(`.product[data-product-id="${productId}"]`);
            if (productDiv) {
                const btnInitial = productDiv.querySelector('.btn-add-initial');
                if (btnInitial) {
                    btnInitial.style.display = 'none';
                }
                const qtyControls = productDiv.querySelector('.quantity-controls');
                if (qtyControls) {
                    qtyControls.style.display = 'inline-block';
                }
                const input = productDiv.querySelector('.quantity-input');
                if (input) {
                    input.value = sessionCart[productId];
                }
            }
        }
    }

    // ОБРАБОТЧИК для начальной кнопки "Добавить (+)"
    document.querySelectorAll('.btn-add-initial').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                },
                body: `product_id=${productId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.quantity) {
                    const productDiv = document.querySelector(`.product[data-product-id="${productId}"]`);
                    if (productDiv) {
                        productDiv.querySelector('.btn-add-initial').style.display = 'none';
                        const qtyControls = productDiv.querySelector('.quantity-controls');
                        qtyControls.style.display = 'inline-block';
                        const input = qtyControls.querySelector('.quantity-input');
                        input.value = data.quantity;
                        updateCartCount();
                    }
                }
            });
        });
    });

    // ОБРАБОТЧИК для кнопки увеличения количества (с учетом типа продукта)
    document.querySelectorAll('.btn-add-increment').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const productDiv = document.querySelector(`.product[data-product-id="${productId}"]`);
            const productType = productDiv.dataset.productType; // Читаем тип продукта из data-атрибута
            const input = productDiv.querySelector('.quantity-input');
            
            // Определяем шаг: 1 для unit и 0.1 для weight
            let step = (productType === 'unit') ? 1 : 0.1;
            let newQuantity = parseFloat(input.value) + step;
            
            // Округляем значение в зависимости от типа
            if (productType === 'unit') {
                newQuantity = Math.round(newQuantity);
            } else {
                newQuantity = Math.round(newQuantity * 10) / 10;
            }
            updateCart(productId, newQuantity, input, productDiv);
        });
    });

    // ОБРАБОТЧИК для кнопки уменьшения количества (с учетом типа продукта)
    document.querySelectorAll('.btn-remove').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const productDiv = document.querySelector(`.product[data-product-id="${productId}"]`);
            const productType = productDiv.dataset.productType;
            const input = productDiv.querySelector('.quantity-input');

            let step = (productType === 'unit') ? 1 : 0.1;
            let newQuantity = parseFloat(input.value) - step;
            
            if (productType === 'unit') {
                newQuantity = Math.round(newQuantity);
            } else {
                newQuantity = Math.round(newQuantity * 10) / 10;
            }
            updateCart(productId, newQuantity, input, productDiv);
        });
    });

    // ОБРАБОТЧИК для ручного изменения количества в поле ввода (на странице списка товаров)
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.dataset.productId;
            const productDiv = document.querySelector(`.product[data-product-id="${productId}"]`);
            const productType = productDiv.dataset.productType;
            let newQuantity = parseFloat(this.value);
            
            if (productType === 'unit') {
                newQuantity = Math.round(newQuantity);
            } else {
                newQuantity = Math.round(newQuantity * 10) / 10;
            }
            updateCart(productId, newQuantity, this, productDiv);
        });
    });

    // ОБРАБОТЧИК для изменения количества на странице корзины
    document.querySelectorAll('.quantity-input-cart').forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.dataset.productId;
            // Если на строке корзины есть data-атрибут с типом, то используем его
            const row = document.querySelector(`tr[data-product-id="${productId}"]`);
            let productType = 'weight'; // По умолчанию предполагаем weight
            if (row && row.dataset.productType) {
                productType = row.dataset.productType;
            }
            let newQuantity = parseFloat(this.value);
            
            if (productType === 'unit') {
                newQuantity = Math.round(newQuantity);
            } else {
                newQuantity = Math.round(newQuantity * 10) / 10;
            }
            updateCart(productId, newQuantity, this, null, true);
        });
    });

    // ОБРАБОТЧИК для кнопки "Удалить" в корзине
    document.querySelectorAll('.btn-remove-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            fetch('/cart/remove/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                },
                body: `product_id=${productId}`
            })
            .then(response => response.json())
            .then(data => {
                const row = document.querySelector(`tr[data-product-id="${productId}"]`);
                if (row) {
                    row.remove();
                }
                updateCartTotal();
                updateCartCount();
            });
        });
    });

    // Функция для обновления количества товара через AJAX
    function updateCart(productId, newQuantity, inputElement, productDiv, isCartPage = false) {
        if (newQuantity < 1) {
            newQuantity = 0;
        }
        fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: `product_id=${productId}&quantity=${newQuantity}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.quantity > 0) {
                if (inputElement) inputElement.value = data.quantity;
                if (productDiv) {
                    const qtyControls = productDiv.querySelector('.quantity-controls');
                    qtyControls.style.display = 'inline-block';
                    const initialAdd = productDiv.querySelector('.btn-add-initial');
                    if (initialAdd) initialAdd.style.display = 'none';
                }
            } else {
                if (productDiv) {
                    const qtyControls = productDiv.querySelector('.quantity-controls');
                    if (qtyControls) qtyControls.style.display = 'none';
                    const initialAdd = productDiv.querySelector('.btn-add-initial');
                    if (initialAdd) initialAdd.style.display = 'inline-block';
                }
                if (isCartPage) {
                    const row = document.querySelector(`tr[data-product-id="${productId}"]`);
                    if (row) row.remove();
                }
            }
            if (isCartPage) {
                updateCartTotal();
            }
            updateCartCount();
        });
    }

    // Функция для обновления итоговой суммы в корзине
    function updateCartTotal() {
        let total = 0;
        document.querySelectorAll('tr[data-product-id]').forEach(row => {
            const productId = row.getAttribute('data-product-id');
            const input = row.querySelector('.quantity-input-cart');
            const quantity = parseFloat(input.value);
            const priceCell = row.children[1];
            const price = parseFloat(priceCell.textContent);
            const itemTotal = quantity * price;
            total += itemTotal;
            const itemTotalCell = row.querySelector('.item-total');
            itemTotalCell.textContent = itemTotal.toFixed(2);
        });
        const totalElem = document.getElementById('cart-total');
        if (totalElem) {
            totalElem.textContent = total.toFixed(2);
        }
    }
});
