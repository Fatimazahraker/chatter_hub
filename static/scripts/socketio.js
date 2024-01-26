document.addEventListener("DOMContentLoaded", () => {
  var socket = io.connect(
    location.protocol + "//" + document.domain + ":" + location.port
  );

  

  const username = document.querySelector("#get-username").innerHTML;
  let room = "";  // Initialize to an empty string initially


  fetch("/get_rooms")
    .then(response => response.json())
    .then(data => {
      // Assuming data.rooms is an array of room names
      if (data.rooms.length > 0) {
        room = data.rooms[2];  // Set the default room to the first room in the list
        joinRoom(room);
      }
    });

    document.querySelector("#send_message").onclick = () => {
      const messageInput = document.querySelector("#user_message");
      const imageInput = document.querySelector("#image_upload");
      const message = messageInput.value;
      
      if (message || imageInput.files.length > 0) {
          let data = { msg: message, username: username, room: room };
          
          // Check if an image is selected
          if (imageInput.files.length > 0) {
              const file = imageInput.files[0];
              const reader = new FileReader();
              
              reader.onload = function (e) {
                  data["image"] = e.target.result; // Add the image data to the data object
                  socket.emit("message", data);
              };
              
              reader.readAsDataURL(file); // Read the image file as a data URL
          } else {
              // If no image is selected, emit the message data without image
              socket.emit("message", data);
          }
          
          messageInput.value = "";
          imageInput.value = ""; // Clear the file input
      }
  };
  

  socket.on('message', data => {
    // Check if the message contains an image
    if (data.image) {
      // Handle displaying the image
      appendImage(data);
    } else {
      // Display current message
      if (data.msg) {
        // Display current messagehw
        if (data.username == username) {
          appendmssg(data);
        }
        // Display other users' messages
        else if (typeof data.username !== 'undefined') {
          appendother(data);
        }
        // Display system message
        else {
          printSysMsg(data.msg);
        }
      }
    }
  scrollDownChatWindow();
});

  

  document.querySelector("#logout-btn").onclick = () => {
    leaveRoom(room);
  };


  document.querySelector("#send_newRoom").onclick = () => {
    socket.emit("new_room", {
      new_room_name: document.querySelector("#new_room").value,
    });
    document.querySelector("#new_room").value = "";
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

 
  document.querySelector("#delete_room").onclick = () => {
    const confirmation = confirm("Are you sure you want to delete this room?");
    if (confirmation) {
      socket.emit("delete_room", { room_name: document.querySelector("#select_deleteroom").value,
      });
    }
    document.querySelector("#select_deleteroom").value = "";
  }

  socket.on("room_deleted", (data) => {
    const deletedRoom = data.room_name;
    console.log(`Received room_deleted event for ${deletedRoom}`);
  
    // Remove the deleted room from the UI immediately
    const roomElements = document.getElementsByClassName("select-room");
    
    for (const roomElement of roomElements) {
      if (roomElement.textContent.trim() === deletedRoom) {
        console.log(`Removing element for ${deletedRoom}`);
        roomElement.remove();
        break;  // Exit the loop once the element is found and removed
      }
    }
  
    console.log(`Room ${deletedRoom} has been deleted.`);
  });
  
  socket.on('delete_room_error', function(data) {
    alert(data.message);
});

document.querySelector("#edit_room").onclick = () => {
  const confirmation = confirm("Are you sure you want to edit this room?");
  if (confirmation) {
    socket.emit("room_edited", { room_name: document.querySelector("#select_editroom").value,
    });
  }
  
}

socket.on("room_edited", (data) => {
  const editedRoom = data.room_name;
  console.log(`Received room_deleted event for ${editedRoom}`);

  // Remove the deleted room from the UI immediately
  const roomElements = document.getElementsByClassName("select-room");
  
  for (const roomElement of roomElements) {
    if (roomElement.textContent.trim() === editedRoom) {
      const newName = prompt(`Enter a new name for ${editedRoom}:`);
      console.log(`editing element for ${editedRoomtedRoom}`);
      if (newName !== null) {
        // Update the room name in the UI
        roomElement.textContent = newName;
        document.querySelector("#select_editroom").value = "";
      }
      break;  // Exit the loop once the element is found and removed
      
    }
  }

  console.log(`Room ${editedRoom} has been deleted.`);
});

socket.on('delete_room_error', function(data) {
  alert(data.message);
});

  function leaveRoom(room) {
    socket.emit("leave", { username: username, room: room });
    document.querySelectorAll(".select-room").forEach((p) => {
      p.style.color = "black";
    });
  }

  function joinRoom(newRoom) {

    socket.emit("join", { username: username, room: newRoom });
    // Fetch messages for the current room
    fetch(`/get_messages/${newRoom}`)
        .then(response => response.json())
        .then(data => {
            // Process the fetched messages
            data.messages.forEach(message => {
              console.log('Message Image:', message.image);
                if (message.username === username) {
                  if (message.image) {
                    appendImage(message);
                   } else {
                      appendmssg(message);
                    }
                } else if (typeof message.username !== 'undefined') {
                  if (message.image) {
                    appendImage(message);
                  } else {
                    appendother(message);
                  }   
                }
            });
        })
        .catch(error => console.error('Error fetching messages:', error.message));

    room = newRoom;
    console.log(`Room ${newRoom} has been JOINED.`);

    // Update the URL without triggering a page reload
    //history.pushState(null, null, `/chat/${room}`);
    console.log (`room ${room}`)
    document.querySelector("#" + CSS.escape(room)).style.color = "#487B98";
    document.querySelector("#" + CSS.escape(room)).style.backgroundColor =
      "white";
    document.querySelector("#display-message-section").innerHTML = "";
    document.querySelector("#user_message").focus();
  }

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

  function appendImage(data) {
    console.log('Image data to dee :', data.image);
   
    const p = document.createElement('p');
    const img = document.createElement('img');
    const span_username = document.createElement('span');
    const span_timestamp = document.createElement('span');
    const br = document.createElement('br');

    p.setAttribute("class", "my-msg");

    // Username
    span_username.setAttribute("class", "my-username");
    span_username.innerText = data.username;

    // Timestamp
    span_timestamp.setAttribute("class", "timestamp");
    span_timestamp.innerText = data.time_stamp;

    // Set image source directly
    img.src = data.image; 
    img.setAttribute("class", "uploaded-image");

    // Set the maximum width and height for the displayed image
    img.style.maxWidth = "100%";
    img.style.maxHeight = "300px";  // You can adjust this value based on your requirements

    // HTML to append
    p.appendChild(span_username);
    p.appendChild(br);
    p.appendChild(img);
    p.appendChild(br);
    p.appendChild(span_timestamp);

    // Append
    document.querySelector('#display-message-section').append(p);
}



  function appendmssg(data) {

    const p = document.createElement('p');
    const span_username = document.createElement('span');
    const span_timestamp = document.createElement('span');
    const br = document.createElement('br')
       
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

  function appendother (data) {
    const p = document.createElement('p');
    const span_username = document.createElement('span');
    const span_timestamp = document.createElement('span');
    const br = document.createElement('br')
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