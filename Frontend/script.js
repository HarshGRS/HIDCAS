// common helpers
const API_BASE = "http://localhost:8001";

// apply dark-mode preference globally
if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark-mode");
}

function getToken() {
    return localStorage.getItem("token");
}

function setToken(t) {
    localStorage.setItem("token", t);
}

function clearToken() {
    localStorage.removeItem("token");
}

function authFetch(path, opts = {}) {
    const token = getToken();
    opts.headers = opts.headers || {};
    if (token) {
        opts.headers["Authorization"] = `Bearer ${token}`;
    }
    return fetch(API_BASE + path, opts).then(async res => {
        if (res.status === 401) {
            // unauthorized, redirect to login
            clearToken();
            window.location = "index.html";
            throw new Error("Unauthorized");
        }
        return res;
    });
}

// login/register page logic
function initAuthPage() {
    const loginPanel = document.getElementById("login-panel");
    const registerPanel = document.getElementById("register-panel");

    document.getElementById("show-register").addEventListener("click", e => {
        e.preventDefault();
        loginPanel.style.display = "none";
        registerPanel.style.display = "block";
    });
    document.getElementById("show-login").addEventListener("click", e => {
        e.preventDefault();
        loginPanel.style.display = "block";
        registerPanel.style.display = "none";
    });

    document.getElementById("login-form").addEventListener("submit", async e => {
        e.preventDefault();
        const username = document.getElementById("login-username").value;
        const password = document.getElementById("login-password").value;
        try {
            const res = await fetch(API_BASE + "/login", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, password})
            });
            const data = await res.json();
            if (res.ok) {
                setToken(data.access_token);
                window.location = "dashboard-main.html";
            } else {
                alert(data.detail || data.message || JSON.stringify(data) || "Login failed");
            }
        } catch (err) {
            console.error(err);
            alert("Network error");
        }
    });

    document.getElementById("register-form").addEventListener("submit", async e => {
        e.preventDefault();
        const username = document.getElementById("reg-username").value;
        const password = document.getElementById("reg-password").value;
        try {
            const res = await fetch(API_BASE + "/register", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, password})
            });
            const data = await res.json();
            if (res.ok) {
                alert("Registration successful. Please login.");
                loginPanel.style.display = "block";
                registerPanel.style.display = "none";
            } else {
                alert(data.detail || data.message || JSON.stringify(data) || "Registration failed");
            }
        } catch (err) {
            console.error(err);
            alert("Network error");
        }
    });
}

// dashboard logic
let currentConversationId = null;
let selectedDocumentId = null;

function initDashboard() {
    if (!getToken()) {
        window.location = "index.html";
        return;
    }
    
    authFetch("/me").then(r => r.json()).then(user => {
            if (user.role === "admin") {
                document.getElementById("admin-nav").style.display = "flex";
            }
        });

    // Check if coming from search
    const storedDocId = localStorage.getItem("selectedDocId");
    const storedDocName = localStorage.getItem("selectedDocName");
    if (storedDocId) {
        selectedDocumentId = parseInt(storedDocId);
        // use the same selection routine so project info is fetched
        selectDocument(selectedDocumentId, storedDocName || "");
        localStorage.removeItem("selectedDocId");
        localStorage.removeItem("selectedDocName");
    }

    document.getElementById("logout-button").addEventListener("click", () => {
        clearToken();
        window.location = "index.html";
    });

    // Clear button
    if (document.getElementById("clear-chat")) {
        document.getElementById("clear-chat").addEventListener("click", () => {
            clearMessages();
            currentConversationId = null;
            selectedDocumentId = null;
            const ul = document.getElementById("conversation-list");
            if (ul) ul.querySelectorAll("li").forEach(li => li.classList.remove("active"));
            const ul2 = document.getElementById("document-list");
            if (ul2) ul2.querySelectorAll("li").forEach(li => li.classList.remove("active"));
        });
    }

    document.getElementById("message-form").addEventListener("submit", async e => {
        e.preventDefault();
        const input = document.getElementById("message-input");
        const text = input.value.trim();
        if (!text) return;
        await sendMessage(text);
        input.value = "";
    });

    document.getElementById("upload-form").addEventListener("submit", async e => {
        e.preventDefault();
        const fileInput = document.getElementById("file-input");
        if (fileInput.files.length === 0) {
            alert("Select a file");
            return;
        }
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        try {
            const res = await authFetch("/documents/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (res.ok) {
                alert(data.message || "Uploaded");
                fileInput.value = "";
                loadDocuments();
            } else {
                alert(data.detail || data.message || JSON.stringify(data) || "Upload failed");
            }
        } catch (err) {
            console.error(err);
            alert("Upload error");
        }

    });

    loadConversations();
    loadDocuments();
}

