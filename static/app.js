let currentSessionId = null;

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessageToChat('user', message);
    input.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (!currentSessionId) {
            currentSessionId = data.session_id;
        }
        
        addMessageToChat('assistant', data.response, data.retrieved_docs);
        loadSessions();
        
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('assistant', 'Sorry, there was an error processing your request.');
    }
}

function addMessageToChat(role, content, retrievedDocs = []) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    let docsHTML = '';
    if (retrievedDocs && retrievedDocs.length > 0) {
        docsHTML = `
            <div class="retrieved-docs">
                <div class="retrieved-docs-title">Referenced ${retrievedDocs.length} document(s)</div>
                ${retrievedDocs.slice(0, 2).map((doc, i) => 
                    `<div>📄 ${doc.metadata?.filename || 'Document'} (relevance: ${(doc.score * 100).toFixed(0)}%)</div>`
                ).join('')}
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-role">${role === 'user' ? 'You' : 'Assistant'}</div>
        <div class="message-content">${content}</div>
        ${docsHTML}
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    const statusDiv = document.getElementById('uploadStatus');
    
    if (files.length === 0) {
        statusDiv.className = 'error';
        statusDiv.textContent = 'Please select files to upload';
        return;
    }
    
    statusDiv.textContent = 'Uploading...';
    statusDiv.className = '';
    
    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            statusDiv.className = 'success';
            statusDiv.textContent = `✓ ${file.name} uploaded successfully (${data.chunks_created} chunks)`;
            
        } catch (error) {
            console.error('Error:', error);
            statusDiv.className = 'error';
            statusDiv.textContent = `✗ Error uploading ${file.name}`;
        }
    }
    
    fileInput.value = '';
    loadDocuments();
}

async function loadDocuments() {
    try {
        const response = await fetch('/api/documents');
        const documents = await response.json();
        
        const docsList = document.getElementById('documentsList');
        docsList.innerHTML = documents.map(doc => `
            <div class="document-item">
                📄 ${doc.filename}<br>
                <small>${doc.chunk_count} chunks</small>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const sessions = await response.json();
        
        const sessionsList = document.getElementById('sessionsList');
        sessionsList.innerHTML = sessions.map(session => `
            <div class="session-item" onclick="loadSession('${session.session_id}')">
                💬 ${new Date(session.updated_at).toLocaleDateString()}<br>
                <small>${session.message_count} messages</small>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        const session = await response.json();
        
        currentSessionId = sessionId;
        
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        
        session.messages.forEach(msg => {
            addMessageToChat(msg.role, msg.content);
        });
        
    } catch (error) {
        console.error('Error loading session:', error);
    }
}

async function newSession() {
    try {
        const response = await fetch('/api/sessions/new', {
            method: 'POST'
        });
        const data = await response.json();
        
        currentSessionId = data.session_id;
        
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        
        loadSessions();
        
    } catch (error) {
        console.error('Error creating session:', error);
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

window.addEventListener('load', () => {
    loadDocuments();
    loadSessions();
});
