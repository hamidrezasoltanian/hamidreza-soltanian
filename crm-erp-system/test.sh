#!/bin/bash
set -e
echo "🧪 Testing CRM/ERP System..."
curl -sSf http://localhost:8000/api/v1/ >/dev/null && echo "✅ Backend OK" || echo "❌ Backend not responding"
curl -sSf http://localhost:3000 >/dev/null && echo "✅ Frontend OK" || echo "❌ Frontend not responding"