async function loadConversations() {
    try {
        const res = await authFetch("/conversations");
        const list = await res.json();
        const ul = document.getElementById("conversation-list");
        ul.innerHTML = "";
        if (!Array.isArray(list) || list.length === 0) {
            ul.innerHTML = '<li class="empty-msg">No recent conversations found.</li>';
            return;
        }
        list.forEach(c => {
            const li = document.createElement("li");
            li.dataset.convId = c.conversation_id;

            // name portion
            const nameSpan = document.createElement("span");
            nameSpan.textContent = c.document_name || `(id ${c.conversation_id})`;
            nameSpan.addEventListener("click", () => {
                selectConversation(c.conversation_id);
            });
            li.appendChild(nameSpan);

            // three-dots menu for actions
            const menuBtn = document.createElement("span");
            menuBtn.className = "action-menu-btn";
            menuBtn.title = "More actions";
            menuBtn.textContent = "⋮";
            menuBtn.addEventListener("click", e => {
                e.stopPropagation();
                // Toggle menu - look for menu attached to body for this conversation
                let menu = document.querySelector(`.action-menu[data-conv-id='${c.conversation_id}']`);
                if (menu) {
                    menu.remove();
                    return;
                }
                menu = document.createElement('div');
                menu.className = 'action-menu';
                menu.dataset.convId = c.conversation_id;
                // place the menu on the page root so it's not clipped by
                // scrollable/overflowing sidebars; we'll position it near the button
                menu.style.position = 'fixed';
                // Only Delete option (remove Download)
                const deleteOpt = document.createElement('div');
                deleteOpt.className = 'action-menu-item';
                deleteOpt.textContent = 'Delete';
                deleteOpt.style.fontSize = '18px';
                deleteOpt.style.fontWeight = 'bold';
                deleteOpt.style.fontc = '#000000';
                deleteOpt.addEventListener('click', (ev) => {
                    ev.stopPropagation();
                    deleteConversation(c.conversation_id);
                    menu.remove();
                });
                menu.appendChild(deleteOpt);
                // Remove any other open menus
                document.querySelectorAll('.action-menu').forEach(m => m.remove());
                                // compute button position and align menu's right edge to the button
                                const rect = menuBtn.getBoundingClientRect();
                                document.body.appendChild(menu);
                                // Calculate menu position to keep it inside viewport
                                let menuWidth = 140;
                                let menuHeight = 48; // estimate, will adjust after rendering
                                setTimeout(() => {
                                    menuWidth = menu.offsetWidth;
                                    menuHeight = menu.offsetHeight;
                                    let left = rect.right - menuWidth;
                                    let top = rect.bottom + 4;
                                    // Prevent overflow right
                                    if (left + menuWidth > window.innerWidth) left = window.innerWidth - menuWidth - 8;
                                    if (left < 0) left = 8;
                                    // Prevent overflow bottom
                                    if (top + menuHeight > window.innerHeight) top = rect.top - menuHeight - 4;
                                    if (top < 0) top = 8;
                                    menu.style.left = left + 'px';
                                    menu.style.top = top + 'px';
                                }, 0);
            });
            li.appendChild(menuBtn);

            ul.appendChild(li);
        });
    } catch (err) {
        console.error(err);
        const ul = document.getElementById("conversation-list");
        ul.innerHTML = '<li class="empty-msg">Error loading conversations.</li>';
    }
} 

