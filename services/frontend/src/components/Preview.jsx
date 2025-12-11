import React, { useEffect, useState } from 'react';
import { getPreview } from '../services/api';
import './Preview.css';

function Preview({ markdown, syntaxHighlighting, isLoading: externalLoading, onLoaded }) {
  const [pdfData, setPdfData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!markdown.trim()) {
      setPdfData(null);
      setError(null);
      return;
    }

    let timeoutId;
    const fetchPreview = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const pdfBase64 = await getPreview(markdown, syntaxHighlighting);
        setPdfData(pdfBase64);
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
  const pdfUrl = pdfData ? `data:application/pdf;base64,${pdfData}#toolbar=0&navpanes=0&scrollbar=0&view=FitH` : null;

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
        ) : !pdfUrl ? (
          <div className="empty-state">
            <p>Start typing to see DOCX preview...</p>
          </div>
        ) : (
          <iframe
            src={pdfUrl}
            className="preview-iframe"
            title="DOCX Preview"
          />
        )}
      </div>
    </div>
  );
}

export default Preview;
