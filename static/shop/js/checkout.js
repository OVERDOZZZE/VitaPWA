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
                window.location.href = 'https://b2b-aikol.vercel.app/order_list/' // Adjust this URL as needed
            } else {
                const data = await response.json();
                alert(data.error || 'Произошла ошибка при оформлении заказа');
                orderBtn.disabled = false;
                orderBtn.innerHTML = '<i class="fas fa-check"></i> Оформить заказ';
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
