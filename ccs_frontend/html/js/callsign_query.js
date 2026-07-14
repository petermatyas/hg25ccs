
$(function() {
    $('#header').load('admin_header.html');
});


function timeConvert(ts) {
    return new Date(ts * 1000).toISOString().slice(0, 19).replace('T', ' ') 
}


document.getElementById("callsignQueryBtnId").addEventListener("click", function(event) {
    let callsign = document.getElementById("callsignId").value;
    let tableEl = document.getElementById("logTableBodyId")

    if (callsign == "") {
        alert("adj meg egy hívójelet")
    } else {
        let url = `${PROTO}${HOST}${BACKENDPORT}/api/v1/logs_by_callsign?callsign=${callsign}`

        tableEl.innerHTML = ""
        fetch(url)
            .then(resp => resp.json())
            .then(data => {
                for (let i=0; i<data.length; i++) {
                    console.log(data[i])
                    let qsoTime = timeConvert(data[i].timestamp)
                    let uploadTime = timeConvert(data[i].upload_timestamp_utc)
                    tableEl.innerHTML += `
                        <tr>
                            <td>${qsoTime}</td>
                            <td>${data[i].band}</td>
                            <td>${data[i].mode}</td>
                            <td>${data[i].qth}</td>
                            <td>${data[i].rst_sent}</td>
                            <td>${data[i].rst_received}</td>
                            <td>${data[i].local_operator}</td>
                            <td>${uploadTime}</td>
                            <td>${data[i].uploaded_filename}</td>
                        </tr>`
                    




                }
            })



    }

    

})

