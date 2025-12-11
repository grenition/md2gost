import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
});

export const getSessionId = () => {
  let sessionId = localStorage.getItem('md2gost_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('md2gost_session_id', sessionId);
  }
  return sessionId;
};

const generateSessionId = () => {
  return 'session_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 9);
};

export const getPreview = async (markdown, syntaxHighlighting = true) => {
  const sessionId = getSessionId();
  const response = await api.post('/preview', {
    markdown,
    syntaxHighlighting,
    sessionId,
  });
  return response.data.pdf;
};

export const downloadDocx = async (markdown, syntaxHighlighting = true) => {
  const sessionId = getSessionId();
  const response = await api.post(
    '/convert',
    {
      markdown,
      syntaxHighlighting,
      sessionId,
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
  const sessionId = getSessionId();
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

