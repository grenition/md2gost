import React, { useState, useEffect, useCallback } from 'react';
import Editor from './components/Editor';
import Preview from './components/Preview';
import Header from './components/Header';
import { getSessionId } from './services/api';
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

function App() {
  const [markdown, setMarkdown] = useState(exampleContent);
  const [syntaxHighlighting, setSyntaxHighlighting] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => getSessionId());

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

export default App;

