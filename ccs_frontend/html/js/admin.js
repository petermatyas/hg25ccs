$(function() {
    $('#header').load('admin_header.html');
});



/*$("#logUploadsSelect").on("change", () => {
    fillLogs();
})*/

$("#logQueryBtn").on("click", () => {
    fillLogs();
})

$("#bandModeSubmitBtn").on("click", () => {
    let callsign = $('#operatorSelect').val();
    let band = $('input[name="band"]:checked').val();
    let mode = $('input[name="mode"]:checked').val();

    console.log(callsign + "   " + band + "    " + mode)
    let errorEl = document.getElementById("error_band_mode")

    errorEl.innerHTML = "";
    if (band == undefined) {
        errorEl.innerText = "nem adtál meg sávot"
        //alert("nem adtál meg sávot")
    } else if (mode == undefined) {
        errorEl.innerText = "nem adtál meg módot"
        //alert("nem adtál meg módot")
    } else if (callsign == "válassz") {
        errorEl.innerText = "nem adtál meg hívójelet"
        //alert("nem adtál meg hívójelet")
    } else {
        let data = JSON.stringify({"callsign":callsign, "mode":mode, "band":band})
        $.ajax({
            //url: `${HOST}:${BACKENDPORT}/active_band`,
            url: `${PROTO}${HOST}${BACKENDPORT}/api/v1/active_band`,
            type: "POST",
            data: data,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                //console.log("response: ")
                //console.log(response);
                if (response.error == null) {
                    fillActiveBands();
                } else {
                    errorEl.innerText = response.error
                    //alert(response.error)
                }
                

                $('input:checkbox').removeAttr('checked');
            },
            error: function(xhr, status, error) {
                console.log("ERROR /api/v1/active_band")
                console.log(xhr.responseText);
            }
        });
    }
});

$("#removeLogModalBtn").on("click", () => {
    removeLogs();
})



function fillActiveBands() {
    removeTable('#activeBandsTable');
    $.ajax({
        //url: `${HOST}:${BACKENDPORT}/active_band`,
        url: `${PROTO}${HOST}${BACKENDPORT}/api/v1/active_band`,
        type: "GET",
        success: function(response) {
            console.log("active bands: ");
            console.log(response);

            for (let i=0; i<response.length; i++) {
                console.log(response[i]);
                let callsign = response[i]["callsign"];
                let band = response[i]["band"];
                let mode = response[i]["mode"];


                tableBody = $("#activeBandsTable tbody");

                let duplicated = false;
                for (let j=0; j<i; j++) {
                    //console.log(response[i]["band"] == response[j]["band"])
                    if (response[i]["band"] == response[j]["band"] && response[i]["mode"] == response[j]["mode"]) {
                        duplicated = true;
                    }
                }
                console.log(duplicated)
                let html = "";
                if (duplicated == true) {
                    html = `<tr class="table-danger"><td>${callsign}</td><td>${band}</td><td>${mode}</td><td><button type="button" class="btn btn-outline-danger btn-sm" id=remove${i}Btn onClick="removeActiveBand(${i})">Törlés</button></td></tr>`;    
                } else {
                    html = `<tr><td>${callsign}</td><td>${band}</td><td>${mode}</td><td><button type="button" class="btn btn-outline-danger btn-sm" id=remove${i}Btn onClick="removeActiveBand(${i})">Törlés</button></td></tr>`;              
                }
                tableBody.append(html)
            }

        },
        error: function(xhr, status, error) {
            console.log(xhr.responseText);
        }
    });
}

function removeTable(id) {
    $(id).find('tbody').html('');
}

function removeActiveBand(lineNr) {
    let callsign = $("#activeBandsTable").find("tbody tr").eq(lineNr).find("td").eq(0).html();
    let band = $("#activeBandsTable").find("tbody tr").eq(lineNr).find("td").eq(1).html();
    let mode = $("#activeBandsTable").find("tbody tr").eq(lineNr).find("td").eq(2).html();

    $.ajax({
        //url: `${HOST}:${BACKENDPORT}/active_band?callsign=${callsign}&band=${band}&mode=${mode}`,
        url: `${PROTO}${HOST}${BACKENDPORT}/api/v1/active_band?callsign=${callsign}&band=${band}&mode=${mode}`,
        type: 'DELETE',
        success: function(response) {
            console.log(response);
            removeTable('#activeBandsTable');
            fillActiveBands();
        },
        error: function(xhr, status, error) {
            console.log(xhr.responseText);
        }
    });
}

function uploadFile() {
    console.log("upload file btn pressed")
    let logFile = document.getElementById("logFileInp").files[0];
    let formData = new FormData();
     
    formData.append("file", logFile);
    //const url = `${HOST}:${BACKENDPORT}/logs`;
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/logs`;
    fetch(url, {method: "POST", body: formData})
    .then(data => {return data.json();})
    .then(data => console.log(data))
    .then(function() {
        removeTable("#lastLogsTable");
    })
    .then(function() {
        fillLogUploadsSelect();
    });
}

function removeLogs() {
    inp = $("#logUploadsSelect").val()
    let filename  = inp.split(";")[0]
    let timestamp = inp.split(";")[1]

    //let url = `${HOST}:${BACKENDPORT}/logs?ts=${timestamp}&filename=${filename}`
    let url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/logs?ts=${timestamp}&filename=${filename}`
    fetch(url, {method: 'DELETE'})
    .then(function() {
        removeTable("#lastLogsTable");
    }).then(() => {
        fillLogUploadsSelect();
    });
    
}

