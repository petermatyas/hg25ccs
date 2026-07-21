$(function() {
    $('#header').load('header.html');
});

// --- Oldal aktiválás ---
// Alapból (index.html) az oldalnak aktiváltnak kell lennie ahhoz, hogy a
// keresés működjön. Az index2.html teszt-oldal a betöltés előtt
// window.CCS_ENFORCE_ACTIVATION = false-ra állítja, így ott a keresés mindig
// működik, függetlenül az aktiválási állapottól.
const CCS_ENFORCE_ACTIVATION =
    (typeof window.CCS_ENFORCE_ACTIVATION === "undefined") ? true : !!window.CCS_ENFORCE_ACTIVATION;

let ccsSiteActive = false;

function ccsLang() {
    const el = document.getElementById("langSelectOption");
    return (el && el.value) ? el.value : "hu";
}

// Igaz, ha most szabad keresni: teszt-oldalon mindig, egyébként csak aktív oldalon.
function ccsSearchAllowed() {
    return !CCS_ENFORCE_ACTIVATION || ccsSiteActive;
}

function ccsInactiveMessage() {
    //return ccsLang() === "en"
    //    ? "The search is not active yet."
    //    : "A keresés még nincs aktiválva.";
    return ""
}

// A keresés gombok engedélyezése/tiltása az aktiválási állapot szerint.
function ccsApplyActivationState() {
    if (!CCS_ENFORCE_ACTIVATION) return; // teszt-oldal: mindig engedélyezett

    const btns = [
        document.getElementById("callsignQueryBtn"),
        document.getElementById("callsignQueryBtnQsl"),
    ];
    btns.forEach(function (btn) {
        if (!btn) return;
        btn.disabled = !ccsSiteActive;
        btn.title = ccsSiteActive ? "" : ccsInactiveMessage();
    });

    const diplomaEl = document.getElementById("diploma_result");
    const qslEl = document.getElementById("qsl_result");
    if (!ccsSiteActive) {
        if (diplomaEl) diplomaEl.textContent = ccsInactiveMessage();
        if (qslEl) qslEl.textContent = ccsInactiveMessage();
    } else {
        if (diplomaEl && diplomaEl.dataset.inactive === "1") diplomaEl.textContent = "";
        if (qslEl && qslEl.dataset.inactive === "1") qslEl.textContent = "";
    }
    if (diplomaEl) diplomaEl.dataset.inactive = ccsSiteActive ? "0" : "1";
    if (qslEl) qslEl.dataset.inactive = ccsSiteActive ? "0" : "1";
}

// Induláskor: ha kötelező az aktiválás, addig tiltjuk a gombokat, amíg a
// szerver meg nem erősíti, hogy az oldal aktív.
if (CCS_ENFORCE_ACTIVATION) {
    ccsApplyActivationState(); // azonnal letiltjuk (ccsSiteActive még false)
    fetch(`${PROTO}${HOST}${BACKENDPORT}/api/v1/site_active`)
        .then(resp => resp.json())
        .then(data => { ccsSiteActive = !!data.active; ccsApplyActivationState(); })
        .catch(() => { ccsSiteActive = false; ccsApplyActivationState(); });
}

document.getElementById("callsign").addEventListener("keypress", (e) => {
    if (e.key == "Enter") document.getElementById("callsignQueryBtn").click();
})

document.getElementById("callsign_qsl").addEventListener("keypress", (e) => {
    if (e.key == "Enter") document.getElementById("callsignQueryBtnQsl").click();
})

document.getElementById("callsignQueryBtnQsl").addEventListener("click", (evt) => {
    evt.preventDefault();

    if (!ccsSearchAllowed()) {
        document.getElementById("qsl_result").textContent = ccsInactiveMessage();
        return;
    }

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

    if (!ccsSearchAllowed()) {
        document.getElementById("diploma_result").textContent = ccsInactiveMessage();
        return;
    }

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






