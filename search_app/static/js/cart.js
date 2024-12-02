document.addEventListener('DOMContentLoaded', function() {
    const removeForms = document.querySelectorAll('[id^="remove-form-"]');

    removeForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();  // ページ遷移を防ぐ

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
});
