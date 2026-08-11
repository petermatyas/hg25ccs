
$(function() {
    // A headert az admin.js tölti be egyszer (az admin.html mindhárom
    // feladat-JS-t egy oldalon tölti); itt nem duplikáljuk.
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
    return fetch(url)
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
        .catch(err => {
            dbMsg("Hiba a letöltésnél: " + err.message, true);
            throw err;
        });
}

function summaryMsg(text, isError) {
    const el = document.getElementById("summaryMsg");
    if (!el) return;
    el.textContent = text;
    el.className = "my-2 " + (isError ? "text-danger" : "text-success");
}

// QSO kimutatás letöltése. A visszajelzés a saját fülén jelenik meg, ezért nem
// a downloadWithAuth()-ot használja (az az Adatbázis fülre írna).
function downloadQsoSummary(format) {
    const minQsoInput = document.getElementById("summaryMinQso");
    const onlyHuInput = document.getElementById("summaryOnlyHungarian");

    const minValidQso = Math.max(1, parseInt(minQsoInput ? minQsoInput.value : "3", 10) || 1);
    const onlyHungarian = onlyHuInput ? onlyHuInput.checked : false;

    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/qso_summary`
        + `?format=${encodeURIComponent(format)}`
        + `&min_valid_qso=${minValidQso}`
        + `&only_hungarian=${onlyHungarian}`;
    const filename = `hg25ccs_qso_kimutatas_${tsString()}.${format === "doc" ? "docx" : "xlsx"}`;

    summaryMsg("Kimutatás készítése...");
    return fetch(url)
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
            summaryMsg("Letöltés kész: " + filename);
        })
        .catch(err => summaryMsg("Hiba a letöltésnél: " + err.message, true));
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

    // Biztonsági zár: amíg az oldal AKTÍV, a tartalom törlése tiltva
    // (nehogy élesben véletlenül kiürüljön az adatbázis). Csak inaktív
    // állapotban engedélyezett.
    const clearBtn = document.getElementById("dbClearBtn");
    if (clearBtn) {
        clearBtn.disabled = active;
        clearBtn.title = active
            ? "Az oldal aktív – előbb deaktiváld az oldalt a törléshez."
            : "";
    }
}

function loadSiteActive() {
    fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/site_active`)
        .then(r => r.json())
        .then(d => setSiteActiveUi(!!d.active))
        .catch(() => setSiteActiveUi(false));
}

function formatBytes(bytes) {
    if (!bytes || bytes < 1024) return `${bytes || 0} B`;
    const units = ["B", "KB", "MB", "GB"];
    let value = bytes;
    let unitIndex = 0;
    while (value >= 1024 && unitIndex < units.length - 1) {
        value /= 1024;
        unitIndex += 1;
    }
    return `${value.toFixed(value >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;");
}

function renderUploadedFiles(files) {
    const tbody = document.getElementById("uploadedFilesTableBody");
    if (!tbody) return;

    tbody.innerHTML = "";
    if (!files.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-muted">Nincsenek feltöltött fájlok.</td></tr>';
        return;
    }

    files.forEach((file) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${escapeHtml(file.filename || "")}</td>
            <td>${formatBytes(file.size_bytes || 0)}</td>
            <td>${new Date((file.modified_at || 0) * 1000).toLocaleString()}</td>
            <td><button type="button" class="btn btn-sm btn-outline-primary">Letöltés</button></td>`;
        row.querySelector("button").addEventListener("click", () => {
            downloadUploadedFile(file.filename || "");
        });
        tbody.appendChild(row);
    });
}

function fetchWithAuth(url, options) {
    return fetch(url, {
        ...(options || {}),
        headers: {
            ...(options && options.headers ? options.headers : {}),
            ...(ccsGetToken ? { Authorization: `Bearer ${ccsGetToken()}` } : {})
        }
    });
}

function removePdfFiles(url, confirmText, successText) {
    if (!confirm(confirmText)) return;
    dbMsg("Törlés folyamatban...");
    fetch(url, { method: "DELETE" })
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(d => {
            const removedCount = d.removed_count ?? (Array.isArray(d.removed) ? d.removed.length : 0);
            dbMsg(`${successText} ${removedCount} fájl törölve.`);
        })
        .catch(err => dbMsg("Hiba a törlésnél: " + err.message, true));
}

