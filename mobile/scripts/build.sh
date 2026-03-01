#!/bin/bash
# Usage: ./scripts/build.sh [dev|staging|prod]

ENV=${1:-dev}

case $ENV in
  dev)
    API_URL="http://localhost:8000/api/v1"
    ;;
  staging)
    API_URL="http://192.158.10.63:8000/api/v1"
    ;;
  prod)
    API_URL="https://api.mycoach-app.com/api/v1"
    ;;
  *)
    echo "Usage: $0 [dev|staging|prod]"
    exit 1
    ;;
esac

echo "🔨 Building for $ENV → $API_URL"

flutter build apk --release \
  --dart-define=ENV=$ENV \
  --dart-define=API_BASE_URL=$API_URL
