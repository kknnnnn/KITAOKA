// 検索フォームの表示/非表示を切り替える
function toggleSearchForm() {
    const formContainer = document.getElementById('search-form-container');
    formContainer.classList.toggle('d-none');
}

// リセットボタンの動作
document.addEventListener('DOMContentLoaded', function () {
    const resetButton = document.getElementById('resetButton');
    if (resetButton) {
        resetButton.addEventListener('click', function () {
            document.getElementById('category').value = '';
            document.getElementById('min_price').value = '';
            document.getElementById('max_price').value = '';
        });
    }
});
