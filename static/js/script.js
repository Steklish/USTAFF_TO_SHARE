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


let autoScrollEnabled = true;
let lastScrollTop = window.pageYOffset;
// Listen for user scrolls
document.addEventListener('scroll', () => {
    // console.info("---")
    let scrollTop = window.pageYOffset;
    if (scrollTop < lastScrollTop) {
        // User is scrolling UP
        console.info('Scrolling up');
        autoScrollEnabled = false;
        // Place your upward-scroll logic here
    }
    lastScrollTop = scrollTop;

    // Calculate if user is NOT at the bottom (allow a threshold for precision)
});

function addMessage(content, type, isMarkdown = false) {
    autoScrollEnabled = true;
    const container = document.getElementById('messages');
    const message = document.createElement('div');
    message.className = `note-block ${type}-note updating`;  // Add 'updating' here to trigger transition
    
    if (isMarkdown) {
        message.innerHTML = `<div class="markdown-content updating">${marked.parse(content)}</div>`; 
        // Add 'updating' class to markdown-content as well
    } else {
        message.textContent = content;
    }
    
    container.appendChild(message);
    
    // Trigger reflow to ensure the browser registers the initial state
    void message.offsetWidth; 
    
    // Remove the 'updating' class after the transition duration (300ms)
    setTimeout(() => {
        message.classList.remove('updating');
        if (isMarkdown) {
            const markdownDiv = message.querySelector('.markdown-content');
            if (markdownDiv) {
                markdownDiv.classList.remove('updating');
            }
        }
    }, 300); // Match your CSS transition duration
    
    return message;
}



async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;

    // Disable input during processing
    input.disabled = true;
    
    // Add user message
    addMessage(message, 'user');
    input.value = '';
    
    // Add loading indicator
    const loadingMessage = addMessage('Loading...', 'bot');
    
    const container = document.getElementById('messages');
    
    if (autoScrollEnabled) {
        console.info("scrolling")
        container.scrollTop = container.scrollHeight;
        
        // Scroll container and window to bottom (optional)
        // For the window (scrolling the whole page)
        window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
        });
        
    }
    try {
        const response = await fetch('/api/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        // Remove loading indicator
        loadingMessage.remove();
        const container = document.getElementById('messages');
        // How close to the bottom (in px) is considered "at the bottom"
        const threshold = 50; 

        // Create container for streaming response
        botMessage = addMessage('', 'bot');
        
        // Process stream chunks
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let text = ''
        let buffer = '';

        let started_answering = false;
        while (true) {
            const { done, value } = await reader.read();
            let chunk = decoder.decode(value, { stream: true });
            if (chunk == "answering..."){
                botMessage.remove()
                botMessage = addMessage('', 'bot');
                text = '';
                started_answering = true;
                continue;
            }
            if (started_answering){
                text += chunk;
            }
            else{
                botMessage.remove()
                botMessage = addMessage('', 'bot');
                text = chunk;
            }
            if (done) break;
            
            update_message(text, botMessage)
        }
        console.info("stream recieved")
        addCollapsibleBlock('Sources', await getMeta());
        if (autoScrollEnabled) {
        console.info("scrolling")
        container.scrollTop = container.scrollHeight;
        
        // Scroll container and window to bottom (optional)
        // For the window (scrolling the whole page)
        window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
        });
        
    }
        // botMessage = addMessage('', 'bot');
        
    } catch (error) {
        loadingMessage.remove();
        addMessage(`Error: ${error.message}`, 'bot');
    } finally {
        input.disabled = false;
        input.focus();
    }
}

async function getMeta() {
    console.info("requesting meta");
    try {
        const metaResponse = await fetch('/api/get_last_message_meta');
        
        if (!metaResponse.ok) {
            throw new Error(`HTTP error! Status: ${metaResponse.status}`);
        }

        const responseData = await metaResponse.json();
        console.info("meta response:", responseData);

        // Extract the metadata string from either 'metadata' or 'data.metadata' field
        const metadata = responseData.metadata || 
                        (responseData.data && responseData.data.metadata) || 
                        null;

        if (!metadata) {
            console.warn("No metadata field found in response");
            return null;
        }

        console.info("Extracted metadata:", metadata);
        return metadata;
    } catch (error) {
        console.error("Fetch failed:", error);
        return null;
    }
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
    return block
}

function update_message(content, message) {
    // Find or create the markdown-content div
    let markdownDiv = message.querySelector('.markdown-content');
    if (!markdownDiv) {
        markdownDiv = document.createElement('div');
        markdownDiv.className = 'markdown-content';
        message.appendChild(markdownDiv);
    }

    // Add the 'updating' class to trigger the transition
    markdownDiv.classList.add('updating');
    // If you have a note-block, add the class there too
    const noteBlock = message.querySelector('.note-block');
    if (noteBlock) {
        noteBlock.classList.add('updating');
    }

    const container = document.getElementById('messages');
    
    // Wait a short time for the transition to start (optional, for smoother effect)
    setTimeout(() => {
        
        // Update the content
        markdownDiv.innerHTML = marked.parse(content);

        // Remove the 'updating' class to trigger the transition back
        markdownDiv.classList.remove('updating');
        if (noteBlock) {
            noteBlock.classList.remove('updating');
        }
    }, 100); // 100ms is usually enough for the transition to be noticed
    if (autoScrollEnabled) {
        console.info("scrolling")
        container.scrollTop = container.scrollHeight;
        
        // Scroll container and window to bottom (optional)
        // For the window (scrolling the whole page)
        window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
        });
        
    }
    else {
        console.info("not scrolling")
    }
}

