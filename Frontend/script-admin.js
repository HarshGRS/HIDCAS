const API_BASE = "http://localhost:8001";

if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark-mode");
}

function getToken() { return localStorage.getItem("token"); }
function clearToken() { localStorage.removeItem("token"); }

function authFetch(path, opts = {}) {
    const token = getToken();
    opts.headers = opts.headers || {};
    if (token) opts.headers["Authorization"] = `Bearer ${token}`;
    return fetch(API_BASE + path, opts).then(async res => {
        if (res.status === 401) { clearToken(); window.location = "index.html"; throw new Error("Unauthorized"); }
        if (res.status === 403) { alert("Access denied. Admins only."); window.location = "dashboard-main.html"; throw new Error("Forbidden"); }
        return res;
    });
}

window.addEventListener("DOMContentLoaded", async () => {
    if (!getToken()) { window.location = "index.html"; return; }

    document.getElementById("logout-button").addEventListener("click", () => {
        clearToken(); window.location = "index.html";
    });

    document.getElementById("create-role-btn").addEventListener("click", createRole);
    document.getElementById("create-perm-btn").addEventListener("click", createPermission);
    document.getElementById("assign-role-btn").addEventListener("click", assignRole);

    await loadMatrix();
    await loadUsersAndRoles();
});


// ===================== MATRIX =====================
async function loadMatrix() {
    try {
        const res = await authFetch("/rbac/matrix");
        if (!res.ok) return;
        const data = await res.json();

        const { roles, permissions, matrix } = data;

        // Build header
        const header = document.getElementById("matrix-header");
        header.innerHTML = "<th>Role \\ Permission</th>";
        permissions.forEach(p => {
            const th = document.createElement("th");
            th.textContent = p.name;
            th.style.color = "#000000";
            header.appendChild(th);
        });

        // Build rows
        const tbody = document.getElementById("matrix-body");
        tbody.innerHTML = "";
        roles.forEach(role => {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.textContent = role.name;
            td.style.color = "#000000";  
            td.style.fontWeight = "600";
            tr.appendChild(td);

            permissions.forEach(perm => {
                const td2 = document.createElement("td");
                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.checked = matrix[role.id]?.permissions.includes(perm.id);
                checkbox.addEventListener("change", async () => {
                    await togglePermission(role.name, perm.name, checkbox.checked);
                });
                td2.appendChild(checkbox);
                tr.appendChild(td2);
            });

            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

async function togglePermission(roleName, permName, grant) {
    try {
        if (grant) {
            const res = await authFetch(
                `/rbac/grant?role_name=${encodeURIComponent(roleName)}&permission_name=${encodeURIComponent(permName)}`,
                { method: "POST" }
            );
            if (!res.ok) {
                const d = await res.json();
                alert(d.detail || "Error granting permission");
            }
        } else {
            const res = await authFetch(
                `/rbac/remove?role_name=${encodeURIComponent(roleName)}&permission_name=${encodeURIComponent(permName)}`,
                { method: "DELETE" }
            );
            if (!res.ok) {
                const d = await res.json();
                alert(d.detail || "Error removing permission");
            }
        }
    } catch (err) {
        console.error(err);
    }
}


// ===================== CREATE ROLE / PERMISSION =====================
async function createRole() {
    const name = document.getElementById("new-role-input").value.trim();
    if (!name) { alert("Enter role name"); return; }
    try {
        const res = await authFetch(
            `/rbac/roles?role_name=${encodeURIComponent(name)}`,
            { method: "POST" }
        );
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            document.getElementById("new-role-input").value = "";
            await loadMatrix();
            await loadUsersAndRoles();
        } else {
            alert(data.detail || "Error creating role");
        }
    } catch (err) { console.error(err); }
}

async function createPermission() {
    const name = document.getElementById("new-perm-input").value.trim();
    if (!name) { alert("Enter permission name"); return; }
    try {
        const res = await authFetch(
            `/rbac/permissions?permission_name=${encodeURIComponent(name)}`,
            { method: "POST" }
        );
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            document.getElementById("new-perm-input").value = "";
            await loadMatrix();
        } else {
            alert(data.detail || "Error creating permission");
        }
    } catch (err) { console.error(err); }
}


// ===================== ASSIGN ROLE =====================
async function loadUsersAndRoles() {
    try {
        const [usersRes, rolesRes] = await Promise.all([
            authFetch("/rbac/users"),
            authFetch("/rbac/roles")
        ]);
        const users = await usersRes.json();
        const roles = await rolesRes.json();

        const userSelect = document.getElementById("user-select");
        userSelect.innerHTML = "<option value=''>-- Select User --</option>";
        users.forEach(u => {
            const opt = document.createElement("option");
            opt.value = u.username;
            opt.textContent = `${u.username} (${u.role})`;
            userSelect.appendChild(opt);
        });

        const roleSelect = document.getElementById("role-select");
        roleSelect.innerHTML = "<option value=''>-- Select Role --</option>";
        roles.forEach(r => {
            const opt = document.createElement("option");
            opt.value = r.name;
            opt.textContent = r.name;
            roleSelect.appendChild(opt);
        });
    } catch (err) { console.error(err); }
}

async function assignRole() {
    const username = document.getElementById("user-select").value;
    const roleName = document.getElementById("role-select").value;
    if (!username || !roleName) { alert("Select user and role both"); return; }
    try {
        const res = await authFetch(
            `/rbac/assign-role?username=${encodeURIComponent(username)}&role_name=${encodeURIComponent(roleName)}`,
            { method: "PUT" }
        );
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            await loadUsersAndRoles();
        } else {
            alert(data.detail || "Error assigning role");
        }
    } catch (err) { console.error(err); }
}