$(document).ready(function () {
    console.error("Document ready");

    function displayError(errorElementId, errorMessage) {
        var errorList = $('#' + errorElementId);
        errorList.empty();
        errorList.append('<li>' + errorMessage + '</li>');
    }

    function clearErrorMessages() {
        $('.error-list').empty();
        $('#clientSideErrorsFlag').val('false');
    }

    window.validateForm = function () {
        console.error("validateForm function called");

        // Clear previous error messages
        clearErrorMessages();

        var usernameInput = $('#Username');
        var passwordInput = $('#password');
        var firmPswdInput = $('#firm-pswrd');

        if (usernameInput.val().trim() === '') {
            displayError('usernameErrors', 'Username cannot be empty.');
            console.error('Username validation error');
        }

        if (passwordInput.val().trim() === '') {
            displayError('passwordErrors', 'Password cannot be empty.');
            console.error('Password validation error');
        }

        if (passwordInput.val() !== firmPswdInput.val()) {
            displayError('firmPswdErrors', 'Passwords do not match.');
            console.error('Passwords do not match validation error');
        }

        // Check if any validation errors occurred
        var hasValidationErrors = $('.error-list').is(':empty');

        // Set the flag based on the validation result
        $('#clientSideErrorsFlag').val(hasValidationErrors ? 'false' : 'true');

        // Return the validation result
        return hasValidationErrors;
    };

    $('#registrationForm').submit(function (event) {
        console.error("Form submitted");

        if (!validateForm()) {
            console.error('Client-side errors flag is false. Proceeding with form submission.');
        } else {
            event.preventDefault(); // Prevent form submission if validation fails
            console.error('Client-side errors flag is true. Preventing form submission.');
            console.error("Form submission prevented");
        }
    });
});
