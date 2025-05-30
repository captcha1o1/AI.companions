"""Core AI functionality for the anime AI girlfriend."""

import os
import asyncio
import json
import subprocess
from datetime import datetime
import openai
from .memory.memory_manager import MemoryManager
from .audio.voice_handler import VoiceRecorder, TextToSpeech
from .audio.music_player import MusicPlayer
from .ui.terminal_ui import TerminalUI
from .characters import get_character, get_all_characters

print("Initializing core module...")

# Default settings
DEFAULT_SETTINGS = {
    "openrouter_token": "",  # API key should be provided by user
    "voice_enabled": True,
    "current_voice": "ja-JP-NanamiNeural",
    "voice_input_duration": 5,  # seconds
    "voice_input_enabled": True,
    "veadotube_path": "E:/abhishek/Coding projects/Masking app/src/veadotube-mini-win-x64/veadotube-mini.exe",
    "music_volume": 0.5,  # Default music volume
    "music_folder": "music"  # Music folder path
}

class AnimeAI:
    def __init__(self, openrouter_token=None):
        print("Initializing AnimeAI components...")
        
        # Start VeaDotube Mini
        try:
            print("Starting VeaDotube Mini...")
            veadotube_path = DEFAULT_SETTINGS["veadotube_path"]
            if os.path.exists(veadotube_path):
                subprocess.Popen([veadotube_path], shell=True)
                print("VeaDotube Mini started successfully!")
            else:
                print("VeaDotube Mini executable not found!")
        except Exception as e:
            print(f"Error starting VeaDotube Mini: {e}")
        
        # Load or create settings first
        try:
            print("Loading settings...")
            self.settings = self.load_settings()
            if openrouter_token:
                print("Using provided OpenRouter token...")
                self.settings['openrouter_token'] = openrouter_token
            
            # Check if we have a valid token
            if not self.settings.get('openrouter_token'):
                print("No API token found. Please set one in the settings menu.")
        except Exception as e:
            print(f"Error loading settings: {e}")
            raise

        # Initialize music player
        print("Initializing music player...")
        self.music_player = MusicPlayer(self.settings)
        
        # Try to play menu music
        self.music_player.play_menu_music()
        
        # Get available characters
        self.characters = get_all_characters()
        
        # Initialize components with current character
        try:
            print("Creating TerminalUI...")
            self.ui = TerminalUI()
            
            # Get current character name from voice ID
            current_voice = self.settings.get('current_voice', 'ja-JP-NanamiNeural')
            character_name = next(
                (name.lower() for name, profile in self.characters.items() 
                 if profile.voice_id == current_voice),
                "yuki"  # default to yuki if not found
            )
            
            print("Creating MemoryManager...")
            self.memory = MemoryManager(character=character_name)
            print("Creating VoiceRecorder...")
            self.voice_recorder = VoiceRecorder()
        except Exception as e:
            print(f"Error initializing components: {e}")
            raise
        
        # Initialize AI client
        try:
            print("Initializing AI client...")
            self.initialize_ai_client()
        except Exception as e:
            print(f"Error initializing AI client: {e}")
            raise
            
        print("Setting up chat history...")
        # Chat history for better context
        self.chat_history = []
        self.session_start = datetime.now()
        
        # Convert to format expected by UI
        self.anime_voices = {
            str(i): (char.voice_id, f"{char.name} ({char.description[:30]}...)")
            for i, char in enumerate(self.characters.values(), 1)
        }
        
        print("AnimeAI initialization complete!")

    def load_settings(self):
        """Load settings from file or create default"""
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Could not load settings file, using defaults: {e}")
            return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """Save current settings to file"""
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
            self.ui.print_fancy(f"Failed to save settings: {e}", style="red")

    def initialize_ai_client(self):
        """Initialize the AI client with current settings"""
        try:
            if not self.settings.get('openrouter_token'):
                print("No OpenRouter token found! Please set one in settings.")
                return
            
            # Set up OpenAI configuration globally
            openai.api_base = "https://openrouter.ai/api/v1"
            openai.api_key = self.settings['openrouter_token']
            
            print("OpenAI configuration ready!")
        except Exception as e:
            print(f"Failed to initialize AI client: {e}")
            self.ui.print_fancy(f"Failed to initialize AI client: {e}", style="red")
            raise

    async def handle_settings(self):
        """Handle settings menu"""
        while True:
            choice = self.ui.show_settings_menu(self.settings)
            
            if choice == "1":
                new_token = self.ui.get_api_key_input()
                if new_token:
                    self.settings['openrouter_token'] = new_token
                    self.initialize_ai_client()
                    self.save_settings()
                    self.ui.print_fancy("API key updated successfully!", style="green")
                    
            elif choice == "2":
                self.settings['voice_enabled'] = not self.settings.get('voice_enabled', True)
                self.save_settings()
                status = "enabled" if self.settings['voice_enabled'] else "disabled"
                self.ui.print_fancy(f"Voice output {status}!", style="green")
                
            elif choice == "3":
                await self.handle_voice_settings()
                
            elif choice == "4":
                # Add voice input settings
                self.settings['voice_input_enabled'] = not self.settings.get('voice_input_enabled', True)
                self.save_settings()
                status = "enabled" if self.settings['voice_input_enabled'] else "disabled"
                self.ui.print_fancy(f"Voice input {status}!", style="green")
                
            elif choice == "5":
                # Add voice input duration setting
                duration = self.ui.get_user_input("Enter recording duration in seconds (3-10)")
                try:
                    duration = int(duration)
                    if 3 <= duration <= 10:
                        self.settings['voice_input_duration'] = duration
                        self.save_settings()
                        self.ui.print_fancy(f"Recording duration set to {duration} seconds!", style="green")
                    else:
                        self.ui.print_fancy("Duration must be between 3 and 10 seconds!", style="yellow")
                except:
                    self.ui.print_fancy("Please enter a valid number!", style="red")
                
            elif choice == "6" or choice.lower() == "back":
                break

    async def handle_music_menu(self):
        """Handle music player menu"""
        while True:
            self.ui.print_fancy("\n🎵 Music Player Menu 🎵", style="cyan")
            print("\nSelect music category:")
            print("1. All Music")
            print("2. Character Themes")
            print("3. Background Music")
            print("4. Back to main menu")
            
            choice = self.ui.get_user_input("\nEnter your choice").lower()
            
            if choice == '4' or choice == 'b':
                break
                
            subfolder = None
            if choice == '2':
                subfolder = 'character_themes'
            elif choice == '3':
                subfolder = 'bgm'
                
            songs = self.music_player.load_songs(subfolder)
            
            if not songs:
                self.ui.print_fancy(
                    "No music files found! Add some .mp3, .wav, or .ogg files to the music folder.", 
                    style="yellow"
                )
                continue
                
            while True:
                self.ui.print_fancy("\nAvailable songs:", style="cyan")
                for i, (song_name, _) in enumerate(songs, 1):
                    print(f"{i}. {song_name}")
                    
                print("\nControls:")
                print("1-{}: Play song".format(len(songs)))
                print("p: Pause/Unpause")
                print("s: Stop")
                print("+: Volume up")
                print("-: Volume down")
                print("b: Back to category selection")
                
                subchoice = self.ui.get_user_input("\nEnter your choice").lower()
                
                if subchoice == 'b':
                    break
                elif subchoice == 'p':
                    if self.music_player.is_playing:
                        self.music_player.pause()
                        self.ui.print_fancy("⏸️ Music paused", style="yellow")
                    else:
                        self.music_player.unpause()
                        self.ui.print_fancy("▶️ Music resumed", style="green")
                elif subchoice == 's':
                    self.music_player.stop()
                    self.ui.print_fancy("⏹️ Music stopped", style="red")
                elif subchoice == '+':
                    new_volume = self.settings['music_volume'] + 0.1
                    self.music_player.set_volume(new_volume)
                    self.ui.print_fancy(f"🔊 Volume: {int(self.settings['music_volume'] * 100)}%", style="cyan")
                elif subchoice == '-':
                    new_volume = self.settings['music_volume'] - 0.1
                    self.music_player.set_volume(new_volume)
                    self.ui.print_fancy(f"🔉 Volume: {int(self.settings['music_volume'] * 100)}%", style="cyan")
                elif subchoice.isdigit():
                    song_index = int(subchoice) - 1
                    if 0 <= song_index < len(songs):
                        _, song_path = songs[song_index]
                        if self.music_player.play_song(song_path):
                            self.ui.print_fancy(f"🎵 Now playing: {songs[song_index][0]}", style="green")
                    else:
                        self.ui.print_fancy("❌ Invalid song number", style="red")
                else:
                    self.ui.print_fancy("❌ Invalid choice", style="red")

    async def handle_voice_settings(self):
        """Handle character selection menu"""
        choice = self.ui.show_voice_settings(
            self.settings.get('current_voice'),
            self.anime_voices
        )
        
        if choice in self.anime_voices:
            old_voice = self.settings.get('current_voice')
            self.settings['current_voice'] = self.anime_voices[choice][0]
            
            # Get character name from voice ID
            character_name = next(
                (name for name, profile in self.characters.items() 
                 if profile.voice_id == self.settings['current_voice']),
                "yuki"  # default to yuki if not found
            )
            
            # Update memory manager with new character
            self.memory.set_character(character_name)
            
            # Try to play character-specific music
            if self.music_player.play_character_theme(character_name):
                self.ui.print_fancy(f"🎵 Playing {character_name}'s theme", style="green")

            self.save_settings()
            self.ui.print_fancy(f"Character changed to {self.anime_voices[choice][1]}!", style="green")

    async def handle_chat(self):
        """Handle chat mode"""
        self.ui.show_chat_interface()
        
        # Get character name based on current voice
        current_voice = self.settings.get('current_voice', 'ja-JP-NanamiNeural')
        character_name = next(
            (name.title() for name, profile in self.characters.items() 
             if profile.voice_id == current_voice),
            "Yuki"  # default to Yuki if not found
        )
        
        while True:
            # Show input options
            self.ui.print_fancy(
                f"\nOptions: [type message] | 'voice' for voice input | 'exit' to return",
                style="bright_blue"
            )
            
            user_input = self.ui.get_user_input("You")
            
            if user_input.lower() == 'exit':
                break
                
            elif user_input.lower() == 'voice':
                transcript = await self.handle_voice_input()
                if not transcript:
                    continue
                user_input = transcript
            
            response = await self.chat_with_ai(user_input)
            if response:
                self.ui.print_fancy(f"{character_name}: {response}", style="bright_magenta")
                if self.settings.get('voice_enabled'):
                    await self.handle_voice_output(response)

    async def interactive_chat(self):
        """Main interactive chat loop"""
        self.ui.show_welcome_screen()
        
        # Command shortcuts mapping
        shortcuts = {
            'c': 'chat',
            'ch': 'character',
            'm': 'music',
            'mem': 'memory',
            's': 'settings',
            'h': 'help',
            'cls': 'clear',
            'q': 'exit'
        }
        
        while True:
            command = self.ui.get_user_input().lower().strip()
            
            # Convert shortcut to full command if applicable
            command = shortcuts.get(command, command)
            
            if command == "exit":
                self.ui.print_fancy("Goodbye! 👋", style="bright_cyan")
                break
                
            elif command == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                self.ui.show_welcome_screen()
                
            elif command == "help":
                self.ui.show_welcome_screen()
                
            elif command == "settings":
                await self.handle_settings()
                
            elif command in ["character", "voice"]:
                await self.handle_voice_settings()
                
            elif command == "memory":
                self.memory.show_memories()
                
            elif command == "music":
                await self.handle_music_menu()
                
            elif command == "chat":
                await self.handle_chat()
                
            else:
                self.ui.print_fancy("Unknown command. Type 'help' to see available commands.", style="yellow")

    async def chat_with_ai(self, user_input, system_prompt=None):
        """Enhanced AI chat with memory context"""
        if system_prompt is None:
            # Get current voice and character profile
            current_voice = self.settings.get('current_voice', 'ja-JP-NanamiNeural')
            character_name = next(
                (name.lower() for name, profile in self.characters.items() 
                 if profile.voice_id == current_voice),
                "yuki"  # default to yuki if not found
            )
            character = get_character(character_name)
            system_prompt = character.get_system_prompt()
        
        if not self.settings.get('openrouter_token'):
            self.ui.print_fancy("❌ OpenRouter token not configured! Please check settings.", "red")
            return None
            
        try:
            # Find relevant memories
            relevant_memories = self.memory.find_relevant_memories(user_input)
            
            # Build context from memories
            memory_context = ""
            if relevant_memories:
                memory_context = "\n\nPrevious relevant conversations:\n"
                for i, memory in enumerate(relevant_memories, 1):
                    memory_context += f"{i}. User: {memory['user']}\n   You: {memory['ai']}\n"
                memory_context += "\nUse this context naturally in your response if relevant.\n"
            
            response = await self._get_ai_response(user_input, system_prompt + memory_context)
            
            # Add to chat history and memory
            if response:
                self.chat_history.append({
                    'user': user_input,
                    'ai': response,
                    'timestamp': datetime.now()
                })
                self.memory.add_memory(user_input, response)
            
            return response
            
        except Exception as e:
            print(f"❌ Error getting AI response: {e}")
            self.ui.print_fancy(f"❌ Error getting AI response: {e}", "red")
            return None

    async def _get_ai_response(self, user_input, system_prompt):
        """Internal method to get AI response - Fixed to work with OpenAI 0.28.0"""
        try:
            print("Sending request to OpenRouter API...")
            
            if not self.settings.get('openrouter_token'):
                self.ui.print_fancy("❌ No API token set! Please configure one in settings.", "red")
                return None
            
            # Ensure OpenAI is configured (redundant but safe)
            openai.api_base = "https://openrouter.ai/api/v1"
            openai.api_key = self.settings['openrouter_token']
            
            # Use synchronous call wrapped in asyncio.to_thread for proper async handling
            def make_api_call():
                return openai.ChatCompletion.create(
                    model="deepseek/deepseek-chat-v3-0324:free",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=150,  # Limit response length
                    headers={
                        "HTTP-Referer": "https://github.com/",
                        "X-Title": "AnimeAI"
                    }
                )
            
            # Run the API call in a thread to avoid blocking
            completion = await asyncio.to_thread(make_api_call)
            
            print("Successfully received response from API")
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Detailed error in _get_ai_response: {str(e)}")
            self.ui.print_fancy(f"❌ Error from AI service: {e}", "red")
            return None

    async def handle_voice_input(self):
        """Handle voice input from user"""
        if not self.settings.get('voice_input_enabled'):
            self.ui.print_fancy("Voice input is disabled in settings!", style="yellow")
            return None
            
        self.ui.print_fancy("🎤 Listening... (speak now)", style="bright_yellow")
        audio_file = self.voice_recorder.record_audio(
            duration=self.settings.get('voice_input_duration', 5)
        )
        
        if audio_file:
            transcript = self.voice_recorder.transcribe_audio(audio_file)
            if transcript:
                self.ui.print_fancy(f"You said: {transcript}", style="bright_cyan")
                try:
                    os.unlink(audio_file)
                except:
                    pass
                return transcript
                
        self.ui.print_fancy("❌ Could not understand audio, please try again", style="red")
        return None

    async def handle_voice_output(self, text):
        """Handle voice output to user"""
        if self.settings.get('voice_enabled'):
            # Get current character's voice settings
            current_voice = self.settings['current_voice']
            character_name = next(
                (name for name, profile in self.characters.items() 
                 if profile.voice_id == current_voice),
                "yuki"  # default to yuki if not found
            )
            character = get_character(character_name)
            
            # Use character's voice settings
            rate = character.voice_settings.get('rate', "-5%")
            pitch = character.voice_settings.get('pitch', "+0Hz")
            
            audio_file = await TextToSpeech.text_to_speech(text, current_voice, rate=rate, pitch=pitch)
            if audio_file:
                await TextToSpeech.play_audio(audio_file)
                try:
                    os.unlink(audio_file)
                except:
                    pass