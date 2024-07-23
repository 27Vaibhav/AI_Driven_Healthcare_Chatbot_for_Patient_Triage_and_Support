document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messages = document.getElementById('messages');

    function appendMessage(text, className) {
        const message = document.createElement('div');
        message.className = `message ${className}`;
        message.innerText = text;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
    }

    sendBtn.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (query === '') return;

        appendMessage(query, 'user-message');
        userInput.value = '';
       
        sendBtn.disabled = true;

        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query })
            });
            const data = await response.json();
            appendMessage(data.response, 'bot-message');
        } catch (error) {
            appendMessage('Error: Could not reach the server.', 'bot-message');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    });

    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            sendBtn.click();
        }
    });
});
