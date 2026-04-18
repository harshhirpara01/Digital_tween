(function () {
  function wire(selectId, otherWrapId, otherInputId, requiredForSubmit) {
    const sel = document.getElementById(selectId);
    const wrap = document.getElementById(otherWrapId);
    const other = document.getElementById(otherInputId);
    if (!sel || !wrap || !other) return;

    function sync() {
      const isOther = sel.value === '__other__';
      wrap.hidden = !isOther;
      other.required = !!requiredForSubmit && isOther;
      if (!isOther) other.value = '';
    }

    sel.addEventListener('change', sync);
    sync();
  }

  function getValue(selectId, otherInputId) {
    const sel = document.getElementById(selectId);
    const other = document.getElementById(otherInputId);
    if (!sel) return '';
    if (sel.value === '__other__') {
      return (other && other.value) ? other.value.trim() : '';
    }
    return sel.value ? sel.value.trim() : '';
  }

  /** Pick matching <option> or switch to Other with custom text */
  function setValue(selectId, otherInputId, professionString) {
    const sel = document.getElementById(selectId);
    const other = document.getElementById(otherInputId);
    if (!sel || !professionString) return;
    const p = String(professionString).trim();
    let matched = false;
    for (let i = 0; i < sel.options.length; i++) {
      const o = sel.options[i];
      if (o.value && o.value !== '__other__' && o.value === p) {
        sel.selectedIndex = i;
        matched = true;
        break;
      }
    }
    if (!matched) {
      sel.value = '__other__';
      if (other) other.value = p;
    }
    sel.dispatchEvent(new Event('change'));
  }

  window.DTProfession = { wire, getValue, setValue };
})();