async function loadDocuments() {
    try {
        // fetch a generous number but only display the first 10
        const res = await authFetch(`/documents/list?skip=0&limit=1000`);
        const docs = await res.json();
        const ul = document.getElementById("document-list");
        ul.innerHTML = "";
        if (!Array.isArray(docs) || docs.length === 0) {
            ul.innerHTML = '<li class="empty-msg">No recent documents found.</li>';
            return;
        }
        docs.forEach((d, idx) => {
            if (idx >= 10) return; // only show 10 recent
            const li = document.createElement("li");
            li.dataset.docId = d.id;

            const nameSpan = document.createElement("span");
            nameSpan.textContent = d.filename;
            nameSpan.addEventListener("click", () => {
                selectDocument(d.id, d.filename);
            });
            li.appendChild(nameSpan);

            const actions = document.createElement("span");
            actions.className = "actions";
            const downloadBtn = document.createElement("span");
            downloadBtn.className = "action-icon";
            downloadBtn.title = "Download document";
            downloadBtn.textContent = "⬇️";
            downloadBtn.addEventListener("click", e => {
                e.stopPropagation();
                downloadDocument(d.id, d.filename);
            });
            const deleteBtn = document.createElement("span");
            deleteBtn.className = "action-icon";
            deleteBtn.title = "Delete document";
            deleteBtn.textContent = "🗑️";
            deleteBtn.addEventListener("click", e => {
                e.stopPropagation();
                deleteDocument(d.id);
            });
            actions.appendChild(downloadBtn);
            actions.appendChild(deleteBtn);
            li.appendChild(actions);

            ul.appendChild(li);
        });

        // highlight a document if one was preselected
        if (selectedDocumentId) {
            highlightSelected("doc", selectedDocumentId);
        }
    } catch (err) {
        console.error(err);
        const ul = document.getElementById("document-list");
        ul.innerHTML = '<li class="empty-msg">Error loading documents.</li>';
    }
}

function selectConversation(id) {
    currentConversationId = id;
    selectedDocumentId = null;
    const title = document.getElementById("chat-title");
    if (title) title.textContent = "Chat History";
    highlightSelected("conv", id);
    loadMessages(id);
}

function selectDocument(id, name) {
    selectedDocumentId = id;
    currentConversationId = null;
    const title = document.getElementById("chat-title");
    if (title) title.textContent = `Chat: ${name}`;
    highlightSelected("doc", id);
    clearMessages();
    appendSystemMessage(`Ready to chat about document: ${name}`);

    // fetch project info and display if available
    authFetch(`/documents/${id}/project`)
        .then(res => {
            if (!res.ok) throw new Error("no info");
            return res.json();
        })
        .then(info => {
            let msg = "Project Info:";
            if (info.company_name) msg += `\nCompany: ${info.company_name}`;
            if (info.project_name) msg += `\nProject: ${info.project_name}`;
            if (info.location) msg += `\nLocation: ${info.location}`;
            if (info.year) msg += `\nYear: ${info.year}`;
            if (info.budget) msg += `\nBudget: ${info.budget}`;
            if (info.loan_amount) msg += `\nLoan: ${info.loan_amount}`;
            appendSystemMessage(msg);
        })
        .catch(() => {
            // ignore if none
        });
} 

function highlightSelected(itemType, id) {
    // clear others
    const convItems = document.querySelectorAll("#conversation-list li");
    convItems.forEach(li => {
        li.classList.remove("active");
    });
    const docItems = document.querySelectorAll("#document-list li");
    docItems.forEach(li => {
        li.classList.remove("active");
    });
    if (itemType === "conv") {
        const node = document.querySelector(`#conversation-list li[data-conv-id='${id}']`);
        if (node) node.classList.add("active");
    } else if (itemType === "doc") {
        const node = document.querySelector(`#document-list li[data-doc-id='${id}']`);
        if (node) node.classList.add("active");
    }
}

async function loadMessages(conversationId) {
    try {
        const res = await authFetch(`/conversations/${conversationId}/messages`);
        const msgs = await res.json();
        renderMessages(msgs);
    } catch (err) {
        console.error(err);
    }
}

