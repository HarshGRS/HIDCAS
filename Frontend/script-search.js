// Search page script
const API_BASE = "http://localhost:8001";

// apply dark-mode preference
if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark-mode");
}

function getToken() {
    return localStorage.getItem("token");
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
            clearToken();
            window.location = "index.html";
            throw new Error("Unauthorized");
        }
        return res;
    });
}

window.addEventListener("DOMContentLoaded", () => {
    if (!getToken()) {
        window.location = "index.html";
        return;
    }

    document.getElementById("logout-button").addEventListener("click", () => {
        clearToken();
        window.location = "index.html";
    });

    document.getElementById("search-btn").addEventListener("click", async () => {
        const query = document.getElementById("search-input").value.trim();
        if (!query) {
            alert("Enter a search term");
            return;
        }
        await searchDocuments(query);
    });

    document.getElementById("search-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            document.getElementById("search-btn").click();
        }
    });

    authFetch("/me").then(r => r.json()).then(user => {
    if (user.role === "admin") {
        document.getElementById("admin-nav").style.display = "flex";
    }
    });
});

async function searchDocuments(query) {
    try {
        const res = await authFetch(`/documents/search?q=${encodeURIComponent(query)}`);
        if (!res.ok) {
            renderResults([]);
            return;
        }
        const docs = await res.json();
        renderResults(docs);
    } catch (err) {
        console.error(err);
        renderResults([]);
    }
}

function renderResults(docs) {
    const container = document.getElementById("search-results");
    container.innerHTML = "";

    if (!Array.isArray(docs) || docs.length === 0) {
        container.innerHTML = "<p class='empty-msg'>No documents found or error occurred.</p>";
        return;
    }

    docs.forEach(doc => {
        const card = document.createElement("div");
        card.className = "result-card";
        card.innerHTML = `
            <h4>${doc.filename}</h4>
            <p>ID: ${doc.id}</p>
            <button onclick=\"startChat(${doc.id}, '${doc.filename.replace(/'/g, "\\'")}')\">Chat</button>
        `;
        container.appendChild(card);
    });
}

async function startChat(docId, docName) {
    // Store selected doc and redirect to dashboard-main
    localStorage.setItem("selectedDocId", docId);
    localStorage.setItem("selectedDocName", docName);
    window.location = "dashboard-main.html";
}
