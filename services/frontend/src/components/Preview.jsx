import React, { useEffect, useState, useRef } from 'react';
import { getPreview } from '../services/api';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import './Preview.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function Preview({ markdown, syntaxHighlighting, isLoading: externalLoading, onLoaded }) {
  const [pdfData, setPdfData] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scale, setScale] = useState(1.5);
  const containerRef = useRef(null);
  const scrollPositionRef = useRef(0);

  useEffect(() => {
    if (!markdown.trim()) {
      setPdfData(null);
      setNumPages(null);
      setError(null);
      return;
    }

    let timeoutId;
    const fetchPreview = async () => {
      if (containerRef.current) {
        scrollPositionRef.current = containerRef.current.scrollTop;
      }

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

  useEffect(() => {
    const updateScale = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth - 40;
        const pdfWidth = 595;
        const newScale = Math.min(containerWidth / pdfWidth, 1.5);
        setScale(newScale);
      }
    };

    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, [pdfData]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    
    const savedScroll = scrollPositionRef.current;
    if (containerRef.current && savedScroll > 0) {
      setTimeout(() => {
        if (containerRef.current) {
          containerRef.current.scrollTop = savedScroll;
        }
      }, 100);
    }
  };

  const onDocumentLoadError = (error) => {
    setError(`Failed to load PDF: ${error.message}`);
  };

  const showLoading = (isLoading || externalLoading) && !pdfData;

  const pdfUrl = pdfData ? `data:application/pdf;base64,${pdfData}` : null;

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
          <div 
            ref={containerRef}
            className="pdf-container"
          >
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={null}
            >
              {Array.from(new Array(numPages), (el, index) => (
                <Page
                  key={`page_${index + 1}`}
                  pageNumber={index + 1}
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                  scale={scale}
                  className="pdf-page"
                />
              ))}
            </Document>
          </div>
        )}
      </div>
    </div>
  );
}

export default Preview;
