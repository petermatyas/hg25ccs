
$(function() {
    // A headert az admin.js tölti be egyszer (az admin.html mindhárom
    // feladat-JS-t egy oldalon tölti); itt nem duplikáljuk.
    const btn = document.getElementById("callsignQueryBtnId");
    const input = document.getElementById("callsignId");
    if (btn) btn.addEventListener("click", queryCallsign);
    if (input) {
        input.addEventListener("keydown", (evt) => {
            if (evt.key === "Enter" || evt.code === "Enter") {
                evt.preventDefault();
                evt.stopPropagation();
                queryCallsign();
            }
        });
    }
});

function timeConvert(ts) {
    return new Date(ts * 1000).toISOString().slice(0, 19).replace('T', ' ')
}

// Hívójel lekérdezés.
function queryCallsign() {
    let callsign = document.getElementById("callsignId").value;
    let tableEl = document.getElementById("logTableBodyId");
    let diplomaStatusEl = document.getElementById("diplomaStatusId");

    if (callsign == "") {
        alert("adj meg egy hívójelet");
        return;
    }

    let url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/logs_by_callsign?callsign=${callsign}`;

    tableEl.innerHTML = "";
    diplomaStatusEl.innerHTML = "";
    fetch(url)
        .then(resp => resp.json())
        .then(data => {
            let qsos = (data && data.qsos) ? data.qsos : [];

            if (data && data.diploma_downloaded) {
                diplomaStatusEl.innerHTML = 'Diploma: <span class="text-success fw-bold">letöltve</span>';
            } else {
                diplomaStatusEl.innerHTML = 'Diploma: <span class="text-danger fw-bold">nincs letöltve</span>';
            }

            for (let i=0; i<qsos.length; i++) {
                let qsoTime = timeConvert(qsos[i].timestamp);
                let uploadTime = timeConvert(qsos[i].upload_timestamp_utc);
                let qslCell = qsos[i].qsl_downloaded
                    ? '<span class="text-success fw-bold">igen</span>'
                    : '<span class="text-danger">nem</span>';
                tableEl.innerHTML += `
                    <tr>
                        <td>${qsoTime}</td>
                        <td>${qsos[i].band}</td>
                        <td>${qsos[i].mode}</td>
                        <td>${qsos[i].qth}</td>
                        <td>${qsos[i].rst_sent}</td>
                        <td>${qsos[i].rst_received}</td>
                        <td>${qsos[i].local_operator}</td>
                        <td>${uploadTime}</td>
                        <td>${qsos[i].uploaded_filename}</td>
                        <td>${qslCell}</td>
                    </tr>`;
            }
        });
}

// A statisztikát csak sikeres bejelentkezés után töltjük be (auth.js hívja).
function ccsOnAuthenticated() {
    fillStats();
    fillVisitStats();

    const botCb = document.getElementById("visitIncludeBots");
    if (botCb) botCb.addEventListener("change", fillVisitStats);
}

// ---- Látogatottsági statisztika (saját számláló) ----

// Egy "top" táblát tölt fel: [{key, count}] -> sorszám, kulcs, darab.
function fillTopTable(tbodyId, rows) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    tbody.innerHTML = "";
    (rows || []).forEach((r, i) => {
        const label = (r.key === "" || r.key === null || r.key === undefined) ? "(nincs)" : r.key;
        tbody.innerHTML += `<tr><td>${i + 1}</td><td>${escapeHtml(String(label))}</td><td>${r.count}</td></tr>`;
    });
    applyCollapsibleRows(tbody);
}

function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function applyCollapsibleRows(tbody, showLastOnly = false) {
    if (!tbody) return;

    const table = tbody.closest("table");
    if (!table) return;

    const existingButtons = table.parentElement ? table.parentElement.querySelectorAll(`[data-collapsible-for="${tbody.id}"]`) : [];
    existingButtons.forEach(btn => btn.remove());

    const rows = Array.from(tbody.querySelectorAll("tr"));
    if (rows.length <= 3) {
        rows.forEach(row => row.classList.remove("d-none"));
        return;
    }

    if (showLastOnly) {
        rows.slice(0, rows.length - 3).forEach(row => row.classList.add("d-none"));
        rows.slice(-3).forEach(row => row.classList.remove("d-none"));
    } else {
        rows.slice(3).forEach(row => row.classList.add("d-none"));
        rows.slice(0, 3).forEach(row => row.classList.remove("d-none"));
    }

    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-link btn-sm p-0 mt-2";
    button.setAttribute("data-collapsible-for", tbody.id);
    button.textContent = showLastOnly ? "Összes megjelenítése" : "Többi megjelenítése";
    button.addEventListener("click", () => {
        const hiddenRows = Array.from(tbody.querySelectorAll("tr.d-none"));
        if (hiddenRows.length > 0) {
            hiddenRows.forEach(row => row.classList.remove("d-none"));
            button.textContent = "Kevesebb megjelenítése";
        } else if (showLastOnly) {
            rows.slice(0, rows.length - 3).forEach(row => row.classList.add("d-none"));
            rows.slice(-3).forEach(row => row.classList.remove("d-none"));
            button.textContent = "Összes megjelenítése";
        } else {
            rows.slice(3).forEach(row => row.classList.add("d-none"));
            rows.slice(0, 3).forEach(row => row.classList.remove("d-none"));
            button.textContent = "Többi megjelenítése";
        }
    });

    table.insertAdjacentElement("afterend", button);
}

function fillVisitStats() {
    const includeBots = document.getElementById("visitIncludeBots");
    const withBots = includeBots && includeBots.checked ? "true" : "false";
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/visit_stats?include_bots=${withBots}`;

    // Az Authorization fejlécet az auth.js globális fetch-felülírása csatolja
    // (ugyanúgy, mint a fillStats()-nál), ezért itt nem kell külön kezelni.
    fetch(url)
        .then(resp => resp.json())
        .then(data => {
            const set = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
            set("v_total_views", data.total_views);
            set("v_unique", data.unique_visitors);
            set("v_new", data.new_views);
            set("v_returning", data.returning_views);
            set("v_returning_visitors", data.returning_visitors);

            // Elköteleződési átlagok (olvasható formában).
            const fmtMs = (ms) => (ms === null || ms === undefined) ? "–"
                : (ms >= 1000 ? (ms / 1000).toFixed(1) + " s" : Math.round(ms) + " ms");
            set("v_avg_load", fmtMs(data.avg_load_time_ms));
            set("v_avg_time", fmtMs(data.avg_time_on_page_ms));
            set("v_avg_scroll", (data.avg_scroll_depth === null || data.avg_scroll_depth === undefined)
                ? "–" : Math.round(data.avg_scroll_depth) + " %");

            fillTopTable("v_countries", data.countries);
            fillTopTable("v_browsers", data.browsers);
            fillTopTable("v_systems", data.systems);
            fillTopTable("v_resolutions", data.resolutions);
            fillTopTable("v_pages", data.pages);
            fillTopTable("v_referrers", data.referrers);
            fillTopTable("v_device_types", data.device_types);
            fillTopTable("v_languages", data.languages);
            fillTopTable("v_timezones", data.timezones);
            fillTopTable("v_connection_types", data.connection_types);
            fillTopTable("v_clicks", data.clicks);
            fillTopTable("v_searched", data.searched_callsigns);

            const dailyBody = document.getElementById("v_daily");
            if (dailyBody) {
                dailyBody.innerHTML = "";
                (data.daily || []).forEach(d => {
                    dailyBody.innerHTML += `<tr><td>${d.day}</td><td>${d.count}</td></tr>`;
                });
                applyCollapsibleRows(dailyBody, true);
            }

            // Letöltések (látogatóval összekötve).
            const dlBody = document.getElementById("v_downloads");
            if (dlBody) {
                dlBody.innerHTML = "";
                (data.downloads || []).forEach(d => {
                    const t = d.timestamp_utc ? timeConvert(d.timestamp_utc) : "";
                    const kind = d.kind === "diploma" ? "Diploma" : "QSL";
                    const country = d.country ? escapeHtml(d.country) : "–";
                    const vh = d.visitor_hash ? escapeHtml(d.visitor_hash) : "–";
                    dlBody.innerHTML += `<tr><td>${t}</td><td>${kind}</td><td>${escapeHtml(d.callsign || "")}</td><td>${country}</td><td><code>${vh}</code></td></tr>`;
                });
                applyCollapsibleRows(dlBody);
            }
        })
        .catch(err => console.error("visit_stats hiba:", err));
}

