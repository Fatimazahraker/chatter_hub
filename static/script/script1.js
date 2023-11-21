// script1.js

$(document).ready(function () {
    // Function to display error messages
    var registrationSuccess = false;
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
        }else {
            // Example validation: Check if the username is between 4 and 25.
            if (usernameInput.val().length < 4 || usernameInput.val().length > 25) {
                displayError('usernameErrors', 'Username must be between 4 and 25 characters.');
            }
        }

        // Example validation: Check if the password is not empty
        if (passwordInput.val().trim() === '') {
            displayError('passwordErrors', 'Password cannot be empty.');
        }else {
            // Example validation: Check if the password is between 4 and 25.
            if (passwordInput.val().length < 4 || passwordInput.val().length > 25) {
                displayError('passwordErrors', 'Password must be between 4 and 25 characters.');
            }
        }

        // Example validation: Check if the passwords match
        if (passwordInput.val() !== firmPswdInput.val()) {
            displayError('firmPswdErrors', 'Passwords do not match.');
        }
        registrationSuccess = true;
    };

    // Attach the validateForm function to the click event of the button
    $('#registrationForm button[type="button"]').on('click', function () {
        validateForm();
        // check the registrationSuccess flag
        if (registrationSuccess) {
            // Make an AJAX request to the Flask server to handle registration
            $.ajax({
                type: 'POST',
                url: '/',
                data: {
                    username: $('#Username').val(),
                    password: $('#password').val(),
                    firm_password: $('#firm-pswrd').val()
                },
                success: function (response) {
                    console.log('Registration success:', response);
                    // You can handle the success response here
                },
                error: function (error) {
                    console.error('Registration error:', error);
                    // You can handle the error response here
                }
            });
        }
    });
});
