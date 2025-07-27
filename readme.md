# 🏨 Hotel Concierge Bot

A sophisticated multi-hotel AI concierge assistant that provides personalized customer service based on hotel-specific policies and local knowledge.

## ✨ Features

- **🏨 Multi-Hotel Support**: Select from different hotels, each with their own policies and information
- **📄 PDF-Based Knowledge**: Each hotel can have its own policy PDF that the bot references for accurate information
- **🤖 Intelligent Conversations**: Powered by Google's Gemini AI with memory and context awareness
- **📅 Booking Management**: Handle reservations and service requests with automatic database logging
- **📋 Task Management**: Track and manage guest requests and staff tasks
- **💻 Modern Web Interface**: Clean, responsive web interface for seamless user interaction
- **🔒 Session Management**: Secure hotel-specific sessions with conversation history

## 🛠️ Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hotel-concierge-bot.git
cd hotel-concierge-bot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

Required API keys:
- **GEMINI_API_KEY**: Get from [Google AI Studio](https://ai.google.dev/)
- **GOOGLE_CLOUD_API_KEY**: Get from [Google Cloud Console](https://console.cloud.google.com/)

### 5. Create Required Directories
```bash
mkdir pdfs
mkdir config models static/css static/js templates
```

### 6. Add Hotel Policy PDFs
Place your hotel policy PDFs in the `pdfs/` directory with the following names:
- `grand_palace_policies.pdf`
- `seaside_resort_policies.pdf`
- `mountain_view_policies.pdf`

### 7. Create Empty `__init__.py` Files
```bash
touch config/__init__.py
touch models/__init__.py
```

### 8. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
hotel-concierge-bot/
├── app.py                     # Main Flask application
├── run.py                     # Production entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration management
├── models/
│   ├── __init__.py
│   ├── database.py           # Database operations
│   └── hotel_bot.py          # AI bot logic
├── templates/
│   └── index.html            # Frontend template
├── static/
│   ├── css/
│   │   └── style.css         # Stylesheet
│   └── js/
│       └── main.js           # Frontend JavaScript
└── pdfs/                     # Hotel policy PDFs
    ├── grand_palace_policies.pdf
    ├── seaside_resort_policies.pdf
    └── mountain_view_policies.pdf
```

## 🚀 Deployment

### Heroku Deployment
1. Create a Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Git:
```bash
git add .
git commit -m "Initial commit"
heroku git:remote -a your-app-name
git push heroku main
```

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Railway will automatically deploy

### Docker Deployment
```bash
docker build -t hotel-concierge-bot .
docker run -p 5000:5000 --env-file .env hotel-concierge-bot
```

## 📖 Usage

1. **Select Hotel**: Choose from available hotels on the main page
2. **Chat Interface**: Interact with the hotel-specific concierge
3. **Make Requests**: Book services, ask questions, request assistance
4. **View History**: Check booking and task history (admin feature)

## 🏨 Adding New Hotels

1. Add hotel record to database via admin interface or direct database insertion
2. Upload hotel policy PDF to `pdfs/` directory
3. Update database with correct PDF filename
4. Restart the application

## 🤖 Bot Capabilities

The AI concierge can help with:
- Hotel amenities and services information
- Local attractions and recommendations
- Restaurant reservations and dining suggestions
- Transportation arrangements
- Room service requests
- Spa and wellness bookings
- Event planning and special requests
- General travel assistance

## 🔧 Configuration

Key configuration options in `.env`:
- `GEMINI_API_KEY`: Google Gemini AI API key
- `GOOGLE_CLOUD_API_KEY`: Google Cloud API key for embeddings
- `SECRET_KEY`: Flask session secret key
- `DEBUG`: Enable/disable debug mode
- `PORT`: Application port (default: 5000)
- `DATABASE_PATH`: SQLite database file path

## 🐛 Troubleshooting

### Common Issues:
1. **API Key Errors**: Ensure your Gemini and Google Cloud API keys are valid and have proper permissions
2. **PDF Loading Issues**: Check that PDF files exist in the `pdfs/` directory and are readable
3. **Database Errors**: Delete `hotel_system.db` to reset the database
4. **Port Issues**: Change the PORT in `.env` if 5000 is already in use

### Logs:
Check the console output for detailed error messages and debugging information.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions, please create an issue on GitHub or contact the development team.

---

Built with ❤️ using Flask, LangChain, and Google Gemini AI