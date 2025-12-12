import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Routes, Route, useNavigate, useParams } from 'react-router-dom';
import Editor from './components/Editor';
import Preview from './components/Preview';
import Header from './components/Header';
import { getSessionId, getSessionData, saveSessionData, api } from './services/api';
import './App.css';

const exampleContent = `# *TABLE OF CONTENTS
[TOC]

# Example Markdown File

This is an example Markdown file demonstrating various elements.

## Headings

Headings are used to organize content.

### Third Level Heading

## Image

![img.png](img.png "Placeholder")

## Table

%goods Products

| Product Name | Price | Quantity |
|--------------|-------|----------|
| Apple        | $1    | 10       |
| Banana       | $0.5  | 20       |

## Equations

Euler's equation: $e^{i\\pi} + 1 = 0$.

And this is an aligned equation:

$$
\\sum_{n=1}^{10} n^2
$$

## Code Fragment

%listing Merge sort

\`\`\`python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))
\`\`\`

## Lists

1. First item
2. Second item
3. Third item

- First element
- Second element
- Third element
`;

function EditorPage() {
  const [markdown, setMarkdown] = useState(exampleContent);
  const [syntaxHighlighting, setSyntaxHighlighting] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isLoadingSession, setIsLoadingSession] = useState(true);
  const saveTimeoutRef = useRef(null);
  const navigate = useNavigate();
  const { shortId } = useParams();

  // Load session and data on mount
  useEffect(() => {
    const loadSession = async () => {
      if (!shortId) {
        navigate('/');
        return;
      }
      
      try {
        const { getSessionIdByShortId } = await import('./services/api');
        const sid = await getSessionIdByShortId(shortId);
        if (!sid) {
          // Invalid short_id, redirect to home
          navigate('/');
          return;
        }
        setSessionId(sid);
        
        // Try to load saved data
        const savedData = await getSessionData(sid);
        if (savedData && savedData.markdown) {
          setMarkdown(savedData.markdown);
          if (savedData.syntaxHighlighting !== undefined) {
            setSyntaxHighlighting(savedData.syntaxHighlighting);
          }
        }
      } catch (err) {
        console.error('Failed to load session:', err);
        navigate('/');
      } finally {
        setIsLoadingSession(false);
      }
    };
    
    loadSession();
  }, [navigate, shortId]);

  // Save data to session when markdown or syntaxHighlighting changes
  useEffect(() => {
    if (!sessionId || isLoadingSession) return;

    // Clear previous timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Debounce save (save after 2 seconds of no changes)
    saveTimeoutRef.current = setTimeout(() => {
      saveSessionData(sessionId, {
        markdown,
        syntaxHighlighting,
      });
    }, 2000);

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [markdown, syntaxHighlighting, sessionId, isLoadingSession]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (markdown.trim()) {
        setIsLoading(true);
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [markdown]);

  const handlePreviewLoaded = useCallback(() => {
    setIsLoading(false);
  }, []);

  if (isLoadingSession) {
    return (
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <Header
        syntaxHighlighting={syntaxHighlighting}
        onSyntaxHighlightingChange={setSyntaxHighlighting}
        markdown={markdown}
      />
      <div className="main-content">
        <Editor
          value={markdown}
          onChange={setMarkdown}
          syntaxHighlighting={syntaxHighlighting}
          sessionId={sessionId}
        />
        <Preview
          markdown={markdown}
          syntaxHighlighting={syntaxHighlighting}
          isLoading={isLoading}
          onLoaded={handlePreviewLoaded}
        />
      </div>
    </div>
  );
}

function HomePage() {
  const navigate = useNavigate();

  useEffect(() => {
    const createAndRedirect = async () => {
      try {
        const response = await api.post('/session/create');
        const { short_id } = response.data;
        navigate(`/edit/${short_id}`, { replace: true });
      } catch (err) {
        console.error('Failed to create session:', err);
      }
    };
    
    createAndRedirect();
  }, [navigate]);

  return (
    <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <div>Redirecting...</div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/edit/:shortId" element={<EditorPage />} />
    </Routes>
  );
}

export default App;