function fillBands() {
    //const url = `${HOST}:${BACKENDPORT}/bands`;
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/bands`;
    fetch(url)
    .then(function(response) {
        return response.json()
    })
    .then(bandArr => {
        for (var i=0; i<bandArr.length; i++) {
            let band = bandArr[i]
            document.getElementById("bandSelector").innerHTML += `<div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="band" id="band_${band}" value="${band}">
                        <label class="form-check-label" for="band_${band}">${band}</label>
                    </div>`
        } 
    })
}

function fillModes() {
    //const url = `${HOST}:${BACKENDPORT}/modes`;
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/modes`;
    fetch(url)
    .then(function(response) {
        return response.json()
    })
    .then(modeArr => {
        for (var i=0; i<modeArr.length; i++) {
            let mode = modeArr[i]
            document.getElementById("modeSelector").innerHTML += `<div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="mode" id="mode_${mode}" value="${mode}">
                        <label class="form-check-label" for="mode_${mode}">${mode}</label>
                    </div>`
        } 
    })
}

function fillOps() {
    //const url = `${HOST}:${BACKENDPORT}/operators`;
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/operators`
    fetch(url)
    .then(function(response) {return response.json()})
    .then(function(operatorArr) {
        for (var i=0; i<operatorArr.length; i++) {
            let operator = operatorArr[i]
            document.getElementById("operatorSelect").innerHTML += `<option value="${operator}">${operator}</option>`
        }
    })
}

function fillLogUploadsSelect() {
    //const url = `${HOST}:${BACKENDPORT}/log_uploads`;
    //const url = `${PROTO}${HOST}:${BACKENDPORT}/api/v1/log_uploads`
    const url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/log_uploads`
    fetch(url)
    .then(function(response) {return response.json()})
    .then(function(dataArr) {
        document.getElementById("logUploadsSelect").innerHTML = "";
        for (var i=0; i<dataArr.length; i++) {
            let filename = dataArr[i][1];
            let ts = dataArr[i][0];
            let datetime = new Date(ts * 1000).toLocaleString();
            console.log(filename + " - " + datetime)
            document.getElementById("logUploadsSelect").innerHTML += `<option value="${filename};${ts}">${datetime} - ${filename}</option>`
        }
    })
}

function fillLogs() {
    removeTable('#lastLogsTable');

    inp = $("#logUploadsSelect").val()
    let filename  = inp.split(";")[0]
    let timestamp = inp.split(";")[1]

    let url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/logs?ts=${timestamp}&filename=${filename}`
    console.log(url)
    fetch(url)
        .then(response => response.json())
        .then(data => {
            for (let i=0; i<data.length; i++) {
                console.log(data[i])
                let ts       = data[i]["log_timestamp_utc"]
                let callsign = data[i]["callsign"]
                let band     = data[i]["band"]
                let mode     = data[i]["mode"]
                let operator = data[i]["local_operator"]
                //let error    = response[i]["error"]
                let datetime = new Date(ts * 1000).toLocaleString();

                var tableId = document.getElementById('lastLogsTable');
                var tBody = tableId.getElementsByTagName('tbody')[0];
                let html = `<tr><td>${datetime}</td><td>${callsign}</td><td>${band}</td><td>${mode}</td><td>${operator}</td></tr>`;
                tBody.innerHTML += html;
            }
        })

        /*.then(data => {data.json()})
        .then(response => {
            for (let i=0; i<response.length; i++) {
                let ts       = response[i]["log_timestamp_utc"]
                let callsign = response[i]["callsign"]
                let band     = response[i]["band"]
                let mode     = response[i]["mode"]
                //let error    = response[i]["error"]
                let datetime = new Date(ts * 1000).toLocaleString();

                tableBody = $("#lastLogsTable tbody")
                let html = `<tr><td>${datetime}</td><td>${callsign}</td><td>${band}</td><td>${mode}</td></tr>`;
                tableBody.append(html)
            }
        })*/

    /*$.ajax({
        //url: `${HOST}:${BACKENDPORT}/logs?ts=${timestamp}&filename=${filename}`,
        url: `${PROTO}${HOST}${BACKENDPORT}/api/v1/logs?ts=${timestamp}&filename=${filename}`,
        type: "GET",
        success: function(response) {
            //console.log(response);

            for (let i=0; i<response.length; i++) {
                let ts       = response[i]["log_timestamp_utc"]
                let callsign = response[i]["callsign"]
                let band     = response[i]["band"]
                let mode     = response[i]["mode"]
                //let error    = response[i]["error"]
                let datetime = new Date(ts * 1000).toLocaleString();

                tableBody = $("#lastLogsTable tbody")
                let html = `<tr><td>${datetime}</td><td>${callsign}</td><td>${band}</td><td>${mode}</td></tr>`;
                tableBody.append(html)
            }

        },
        error: function(xhr, status, error) {
            console.log(xhr.responseText);
        }
    });*/
}




// A védett admin tartalmat csak sikeres bejelentkezés után töltjük be.
// Ezt a függvényt az auth.js hívja meg, miután a token érvényes.
function initAdmin() {
    fillActiveBands();
    fillBands();
    fillModes();
    fillOps();
    fillLogUploadsSelect();
}