function renderMessages(msgs) {
    const container = document.getElementById("messages");
    container.innerHTML = "";
    msgs.forEach(m => {
        const div = document.createElement("div");
        div.className = `message ${m.role}`;
        const content = document.createElement("div");
        content.className = "message-content";
        content.textContent = m.content;
        div.appendChild(content);
        container.appendChild(div);
    });
    container.scrollTop = container.scrollHeight;
}

function clearMessages() {
    document.getElementById("messages").innerHTML = "";
}

function appendSystemMessage(text) {
    const container = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "message assistant";
    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = text;
    div.appendChild(content);
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

async function sendMessage(text) {
    // append user text immediately for responsiveness
    const container = document.getElementById("messages");
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    const userContent = document.createElement("div");
    userContent.className = "message-content";
    userContent.textContent = text;
    userDiv.appendChild(userContent);
    container.appendChild(userDiv);
    container.scrollTop = container.scrollHeight;

    let payload = {message: text};
    if (currentConversationId) {
        payload.conversation_id = currentConversationId;
    } else if (selectedDocumentId) {
        payload.document_id = selectedDocumentId;
    } else {
        alert("Select a conversation or document first");
        return;
    }

    try {
        const res = await authFetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || data.message || JSON.stringify(data) || "Error");
            return;
        }

        // append assistant answer
        const botDiv = document.createElement("div");
        botDiv.className = "message assistant";
        const botContent = document.createElement("div");
        botContent.className = "message-content";
        botContent.textContent = data.answer;
        botDiv.appendChild(botContent);
        container.appendChild(botDiv);
        container.scrollTop = container.scrollHeight;

        // update conversation id if new
        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
            // refresh list to include new conversation
            loadConversations();
            highlightSelected("conv", currentConversationId);
        }
    } catch (err) {
        console.error(err);
    }
}



// helper actions
async function downloadDocument(docId, filename) {
    try {
        const res = await authFetch(`/documents/${docId}/download`);
        if (!res.ok) {
            const data = await res.json();
            alert(data.detail || data.message || "Download failed");
            return;
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename || "document";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error(err);
        alert("Error downloading");
    }
}

async function deleteDocument(docId) {
    if (!confirm("Delete this document?")) return;
    try {
        const res = await authFetch(`/documents/${docId}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || data.message || "Delete failed");
            return;
        }
        loadDocuments();
        if (selectedDocumentId === docId) {
            clearMessages();
            currentConversationId = null;
            selectedDocumentId = null;
            const title = document.getElementById("chat-title");
            if (title) title.textContent = "Start a New Conversation";
        }
        alert(data.message || "Deleted");
    } catch (err) {
        console.error(err);
    }
}

async function downloadConversation(convId) {
    try {
        const res = await authFetch(`/conversations/${convId}/messages`);
        if (!res.ok) {
            const data = await res.json();
            alert(data.detail || data.message || "Unable to fetch messages");
            return;
        }
        const msgs = await res.json();
        let text = "";
        msgs.forEach(m => {
            text += `[${m.role}] ${m.content}\n`;
        });
        const blob = new Blob([text], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `conversation_${convId}.txt`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error(err);
        alert("Error downloading conversation");
    }
}

async function deleteConversation(convId) {
    if (!confirm("Delete this conversation?")) return;
    try {
        const res = await authFetch(`/conversations/${convId}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || data.message || "Delete failed");
            return;
        }
        loadConversations();
        if (currentConversationId === convId) {
            clearMessages();
            currentConversationId = null;
            const title = document.getElementById("chat-title");
            if (title) title.textContent = "Start a New Conversation";
        }
        alert(data.message || "Conversation deleted");
    } catch (err) {
        console.error(err);
    }
}

// entry
// close any open action menus when clicking outside
document.addEventListener('click', () => {
    document.querySelectorAll('.action-menu').forEach(m => m.remove());
});
window.addEventListener("DOMContentLoaded", () => {
    const pathname = window.location.pathname;
    if (pathname.endsWith("/dashboard.html") || pathname.endsWith("/dashboard-main.html")) {
        initDashboard();
    } else {
        initAuthPage();
    }
});
