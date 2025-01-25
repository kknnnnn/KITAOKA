document.addEventListener('DOMContentLoaded', function () {
    // 削除ボタンの処理
    const removeForms = document.querySelectorAll('[id^="remove-form-"]');
    removeForms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // ページ遷移を防ぐ

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
            })
                .then(response => {
                    if (response.redirected) {
                        // リダイレクトが発生したらカート画面へ遷移
                        window.location.href = response.url;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });

    // 数量変更の処理
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            const row = input.closest('tr'); // 親の行要素を取得
            const price = parseFloat(input.dataset.price); // 単価を取得
            const quantity = parseInt(input.value); // 新しい数量を取得
            const subtotalElement = row.querySelector('.item-subtotal'); // 小計要素を取得
            const totalPriceElement = document.getElementById('total-price'); // 合計金額要素を取得

            if (!isNaN(quantity) && quantity > 0) {
                // 小計を更新
                const newSubtotal = price * quantity;
                subtotalElement.textContent = newSubtotal.toLocaleString() + '円'; // 小計に「円」を追加

                // 合計金額を再計算
                let total = 0;
                document.querySelectorAll('.item-subtotal').forEach(function (subtotal) {
                    total += parseFloat(subtotal.textContent.replace(/[^0-9.-]+/g, '')); // 数値部分だけを取得
                });
                totalPriceElement.textContent = total.toLocaleString() + '円'; // 合計金額に「円」を追加

                // サーバーに数量更新を送信
                const productId = row.dataset.productId;
                updateQuantityOnServer(productId, quantity);
            }
        });
    });

    // 数量更新をサーバーに送信する関数
    function updateQuantityOnServer(productId, quantity) {
        fetch(`/cart/update_quantity/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ quantity: quantity }),
        })
            .then(response => {
                if (!response.ok) {
                    console.error('Failed to update quantity:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Error updating quantity:', error);
            });
    }

    // CSRFトークンを取得する関数
    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
});
