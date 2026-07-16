// Az API ugyanazon az origin-en van, mint az oldal: az nginx a /api kéréseket
// a backendre proxyzza. Ezért a címet az oldal saját URL-jéből vesszük, nem
// írjuk be fixen - így domainváltáskor sincs teendő.
const PROTO = window.location.protocol + "//"
const HOST = window.location.host
const BACKENDPORT = ""


/* Lokális fejlesztés külön futó backendhez (nem az nginxen keresztül):
const PROTO="http://"
const HOST="localhost"
const BACKENDPORT=":8800"
*/




hideLanguage("en");
showLanguage("hu"); 



window.addEventListener('load', function () {
    // A nyelvválasztó csak a header.html-t használó oldalakon létezik; az
    // admin.html-en (admin_header.html) nincs. Ezért mindenhol null-ra
    // ellenőrizzük: enélkül itt kivétel szállna el, és a handler további
    // része le sem futna.
    const langSelectorEl = document.getElementById("langSelectOption");

    let langCookie = document.cookie;
    console.log("cookie", langCookie)
    if (langCookie == "lang=en") {
        hideLanguage("hu");
        showLanguage("en");
        if (langSelectorEl) langSelectorEl.value = "en";
    } else if (langCookie == "lang=hu") {
        hideLanguage("en");
        showLanguage("hu");
        if (langSelectorEl) langSelectorEl.value = "hu";
    } else {
        hideLanguage("en");
        showLanguage("hu");
        if (langSelectorEl) langSelectorEl.value = "hu";
    }


    if (langSelectorEl) {
        langSelectorEl.addEventListener("click", function (evt){
            if (langSelectorEl.value == "hu") {
                hideLanguage("en");
                showLanguage("hu");
                document.cookie = "lang=hu";
            } else if (langSelectorEl.value == "en") {
                hideLanguage("hu");
                showLanguage("en");
                document.cookie = "lang=en";
            } else {
                hideLanguage("en");
                showLanguage("hu");
            }
        })
    }


})





//function changeLanguage(event) {   }



function hideLanguage(langCode) {
    var divsToHide = document.getElementsByClassName(langCode);
    for(var i = 0; i < divsToHide.length; i++) {
        divsToHide[i].style.display = "none";
    }
}
function showLanguage(langCode) {
    var divsToHide = document.getElementsByClassName(langCode);
    for(var i = 0; i < divsToHide.length; i++) {
        divsToHide[i].style.display = "inline";
    }
}



