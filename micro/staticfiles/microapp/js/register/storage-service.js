(function() {
  const DEFAULT_THRESHOLD_BYTES = 256 * 1024; // 256KB
  const POINTER_FLAG = '__remote';

  function getCsrfToken() {
    const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenElement) return tokenElement.value;
    const name = 'csrftoken=';
    const cookies = document.cookie.split(';');
    for (const c of cookies) {
      const v = c.trim();
      if (v.startsWith(name)) return decodeURIComponent(v.substring(name.length));
    }
    return null;
  }

  async function apiRequest(url, method = 'GET', data = null) {
    const headers = { 'Accept': 'application/json' };
    const token = getCsrfToken();
    if (token) headers['X-CSRFToken'] = token;
    if (data !== null) headers['Content-Type'] = 'application/json';
    const resp = await fetch(url, { method, headers, body: data !== null ? JSON.stringify(data) : null });
    const ct = resp.headers.get('content-type');
    if (ct && ct.includes('application/json')) {
      const json = await resp.json();
      if (!resp.ok || json.status === 'error') {
        const msg = json.message || 'Request failed';
        throw new Error(msg);
      }
      return json;
    }
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.text();
  }

  function tryParse(jsonText) {
    try { return JSON.parse(jsonText); } catch { return null; }
  }

  function isPointer(val) {
    return val && typeof val === 'object' && val[POINTER_FLAG] === true && val.key && val.projectId;
  }

  function toPointer(projectId, key) {
    return { [POINTER_FLAG]: true, projectId, key, savedAt: Date.now() };
  }

  function byteLengthOf(obj) {
    try { return new Blob([JSON.stringify(obj)]).size; } catch { return 0; }
  }

  const RegisterStorage = {
    thresholdBytes: DEFAULT_THRESHOLD_BYTES,

    setThreshold(bytes) { this.thresholdBytes = bytes; },

    // Save JSON value for a key, auto-remote if too large
    async saveKey(projectId, key, value) {
      const size = byteLengthOf(value);
      if (size > this.thresholdBytes) {
        await apiRequest(`/api/register/${projectId}/state/${encodeURIComponent(key)}/save/`, 'POST', value);
        localStorage.setItem(key, JSON.stringify(toPointer(projectId, key)));
        return { stored: 'remote', size };
      } else {
        localStorage.setItem(key, JSON.stringify(value));
        return { stored: 'local', size };
      }
    },

    // Force save to remote regardless of size
    async saveKeyRemote(projectId, key, value) {
      await apiRequest(`/api/register/${projectId}/state/${encodeURIComponent(key)}/save/`, 'POST', value);
      localStorage.setItem(key, JSON.stringify(toPointer(projectId, key)));
      return { stored: 'remote', size: byteLengthOf(value) };
    },

    // Load JSON for a key; resolves pointer automatically
    async loadKey(projectId, key) {
      const raw = localStorage.getItem(key);
      const parsed = tryParse(raw);
      if (isPointer(parsed)) {
        const pid = parsed.projectId || projectId;
        const res = await apiRequest(`/api/register/${pid}/state/${encodeURIComponent(key)}/`, 'GET');
        return res.data;
      }
      return parsed;
    },

    // Remove both local and remote
    async removeKey(projectId, key) {
      const raw = localStorage.getItem(key);
      const parsed = tryParse(raw);
      localStorage.removeItem(key);
      if (isPointer(parsed)) {
        try { await apiRequest(`/api/register/${projectId}/state/${encodeURIComponent(key)}/delete/`, 'DELETE'); } catch (e) { /* ignore */ }
      }
      return true;
    },

    // Ensure heavy keys are remote; if local and large, push to remote
    async ensureRemote(projectId, key) {
      const raw = localStorage.getItem(key);
      const parsed = tryParse(raw);
      if (isPointer(parsed)) return 'remote';
      if (!parsed) return 'missing';
      if (byteLengthOf(parsed) <= this.thresholdBytes) return 'local';
      await this.saveKeyRemote(projectId, key, parsed);
      return 'remote';
    }
  };

  window.RegisterStorage = RegisterStorage;
})(); 