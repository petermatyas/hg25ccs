$(function() {
    $('#header').load('header.html');
});



document.getElementById("callsignQueryBtn").addEventListener("click", (evt) => {
    evt.preventDefault();
    
    const lang = document.getElementById("langSelectOption").value;
    if (lang == "hu") {
        document.getElementById("qsl_result").innerHTML = "folyamatban..."
    } else {
        document.getElementById("qsl_result").innerHTML = "in progress..."
    }

    //console.log("lanuage: " + lang)
    const callsign = document.getElementById("callsign").value;

    let url_qsl = `${PROTO}${HOST}${BACKENDPORT}/api/v1/generate_qsl?callsign=${callsign}&lang=${lang}`
    let url_diploma = `${PROTO}${HOST}${BACKENDPORT}/api/v1/generate_diploma?callsign=${callsign}&lang=${lang}`

    const promises = [
        fetch(url_qsl).then(resp => resp.json()),
        fetch(url_diploma).then(resp => resp.json())
    ];


    Promise.all(promises)
    .then(data => {
        let res_qsl = data[0]
        let res_diploma = data[1]
        
        //console.log("-------", res_diploma)

        qslEl = document.getElementById("qsl_result")
        qslEl.innerHTML = "";
        if (res_diploma["qso"].length > 0) {
            
            if (lang == "hu") {
                qslEl.innerHTML = "QSL lapok: "
            } else {
                qslEl.innerHTML = "QSL cards: "
            }
            
            for (let i=0; i<res_diploma["qso"].length; i++) {
                //console.log(res_diploma["qso"][i])
                let ts = res_diploma["qso"][i]["timestamp"]
                //console.log("--------", ts)
                let nr = i+1
                qslEl.innerHTML += `<a href="${PROTO}${HOST}${BACKENDPORT}/api/v1/download_qsl?callsign=${callsign}&timestamp=${ts}&fileNr=${nr}">${nr}</a>&nbsp;`
        
            }
        } else {
            if (lang == "hu") {
                qslEl.innerHTML = "0 QSL lap"
            } else {
                qslEl.innerHTML = "0 QSL card"
            }
        }
        



    })

    
})