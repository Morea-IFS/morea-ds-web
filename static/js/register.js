document.addEventListener("DOMContentLoaded", function() {
    const password = document.getElementById("password");
    const confirm_password = document.getElementById("confirm_password");
    const error_confirm = document.getElementById("error_confirm");
    const form = document.querySelector("form");

    function validateConfirmPassword() {
        if (password.value !== confirm_password.value) {
            error_confirm.textContent = "As senhas não coincidem";
            return false;
        } else {
            error_confirm.textContent = "";
            return true;
        }
    }
});