function removeTable(id) {
    $(id).find('tbody').html('');
}

// Az ország statisztikából ennyi sor látszik alapból.
const COUNTRY_LIMIT = 10;

// A 10. sor utáni országok mutatása/elrejtése. A gomb felirata a rejtett
// sorok számát mutatja; 10-nél kevesebb országnál a gomb sem jelenik meg.
function setupCountryToggle(hiddenCount) {
    const btn = document.getElementById("countryToggleBtn");
    if (!btn) return;

    if (hiddenCount <= 0) {
        btn.classList.add("d-none");
        return;
    }

    const setLabel = (opened) => {
        btn.textContent = opened ? "Kevesebb" : `További ${hiddenCount} ország`;
    };

    btn.classList.remove("d-none");
    setLabel(false);

    // onclick (nem addEventListener): a statisztika többszöri betöltésekor se
    // halmozódjanak a kezelők.
    btn.onclick = () => {
        const rows = document.querySelectorAll("#countryStatTableId tbody tr.country-extra");
        if (!rows.length) return;

        const opened = !rows[0].classList.contains("d-none");
        rows.forEach(row => row.classList.toggle("d-none", opened));
        setLabel(!opened);
    };
}

function fillStats() {
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/statistics`;
    fetch(url)
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        console.log(data);
        // Fill 2026 (current) and leave 2035 empty; 2025 has some static values.
        const set = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = (val === undefined || val === null) ? "" : val; };

        // 2026 (from backend)
        set("y2026_nr_of_qso", data["nr_of_qso"] || 0);
        set("y2026_nr_of_valid_diploma", (data["validDiploma"] || []).length);
        set("y2026_nr_of_countries", data["nr_of_countries"] || 0);
        set("y2026_participants", data["participanst_nr"] || 0);
        set("y2026_1_valid_qso", (data["1validQso"] || []).length);
        set("y2026_2_valid_qso", (data["2validQso"] || []).length);
        set("y2026_downloaded_diploma_nr", data["downlodedDiplomaNr"] || 0);

        // 2025: some fixed historical values (others left blank)
        // y2025_* fields for QSO/diploma/countries were set in HTML; set others to blank
        set("y2025_participants", "");
        set("y2025_1_valid_qso", "");
        set("y2025_2_valid_qso", "");
        set("y2025_downloaded_diploma_nr", "");

        // No 2035 column — nothing to clear.


        //document.getElementById("1qso").innerText = data["1validQso"].join(" ")

        // Diplomát szerzettek: hívójelenként a diploma-letöltés és a letöltött
        // QSL lapok száma a maximálisból.
        const diplomaBody = document.getElementById("diploma");
        if (diplomaBody) {
            diplomaBody.innerHTML = "";
            let details = data["validDiplomaDetails"];
            if (!details) {
                // Visszafelé kompatibilis tartalék, ha a backend még csak a
                // hívójel-listát adja (részletek nélkül).
                details = (data["validDiploma"] || []).map(c => ({ callsign: c }));
            }
            details.forEach(d => {
                let diplomaCell = d.diploma_downloaded
                    ? '<span class="text-success fw-bold">igen</span>'
                    : '<span class="text-danger">nem</span>';
                let qslCell = (d.qsl_total === undefined)
                    ? "–"
                    : `${d.qsl_downloaded || 0} / ${d.qsl_total}`;
                diplomaBody.innerHTML += `<tr><td>${d.callsign}</td><td>${diplomaCell}</td><td>${qslCell}</td></tr>`;
            });
        }

        // 2-QSO participants table
        const twoQsoBody = document.getElementById("twoQso");
        if (twoQsoBody) {
            twoQsoBody.innerHTML = "";
            const twoDetails = data.twoQsoDetails || [];
            twoDetails.forEach(d => {
                const qslCell = (d.qsl_total === undefined) ? "–" : `${d.qsl_downloaded} / ${d.qsl_total}`;
                twoQsoBody.innerHTML += `<tr><td>${d.callsign}</td><td>${qslCell}</td></tr>`;
            });
            applyCollapsibleRows(twoQsoBody);
        }

        removeTable("#statBandModeTableId");
        tableBody = $("#statBandModeTableId")


        let keys1 = Object.keys(data.modeBand)

        const bands = ["70cm","2m","4m","6m","10m","12m","15m","17m","20m","30m","40m","60m","80m","160m"];
        const columnTotals = {};
        bands.forEach(b => columnTotals[b] = 0);
        let grandTotal = 0;

        for (let i=0; i<keys1.length; i++) {
            let d = data.modeBand[keys1[i]] || {};
            let html = `<tr>`;
            html += `<td>${keys1[i]}</td>`;

            let rowSum = 0;
            bands.forEach(b => {
                const v = Number(d[b] || 0);
                rowSum += v;
                columnTotals[b] += v;
                const disp = (v === 0) ? '-' : v;
                html += `<td>${disp}</td>`;
            });

            const rowDisp = (rowSum === 0) ? '-' : rowSum;
            html += `<td>${rowDisp}</td>`;
            grandTotal += rowSum;
            html += `</tr>`;
            tableBody.append(html);
        }

        // Append totals row
        let totalsHtml = `<tr class="table-secondary fw-bold"><td>Összesen</td>`;
        bands.forEach(b => {
            const cdisp = (columnTotals[b] === 0) ? '-' : columnTotals[b];
            totalsHtml += `<td>${cdisp}</td>`;
        });
        const gdisp = (grandTotal === 0) ? '-' : grandTotal;
        totalsHtml += `<td>${gdisp}</td></tr>`;
        tableBody.append(totalsHtml);

        // Ország statisztika (a backend rekordszám szerint csökkenő sorrendben adja).
        // Az első COUNTRY_LIMIT sor látszik, a többi elrejtve készül el, és a
        // táblázat alatti gombbal nyitható/zárható.
        removeTable("#countryStatTableId");
        let countryBody = $("#countryStatTableId tbody")
        let countries = data.countries || []
        for (let i=0; i<countries.length; i++) {
            let extraClass = i < COUNTRY_LIMIT ? "" : ' class="country-extra d-none"'
            let row = `<tr${extraClass}><td>${i+1}</td><td>${countries[i].country}</td><td>${countries[i].count}</td></tr>`
            countryBody.append(row)
        }
        setupCountryToggle(countries.length - COUNTRY_LIMIT)

    })
}
