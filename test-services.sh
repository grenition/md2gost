#!/bin/bash

echo "Testing MD2GOST Services..."
echo ""

echo "1. Testing API Service through Gateway..."
curl -s http://localhost/api/health | jq . || echo "Failed"
echo ""

echo "2. Testing Frontend..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Frontend accessible (HTTP $HTTP_CODE)"
else
    echo "✗ Frontend not accessible (HTTP $HTTP_CODE)"
fi
echo ""

echo "3. Testing Preview Endpoint..."
PREVIEW_RESPONSE=$(curl -s -X POST http://localhost/api/preview \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Test\n\nThis is a test.", "syntaxHighlighting": true}')
if echo "$PREVIEW_RESPONSE" | jq -e '.html' > /dev/null 2>&1; then
    echo "✓ Preview endpoint working"
    echo "$PREVIEW_RESPONSE" | jq -r '.html' | head -3
else
    echo "✗ Preview endpoint failed"
    echo "$PREVIEW_RESPONSE" | head -5
fi
echo ""

echo "Tests completed!"

