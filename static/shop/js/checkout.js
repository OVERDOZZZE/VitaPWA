document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('checkout-form');
    const orderBtn = document.getElementById('order-btn');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        orderBtn.disabled = true;
        orderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                },
            });

        if (response.ok) {
            alert('Заказ успешно оформлен');
            window.location.replace('/order_list/'); // Add this line for redirect
        } else {
            const data = await response.json();
            alert(data.error || 'Произошла ошибка при оформлении заказа');
            orderBtn.disabled = false;
            orderBtn.innerHTML = '<i class="fas fa-check"></i> Оформить заказ';
            window.location.replace('/cart/'); // Add this line for redirect
        }
        } catch (error) {
            console.error('Error submitting order:', error);
            alert('Произошла ошибка. Пожалуйста, попробуйте еще раз.');
            orderBtn.disabled = false;
            orderBtn.innerHTML = '<i class="fas fa-check"></i> Оформить заказ';
        }
    });

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
