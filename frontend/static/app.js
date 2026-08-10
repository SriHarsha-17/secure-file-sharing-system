async function api(url, options={}) {
  function getCookie(name) {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const parts = cookie.trim().split("=");

        if (parts[0] === name) {
            return decodeURIComponent(parts.slice(1).join("="));
        }
    }

    return null;
}


async function api(url, options = {}) {

    const opts = {
        ...options,
        credentials: "same-origin",
        headers: {
            ...(options.headers || {})
        }
    };

    // Get Django CSRF token
    const csrfToken = getCookie("csrftoken");

    if (csrfToken) {
        opts.headers["X-CSRFToken"] = csrfToken;
    }

    // Convert JavaScript objects to JSON
    if (
        opts.body &&
        !(opts.body instanceof FormData) &&
        typeof opts.body !== "string"
    ) {
        opts.headers["Content-Type"] = "application/json";
        opts.body = JSON.stringify(opts.body);
    }

    const response = await fetch(url, opts);

    const contentType = response.headers.get("content-type") || "";

    let data;

    if (contentType.includes("application/json")) {
        data = await response.json();
    } else {
        data = await response.text();
    }

    if (!response.ok) {
        throw new Error(
            typeof data === "object" && data.detail
                ? data.detail
                : data || "Request failed"
        );
    }

    return data;
}
}

function show(id) {
  ["login","register","files","spaces"].forEach(x => {
    document.getElementById(x).hidden = x !== id;
  });
  if (id === "files") loadFiles();
  if (id === "spaces") loadSpaces();
}

async function register() {
  try {
    const data = await api("/api/accounts/register/", {
      method:"POST",
      body:{
        username:document.getElementById("reg-user").value,
        email:document.getElementById("reg-email").value,
        password:document.getElementById("reg-pass").value
      }
    });
    document.getElementById("reg-out").textContent = JSON.stringify(data,null,2);
  } catch(e){ document.getElementById("reg-out").textContent=e.message; }
}

async function login() {
    try {
        const data = await api("/api/accounts/login/", {
            method: "POST",
            body: {
                username: document.getElementById("login-user").value,
                password: document.getElementById("login-pass").value
            }
        });

        if (data.mfa_required) {
            document.getElementById("mfa-box").hidden = false;
        }

        document.getElementById("login-out").textContent =
            JSON.stringify(data, null, 2);

    } catch (e) {
        document.getElementById("login-out").textContent = e.message;
    }
}

async function verifyMfa() {
  try {
    const data = await api("/api/accounts/verify-mfa/", {
      method:"POST",
      body:{otp:document.getElementById("otp").value}
    });
    document.getElementById("login-out").textContent=JSON.stringify(data,null,2);
  } catch(e){ document.getElementById("login-out").textContent=e.message; }
}

async function logout() {
  await api("/api/accounts/logout/", {method:"POST"});
  alert("Logged out");
}

async function encryptAndUpload() {
  const input=document.getElementById("file-input");
  if(!input.files.length) return alert("Choose a file first");
  try {
    const result=await CryptoClient.encryptFile(input.files[0]);

    // The AES key is exported for the client-side sharing layer.
    // In a production deployment, wrap this key for the authorized recipient
    // using a recipient public key rather than sending it in plaintext.
    sessionStorage.setItem("key:"+result.originalName, result.keyB64);
    sessionStorage.setItem("nonce:"+result.originalName, result.nonceB64);

    const form=new FormData();
    form.append("file", result.ciphertext, result.originalName+".enc");
    form.append("original_name", result.originalName);
    form.append("nonce_b64", result.nonceB64);
    form.append("file_hash", result.plaintextHash);

    const data=await api("/api/files/upload/", {method:"POST",body:form});
    document.getElementById("file-list").insertAdjacentHTML(
      "afterbegin",
      `<div class="file-item"><b>${escapeHtml(data.original_name)}</b>
      <div>Encrypted with ${data.algorithm}</div>
      <div>File ID: ${data.id}</div></div>`
    );
  } catch(e){ alert(e.message); }
}

async function loadFiles() {
  try {
    const data=await api("/api/files/mine/");
    const all=[...(data.owned||[]),...(data.shared||[])];
    document.getElementById("file-list").innerHTML=all.map(f =>
      `<div class="file-item">
        <b>${escapeHtml(f.original_name)}</b>
        <div>${f.algorithm} | ${f.size_bytes} bytes</div>
        <button onclick="downloadCipher('${f.id}','${escapeHtml(f.original_name)}')">Download encrypted</button>
        <button onclick="createShare('${f.id}')">Create share</button>
      </div>`
    ).join("");
  } catch(e){ document.getElementById("file-list").textContent=e.message; }
}

async function downloadCipher(id,name) {
  try {
    const blob=await api(`/api/files/${id}/download/`);
    const a=document.createElement("a");
    a.href=URL.createObjectURL(blob);
    a.download=name+".enc";
    a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href),1000);
  } catch(e){ alert(e.message); }
}

async function createShare(id) {
  try {
    const data=await api(`/api/files/${id}/share/`, {
      method:"POST",
      body:{expires_minutes:60,max_downloads:1}
    });
    const url=location.origin+"/share.html?token="+encodeURIComponent(data.token);
    await navigator.clipboard.writeText(url);
    alert("Share URL copied:\n"+url);
  } catch(e){ alert(e.message); }
}

async function createSpace() {
  try {
    const data=await api("/api/spaces/", {
      method:"POST",
      body:{name:document.getElementById("space-name").value}
    });
    document.getElementById("space-list").insertAdjacentHTML(
      "afterbegin",
      `<div class="space-item"><b>${escapeHtml(data.name)}</b> (${data.id})</div>`
    );
  } catch(e){ alert(e.message); }
}

async function loadSpaces() {
  try {
    const data=await api("/api/spaces/mine/");
    document.getElementById("space-list").innerHTML=data.map(s =>
      `<div class="space-item"><b>${escapeHtml(s.name)}</b><br>${s.id}</div>`
    ).join("");
  } catch(e){ document.getElementById("space-list").textContent=e.message; }
}

async function loadAudit() {
  try {
    const data=await api("/api/audit/events/");
    document.getElementById("audit-out").textContent=JSON.stringify(data,null,2);
  } catch(e){ document.getElementById("audit-out").textContent=e.message; }
}

function escapeHtml(s){
  return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
}
