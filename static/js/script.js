document.addEventListener('DOMContentLoaded', () => {
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Update the click handler to toggle collapsed state
    document.body.addEventListener('click', (e) => {
        if (e.target.closest('.collapsible-header')) {
            const header = e.target.closest('.collapsible-header');
            const content = header.nextElementSibling;
            
            header.classList.toggle('collapsed');
            content.style.display = header.classList.contains('collapsed') ? 'none' : 'block';
        }
    });
});

function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (message) {
        // Disable input and button while processing
        const input = document.getElementById('userInput');
        input.disabled = true;
        
        addMessage(message, 'user');
        input.value = '';
        
        // Add loading placeholder
        addMessage('Loading...', 'bot');
        
        // Send request to backend and wait for response
        setTimeout(async () => {
            try {
                const res = await fetch('/api/get-recipe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });
                
                // Remove loading placeholder
                const container = document.getElementById('messages');
                container.removeChild(container.lastChild);
                
                const data = await res.json();
                addMessage(data.data, 'bot', true);
                
                // Add collapsible info block with metadata
                setTimeout(() => {
                    addCollapsibleBlock('Sources', data.metadata);
                }, 300);
            } catch (err) {
                // Remove loading placeholder
                const container = document.getElementById('messages');
                container.removeChild(container.lastChild);
                addMessage('Sorry, there was an error processing your request.', 'bot');
            } finally {
                // Re-enable input
                input.disabled = false;
            }
        }, 800);
    }
}

function addMessage(content, type, isMarkdown = false) {
    const container = document.getElementById('messages');
    const message = document.createElement('div');
    message.className = `note-block ${type}-note`;
    
    if (isMarkdown) {
        message.innerHTML = `<div class="markdown-content">${marked.parse(content)}</div>`;
    } else {
        message.textContent = content;
    }
    
    container.appendChild(message);
    
    // Scroll both the container and window to bottom
    container.scrollTop = container.scrollHeight;
    window.scrollTo(0, document.body.scrollHeight);
}

function addCollapsibleBlock(title, content) {
    const container = document.getElementById('messages');
    
    const block = document.createElement('div');
    block.className = 'collapsible';
    block.innerHTML = `
        <div class="collapsible-header collapsed">${title}</div>
        <div class="markdown-content" style="display: none;">${marked.parse(content)}</div>
    `;
    
    container.appendChild(block);
    container.scrollTop = container.scrollHeight;
}

