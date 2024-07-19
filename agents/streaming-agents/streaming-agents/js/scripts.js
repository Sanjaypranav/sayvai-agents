const chatContainer = document.getElementById("chatContainer");
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");

        sendButton.addEventListener("click", sendMessage);

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (message === "") {
                return;
            }

            const response = await fetch('http://127.0.0.1:8000/query-stream/?query=' + encodeURIComponent(message));
            const reader = response.body.getReader();

            let responseText = '';
            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    break;
                }

                responseText += new TextDecoder("utf-8").decode(value);

                const messageElement = document.createElement("div");
                messageElement.className = "message";
                messageElement.textContent = responseText;
                chatContainer.innerHTML = '';
                chatContainer.appendChild(messageElement);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            messageInput.value = "";
        }