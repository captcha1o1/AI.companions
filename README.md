# AI.companions

An AI-powered application that combines text-to-speech, speech-to-text, and music features for an interactive experience.

## Features
- Constamizable Character, as per need.
- Voice interaction support
- Text-to-speech capabilities using Edge TTS
- Music playback functionality
- Advanced Memory for the AI to remember important stuff

## Prerequisites
- Python 3.8 or higher
- Windows 10/11 (for Edge TTS support)
- A valid OpenRouter API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/masking-app.git
cd masking-app
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the settings:
   - Update the `openrouter_token` with your API key
   - Adjust other settings as needed

## Configuration
The `settings.json` file contains the following options:
- `voice_enabled`: Enable/disable voice output
- `voice`: Default voice for text-to-speech (e.g., "ja-JP-NanamiNeural")
- `current_voice`: Current active voice
- `openrouter_token`: Your OpenRouter API key
- `voice_input_enabled`: Enable/disable voice input
- `music_folder`: Directory for music files
- `music_volume`: Music playback volume (0.0 to 1.0)

## Usage
1. Ensure your settings are configured correctly
2. Place any music files you want to use in the `music` directory
3. Run the application:
```bash
python src/main.py
```
4. Put your Open router key in the - menu --> API key

## Project Structure
```
app/
├── src/
│   ├── memories/      # Memory management
│   └── anime_ai/      # AI interaction components
├── music/             # Music files directory
├── requirements.txt   # Python dependencies
└── settings.json      # Application configuration
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
