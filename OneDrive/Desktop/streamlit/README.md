# 🧘 Parmatma - AI-Powered Health & Wellness Platform

A comprehensive health and wellness application built with Streamlit, featuring AI-powered coaching, health tracking, and personalized wellness insights.

## 🌟 Features

### 🏠 **Personal Profile Management**
- Complete user profile setup with BMI tracking
- Personalized health metrics and recommendations
- Age, gender, height, and weight tracking

### 📊 **BMI Calculator**
- Real-time BMI calculation and categorization
- Color-coded health status indicators
- Personalized advice based on BMI category

### 🥗 **AI Nutrition Coach**
- Personalized weekly nutrition plans
- Dietary preference customization (Vegetarian, Vegan, Keto, etc.)
- Allergy and food avoidance management
- Detailed or brief meal planning options
- Powered by Google's Gemini AI

### 💪 **Exercise Routines**
- Customizable workout plans for different body parts
- Fitness level-based routines (Beginner, Intermediate, Advanced)
- Flexible workout duration (10-120 minutes)
- Goal-oriented exercise recommendations

### 🩺 **Symptom Checker**
- AI-powered symptom analysis
- Disease prediction with confidence scores
- Top 3 most likely conditions based on symptoms
- Quick health assessment tool

### 🧠 **Mental Health Support Chat**
- Real-time AI wellness coaching
- Sentiment analysis of user messages
- Emotional support and guidance
- Chat history tracking
- Mood-based recommendations

### 🌌 **Digital Soul Twin**
- Advanced health tracking avatar
- Daily habit monitoring (sleep, exercise, meals)
- Mood and emotion tracking with sentiment analysis
- Time-weighted wellness scoring
- Predictive health insights
- Visual mood trend analysis
- Personalized wellness suggestions

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Streamlit
- Google API Key (for AI features)
- Supabase account (for data storage)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/someshhh-45/Paramathma.git
   cd Paramathma
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.streamlit/secrets.toml` file:
   ```toml
   GOOGLE_API_KEY = "your_google_api_key"
   SUPABASE_URL = "your_supabase_url"
   SUPABASE_KEY = "your_supabase_key"
   ```

4. **Run the application**
   ```bash
   streamlit run ptest.py
   ```

## 📁 Project Structure

```
Paramathma/
├── ptest.py              # Main Streamlit application
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
├── .streamlit/          # Streamlit configuration
│   └── secrets.toml     # Environment variables (not tracked)
└── README.md            # Project documentation
```

## 🛠️ Dependencies

- **streamlit** - Web app framework
- **supabase** - Database and backend services
- **textblob** - Natural language processing for sentiment analysis
- **requests** - HTTP library for API calls
- **numpy** - Numerical computing
- **pandas** - Data manipulation and analysis
- **matplotlib** - Data visualization for charts and graphs

## 🔧 Configuration

### Google AI Integration
The app uses Google's Gemini AI model for:
- Nutrition planning
- Exercise routine generation
- Symptom analysis
- Mental health coaching

### Supabase Integration
Used for:
- User data storage
- Health metrics tracking
- Session management

## 🎯 Key Features Explained

### Digital Soul Twin Algorithm
The Digital Soul Twin uses a sophisticated time-weighted scoring system:
- **Sleep Score**: Based on 7-9 hours optimal range
- **Exercise Score**: Weighted by activity duration
- **Nutrition Score**: Quality-based meal assessment
- **Mood Score**: Sentiment analysis of daily inputs
- **Wellness Score**: Combined metric (0.0 - 1.0)

### AI Coaching
- Personalized responses based on user profile
- Context-aware recommendations
- Sentiment-driven emotional support
- Adaptive coaching based on historical data

## 🚀 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with one click
4. Add secrets in Streamlit Cloud dashboard

### Local Development
```bash
streamlit run ptest.py --server.port 8501
```

## 🔒 Security & Privacy

- Sensitive data stored securely in Supabase
- API keys managed through environment variables
- No personal health data exposed in code
- GDPR-compliant data handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent health coaching
- **Streamlit** for the amazing web framework
- **Supabase** for backend infrastructure
- **TextBlob** for sentiment analysis capabilities

## 📞 Support

For support, email your-email@example.com or create an issue in this repository.

## 🔮 Future Enhancements

- [ ] Integration with wearable devices
- [ ] Advanced health analytics dashboard
- [ ] Social features for wellness communities
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Telemedicine integration
- [ ] Advanced AI diagnostics

---

**Made with ❤️ for better health and wellness**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF6B6B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Google AI](https://img.shields.io/badge/Google%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google/)