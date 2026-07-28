// Saját, süti-mentes látogatószámláló kliens oldala.
//
// Egyetlen dolgot csinál: oldalbetöltéskor elküld egy "hit" jelzést a
// backendnek a jelenlegi oldalról, a képernyőfelbontásról és az ablakméretről.
// Sütit / localStorage-t NEM használ, ezért nincs szükség cookie-bannerre.
// A böngészőt, az operációs rendszert és az országot a backend állapítja meg
// (User-Agent, illetve IP alapján), itt azokat nem küldjük.
//
// Az API címét ugyanúgy az oldal saját URL-jéből vesszük, mint a common.js.

(function () {
    // Az admin/statisztika oldalakat ne számoljuk (azok nem "látogatók").
    var path = window.location.pathname;
    if (/(admin|statistics|db_admin)\.html$/i.test(path)) {
        return;
    }

    // API-alap: elsődlegesen a common.js-ben definiált konstansokból, de ha
    // az analytics.js önmagában töltődne be, legyen tartalék is.
    var proto = (typeof PROTO !== "undefined") ? PROTO : (window.location.protocol + "//");
    var host = (typeof HOST !== "undefined") ? HOST : window.location.host;
    var port = (typeof BACKENDPORT !== "undefined") ? BACKENDPORT : "";
    var url = proto + host + port + "/api/v1/hit";

    var payload = {
        path: path,
        referrer: document.referrer || "",
        screen_w: window.screen ? window.screen.width : null,
        screen_h: window.screen ? window.screen.height : null,
        viewport_w: window.innerWidth || null,
        viewport_h: window.innerHeight || null,
        device_pixel_ratio: window.devicePixelRatio ? String(window.devicePixelRatio) : null
    };

    // Nem blokkoló, hibát elnyelő küldés. A fetch keepalive-val az oldalzárás
    // sem szakítja meg. (sendBeacon nem jó: az text/plain-t küld, itt JSON kell.)
    try {
        fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            keepalive: true
        }).catch(function () { /* csend: a statisztika sosem zavarja a látogatót */ });
    } catch (e) {
        /* ignore */
    }
})();
