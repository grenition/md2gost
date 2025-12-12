import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
});

export const getShortIdFromURL = () => {
  const path = window.location.pathname;
  const match = path.match(/^\/edit\/([a-z0-9]+)$/);
  return match ? match[1] : null;
};

export const setShortIdInURL = (shortId) => {
  const newPath = `/edit/${shortId}`;
  window.history.replaceState({}, '', newPath);
};

export const getSessionIdByShortId = async (shortId) => {
  try {
    const response = await api.get(`/session/short/${shortId}`);
    return response.data.session_id;
  } catch (err) {
    console.error('Failed to get session by short ID:', err);
    return null;
  }
};

export const getSessionId = async () => {
  // First, try to get short_id from URL path
  let shortId = getShortIdFromURL();
  
  if (shortId) {
    // Try to get session_id by short_id
    const sessionId = await getSessionIdByShortId(shortId);
    if (sessionId) {
      return sessionId;
    }
    // If short_id is invalid, return null (will redirect in component)
    return null;
  }
  
  // No short_id in URL, should not happen in EditorPage
  // This function should only be called when shortId is in URL
  return null;
};

export const getPreview = async (markdown, syntaxHighlighting = true) => {
  const sessionId = await getSessionId();
  if (!sessionId) return null;
  
  const response = await api.post('/preview', {
    markdown,
    syntax_highlighting: syntaxHighlighting,
    session_id: sessionId,
  });
  return response.data.pdf;
};

export const downloadDocx = async (markdown, syntaxHighlighting = true) => {
  const sessionId = await getSessionId();
  if (!sessionId) return;
  
  const response = await api.post(
    '/convert',
    {
      markdown,
      syntax_highlighting: syntaxHighlighting,
      session_id: sessionId,
    },
    {
      responseType: 'blob',
    }
  );

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'document.docx');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const uploadImage = async (file) => {
  const sessionId = await getSessionId();
  if (!sessionId) throw new Error('No session');
  
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/images/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      'X-Session-Id': sessionId
    }
  });
  
  return response.data;
};

export const getSessionData = async (sessionId) => {
  try {
    const response = await api.get(`/session/${sessionId}/data`);
    return response.data.data || {};
  } catch (err) {
    console.error('Failed to load session data:', err);
    return null;
  }
};

export const saveSessionData = async (sessionId, data) => {
  try {
    await api.post(`/session/${sessionId}/data`, { data });
  } catch (err) {
    console.error('Failed to save session data:', err);
  }
};

// Export api for use in other modules
export { api };
