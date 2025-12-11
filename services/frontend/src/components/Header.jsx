import React from 'react';
import { downloadDocx } from '../services/api';
import './Header.css';

function Header({ syntaxHighlighting, onSyntaxHighlightingChange, markdown }) {
  const [isDownloading, setIsDownloading] = React.useState(false);
  const [toast, setToast] = React.useState(null);

  const showToast = (message, isError = false) => {
    setToast({ message, isError });
    setTimeout(() => setToast(null), 3000);
  };

  const handleDownload = async () => {
    if (!markdown.trim()) {
      showToast('Document is empty', true);
      return;
    }

    setIsDownloading(true);
    try {
      await downloadDocx(markdown, syntaxHighlighting);
      showToast('Document downloaded successfully');
    } catch (error) {
      showToast(error.message, true);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <>
      <div className="header">
        <h1>MD2GOST</h1>
        <p className="header-subtitle">Markdown to DOCX Converter</p>
        <div className="header-actions">
          <label className="checkbox-container">
            <input
              type="checkbox"
              checked={syntaxHighlighting}
              onChange={(e) => onSyntaxHighlightingChange(e.target.checked)}
            />
            <span>Syntax Highlighting</span>
          </label>
          <button
            className="btn btn-primary"
            onClick={handleDownload}
            disabled={isDownloading}
          >
            {isDownloading ? 'Downloading...' : 'Download DOCX'}
          </button>
        </div>
      </div>
      {toast && (
        <div className={`toast ${toast.isError ? 'error' : ''}`}>
          {toast.message}
        </div>
      )}
    </>
  );
}

export default Header;
