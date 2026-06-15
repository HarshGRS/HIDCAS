// Settings page script
const API_BASE = "http://localhost:8001";

// apply dark-mode preference
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

    // Dark mode toggle
    const darkModeToggle = document.getElementById("dark-mode");
    const savedDarkMode = localStorage.getItem("darkMode") === "true";
    if (savedDarkMode) {
        darkModeToggle.checked = true;
        document.body.classList.add("dark-mode");
    }
    darkModeToggle.addEventListener("change", () => {
        localStorage.setItem("darkMode", darkModeToggle.checked);
        document.body.classList.toggle("dark-mode");
    });

    // Notifications toggle
    const notificationsToggle = document.getElementById("notifications");
    const savedNotifications = localStorage.getItem("notifications") !== "false";
    if (savedNotifications) {
        notificationsToggle.checked = true;
    }
    notificationsToggle.addEventListener("change", () => {
        localStorage.setItem("notifications", notificationsToggle.checked);
    });

    // Change password
    document.getElementById("change-password-btn").addEventListener("click", async () => {
        const current = document.getElementById("current-password").value;
        const newPass = document.getElementById("new-password").value;
        const confirm = document.getElementById("confirm-password").value;

        if (!current || !newPass || !confirm) {
            alert("Fill all password fields");
            return;
        }

        if (newPass !== confirm) {
            alert("Passwords do not match");
            return;
        }

        alert("Password change feature coming soon");
        // TODO: Implement password change endpoint in backend
    });

    // Delete account
    document.getElementById("delete-account-btn").addEventListener("click", async () => {
        if (!confirm("Are you sure? This cannot be undone.")) {
            return;
        }
        alert("Account deletion feature coming soon");
        // TODO: Implement account deletion endpoint in backend
    });

    authFetch("/me").then(r => r.json()).then(user => {
        if (user.role === "admin") {
            document.getElementById("admin-nav").style.display = "flex";
       }
    });
});
