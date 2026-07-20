
$(function() {
    $('#header').load('admin_header.html');
});

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
