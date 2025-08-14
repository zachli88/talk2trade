# Talk2Trade - AI Trading Assistant

A modern, ChatGPT-like web interface for your AI trading assistant that supports both text and audio input.

## Features

- 🎨 **Modern UI**: Clean, ChatGPT-inspired interface with responsive design
- 💬 **Text Chat**: Send text messages and get AI responses
- 🎤 **Audio Input**: Record and send audio messages
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔄 **Conversation Management**: Start new chats and maintain conversation history
- ⚡ **Real-time Interaction**: Smooth animations and typing indicators

## Screenshots

The app features:

- Dark sidebar with chat history
- Clean main chat area with message bubbles
- Input area with text and audio recording capabilities
- Welcome screen with feature highlights
- Responsive design for all screen sizes

## Installation

1. **Clone the repository** (if you haven't already):

   ```bash
   git clone <your-repo-url>
   cd talk2trade
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:

   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Text Chat

- Type your message in the input box
- Press Enter to send (Shift+Enter for new line)
- Click the paper plane button to send

### Audio Recording

- Click the microphone button to start recording
- Speak your message
- Click the stop button to end recording
- The audio will be automatically sent and processed

### Starting New Chats

- Click the "New Chat" button in the sidebar
- This will clear the current conversation and start fresh

## Project Structure

```
talk2trade/
├── app.py              # Flask web application
├── main.py             # Your existing trading logic
├── clients.py          # Your existing API clients
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   └── index.html     # Main chat interface
├── static/            # Static assets
│   ├── css/
│   │   └── style.css  # Main stylesheet
│   └── js/
│       └── app.js     # Frontend JavaScript
└── README.md          # This file
```

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send text message
- `POST /api/audio` - Send audio message
- `GET /api/conversations/<id>` - Get conversation history

## Customization

### Backend Integration

The app is designed to easily integrate with your existing trading logic. In `app.py`, you can:

1. **Modify the chat endpoint** (`/api/chat`) to integrate with your trading algorithms
2. **Enhance the audio endpoint** (`/api/audio`) to process audio using speech-to-text
3. **Add authentication** and user management
4. **Connect to databases** for persistent conversation storage

### Frontend Styling

- **Colors**: Modify the CSS variables in `static/css/style.css`
- **Layout**: Adjust the HTML structure in `templates/index.html`
- **Functionality**: Extend the JavaScript in `static/js/app.js`

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Audio Recording

The app uses the Web Audio API for recording. Make sure to:

- Use HTTPS in production (required for audio recording)
- Grant microphone permissions when prompted
- Test audio functionality in supported browsers

## Development

To run in development mode:

```bash
export FLASK_ENV=development
python app.py
```

The app will automatically reload when you make changes to the code.

## Production Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up proper environment variables
3. Configure HTTPS for audio recording
4. Add authentication and rate limiting
5. Use a production database for conversation storage

## Troubleshooting

### Common Issues

1. **Audio not working**: Check browser permissions and HTTPS requirement
2. **Flask not found**: Ensure you've installed requirements with `pip install -r requirements.txt`
3. **Port already in use**: Change the port in `app.py` or kill the process using the port

### Debug Mode

Enable debug mode by setting:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of your Talk2Trade application. Modify and use as needed for your trading platform.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the browser console for JavaScript errors
3. Check the Flask application logs
4. Ensure all dependencies are properly installed
