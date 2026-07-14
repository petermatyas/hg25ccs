$(function() {
    $('#header').load('header.html');
});

document.getElementById("callsign").addEventListener("keypress", (e) => {
    if (e.key == "Enter") document.getElementById("callsignQueryBtn").click();
})

document.getElementById("callsign_qsl").addEventListener("keypress", (e) => {
    if (e.key == "Enter") document.getElementById("callsignQueryBtnQsl").click();
})

document.getElementById("callsignQueryBtnQsl").addEventListener("click", (evt) => {
    evt.preventDefault();

    const lang = document.getElementById("langSelectOption").value;
    if (lang == "hu") {
        document.getElementById("qsl_result").innerHTML = "folyamatban..."
    } else {
        document.getElementById("qsl_result").innerHTML = "in progress..."
    }

    const callsign = document.getElementById("callsign_qsl").value;

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

        qslEl = document.getElementById("qsl_result")
        qslEl.innerHTML = "";
        if (res_diploma["qso"].length > 0) {

            if (lang == "hu") {
                qslEl.innerHTML = "QSL lapok: "
            } else {
                qslEl.innerHTML = "QSL cards: "
            }

            for (let i=0; i<res_diploma["qso"].length; i++) {
                let ts = res_diploma["qso"][i]["timestamp"]
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

document.getElementById("callsignQueryBtn").addEventListener("click", (evt) => {
    evt.preventDefault();
    
    const lang = document.getElementById("langSelectOption").value;
    if (lang == "hu") {
        document.getElementById("diploma_result").innerHTML = "folyamatban..."
    } else {
        document.getElementById("diploma_result").innerHTML = "in progress..."
    }

    //console.log("lanuage: " + lang)
    const callsign = document.getElementById("callsign").value;

    let url_qsl = `${PROTO}${HOST}${BACKENDPORT}/api/v1/generate_qsl?callsign=${callsign}&lang=${lang}`
    let url_diploma = `${PROTO}${HOST}${BACKENDPORT}/api/v1/generate_diploma?callsign=${callsign}&lang=${lang}`

    const promises = [
        fetch(url_qsl).then(resp => resp.json()),
        fetch(url_diploma).then(resp => resp.json())
    ];




    fetch(url_diploma)
    .then(resp => resp.json())
    .then(res_diploma => {
        console.log(res_diploma)


        let txt = ""
        if (res_diploma.nr_of_valid_qso < 3){
            if (lang == "hu") {
                txt = `${res_diploma.nr_of_valid_qso} érvényes QSO.</br>`
            } else {
                txt = `${res_diploma.nr_of_valid_qso} valid QSO.</br>`
            }
        } else {
            if (lang == "hu") {
                txt = `${res_diploma.nr_of_valid_qso} érvényes QSO. <b>Gratulálunk a diplomához!</b></br>`
            } else {
                txt = `${res_diploma.nr_of_valid_qso} valid QSO. <b>Congratulation for the diploma!</b></br>`
            }
        }
        document.getElementById("diploma_result").innerHTML = txt

        if (res_diploma.deserve == true) {
            let download_txt = ""
            if (lang == "hu") {
                download_txt = "Letöltés"
            } else {
                download_txt = "Download"
            }

            document.getElementById("diploma_result").innerHTML += `<a href="${PROTO}${HOST}${BACKENDPORT}/api/v1/download_diploma?callsign=${callsign}"><h3>${download_txt}</h3></a>`
        }

    })


})






