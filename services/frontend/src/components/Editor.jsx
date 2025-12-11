import React, { useRef, useEffect, useCallback } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import { EditorView } from '@codemirror/view';
import { uploadImage } from '../services/api';
import './Editor.css';

function Editor({ value, onChange, syntaxHighlighting, sessionId }) {
  const editorRef = useRef(null);
  const containerRef = useRef(null);
  
  const insertImageMarkdown = useCallback(async (file) => {
    try {
      const result = await uploadImage(file);
      const markdownText = `![${result.filename}](${result.filename} "Placeholder")\n`;
      
      if (editorRef.current?.view) {
        const view = editorRef.current.view;
        const { from } = view.state.selection.main;
        const transaction = view.state.update({
          changes: { from, insert: markdownText }
        });
        view.dispatch(transaction);
      } else {
        onChange(value + markdownText);
      }
    } catch (err) {
      console.error('Failed to upload image:', err);
      alert('Failed to upload image: ' + (err.response?.data?.error || err.message));
    }
  }, [value, onChange]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handlePaste = async (e) => {
      const items = Array.from(e.clipboardData.items);
      for (const item of items) {
        if (item.type.indexOf('image') !== -1) {
          e.preventDefault();
          e.stopPropagation();
          const file = item.getAsFile();
          if (file) {
            await insertImageMarkdown(file);
          }
          return;
        }
      }
    };

    const handleDrop = async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const files = Array.from(e.dataTransfer.files);
      const imageFiles = files.filter(f => f.type.startsWith('image/'));
      
      if (imageFiles.length > 0) {
        for (const file of imageFiles) {
          await insertImageMarkdown(file);
        }
      }
    };

    const handleDragOver = (e) => {
      e.preventDefault();
      e.stopPropagation();
      e.dataTransfer.dropEffect = 'copy';
    };

    container.addEventListener('paste', handlePaste, true);
    container.addEventListener('drop', handleDrop, true);
    container.addEventListener('dragover', handleDragOver, true);

    return () => {
      container.removeEventListener('paste', handlePaste, true);
      container.removeEventListener('drop', handleDrop, true);
      container.removeEventListener('dragover', handleDragOver, true);
    };
  }, [insertImageMarkdown]);

  const extensions = [
    markdown(),
    EditorView.lineWrapping,
    EditorView.theme({
      '&': {
        fontSize: '15px',
        fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Fira Code", "Droid Sans Mono", "Source Code Pro", monospace',
      },
      '.cm-content': {
        padding: '20px',
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
      },
      '.cm-scroller': {
        fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Fira Code", "Droid Sans Mono", "Source Code Pro", monospace',
      },
      '.cm-editor': {
        backgroundColor: 'var(--bg-primary)',
      },
      '.cm-gutters': {
        backgroundColor: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-color)',
      },
      '.cm-lineNumbers .cm-gutterElement': {
        color: 'var(--text-secondary)',
      },
      '.cm-selectionBackground': {
        backgroundColor: '#b3d4fc !important',
      },
      '&.cm-focused .cm-selectionBackground': {
        backgroundColor: '#b3d4fc !important',
      },
      '.cm-focused .cm-selectionBackground': {
        backgroundColor: '#b3d4fc !important',
      },
      '.cm-selectionMatch': {
        backgroundColor: '#b3d4fc !important',
      },
      '& ::selection': {
        backgroundColor: '#b3d4fc !important',
      },
      '& ::-moz-selection': {
        backgroundColor: '#b3d4fc !important',
      },
    }),
  ];

  return (
    <div className="editor-panel" ref={containerRef}>
      <div className="panel-header">
        <span>Markdown Editor</span>
      </div>
      <div className="panel-content">
        <CodeMirror
          ref={editorRef}
          value={value}
          onChange={onChange}
          extensions={extensions}
          basicSetup={{
            lineNumbers: true,
            foldGutter: true,
            dropCursor: false,
            allowMultipleSelections: false,
            indentOnInput: true,
            bracketMatching: true,
            closeBrackets: true,
            autocompletion: true,
            highlightSelectionMatches: true,
          }}
        />
      </div>
    </div>
  );
}

export default Editor;
