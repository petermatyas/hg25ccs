// Saját, süti-mentes látogatószámláló kliens oldala.
//
// Oldalbetöltéskor küld egy "hit" jelzést (útvonal, felbontás, nyelv, időzóna,
// kapcsolat típusa, stb.), majd kilépéskor egy frissítést az oldalon töltött
// időről, a görgetési mélységről és a betöltési időről. A fontos kattintásokat
// (keresés, letöltés) külön eseményként rögzíti.
//
// Sütit / localStorage-t NEM használ, ezért nincs szükség cookie-bannerre.
// A böngészőt, OS-t, eszköztípust és országot a backend állapítja meg.

(function () {
    // Az admin/statisztika oldalakat ne számoljuk (azok nem "látogatók").
    var path = window.location.pathname;
    if (/(admin|statistics|db_admin)\.html$/i.test(path)) {
        return;
    }

    // API-alap: elsődlegesen a common.js-ben definiált konstansokból, tartalékkal.
    var proto = (typeof PROTO !== "undefined") ? PROTO : (window.location.protocol + "//");
    var host = (typeof HOST !== "undefined") ? HOST : window.location.host;
    var port = (typeof BACKENDPORT !== "undefined") ? BACKENDPORT : "";
    var base = proto + host + port;

    // --- Kliens-oldali jelzések ---
    function connectionType() {
        var c = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        return (c && c.effectiveType) ? c.effectiveType : null;
    }
    function timezone() {
        try { return Intl.DateTimeFormat().resolvedOptions().timeZone || null; }
        catch (e) { return null; }
    }

    var payload = {
        path: path,
        referrer: document.referrer || "",
        screen_w: window.screen ? window.screen.width : null,
        screen_h: window.screen ? window.screen.height : null,
        viewport_w: window.innerWidth || null,
        viewport_h: window.innerHeight || null,
        device_pixel_ratio: window.devicePixelRatio ? String(window.devicePixelRatio) : null,
        language: navigator.language || null,
        timezone: timezone(),
        connection_type: connectionType()
    };

    var visitId = null;
    var startTime = Date.now();
    var maxScroll = 0;

    function post(url, data, useBeacon) {
        // Kilépéskor a sendBeacon a legmegbízhatóbb; egyébként fetch keepalive.
        try {
            if (useBeacon && navigator.sendBeacon) {
                var blob = new Blob([JSON.stringify(data)], { type: "application/json" });
                navigator.sendBeacon(url, blob);
                return;
            }
            fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
                keepalive: true
            }).catch(function () {});
        } catch (e) { /* csend */ }
    }

    // 1) Oldalbetöltés rögzítése; a válaszból megjegyezzük a visit id-t.
    try {
        fetch(base + "/api/v1/hit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            keepalive: true
        })
        .then(function (r) { return r.json(); })
        .then(function (d) { if (d && d.id) visitId = d.id; })
        .catch(function () {});
    } catch (e) { /* csend */ }

    // 2) Görgetési mélység követése (max %).
    function trackScroll() {
        var doc = document.documentElement;
        var scrollable = (doc.scrollHeight - window.innerHeight);
        var pct = scrollable > 0
            ? Math.round((window.scrollY || doc.scrollTop || 0) / scrollable * 100)
            : 100;
        if (pct > maxScroll) maxScroll = Math.min(100, Math.max(0, pct));
    }
    window.addEventListener("scroll", trackScroll, { passive: true });
    trackScroll();

    // 3) Kilépéskor: idő az oldalon + görgetés + betöltési idő frissítése.
    var sent = false;
    function sendUpdate() {
        if (sent || !visitId) return;
        sent = true;
        var loadMs = null;
        try {
            var nav = performance.getEntriesByType("navigation")[0];
            if (nav && nav.loadEventEnd) loadMs = Math.round(nav.loadEventEnd);
            else if (performance.timing && performance.timing.loadEventEnd) {
                loadMs = performance.timing.loadEventEnd - performance.timing.navigationStart;
            }
        } catch (e) {}
        post(base + "/api/v1/hit_update", {
            visit_id: visitId,
            time_on_page_ms: Date.now() - startTime,
            scroll_depth: maxScroll,
            load_time_ms: loadMs
        }, true);
    }
    // A visibilitychange (hidden) a legmegbízhatóbb mobilon is; a pagehide tartalék.
    document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === "hidden") sendUpdate();
    });
    window.addEventListener("pagehide", sendUpdate);

    // 4) Kattintás-események: keresés gombok és letöltés linkek.
    function eventLabelFor(target) {
        if (!target || !target.closest) return null;
        if (target.closest("#callsignQueryBtn")) return "diploma_search";
        if (target.closest("#callsignQueryBtnQsl")) return "qsl_search";
        var a = target.closest("a[href]");
        if (a) {
            var href = a.getAttribute("href") || "";
            if (href.indexOf("/download_diploma") !== -1) return "diploma_download";
            if (href.indexOf("/download_qsl") !== -1) return "qsl_download";
        }
        return null;
    }
    document.addEventListener("click", function (evt) {
        var label = eventLabelFor(evt.target);
        if (label) {
            post(base + "/api/v1/event", { path: path, event: label }, false);
        }
    });
})();
