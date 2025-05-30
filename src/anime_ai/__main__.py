"""Main entry point for the anime AI application."""

import os
import sys
import asyncio
import argparse
import subprocess
import traceback

def launch_new_window():
    """Launch the application in a new terminal window"""
    if sys.platform == 'win32':
        # For Windows
        cmd = ['start', 'cmd', '/k', 'python', '-m', 'src.anime_ai', '--in-terminal']
        subprocess.run(cmd, shell=True)
    else:
        # For Linux/Mac
        terminal = os.getenv('TERMINAL', 'gnome-terminal')
        cmd = [terminal, '--', 'python', '-m', 'src.anime_ai', '--in-terminal']
        subprocess.Popen(cmd)

def main():
    parser = argparse.ArgumentParser(description="Enhanced Anime AI Girlfriend with Memory & Voice")
    parser.add_argument("--openrouter-token", help="OpenRouter API token")
    parser.add_argument("--no-ui", action="store_true", help="Disable Rich UI")
    parser.add_argument("--in-terminal", action="store_true", help="Already running in new terminal")
    args = parser.parse_args()
    
    # If not already in a new terminal, launch one
    if not args.in_terminal:
        print("Launching new terminal window...")
        launch_new_window()
        return
        
    # Keep terminal window open
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        from .core import AnimeAI
        from .ui.terminal_ui import TerminalUI
        
        # Create UI first for loading screen
        ui = TerminalUI()
        ui.show_loading_screen([
            "Initializing components",
            "Loading AI modules",
            "Setting up music system",
            "Preparing workspace"
        ])
        
        # Create AnimeAI instance
        ai = AnimeAI(openrouter_token=args.openrouter_token)
        
        # Start interactive chat
        asyncio.run(ai.interactive_chat())
        
    except KeyboardInterrupt:
        print("\nGoodbye! Press any key to exit...")
    except ImportError as e:
        print(f"\nFailed to import required modules: {e}")
        print("Make sure all requirements are installed with: pip install -r requirements.txt")
        traceback.print_exc()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        traceback.print_exc()
    
    print("\nPress any key to exit...")
    if os.name == 'nt':
        os.system('pause')
    else:
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 