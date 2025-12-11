import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import { EditorView } from '@codemirror/view';
import './Editor.css';

function Editor({ value, onChange, syntaxHighlighting }) {
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
    <div className="editor-panel">
      <div className="panel-header">
        <span>Markdown Editor</span>
      </div>
      <div className="panel-content">
        <CodeMirror
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
