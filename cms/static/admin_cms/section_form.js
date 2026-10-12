/* Content-block editor: shows only the fields the chosen block type uses, renames them to what they
   look like on the website, explains where they appear, and live-previews design changes. */
document.addEventListener('DOMContentLoaded', function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var kindSel = $('#id_kind'); if (!kindSel) return;
  var UI = JSON.parse($('#kind-ui').textContent);
  var CF = JSON.parse($('#content-fields').textContent);
  var IF = JSON.parse($('#item-fields').textContent);
  var SL = JSON.parse($('#slot-labels').textContent);

  /* ---------- guide box under the "type" dropdown ---------- */
  var guide = document.createElement('div'); guide.id = 'kind-guide';
  kindSel.closest('.form-row').insertAdjacentElement('afterend', guide);

  function box(name, root) {           // the element holding one field (label + input + help)
    var r = root || document;
    return $('.fieldBox.field-' + name, r) || $('.form-row.field-' + name, r);
  }
  function setHint(el, text) {
    var h = $('.help', el);
    if (!h) { h = document.createElement('div'); h.className = 'help'; el.appendChild(h); }
    h.textContent = text || ''; h.style.display = text ? '' : 'none';
  }
  function setLabel(el, text) { var l = $('label', el); if (l) l.textContent = text + ':'; }
  function rowHidden(row) {
    var boxes = $$('.fieldBox', row);
    return boxes.length ? boxes.every(function (b) { return b.style.display === 'none'; }) : row.style.display === 'none';
  }

  /* ---------- content fields ---------- */
  function applyContent() {
    var cfg = UI[kindSel.value] || { fields: {} };
    var fields = cfg.fields || {};
    CF.forEach(function (name) {
      var el = box(name); if (!el) return;
      var spec = fields[name];
      el.style.display = spec ? '' : 'none';
      if (spec) { setLabel(el, spec.label); setHint(el, spec.hint); }
    });
    // alt text rides along with the image when it has no spec of its own
    var alt = box('image_alt'); if (alt && fields.image && !fields.image_alt) alt.style.display = '';
    if (alt && fields.image && !fields.image_alt) { setLabel(alt, 'Photo description'); setHint(alt, 'Read aloud by screen readers and used by Google.'); }

    // rows / fieldsets that ended up empty
    $$('fieldset.module').forEach(function (fs) {
      var rows = $$('.form-row', fs);
      if (!rows.length || fs.classList.contains('keep')) return;
      var isContent = rows.some(function (r) { return CF.some(function (n) { return r.classList.contains('field-' + n); }); });
      if (!isContent) return;
      rows.forEach(function (r) { r.style.display = rowHidden(r) ? 'none' : ''; });
      fs.style.display = rows.every(function (r) { return r.style.display === 'none'; }) ? 'none' : '';
    });

    // layout: a friendly dropdown instead of a free-text box
    var old = $('#cms_layout_sel'); if (old) old.remove();
    var li = $('#id_layout');
    if (li && cfg.layouts) {
      li.style.display = 'none';
      var sel = document.createElement('select'); sel.id = 'cms_layout_sel';
      cfg.layouts.forEach(function (o) { var op = document.createElement('option'); op.value = o[0]; op.textContent = o[1]; sel.appendChild(op); });
      if (!cfg.layouts.some(function (o) { return o[0] === li.value; })) li.value = cfg.layouts[0][0];
      sel.value = li.value;
      sel.onchange = function () { li.value = sel.value; };
      li.insertAdjacentElement('afterend', sel);
    } else if (li) { li.style.display = ''; }

    // guide
    var text = '<span class="g-ico">' + (cfg.icon || '▫️') + '</span><div><b>' + (cfg.name || '') + '</b> — ' + (cfg.where || '') +
      (cfg.note ? '<br><em>' + cfg.note + '</em>' : '') + '</div>';
    guide.innerHTML = text; guide.style.display = cfg.where ? 'flex' : 'none';
  }

  /* ---------- items (repeating rows / photos / tiles …) ---------- */
  function applyItems() {
    var cfg = (UI[kindSel.value] || {}).items;
    var group = $('#items-group') || $('.inline-group');
    if (!group) return;
    var head = $('h2', group);
    var note = $('.cms-items-note', group);
    if (!note) { note = document.createElement('p'); note.className = 'cms-items-note'; head.insertAdjacentElement('afterend', note); }
    if (!cfg) {
      group.classList.add('no-items');
      note.textContent = 'This type of block has no repeating items. Everything is in the fields above.';
      $$('.inline-related', group).forEach(function (r) { r.style.display = 'none'; });
      var add = $('.add-row', group); if (add) add.style.display = 'none';
      if (head) head.textContent = 'Items';
      return;
    }
    group.classList.remove('no-items');
    var add2 = $('.add-row', group); if (add2) add2.style.display = '';
    if (head) head.textContent = cfg.label;
    note.textContent = cfg.hint || '';
    $$('.inline-related', group).forEach(function (r) { r.style.display = ''; applyItem(r, cfg); });
  }
  function applyItem(row, cfg) {
    var fields = cfg.fields || {};
    IF.forEach(function (name) {
      if (name === 'slot') return;
      var el = box(name, row); if (!el) return;
      var spec = fields[name]; el.style.display = spec ? '' : 'none';
      if (spec) { setLabel(el, spec.label); setHint(el, spec.hint); }
    });
    // slot dropdown: only the choices that make sense for this block
    var slotEl = box('slot', row), sel = slotEl && $('select', slotEl);
    if (sel) {
      if (!sel._all) sel._all = $$('option', sel).map(function (o) { return [o.value, o.textContent]; });
      var allowed = cfg.slots || (cfg.default_slot ? [cfg.default_slot] : []);
      if (allowed.length > 1) {
        var cur = sel.value; sel.innerHTML = '';
        allowed.forEach(function (v) { var o = document.createElement('option'); o.value = v; o.textContent = (SL[v] || v); sel.appendChild(o); });
        sel.value = allowed.indexOf(cur) >= 0 ? cur : allowed[0];
        slotEl.style.display = ''; setLabel(slotEl, 'Where it goes'); setHint(slotEl, 'Which part of the block this item belongs to.');
      } else {
        var v = allowed[0] || '';
        sel.innerHTML = ''; var o = document.createElement('option'); o.value = v; o.textContent = SL[v] || 'Normal item'; sel.appendChild(o); sel.value = v;
        slotEl.style.display = 'none';
      }
    }
    // hide rows whose boxes are all hidden
    $$('.form-row', row).forEach(function (r) { r.style.display = rowHidden(r) ? 'none' : ''; });
  }

  function applyAll() { applyContent(); applyItems(); }
  kindSel.addEventListener('change', applyAll);
  document.addEventListener('formset:added', function () { setTimeout(applyItems, 0); });
  applyAll();

  /* ---------- live preview of this block ---------- */
  var pv = $('#blockPreview'); if (!pv) return;
  var frame = $('iframe', pv), scale = $('.pv-scale', pv); if (!frame) return;
  var domId = pv.dataset.domId, orig = '';
  function fit() { window.cmsFit(frame, scale, 1120); }
  var live = [
    ['id_bg_color', 'backgroundColor'], ['id_text_color', 'color'], ['id_bg_gradient', 'backgroundImage'],
    ['id_padding_top', 'paddingTop', 'px'], ['id_padding_bottom', 'paddingBottom', 'px'], ['id_min_height', 'minHeight', 'px'],
    ['id_align', 'textAlign'], ['id_font_family', 'fontFamily'], ['id_accent_color', '--sec-accent']
  ];
  function applyLive() {
    var doc = frame.contentDocument; if (!doc) return;
    var el = doc.getElementById(domId); if (!el) return;
    el.setAttribute('style', orig);
    live.forEach(function (x) {
      var inp = document.getElementById(x[0]); if (!inp || !inp.value.trim()) return;
      var v = inp.value.trim() + (x[2] || '');
      if (x[1].indexOf('--') === 0) el.style.setProperty(x[1], v); else el.style[x[1]] = v;
    });
    fit();
  }
  frame.addEventListener('load', function () {
    var el = frame.contentDocument.getElementById(domId);
    orig = el ? (el.getAttribute('style') || '') : '';
    fit(); setTimeout(fit, 400); setTimeout(fit, 1200);
  });
  live.forEach(function (x) { var inp = document.getElementById(x[0]); if (inp) ['input', 'change'].forEach(function (ev) { inp.addEventListener(ev, applyLive); }); });
  window.addEventListener('resize', fit);
  $('[data-act=reload]', pv).onclick = function () { frame.contentWindow.location.reload(); };
  $('[data-act=size]', pv).onclick = function (e) { pv.classList.toggle('big'); e.target.textContent = pv.classList.contains('big') ? '⤡ Smaller' : '⤢ Bigger'; setTimeout(fit, 60); };
});
