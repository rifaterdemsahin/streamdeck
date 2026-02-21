/**
 * Self-Learner Checklist Widget
 * Adds a "I've learned this" checkbox to the bottom-right of every page.
 * When checked, saves state to localStorage and shows a "remembered" banner instead.
 * Include this script before </body> on any page: <script src="learner-checklist.js"></script>
 */
(function () {
    'use strict';

    // Derive a unique key from the page filename
    var path = window.location.pathname;
    var pageKey = 'learner_' + path.split('/').pop().replace(/\.html?$/, '');

    // Inject CSS
    var style = document.createElement('style');
    style.textContent = [
        '/* Learner Checklist Widget */',
        '.learner-widget{position:fixed;bottom:20px;right:20px;z-index:9999;font-family:"Segoe UI",Tahoma,Geneva,Verdana,sans-serif;transition:all .3s ease}',
        '.learner-checkbox-wrap{background:rgba(0,0,0,.75);backdrop-filter:blur(8px);border:2px solid rgba(255,215,0,.4);border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:10px;cursor:pointer;transition:all .3s;box-shadow:0 4px 20px rgba(0,0,0,.4)}',
        '.learner-checkbox-wrap:hover{border-color:#ffd700;transform:translateY(-2px);box-shadow:0 6px 25px rgba(255,215,0,.2)}',
        '.learner-checkbox-wrap input[type=checkbox]{width:20px;height:20px;accent-color:#ffd700;cursor:pointer;flex-shrink:0}',
        '.learner-checkbox-wrap label{color:#fff;font-size:.95em;cursor:pointer;user-select:none}',
        '.learner-remembered-banner{background:linear-gradient(135deg,rgba(76,175,80,.2),rgba(76,175,80,.1));border:2px solid rgba(76,175,80,.5);border-radius:12px;padding:12px 18px;display:flex;align-items:center;gap:10px;box-shadow:0 4px 20px rgba(0,0,0,.3);animation:learnerFadeIn .5s ease}',
        '.learner-remembered-banner .learner-icon{font-size:1.4em}',
        '.learner-remembered-banner .learner-text{color:rgba(255,255,255,.85);font-size:.9em}',
        '.learner-remembered-banner .learner-undo{background:none;border:1px solid rgba(255,255,255,.3);color:rgba(255,255,255,.7);padding:4px 10px;border-radius:6px;cursor:pointer;font-size:.8em;transition:all .2s;margin-left:6px}',
        '.learner-remembered-banner .learner-undo:hover{border-color:#ffd700;color:#ffd700}',
        '.learner-page-dimmed .container,.learner-page-dimmed .coming-soon{opacity:.75;transition:opacity .3s}',
        '.learner-top-banner{position:fixed;top:0;left:0;right:0;z-index:9998;background:linear-gradient(90deg,rgba(76,175,80,.9),rgba(56,142,60,.9));color:#fff;text-align:center;padding:8px 15px;font-size:.9em;font-family:"Segoe UI",Tahoma,Geneva,Verdana,sans-serif;box-shadow:0 2px 10px rgba(0,0,0,.3);animation:learnerSlideDown .4s ease}',
        '.learner-top-banner a{color:#ffd700;margin-left:10px;cursor:pointer;text-decoration:underline;font-size:.85em}',
        '@keyframes learnerFadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}',
        '@keyframes learnerSlideDown{from{transform:translateY(-100%)}to{transform:translateY(0)}}'
    ].join('\n');
    document.head.appendChild(style);

    // Check stored state
    var isRemembered = localStorage.getItem(pageKey) === 'true';

    // Build widget
    var widget = document.createElement('div');
    widget.className = 'learner-widget';

    function renderCheckbox() {
        widget.innerHTML = '';
        var wrap = document.createElement('div');
        wrap.className = 'learner-checkbox-wrap';

        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.id = 'learner-cb';

        var lbl = document.createElement('label');
        lbl.htmlFor = 'learner-cb';
        lbl.textContent = '📝 I\'ve learned this';

        wrap.appendChild(cb);
        wrap.appendChild(lbl);
        widget.appendChild(wrap);

        cb.addEventListener('change', function () {
            if (cb.checked) {
                localStorage.setItem(pageKey, 'true');
                renderRemembered();
                showTopBanner();
                dimPage();
            }
        });
    }

    function renderRemembered() {
        widget.innerHTML = '';
        var banner = document.createElement('div');
        banner.className = 'learner-remembered-banner';

        var icon = document.createElement('span');
        icon.className = 'learner-icon';
        icon.textContent = '✅';

        var text = document.createElement('span');
        text.className = 'learner-text';
        text.textContent = 'Page remembered';

        var undo = document.createElement('button');
        undo.className = 'learner-undo';
        undo.textContent = '↩ Review again';
        undo.addEventListener('click', function () {
            localStorage.removeItem(pageKey);
            removeTopBanner();
            undimPage();
            renderCheckbox();
        });

        banner.appendChild(icon);
        banner.appendChild(text);
        banner.appendChild(undo);
        widget.appendChild(banner);
    }

    function showTopBanner() {
        if (document.getElementById('learner-top-banner')) return;
        var tb = document.createElement('div');
        tb.className = 'learner-top-banner';
        tb.id = 'learner-top-banner';
        tb.innerHTML = '✅ This page is remembered — you\'ve already learned this content!<a id="learner-top-undo">Review again</a>';
        document.body.appendChild(tb);
        document.getElementById('learner-top-undo').addEventListener('click', function () {
            localStorage.removeItem(pageKey);
            removeTopBanner();
            undimPage();
            renderCheckbox();
        });
    }

    function removeTopBanner() {
        var tb = document.getElementById('learner-top-banner');
        if (tb) tb.remove();
    }

    function dimPage() {
        document.body.classList.add('learner-page-dimmed');
    }

    function undimPage() {
        document.body.classList.remove('learner-page-dimmed');
    }

    // Initial render
    if (isRemembered) {
        renderRemembered();
        showTopBanner();
        dimPage();
    } else {
        renderCheckbox();
    }

    document.body.appendChild(widget);
})();
