#!/bin/bash
set -e

echo "🔧 Environment Setup Wizard"
echo "============================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Overwrite? (yes/no): " overwrite
    if [ "$overwrite" != "yes" ]; then
        exit 0
    fi
fi

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Get OpenAI key
read -p "Enter OpenAI API key (or press Enter to skip): " OPENAI_KEY
if [ -z "$OPENAI_KEY" ]; then
    OPENAI_KEY="sk-your-key-here"
fi

# Generate NextAuth secret
NEXTAUTH_SECRET=$(openssl rand -hex 32)

# Create .env
cat > .env << EOF
# Backend
JWT_SECRET=$JWT_SECRET
OPENAI_API_KEY=$OPENAI_KEY
LLM_MODEL=gpt-4o-mini

# Frontend
NEXTAUTH_SECRET=$NEXTAUTH_SECRET
EOF

echo ""
echo "✅ .env file created!"
echo ""
echo "📝 Please review and edit .env if needed"
echo ""
