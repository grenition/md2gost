import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
});

export const getPreview = async (markdown, syntaxHighlighting = true) => {
  const response = await api.post('/preview', {
    markdown,
    syntaxHighlighting,
  });
  return response.data.html;
};

export const downloadDocx = async (markdown, syntaxHighlighting = true) => {
  const response = await api.post(
    '/convert',
    {
      markdown,
      syntaxHighlighting,
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

