// CCS admin hitelesítés (kliens oldal).
//
// A token a localStorage-ban tárolódik, és minden API-híváshoz automatikusan
// hozzáadódik az Authorization fejléc. A belépőkapu (ccsInitGate) a szerveren
// ellenőrzi a token érvényességét, és csak utána tölti be az admin tartalmat.

const CCS_TOKEN_KEY = "ccs_admin_token";

function ccsGetToken() {
    return localStorage.getItem(CCS_TOKEN_KEY) || "";
}
function ccsSetToken(t) {
    localStorage.setItem(CCS_TOKEN_KEY, t);
}
function ccsClearToken() {
    localStorage.removeItem(CCS_TOKEN_KEY);
}

function ccsApiBase() {
    // PROTO / HOST / BACKENDPORT a common.js-ben van definiálva.
    return `${PROTO}${HOST}${BACKENDPORT}`;
}

// Minden jQuery ajax kéréshez csatoljuk a tokent.
$.ajaxSetup({
    beforeSend: function (xhr) {
        const t = ccsGetToken();
        if (t) xhr.setRequestHeader("Authorization", "Bearer " + t);
    }
});

// A natív fetch hívásokhoz is csatoljuk a tokent, és lekezeljük a 401-et.
(function () {
    const origFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
        init = init || {};
        const t = ccsGetToken();
        if (t) {
            const headers = new Headers(init.headers || {});
            headers.set("Authorization", "Bearer " + t);
            init.headers = headers;
        }
        const url = (typeof input === "string") ? input : (input && input.url) || "";
        return origFetch(input, init).then(function (resp) {
            // A bejelentkezés 401-e normális (hibás jelszó), azt a hívó kezeli.
            if (resp.status === 401 && url.indexOf("/api/v1/login") === -1) {
                ccsHandleUnauthorized();
            }
            return resp;
        });
    };
})();

function ccsHandleUnauthorized() {
    ccsClearToken();
    ccsShowLogin("Lejárt a munkamenet, jelentkezz be újra.");
}

function ccsShowLogin(message) {
    const content = document.getElementById("adminContent");
    const gate = document.getElementById("loginGate");
    if (content) content.style.display = "none";
    if (gate) gate.style.display = "block";
    const err = document.getElementById("loginError");
    if (err) err.innerText = message || "";
}

// Sikeres bejelentkezés után lefuttatja az oldalspecifikus inicializálást.
// admin.html -> initAdmin(), egyéb védett oldalak -> ccsOnAuthenticated().
function ccsRunAuthenticated() {
    if (typeof initAdmin === "function") initAdmin();
    if (typeof ccsOnAuthenticated === "function") ccsOnAuthenticated();
}

function ccsShowAdmin() {
    const content = document.getElementById("adminContent");
    const gate = document.getElementById("loginGate");
    if (gate) gate.style.display = "none";
    if (content) content.style.display = "block";
}

function ccsLogout() {
    ccsClearToken();
    ccsShowLogin("");
}

function ccsLogin(username, password) {
    return fetch(`${ccsApiBase()}/api/v1/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username, password: password })
    }).then(function (resp) {
        if (!resp.ok) throw new Error("login_failed");
        return resp.json();
    }).then(function (data) {
        ccsSetToken(data.token);
        return data;
    });
}

// Belépőkapu: a meglévő token ellenőrzése a szerveren, majd a megfelelő nézet.
function ccsInitGate() {
    const token = ccsGetToken();
    if (!token) {
        ccsShowLogin("");
        return;
    }
    fetch(`${ccsApiBase()}/api/v1/me`)
        .then(function (resp) {
            if (!resp.ok) throw new Error("invalid");
            ccsShowAdmin();
            ccsRunAuthenticated();
        })
        .catch(function () {
            ccsClearToken();
            ccsShowLogin("");
        });
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("loginForm");
    if (form) {
        form.addEventListener("submit", function (evt) {
            evt.preventDefault();
            const username = document.getElementById("loginUsername").value;
            const password = document.getElementById("loginPassword").value;
            const errEl = document.getElementById("loginError");
            if (errEl) errEl.innerText = "";

            ccsLogin(username, password)
                .then(function () {
                    document.getElementById("loginPassword").value = "";
                    ccsShowAdmin();
                    ccsRunAuthenticated();
                })
                .catch(function () {
                    if (errEl) errEl.innerText = "Hibás felhasználónév vagy jelszó.";
                });
        });
    }

    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", ccsLogout);
    }

    ccsInitGate();
});
