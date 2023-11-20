// script1.js

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
    window.validateForm = function () {
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

        // Example validation: Check if the passwords match
        if (passwordInput.val() !== firmPswdInput.val()) {
            displayError('firmPswdErrors', 'Passwords do not match.');
        }
    };

    // Attach the validateForm function to the click event of the button
    $('button').on('click', function () {
        validateForm();
    });
});
