const PROTO="https://"
const HOST="hg25ccs.hu"
const BACKENDPORT=""


/*const HOST="localhost"
const PROTO="http://"
const BACKENDPORT=":8800"
*/




hideLanguage("en");
showLanguage("hu"); 



window.addEventListener('load', function () {
    let langCookie = document.cookie; 
    console.log("cookie", langCookie)
    if (langCookie == "lang=en") {
        hideLanguage("hu");
        showLanguage("en"); 
        console.log(document.getElementById("langSelectOption").value)
        document.getElementById("langSelectOption").value = "en";
    } else if (langCookie == "lang=hu") {
        hideLanguage("en");
        showLanguage("hu");
        document.getElementById("langSelectOption").value = "hu";
    } else {
        hideLanguage("en");
        showLanguage("hu");
        document.getElementById("langSelectOption").value = "hu";
    }


    document.getElementById("langSelectOption").addEventListener("click", function (evt){
        langSelectorEl = document.getElementById("langSelectOption")
        //console.log("----------" + langSelectorEl.value);
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



