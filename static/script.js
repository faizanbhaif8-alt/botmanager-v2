// Bot Manager V2 - Frontend JavaScript
let currentSessionId = null;
let generatedFiles = null;

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('promptInput');
    if (textarea) {
        textarea.addEventListener('input', autoResize);
    }
    
    // Enter key to submit (Ctrl+Enter for new line)
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
            e.preventDefault();
            generateBot();
        }
    });
});

function autoResize() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function addMessage(content, type = 'bot', files = null) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`;
    
    if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="max-w-3xl bg-gradient-to-br from-purple-600/40 to-blue-600/40 backdrop-blur-lg rounded-2xl p-4 border border-purple-500/30">
                <p class="text-white">${escapeHtml(content)}</p>
            </div>
        `;
    } else {
        let filesHtml = '';
        if (files && Object.keys(files).length > 0) {
            filesHtml = `
                <div class="mt-4">
                    <p class="text-sm text-purple-300 mb-2"><i class="fas fa-file-code mr-2"></i>Generated Files (${Object.keys(files).length}):</p>
                    <div class="file-list">
                        ${Object.keys(files).map(file => `
                            <div class="file-item">
                                <span class="file-name"><i class="fas fa-file mr-2"></i>${file}</span>
                                <span class="file-size">${formatFileSize(files[file]?.length || 0)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="max-w-3xl bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg rounded-2xl p-5 border border-white/10">
                <div class="flex items-center space-x-3 mb-3">
                    <div class="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                        <i class="fas fa-robot text-white text-sm"></i>
                    </div>
                    <div>
                        <p class="font-semibold text-white">Bot Manager</p>
                        <p class="text-xs text-gray-400">AI Assistant</p>
                    </div>
                </div>
                <div class="text-gray-200 leading-relaxed message-content">${marked.parse(escapeHtml(content))}</div>
                ${filesHtml}
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function scrollToBottom() {
    const chatArea = document.getElementById('chatArea');
    chatArea.scrollTop = chatArea.scrollHeight;
}

async function generateBot() {
    const prompt = document.getElementById('promptInput').value.trim();
    
    if (!prompt) {
        showToast('Please describe the bot you want to create!', 'error');
        return;
    }
    
    // Add user message
    addMessage(prompt, 'user');
    document.getElementById('promptInput').value = '';
    autoResize.call(document.getElementById('promptInput'));
    
    showLoading();
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                bot_type: 'chatbot',
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.session_id;
            generatedFiles = data.files;
            
            const fileCount = Object.keys(data.files).length;
            const message = `✅ **Bot generated successfully!**\n\nI've created ${fileCount} files for your bot.\n\n**Files created:**\n${Object.keys(data.files).map(f => `- \`${f}\``).join('\n')}\n\nYou can now deploy this bot to GitHub or preview it.`;
            
            addMessage(message, 'bot', data.files);
            showDeploySection();
            showToast(`Successfully generated ${fileCount} files!`, 'success');
        } else {
            addMessage(`❌ **Generation Failed**\n\n${data.error || 'Unknown error occurred. Please try again.'}`, 'bot');
            showToast(data.error || 'Generation failed', 'error');
        }
    } catch (error) {
        console.error('Generation error:', error);
        addMessage(`❌ **Network Error**\n\nFailed to connect to the server. Please check if the backend is running.`, 'bot');
        showToast('Failed to connect to server', 'error');
    } finally {
        hideLoading();
    }
}

function showDeploySection() {
    const deploySection = document.getElementById('deploySection');
    deploySection.classList.remove('hidden');
    
    // Generate default repo name from prompt
    const prompt = document.getElementById('promptInput').value.trim();
    if (prompt) {
        const defaultName = prompt.substring(0, 30).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
        document.getElementById('repoName').value = defaultName || 'my-awesome-bot';
    }
}

function hideDeploySection() {
    document.getElementById('deploySection').classList.add('hidden');
}

async function deployToGithub() {
    const repoName = document.getElementById('repoName').value.trim();
    const repoDesc = document.getElementById('repoDesc').value.trim();
    
    if (!repoName) {
        showToast('Please enter a repository name', 'error');
        return;
    }
    
    if (!currentSessionId) {
        showToast('No bot generated. Please generate a bot first.', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                repo_name: repoName,
                description: repoDesc || 'Bot generated by Bot Manager V2',
                commit_message: 'Initial bot deployment'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessage(`🚀 **Deployment Successful!**\n\nYour bot has been deployed to GitHub!\n\n🔗 **Repository:** ${data.repository_url}\n\n📁 **Files Deployed:** ${data.files_deployed.length}\n\nYou can now access your bot at the repository URL.`, 'bot');
            showToast('Successfully deployed to GitHub!', 'success');
            hideDeploySection();
            currentSessionId = null;
            generatedFiles = null;
        } else {
            addMessage(`❌ **Deployment Failed**\n\n${data.error || 'Unknown deployment error'}`, 'bot');
            showToast(data.error || 'Deployment failed', 'error');
        }
    } catch (error) {
        console.error('Deployment error:', error);
        addMessage(`❌ **Deployment Error**\n\nFailed to deploy to GitHub. Please check your GitHub token configuration.`, 'bot');
        showToast('Deployment failed', 'error');
    } finally {
        hideLoading();
    }
}

async function previewBot() {
    if (!currentSessionId) {
        showToast('No bot generated. Please generate a bot first.', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.html) {
            const modal = document.getElementById('previewModal');
            const iframe = document.getElementById('previewFrame');
            
            // Write HTML to iframe
            iframe.srcdoc = data.html;
            modal.classList.remove('hidden');
        } else {
            showToast('Failed to generate preview', 'error');
        }
    } catch (error) {
        console.error('Preview error:', error);
        showToast('Preview generation failed', 'error');
    } finally {
        hideLoading();
    }
}

function closePreview() {
    const modal = document.getElementById('previewModal');
    modal.classList.add('hidden');
    const iframe = document.getElementById('previewFrame');
    iframe.srcdoc = '';
}

function clearChat() {
    if (confirm('Clear all messages? This will reset your current session.')) {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.innerHTML = '';
        currentSessionId = null;
        generatedFiles = null;
        hideDeploySection();
        
        // Re-add welcome message
        addMessage(`Welcome back! 🎉\n\nReady to create another amazing bot? Just describe what you want to build!`, 'bot');
    }
}

async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            const configStatus = data.config_status === 'valid' ? '✅ All configured' : '⚠️ Missing some keys';
            showToast(`System Healthy | ${configStatus}`, 'success');
        } else {
            showToast('System issues detected', 'error');
        }
    } catch (error) {
        showToast('Health check failed', 'error');
    }
}

// Markdown parser (simple version)
const marked = {
    parse: function(text) {
        let html = text;
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Italic
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        // Code blocks
        html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<div class="message-code"><pre><code class="language-$1">$2</code></pre></div>');
        // Inline code
        html = html.replace(/`(.*?)`/g, '<code class="bg-black/30 px-1 py-0.5 rounded">$1</code>');
        // Lists
        html = html.replace(/^\s*[-*+]\s+(.*)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul class="list-disc list-inside mt-2">$1</ul>');
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }
};