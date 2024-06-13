document.addEventListener("DOMContentLoaded", function() {
    const password = document.getElementById("password");
    const confirm_password = document.getElementById("confirm_password");
    const error_confirm = document.getElementById("error_confirm");
    const form = document.querySelector("form");

    function validateConfirmPassword() {
        if (password.value !== confirm_password.value) {
            error_confirm.textContent = "Passwords don't match";
            return false;
        } else {
            error_confirm.textContent = "";
            return true;
        }
    }

    password.addEventListener("input", validateConfirmPassword);
    confirm_password.addEventListener("input", validateConfirmPassword);

    form.addEventListener("submit", function(event) {
        if (!validateConfirmPassword()) {
            event.preventDefault();
            alert("Passwords don't match. Please correct the errors.");
        }
    });
});
