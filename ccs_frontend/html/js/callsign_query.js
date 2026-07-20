
$(function() {
    $('#header').load('admin_header.html');
});


function timeConvert(ts) {
    return new Date(ts * 1000).toISOString().slice(0, 19).replace('T', ' ')
}


document.getElementById("callsignQueryBtnId").addEventListener("click", function(event) {
    let callsign = document.getElementById("callsignId").value;
    let tableEl = document.getElementById("logTableBodyId")
    let diplomaStatusEl = document.getElementById("diplomaStatusId")

    if (callsign == "") {
        alert("adj meg egy hívójelet")
    } else {
        let url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/logs_by_callsign?callsign=${callsign}`

        tableEl.innerHTML = ""
        diplomaStatusEl.innerHTML = ""
        fetch(url)
            .then(resp => resp.json())
            .then(data => {
                // A backend most objektumot ad vissza: { diploma_downloaded, qsos }
                let qsos = (data && data.qsos) ? data.qsos : []

                // Diploma letöltési státusz sor
                if (data && data.diploma_downloaded) {
                    diplomaStatusEl.innerHTML = 'Diploma: <span class="text-success fw-bold">letöltve</span>'
                } else {
                    diplomaStatusEl.innerHTML = 'Diploma: <span class="text-danger fw-bold">nincs letöltve</span>'
                }

                for (let i=0; i<qsos.length; i++) {
                    console.log(qsos[i])
                    let qsoTime = timeConvert(qsos[i].timestamp)
                    let uploadTime = timeConvert(qsos[i].upload_timestamp_utc)
                    let qslCell = qsos[i].qsl_downloaded
                        ? '<span class="text-success fw-bold">igen</span>'
                        : '<span class="text-danger">nem</span>'
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
                        </tr>`
                }
            })
    }
})
