
## **5. `setup.sh` - SETUP SCRIPT**
```bash
#!/bin/bash

# ============================================
# 🎭 MAR PD Bot - Setup Script
# ============================================

echo "🎭 MAR PD Bot Setup Script"
echo "=========================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment!"
    exit 1
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs backups data/media data/users

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Copying environment file..."
    cp .env.example .env
    
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your credentials"
    echo "   You need to set:"
    echo "   1. BOT_TOKEN (from @BotFather)"
    echo "   2. BOT_OWNER_ID (your Telegram ID)"
    echo "   3. FIREBASE_API_KEY"
    echo "   4. FIREBASE_PROJECT_ID"
    echo "   5. BKASH_NUMBER"
    echo "   6. NAGAD_NUMBER"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Create default Firebase config if needed
if [ ! -f firebase-config.json ]; then
    echo "🔥 Creating Firebase config template..."
    cat > firebase-config.json << EOF
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40your-project.iam.gserviceaccount.com"
}
EOF
    echo "⚠️  Please update firebase-config.json with your Firebase credentials"
fi

# Set executable permissions
echo "🔧 Setting permissions..."
chmod +x main.py
chmod +x run.py

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
from core.database import Database
import asyncio

async def init_db():
    db = Database()
    success = await db.initialize()
    if success:
        print('✅ Database initialized successfully')
    else:
        print('❌ Database initialization failed')

asyncio.run(init_db())
"

echo ""
echo "========================================"
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file:"
echo "   nano .env"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the bot:"
echo "   python main.py"
echo "   or"
echo "   ./run.py"
echo ""
echo "4. For production, consider using:"
echo "   - PM2 for process management"
echo "   - Nginx for reverse proxy"
echo "   - SSL certificates for security"
echo ""
echo "📞 Need help? Contact: @mar_pd_support"
echo "========================================"