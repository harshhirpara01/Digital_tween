/* global document, window */
(function () {
  const mouthTalkingClass = 'buddy-talking';

  function fmtLine(s) {
    return s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  }

  function say(lines) {
    const el = document.getElementById('buddyText');
    const buddy = document.getElementById('buddy');
    const mouth = document.getElementById('buddyMouth');
    if (!el || !buddy) return;

    const flat = Array.isArray(lines) ? lines.join(' ') : String(lines);
    el.innerHTML = '';
    buddy.classList.add(mouthTalkingClass);
    if (mouth) mouth.classList.add('buddy-mouth-active');

    let i = 0;
    const full = flat;
    const tick = () => {
      i += 1;
      const chunk = full.slice(0, i);
      el.innerHTML = fmtLine(chunk);
      if (i < full.length) {
        window.requestAnimationFrame(() => setTimeout(tick, 18 + Math.random() * 14));
      } else {
        setTimeout(() => {
          buddy.classList.remove(mouthTalkingClass);
          if (mouth) mouth.classList.remove('buddy-mouth-active');
        }, 600);
      }
    };
    tick();
  }

  window.Buddy = { say, fmtLine };
})();
