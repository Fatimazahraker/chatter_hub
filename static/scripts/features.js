document.addEventListener('DOMContentLoaded', () => {

    const emojiSelectorIcon = document.getElementById('emojiSelectorIcon');
  const emojiSelector = document.getElementById('emojiSelector');

  emojiSelectorIcon.addEventListener('click', () => {
    emojiSelector.classList.toggle('active');
  });

  fetch('https://emoji-api.com/emojis?access_key=ff394963ee82187b533833121345244ff3c457ee')
    .then(res => res.json())
    .then(data => loadEmoji(data))

  const emojiSearchInput = document.getElementById('emojiSearch');
  const emojiList = document.getElementById('emojiList');
  
  // Event listener for emoji search
  emojiSearchInput.addEventListener('input', () => {
    const searchQuery = emojiSearchInput.value.toLowerCase();

    // Filter emojis based on the search query
    Array.from(emojiList.children).forEach((emoji) => {
        const emojiText = emoji.textContent.toLowerCase();
        if (emojiText.includes(searchQuery)) {
            emoji.style.display = 'block';
        } else {
            emoji.style.display = 'none';
        }
    });
});

  function loadEmoji(data) {
    data.forEach(emoji => {
        let li = document.createElement('li');
        li.textContent = emoji.character;
        emojiList.appendChild(li);
    });
  }
  
  document.getElementById('emojiList').addEventListener('click', (event) => {
    if (event.target.tagName === 'LI') {
        const selectedEmoji = event.target.textContent;
        document.querySelector("#user_message").value += selectedEmoji;
    }
  });

  document.getElementById("show_create_input").addEventListener("click", function() {
    var createInputWrapper = document.getElementById("create_input_wrapper");
    if (createInputWrapper.style.display === "none") {
        createInputWrapper.style.display = "block";
    } else {
        createInputWrapper.style.display = "none";
    }
});

document.getElementById("show_delete_input").addEventListener("click", function() {
    var deleteInputWrapper = document.getElementById("delete_input_wrapper");
    if (deleteInputWrapper.style.display === "none") {
        deleteInputWrapper.style.display = "block";
    } else {
        deleteInputWrapper.style.display = "none";
    }
});
});