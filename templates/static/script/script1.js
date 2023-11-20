// script1.js
console.log('Script1.js is loaded!');
$(document).ready(function () {
    // Function to display error messages
    function displayError(errorElementId, errorMessage) {
        var errorList = $('#' + errorElementId);
        errorList.empty(); // Clear previous error messages

        // Append the new error message
        errorList.append('<li>' + errorMessage + '</li>');
    }

    // Function to clear previous error messages
    function clearErrorMessages() {
        $('.error-list').empty(); // Clear all error lists
    }

    // Example validation function
    function validateForm() {
        // Clear previous error messages
        clearErrorMessages();

        // Perform client-side validation
        var usernameInput = $('#Username');
        var passwordInput = $('#password');
        var firmPswdInput = $('#firm-pswrd');

        // Example validation: Check if the username is not empty
        if (usernameInput.val().trim() === '') {
            displayError('usernameErrors', 'Username cannot be empty.');
        }

        // Example validation: Check if the password is not empty
        if (passwordInput.val().trim() === '') {
            displayError('passwordErrors', 'Password cannot be empty.');
        }
        // ... (rest of the validation logic)

    }
});
