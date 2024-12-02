document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-to-cart-form');
    const messageDiv = document.getElementById('cart-message');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // ページ遷移を防ぐ
        
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // 以前のメッセージを隠す
            messageDiv.style.display = 'none';

            // 新しいメッセージを表示
            messageDiv.textContent = data.message;
            messageDiv.style.display = 'block';  // メッセージを表示

            // 数秒後にメッセージを非表示にする
            setTimeout(function() {
                messageDiv.style.display = 'none';
            }, 3000);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
