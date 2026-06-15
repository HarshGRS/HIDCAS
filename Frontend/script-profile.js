// Profile page script
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

    loadUserProfile();
});

async function loadUserProfile() {
    try {
        const res = await authFetch("/me");
        if (!res.ok) {
            document.getElementById("profile-username").textContent = "Not available";
            document.getElementById("profile-role").textContent = `Role: -`;
            document.getElementById("user-id").textContent = "-";
            document.getElementById("member-since").textContent = "-";
            document.getElementById("permissions-list").innerHTML = "<li class='empty-msg'>Unable to load profile.</li>";
            return;
        }
        const user = await res.json();

        document.getElementById("profile-username").textContent = user.username || "Not available";
        document.getElementById("profile-role").textContent = `Role: ${user.role || "N/A"}`;
        document.getElementById("user-id").textContent = user.id || "-";
        document.getElementById("member-since").textContent = new Date().toLocaleDateString();

        // Render permissions
        const permList = document.getElementById("permissions-list");
        permList.innerHTML = "";
        if (user.permissions && user.permissions.length > 0) {
            user.permissions.forEach(perm => {
                const li = document.createElement("li");
                li.textContent = perm;
                permList.appendChild(li);
            });
        } else {
            permList.innerHTML = "<li class='empty-msg'>No permissions</li>";
        }
        if (user.role === "admin") {
            document.getElementById("admin-nav").style.display = "flex";
        }
    } catch (err) {
        console.error(err);
        document.getElementById("profile-username").textContent = "Not available";
        document.getElementById("profile-role").textContent = `Role: -`;
        document.getElementById("user-id").textContent = "-";
        document.getElementById("member-since").textContent = "-";
        document.getElementById("permissions-list").innerHTML = "<li class='empty-msg'>Error loading profile.</li>";
    }
}
