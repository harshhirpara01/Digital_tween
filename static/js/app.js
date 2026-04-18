/* global window, document, localStorage, fetch, atob */
(function () {
  const TOKEN_KEY = 'dt_token';

  function toast(msg, kind) {
    const el = document.getElementById('dt-toast');
    if (!el) return;
    el.textContent = msg;
    el.hidden = false;
    el.classList.remove('dt-toast-ok', 'dt-toast-err');
    el.classList.add(kind === 'ok' ? 'dt-toast-ok' : 'dt-toast-err');
    clearTimeout(el._t);
    el._t = setTimeout(() => { el.hidden = true; }, 4200);
  }

  function parseJwt(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const json = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join(''),
      );
      return JSON.parse(json);
    } catch (e) {
      return null;
    }
  }

  function setToken(t) {
    localStorage.setItem(TOKEN_KEY, t);
    try {
      const p = parseJwt(t);
      if (p && p.id != null) localStorage.setItem('dt_uid', String(p.id));
    } catch (e) { /* ignore */ }
  }

  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('dt_uid');
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getUserId() {
    const raw = localStorage.getItem('dt_uid');
    if (raw) return raw;
    const t = getToken();
    const p = t && parseJwt(t);
    return p && p.id != null ? String(p.id) : null;
  }

  function authHeaders() {
    const t = getToken();
    const h = { 'Content-Type': 'application/json' };
    if (t) h.Authorization = 'Bearer ' + t;
    return h;
  }

  function requireAuth() {
    if (!getToken()) {
      toast('Please login first', 'err');
      window.location.href = '/login';
      return false;
    }
    return true;
  }

  window.DT = {
    toast,
    setToken,
    clearToken,
    getToken,
    getUserId,
    authHeaders,
    requireAuth,
    parseJwt,
  };
})();
