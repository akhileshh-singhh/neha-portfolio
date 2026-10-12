/* Scale an iframe (rendered at `baseW` px wide) down to the width of its container. */
window.cmsFit = function (frame, scaleBox, baseW) {
  try {
    var doc = frame.contentDocument; if (!doc || !doc.documentElement) return;
    var mn = doc.querySelector('main.g'), h = Math.max(mn ? mn.offsetHeight : doc.documentElement.scrollHeight, 40);
    var w = scaleBox.parentElement.clientWidth || 400, s = w / baseW;
    frame.style.width = baseW + 'px'; frame.style.height = h + 'px';
    frame.style.transform = 'scale(' + s + ')'; frame.style.transformOrigin = '0 0';
    scaleBox.style.height = Math.ceil(h * s) + 'px'; scaleBox.style.width = w + 'px';
  } catch (e) {}
};
