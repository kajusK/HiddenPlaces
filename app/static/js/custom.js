/* Apply dselect handling to corresponding class */
document.querySelectorAll('.dselect').forEach(el => dselect(el))

/**
 * Show android like toast
 *
 * @param text          Text to show in toast
 * @param timeout_ms    Timeout for toast showing
 */
function toast(text, timeout_ms=2000) {
    const el = document.getElementById("toast");
    el.className = "show";
    el.innerHTML = text;
    setTimeout(function(){
        el.className = el.className.replace("show", "");
    }, 3000);
}

/**
 * Copy text to clipboard
 *
 * @param text      Text to be copied to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    toast("Copied to clipboard");
}
