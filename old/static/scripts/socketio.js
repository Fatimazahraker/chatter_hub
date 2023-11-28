/**
 * Chat Application Frontend
 *
 * This script handles the frontend functionality of a chat application using WebSocket.
 * It includes features such as connecting to the WebSocket, displaying incoming messages,
 * sending messages, switching chat rooms, and handling system messages.
 *
 * Usage:
 * - Include this script in the HTML file where the chat interface is displayed.
 * - Connects to the WebSocket on page load.
 * - Displays incoming messages and handles user interactions.
 */

// Document Ready Event Listener
document.addEventListener('DOMContentLoaded', () => {
    // Connect to WebSocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    let room = "Lounge"; // Set a default room
    joinRoom(room);

    // Display incoming messages
    socket.on('message', data => {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_time = document.createElement('span');
        const br = document.createElement('br');

        if (data.username) {
            // Display user message
            span_username.innerHTML = data.username;
            span_time.innerHTML = data.time_stamp;
            p.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_time.outerHTML;
            document.querySelector('#display-message-section').append(p);
        } else {
            // Display system message
            printSysMsg(data.msg);
        }
    });

    // Send message
    document.querySelector('#send_message').onclick = () => {
        socket.send({'msg': document.querySelector('#user_mssg').value, 'username': username, 'room': room});
        // Clear input area
        document.querySelector('#user_mssg').value = '';
    }

    // Handle room selection
    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            let newRoom = p.innerHTML;
            if(newRoom == room) {
                // Inform user if already in the selected room
                msg = `You are already in ${room} room.`;
                printSysMsg(msg);
            } else {
                // Leave current room and join the new one
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        }
    });

    // Leave room
    function leaveRoom(room) {
        socket.emit('leave', {'username': username, 'room': room});
    }

    // Join room
    function joinRoom(room) {
        socket.emit('join', {'username': username, 'room': room});
        // Clear message area
        document.querySelector('#display-message-section').innerHTML = '';
        // Focus the input area
        document.querySelector('#user_mssg').focus();
    }

    // Print system message
    function printSysMsg(msg) {
        const p = document.createElement('p');
        p.innerHTML = msg;
        document.querySelector('#display-message-section').append(p);
    }
});
