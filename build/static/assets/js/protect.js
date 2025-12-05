// -----------------------------
// Disable Right-Click
// -----------------------------
document.addEventListener("contextmenu", event => event.preventDefault());

// -----------------------------
// Disable Copy, Cut, Paste
// -----------------------------
document.addEventListener('copy', e => e.preventDefault());
document.addEventListener('cut', e => e.preventDefault());
document.addEventListener('paste', e => e.preventDefault());

// -----------------------------
// Disable Developer Shortcuts
// -----------------------------
document.onkeydown = function(e) {
    // F12
    if (e.keyCode === 123) return false;

    // Ctrl+Shift+I (Inspect)
    if (e.ctrlKey && e.shiftKey && e.keyCode === 73) return false;

    // Ctrl+U (View Source)
    if (e.ctrlKey && e.keyCode === 85) return false;

    // Ctrl+S (Save Page)
    if (e.ctrlKey && e.keyCode === 83) return false;

    // Ctrl+C (Copy)
    if (e.ctrlKey && e.keyCode === 67) return false;
};

// -----------------------------
// Disable Text Selection
// -----------------------------
document.addEventListener('selectstart', e => e.preventDefault());

// -----------------------------
// Disable Image Dragging
// -----------------------------
const images = document.querySelectorAll('img');
images.forEach(img => img.setAttribute('draggable', 'false'));
