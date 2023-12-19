document.addEventListener("DOMContentLoaded", () => {
  var socket = io.connect(
    location.protocol + "//" + document.domain + ":" + location.port
  );
  const username = document.querySelector("#get-username").innerHTML;
  let room = "";  // Initialize to an empty string initially

  // Fetch the list of rooms from the server
  // Assuming you have a route in your Flask app to retrieve the list of rooms
  fetch("/get_rooms")
    .then(response => response.json())
    .then(data => {
      // Assuming data.rooms is an array of room names
      if (data.rooms.length > 0) {
        room = data.rooms[4];  // Set the default room to the first room in the list
        joinRoom(room);
      }
    });

  document.querySelector("#send_message").onclick = () => {
    socket.emit("message", {
      msg: document.querySelector("#user_message").value,
      username: username,
      room: room,
    });
    document.querySelector("#user_message").value = "";
  };

  socket.on('message', data => {

    // Display current message
    if (data.msg) {
        const p = document.createElement('p');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span');
        const br = document.createElement('br')
        // Display user's own message
        if (data.username == username) {
                p.setAttribute("class", "my-msg");

                // Username
                span_username.setAttribute("class", "my-username");
                span_username.innerText = data.username;

                // Timestamp
                span_timestamp.setAttribute("class", "timestamp");
                span_timestamp.innerText = data.time_stamp;

                // HTML to append
                p.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML

                //Append
                document.querySelector('#display-message-section').append(p);
        }
        // Display other users' messages
        else if (typeof data.username !== 'undefined') {
            p.setAttribute("class", "others-msg");

            // Username
            span_username.setAttribute("class", "other-username");
            span_username.innerText = data.username;

            // Timestamp
            span_timestamp.setAttribute("class", "timestamp");
            span_timestamp.innerText = data.time_stamp;
            
            // Content of the message
            //p.innerText = data.msg;

            // HTML to append
            p.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;

            //Append
            document.querySelector('#display-message-section').append(p);
        }
        // Display system message
        else {
            printSysMsg(data.msg);
        }


    }
    scrollDownChatWindow();
});

  function selectRoom() {
    document.querySelectorAll(".select-room").forEach((li) => {
      li.onclick = () => {
        let newRoom = li.innerHTML;
        if (newRoom === room) {
          msg = `You are already in ${room} room.`;
          printSysMsg(msg);
        } else {
          leaveRoom(room);
          joinRoom(newRoom);
          room = newRoom;
        }
      };
    });
  }

  document.querySelector("#send_newRoom").onclick = () => {
    socket.emit("new_room", {
      new_room_name: document.querySelector("#new_room").value,
    });
  };

  socket.on("new room received", (room) => {
    let createRoom = room.new_room_name;
    const li = document.createElement("li");
    li.innerHTML = createRoom;
    li.setAttribute("class", "select-room cursor-pointer");
    li.setAttribute("id", createRoom);

    const roomsList = document.querySelector("#roomsList");
    if (roomsList) {
      roomsList.appendChild(li);
      selectRoom();
    } else {
      console.error('The "rooms" container does not exist.');
    }
  });

  document.querySelector("#logout-btn").onclick = () => {
    leaveRoom(room);
  };

  function leaveRoom(room) {
    socket.emit("leave", { username: username, room: room });
    document.querySelectorAll(".select-room").forEach((p) => {
      p.style.color = "black";
    });
  }

  function joinRoom(newRoom) {
    socket.emit("join", { username: username, room: newRoom });
    room = newRoom;
    document.querySelector("#" + CSS.escape(room)).style.color = "#487B98";
    document.querySelector("#" + CSS.escape(room)).style.backgroundColor =
      "white";
    document.querySelector("#display-message-section").innerHTML = "";
    document.querySelector("#user_message").focus();
  }

  function scrollDownChatWindow() {
    const chatWindow = document.querySelector("#display-message-section");
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function printSysMsg(msg) {
    const p = document.createElement("p");
    p.setAttribute("class", "system-msg");
    p.innerHTML = msg;
    document.querySelector("#display-message-section").append(p);
    scrollDownChatWindow();
    document.querySelector("#user_message").focus();
  }

  selectRoom(); // Call selectRoom function initially to set up room selection
});