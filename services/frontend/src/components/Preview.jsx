import React, { useEffect, useState } from 'react';
import { getPreview } from '../services/api';
import './Preview.css';

function Preview({ markdown, syntaxHighlighting, isLoading: externalLoading, onLoaded }) {
  const [html, setHtml] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!markdown.trim()) {
      setHtml('<div class="empty-state">Start typing to see DOCX preview...</div>');
      setError(null);
      return;
    }

    let timeoutId;
    const fetchPreview = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const previewHtml = await getPreview(markdown, syntaxHighlighting);
        setHtml(previewHtml);
        onLoaded();
      } catch (err) {
        setError(err.message);
        onLoaded();
      } finally {
        setIsLoading(false);
      }
    };

    timeoutId = setTimeout(fetchPreview, 1000);

    return () => clearTimeout(timeoutId);
  }, [markdown, syntaxHighlighting, onLoaded]);

  const showLoading = isLoading || externalLoading;

  return (
    <div className="preview-panel">
      <div className="panel-header">
        <span>DOCX Preview</span>
      </div>
      <div className="panel-content">
        {showLoading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Generating preview...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <p>Error generating preview: {error}</p>
          </div>
        ) : (
          <div
            className="preview-content"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        )}
      </div>
    </div>
  );
}

export default Preview;
