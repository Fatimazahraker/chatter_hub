$(document).ready(function () {
    function displayError(errorElementId, errorMessage) {
        var errorList = $('#' + errorElementId);
        errorList.empty();
        errorList.append('<li>' + errorMessage + '</li>');
    }

    function clearErrorMessages() {
        $('.error-list').empty();
    }

    window.validateForm = function () {
        clearErrorMessages();

        var usernameInput = $('#Username');
        var passwordInput = $('#password');
        var firmPswdInput = $('#firm-pswrd');

        if (usernameInput.val().trim() === '') {
            displayError('usernameErrors', 'Username cannot be empty.');
        }

        if (passwordInput.val().trim() === '') {
            displayError('passwordErrors', 'Password cannot be empty.');
        }

        if (passwordInput.val() !== firmPswdInput.val()) {
            displayError('firmPswdErrors', 'Passwords do not match.');
        }

        return $('.error-list li').length === 0;
    };

    $('#registrationForm').submit(function (event) {
        event.preventDefault();

        if (validateForm()) {
            $.ajax({
                type: 'POST',
                url: '/',
                data: $('#registrationForm').serialize(),
                success: function(response) {
                    if (response.status === 'success') {
                        console.log('Form submitted successfully', response);
                        alert(response.message);
                    } else if (response.status === 'error') {
                        console.log('Form submission error', response.message);
                        alert(response.message);
                    }
                },
                error: function(xhr, status, error) {
                    console.log('AJAX request error:', status, error);
                    alert('An error occurred during the form submission. Please check the console for details.');
                }
            });
        }
    });
});
