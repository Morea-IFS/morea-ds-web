document.addEventListener('DOMContentLoaded', function () {
    const closeButtons = document.querySelectorAll('.close-error, .close-message');
    if (closeButtons.length > 0) {
        closeButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                const parentDiv = button.closest('.errors, .message');
                if (parentDiv) {
                    parentDiv.remove();
                }
            });
        });
    }
});