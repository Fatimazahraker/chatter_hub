document.addEventListener('DOMContentLoaded', () => {
    // Make 'enter' key is message submit
    let msg = document.querySelector('#user_mssg');
    msg.addEventListener('keyup', event => {
        event.preventDefault();
        if (event.keyCode === 13) {
            document.querySelector('#send_message').click();
        }
    });
})