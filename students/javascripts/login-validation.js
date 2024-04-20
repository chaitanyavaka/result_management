document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        // Perform client-side validation
        if (email.trim() === "") {
            alert("Please enter your email.");
            return;
        }

        if (password.trim() === "") {
            alert("Please enter your password.");
            return;
        }

        // If all fields are filled, submit the form
        form.submit();
    });
});
