"""Music player functionality for the anime AI."""

import os
import pygame

class MusicPlayer:
    def __init__(self, settings):
        """Initialize the music player with settings"""
        # Initialize pygame mixer with better audio quality
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        self.settings = settings
        self.current_song = None
        self.is_playing = False
        
        # Ensure music directories exist
        self.setup_music_directories()
        
    def setup_music_directories(self):
        """Create necessary music directories if they don't exist"""
        # Main music directory
        if not os.path.exists(self.settings['music_folder']):
            os.makedirs(self.settings['music_folder'])
            print(f"Created '{self.settings['music_folder']}' folder")
            
        # Character themes directory
        character_themes_dir = os.path.join(self.settings['music_folder'], 'character_themes')
        if not os.path.exists(character_themes_dir):
            os.makedirs(character_themes_dir)
            print(f"Created 'character_themes' folder")
            
        # Background music directory
        bgm_dir = os.path.join(self.settings['music_folder'], 'bgm')
        if not os.path.exists(bgm_dir):
            os.makedirs(bgm_dir)
            print(f"Created 'bgm' folder")
        
    def load_songs(self, subfolder=None):
        """Load all music files from the specified folder"""
        folder = self.settings['music_folder']
        if subfolder:
            folder = os.path.join(folder, subfolder)
            
        if not os.path.exists(folder):
            print(f"Folder '{folder}' does not exist!")
            return []
            
        songs = []
        for file in os.listdir(folder):
            if file.endswith(('.mp3', '.wav', '.ogg')):
                songs.append((file, os.path.join(folder, file)))
        return songs
        
    def play_song(self, song_path, loop=True):
        """Play a single song"""
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play(-1 if loop else 0)  # -1 means loop indefinitely
            pygame.mixer.music.set_volume(self.settings['music_volume'])
            
            # Set up an event handler for song end
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            
            self.current_song = song_path
            self.is_playing = True
            print(f"🎵 Now playing: {os.path.basename(song_path)}")
            return True
        except Exception as e:
            print(f"❌ Error playing {song_path}: {str(e)}")
            return False
            
    def play_character_theme(self, character_name):
        """Play a character's theme music"""
        theme_path = os.path.join(
            self.settings['music_folder'], 
            'character_themes', 
            f"{character_name}.mp3"
        )
        if os.path.exists(theme_path):
            return self.play_song(theme_path)
        return False
        
    def play_menu_music(self):
        """Play the menu background music"""
        menu_path = os.path.join(self.settings['music_folder'], 'bgm', 'menu.mp3')
        if os.path.exists(menu_path):
            return self.play_song(menu_path)
        return False
        
    def stop(self):
        """Stop the current song"""
        pygame.mixer.music.stop()
        self.is_playing = False
        
    def pause(self):
        """Pause the current song"""
        pygame.mixer.music.pause()
        self.is_playing = False
        
    def unpause(self):
        """Unpause the current song"""
        pygame.mixer.music.unpause()
        self.is_playing = True
        
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.settings['music_volume'] = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.settings['music_volume'])
        
    def get_current_song_name(self):
        """Get the name of the currently playing song"""
        if self.current_song:
            return os.path.basename(self.current_song)
        return None 