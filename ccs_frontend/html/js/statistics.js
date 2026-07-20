
$(function() {
    $('#header').load('admin_header.html');

    const btn = document.getElementById("callsignQueryBtnId");
    if (btn) btn.addEventListener("click", queryCallsign);
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
}

function removeTable(id) {
    $(id).find('tbody').html('');
}

function fillStats() {
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/statistics`;
    fetch(url)
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        console.log(data);
        document.getElementById("nr_of_qso").innerHTML = data["nr_of_qso"];
        document.getElementById("nr_of_participants").innerHTML = data["participanst_nr"];
        document.getElementById("1_valid_qso").innerHTML = data["1validQso"].length;
        document.getElementById("2_valid_qso").innerHTML = data["2validQso"].length;
        document.getElementById("nr_of_valid_diploma").innerHTML = data["validDiploma"].length;
        document.getElementById("downloaded_diploma_nr").innerHTML = data["downlodedDiplomaNr"];


        //document.getElementById("1qso").innerText = data["1validQso"].join(" ")
        document.getElementById("diploma").innerText = data["validDiploma"].join(", ")

        removeTable("#statBandModeTableId");
        tableBody = $("#statBandModeTableId")


        let keys1 = Object.keys(data.modeBand)
        for (let i=0; i<keys1.length; i++) {

            let d = data.modeBand[keys1[i]]
            console.log(d)
            let html = `<tr>`
            html += `<td>${keys1[i]}</td>`
            html += `<td>${d["70cm"]}</td>`
            html += `<td>${d["2m"]}</td>`
            html += `<td>${d["4m"]}</td>`
            html += `<td>${d["6m"]}</td>`
            html += `<td>${d["10m"]}</td>`
            html += `<td>${d["12m"]}</td>`
            html += `<td>${d["15m"]}</td>`
            html += `<td>${d["17m"]}</td>`
            html += `<td>${d["20m"]}</td>`
            html += `<td>${d["30m"]}</td>`
            html += `<td>${d["40m"]}</td>`
            html += `<td>${d["60m"]}</td>`
            html += `<td>${d["80m"]}</td>`
            html += `<td>${d["160m"]}</td>`
            html += `<td>${d["other"]}</td>`
            html += `<td>${d["error"]}</td>`

            html += `</tr>`
            tableBody.append(html)

        }

        // Ország statisztika (a backend rekordszám szerint csökkenő sorrendben adja)
        removeTable("#countryStatTableId");
        let countryBody = $("#countryStatTableId tbody")
        let countries = data.countries || []
        for (let i=0; i<countries.length; i++) {
            let row = `<tr><td>${i+1}</td><td>${countries[i].country}</td><td>${countries[i].count}</td></tr>`
            countryBody.append(row)
        }

    })
}