function loadUploadedFiles() {
    fetchWithAuth(`${PROTO}${HOST}${BACKENDPORT}/api/v1/uploaded_files`)
        .then(r => r.json())
        .then(files => {
            const normalized = (files || []).map((file) => {
                if (file && typeof file === "object" && "filename" in file) return file;
                if (Array.isArray(file) && file.length >= 2) {
                    return { filename: file[1], size_bytes: 0, modified_at: file[0] };
                }
                return null;
            }).filter(Boolean);

            if (normalized.length) {
                renderUploadedFiles(normalized);
                return;
            }

            return fetchWithAuth(`${PROTO}${HOST}${BACKENDPORT}/api/v1/log_uploads`)
                .then(r => r.json())
                .then(uploadRows => {
                    const fallback = (uploadRows || []).map((row) => {
                        if (Array.isArray(row) && row.length >= 2) {
                            return { filename: row[1], size_bytes: 0, modified_at: row[0] };
                        }
                        return null;
                    }).filter(Boolean);
                    renderUploadedFiles(fallback);
                });
        })
        .catch(err => {
            const tbody = document.getElementById("uploadedFilesTableBody");
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-danger">A fájlok listázása sikertelen.</td></tr>';
            }
            console.error(err);
        });
}

function downloadUploadedFile(filename) {
    if (!filename) return;
    downloadWithAuth(`${PROTO}${HOST}${BACKENDPORT}/api/v1/download_uploaded_file?filename=${encodeURIComponent(filename)}`, filename)
        .catch(() => {
            dbMsg(`A fájl letöltése nem sikerült: ${filename}`, true);
        });
}

function bindSummaryTab() {
    const docBtn = document.getElementById("summaryDocBtn");
    const xlsBtn = document.getElementById("summaryXlsBtn");
    if (docBtn) docBtn.addEventListener("click", () => downloadQsoSummary("doc"));
    if (xlsBtn) xlsBtn.addEventListener("click", () => downloadQsoSummary("xls"));
}

function bindDbAdmin() {
    bindSummaryTab();

    // 0) Oldal aktiválása
    const siteToggle = document.getElementById("siteActiveToggle");
    if (typeof loadUploadedFiles === "function" && document.getElementById("uploadedFilesTableBody")) {
        loadUploadedFiles();
    }
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

    // 3) Feltöltött logfájlok listázása
    loadUploadedFiles();

    // 4) Export (JSON)
    document.getElementById("dbExportBtn").addEventListener("click", function() {
        downloadWithAuth(`${PROTO}${HOST}${BACKENDPORT}/api/v1/export_logs`, `logs_export_${tsString()}.json`);
    });

    // 5) Import (JSON) (MEGERŐSÍTÉSSEL)
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

    // 6) Tartalom törlése (MEGERŐSÍTÉSSEL)
    document.getElementById("dbClearBtn").addEventListener("click", function() {
        if (!confirm("Biztosan TÖRLÖD az adatbázis teljes log-tartalmát?\n\nEz a művelet NEM vonható vissza!")) return;

        dbMsg("Törlés folyamatban...");
        fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/clear_db`, { method: "DELETE" })
            .then(r => r.json())
            .then(d => dbMsg(`Törölve: ${d.deleted} bejegyzés.`))
            .catch(err => dbMsg("Hiba a törlésnél: " + err.message, true));
    });

    document.getElementById("removeDiplomasBtn").addEventListener("click", function() {
        removePdfFiles(
            `${PROTO}${HOST}${BACKENDPORT}/api/v1/remove_diplomas`,
            "Biztosan törlöd a /diplomas mappában lévő PDF fájlokat?\n\nEz a művelet NEM vonható vissza!",
            "Diploma PDF fájlok törölve."
        );
    });

    document.getElementById("removeSqlBtn").addEventListener("click", function() {
        removePdfFiles(
            `${PROTO}${HOST}${BACKENDPORT}/api/v1/remove_qsls`,
            "Biztosan törlöd a /sql (QSL) mappában lévő PDF fájlokat?\n\nEz a művelet NEM vonható vissza!",
            "QSL PDF fájlok törölve."
        );
    });
}
