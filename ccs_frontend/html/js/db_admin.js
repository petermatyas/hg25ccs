
$(function() {
    $('#header').load('admin_header.html');
    bindDbAdmin();
});


function dbMsg(text, isError) {
    const el = document.getElementById("dbActionMsg");
    if (!el) return;
    el.textContent = text;
    el.className = "my-2 " + (isError ? "text-danger" : "text-success");
}

function tsString() {
    return new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
}

// Auth-os letöltés: a fetch az auth.js wrapperből kapja a tokent,
// a választ blobként töltjük le (a sima <a href> nem küldene tokent).
function downloadWithAuth(url, filename) {
    dbMsg("Letöltés folyamatban...");
    fetch(url)
        .then(resp => {
            if (!resp.ok) throw new Error("HTTP " + resp.status);
            return resp.blob();
        })
        .then(blob => {
            const objUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = objUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(objUrl);
            dbMsg("Letöltés kész: " + filename);
        })
        .catch(err => dbMsg("Hiba a letöltésnél: " + err.message, true));
}

// Az oldal aktiválási állapotának megjelenítése a kapcsolón és a felirat.
function setSiteActiveUi(active) {
    const toggle = document.getElementById("siteActiveToggle");
    const state = document.getElementById("siteActiveState");
    if (toggle) toggle.checked = active;
    if (state) {
        state.textContent = active ? "AKTÍV" : "INAKTÍV";
        state.className = active ? "text-success" : "text-danger";
    }
}

function loadSiteActive() {
    fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/site_active`)
        .then(r => r.json())
        .then(d => setSiteActiveUi(!!d.active))
        .catch(() => setSiteActiveUi(false));
}

function bindDbAdmin() {
    // 0) Oldal aktiválása
    const siteToggle = document.getElementById("siteActiveToggle");
    if (siteToggle) {
        loadSiteActive();
        siteToggle.addEventListener("change", function () {
            const active = siteToggle.checked;
            dbMsg("Mentés...");
            fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/site_active`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ active: active })
            })
                .then(r => r.json())
                .then(d => {
                    setSiteActiveUi(!!d.active);
                    dbMsg(d.active ? "Az oldal aktiválva – a keresés működik." : "Az oldal deaktiválva – a keresés nem működik.");
                })
                .catch(err => {
                    dbMsg("Hiba az állapot mentésénél: " + err.message, true);
                    loadSiteActive(); // visszaállítjuk a kapcsolót a valós állapotra
                });
        });
    }

    // 1) Teljes adatbázis letöltése
    document.getElementById("dbDownloadBtn").addEventListener("click", function() {
        downloadWithAuth(`${PROTO}${HOST}${BACKENDPORT}/api/v1/download_db`, `logs_${tsString()}.sqlite3`);
    });

    // 2) Teljes adatbázis feltöltése (MEGERŐSÍTÉSSEL)
    document.getElementById("dbUploadBtn").addEventListener("click", function() {
        const inp = document.getElementById("dbUploadFile");
        if (!inp.files.length) { dbMsg("Válassz egy .sqlite3 fájlt!", true); return; }
        if (!confirm("Biztosan FELÜLÍROD a teljes adatbázist a feltöltött fájllal?\n\nA jelenlegi tartalom elveszik!")) return;

        const fd = new FormData();
        fd.append("file", inp.files[0]);
        dbMsg("Feltöltés folyamatban...");
        fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/upload_db`, { method: "POST", body: fd })
            .then(r => r.json())
            .then(d => dbMsg(d.note || "Adatbázis feltöltve."))
            .catch(err => dbMsg("Hiba a feltöltésnél: " + err.message, true));
    });

    // 3) Export (JSON)
    document.getElementById("dbExportBtn").addEventListener("click", function() {
        downloadWithAuth(`${PROTO}${HOST}${BACKENDPORT}/api/v1/export_logs`, `logs_export_${tsString()}.json`);
    });

    // 4) Import (JSON) (MEGERŐSÍTÉSSEL)
    document.getElementById("dbImportBtn").addEventListener("click", function() {
        const inp = document.getElementById("dbImportFile");
        if (!inp.files.length) { dbMsg("Válassz egy .json fájlt!", true); return; }
        if (!confirm("Biztosan importálod a bejegyzéseket a fájlból?\n\nA meglévők megmaradnak, az újak hozzáadódnak.")) return;

        const fd = new FormData();
        fd.append("file", inp.files[0]);
        dbMsg("Import folyamatban...");
        fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/import_logs`, { method: "POST", body: fd })
            .then(r => r.json())
            .then(d => dbMsg(`Import kész: ${d.added} új bejegyzés (a fájlban összesen ${d.total_in_file}).`))
            .catch(err => dbMsg("Hiba az importnál: " + err.message, true));
    });

    // 5) Tartalom törlése (MEGERŐSÍTÉSSEL)
    document.getElementById("dbClearBtn").addEventListener("click", function() {
        if (!confirm("Biztosan TÖRLÖD az adatbázis teljes log-tartalmát?\n\nEz a művelet NEM vonható vissza!")) return;

        dbMsg("Törlés folyamatban...");
        fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/clear_db`, { method: "DELETE" })
            .then(r => r.json())
            .then(d => dbMsg(`Törölve: ${d.deleted} bejegyzés.`))
            .catch(err => dbMsg("Hiba a törlésnél: " + err.message, true));
    });
}
