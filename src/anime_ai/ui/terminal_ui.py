"""Terminal UI functionality for the anime AI."""

import time
import asyncio
import random
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.layout import Layout
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.prompt import Prompt, Confirm
    from rich.align import Align
    from rich.padding import Padding
    from rich.columns import Columns
    from rich.syntax import Syntax
    from rich.rule import Rule
    from rich import box
    from rich.style import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich UI not available. Install: pip install rich")

class TerminalUI:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.layout = Layout() if RICH_AVAILABLE else None
        self.theme_colors = ["bright_magenta", "bright_cyan", "bright_blue", "bright_green"]
        self.current_theme = 0
        self.cassette_frames = [
            "┌─────────────────────────────────────┐",
            "│  ⚫          MUSIC IS LIFE     ⚫  │",
            "│ ╭─────────────────────────────────╮ │",
            "│ │  ████████████████████████████  │ │",
            "│ │  ████████████████████████████  │ │",
            "│ ╰─────────────────────────────────╯ │",
            "└─────────────────────────────────────┘"
        ]
        self.cassette_pos = 0
        self.setup_layout()
        
    def setup_layout(self):
        """Setup the main layout structure"""
        if not RICH_AVAILABLE:
            return
            
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
    def get_theme_color(self, offset=0):
        """Get current theme color with optional offset"""
        idx = (self.current_theme + offset) % len(self.theme_colors)
        return self.theme_colors[idx]

    def animate_text(self, text: str, style="bright_cyan", speed=0.03):
        """Animate text appearing character by character"""
        if not RICH_AVAILABLE:
            print(text)
            return
            
        with Live(console=self.console, refresh_per_second=20) as live:
            displayed_text = ""
            for char in text:
                displayed_text += char
                live.update(Text(displayed_text + "▋", style=style))
                time.sleep(speed)
            live.update(Text(displayed_text, style=style))

    def show_loading_screen(self, steps: List[str]):
        """Show an animated loading screen with progress"""
        if not RICH_AVAILABLE:
            for step in steps:
                print(f"Loading: {step}...")
                time.sleep(0.5)
            return
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="bright_magenta", finished_style="bright_green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            tasks = {}
            for step in steps:
                tasks[step] = progress.add_task(
                    f"✨ {step}...", 
                    total=100
                )
            
            for step, task_id in tasks.items():
                for i in range(100):
                    progress.update(task_id, advance=1)
                    time.sleep(0.01)
                progress.update(task_id, description=f"🌟 {step} - Complete!")

    def get_next_cassette_frame(self):
        """Get next frame of cassette animation"""
        frame_lines = []
        for i, line in enumerate(self.cassette_frames):
            if "████" in line:
                # Animate the tape reels
                tape_line = line.replace("████████████████████████████", 
                                      "█" * (20 + (self.cassette_pos % 8)) + 
                                      "░" * (8 - (self.cassette_pos % 8)))
                frame_lines.append(tape_line)
            else:
                frame_lines.append(line)
        
        self.cassette_pos = (self.cassette_pos + 1) % 20
        return "\n".join(frame_lines)

    def show_settings_menu(self, current_settings):
        """Show enhanced settings menu with better alignment"""
        if not RICH_AVAILABLE:
            print("\n=== Settings ===")
            print("1. API Key")
            print("2. Voice Output")
            print("3. Character")
            print("4. Voice Input")
            print("5. Recording Duration")
            print("6. Back")
            return self.get_user_input("\nSelect option (1-6)")
            
        self.clear_screen()
        
        settings_table = Table(
            show_header=True,
            header_style="bold bright_green",
            border_style="bright_green",
            box=box.ROUNDED,
            padding=(1, 2),
            width=70
        )
        
        settings_table.add_column("Option", style="cyan", width=18)
        settings_table.add_column("Current Value", style="white", width=20)
        settings_table.add_column("Description", style="bright_black", width=25)
        
        api_key = current_settings.get('openrouter_token', '')
        masked_key = "••••" + api_key[-4:] if api_key else "Not set"
        
        settings = [
            ("🔑 1. API Key", masked_key, "OpenRouter API token"),
            ("🔊 2. Voice Output", "ON ✅" if current_settings.get('voice_enabled') else "OFF ❌", "Enable/disable voice"),
            ("👤 3. Character", current_settings.get('current_voice', 'Default'), "Change AI personality"),
            ("🎤 4. Voice Input", "ON ✅" if current_settings.get('voice_input_enabled') else "OFF ❌", "Enable/disable voice input"),
            ("⏱️ 5. Duration", f"{current_settings.get('voice_input_duration', 5)}s", "Recording length"),
            ("🔙 6. Back", "Return to menu", "Exit settings")
        ]
        
        for option, value, desc in settings:
            settings_table.add_row(option, value, desc)
        
        panel = Panel(
            Align.center(settings_table),
            box=box.ROUNDED,
            border_style="bright_green",
            title="⚙️ Settings Panel ⚙️",
            padding=(1, 2)
        )
        
        self.console.print(Align.center(panel))
        self.console.print()
        
        result = self.get_user_input("✨ Select option (1-6)")
        return result

    def show_welcome_screen(self):
        """Display welcome screen"""
        self.clear_screen()
        if not RICH_AVAILABLE:
            print("\n=== Welcome to AI Companions ===")
            print("\nAvailable commands:")
            print("chat (c) - Start chatting")
            print("character (ch) - Change character")
            print("music (m) - Music player")
            print("memory (mem) - View history")
            print("settings (s) - Settings")
            print("help (h) - Show this help")
            print("clear (cls) - Clear screen")
            print("exit (q) - Exit")
            return

        title = Text("✨ Welcome to AI Companions ✨", style="bright_green bold")
        
        main_panel = Panel(
            Align.center(title),
            border_style="bright_green",
            box=box.ROUNDED,
            padding=(1, 2),
            title="🌸 Welcome 🌸"
        )
        
        commands = Table(
            show_header=True,
            header_style="bold bright_green",
            border_style="bright_green",
            box=box.ROUNDED,
            padding=(0, 2),
            width=65
        )
        
        commands.add_column("Command", style="cyan", width=15)
        commands.add_column("Description", style="white", width=25)
        commands.add_column("Key", style="bright_black", width=8)
        
        command_list = [
            ("Chat", "Talk with AI 💬", "c"),
            ("Character", "Change AI 🎭", "ch"),
            ("Music", "Play music 🎵", "m"),
            ("Memory", "View history 📝", "mem"),
            ("Settings", "Options/Settings ⚙️", "s"),
            ("Help", "Show help 💡", "h"),
            ("Clear", "Clear UI 🧹", "cls"),
            ("Exit", "Quit 🚪", "q")
        ]
        
        for cmd, desc, shortcut in command_list:
            commands.add_row(cmd, desc, shortcut)
        
        current_time = datetime.now().strftime("%H:%M:%S")
        status = f"🕐 {current_time} | 💫 AI Active | 🎵 Ready"
        
        self.console.print()
        self.console.print(Align.center(main_panel))
        self.console.print()
        self.console.print(Align.center(commands))
        self.console.print()
        self.console.print(Align.center(Text(status, style="bright_green")))
        self.console.print()

    def show_chat_interface(self, username="You", character_name="AI"):
        """Show enhanced chat interface with animations"""
        if not RICH_AVAILABLE:
            print("\n=== Chat Mode ===")
            print(f"Chatting with: {character_name}")
            return
            
        self.clear_screen()
        
        chat_panel = Panel(
            Align.center(
                Text(
                    f"✨ Chat session started with {character_name}! ✨\n\n"
                    "💬 Type your message below\n"
                    "🎤 Say 'voice' for voice input\n"
                    "❌ Type 'exit' to return to menu",
                    style="bright_cyan"
                )
            ),
            box=box.ROUNDED,
            border_style="bright_green",
            title=f"💫 Chat with {character_name} 💫"
        )
        
        self.console.print(chat_panel)

    def show_music_player(self, current_song=None, volume=1.0):
        """Show enhanced Spotify-like music player with animations"""
        if not RICH_AVAILABLE:
            print("\n=== Music Player ===")
            if current_song:
                print(f"Now Playing: {current_song}")
            print(f"Volume: {int(volume * 100)}%")
            return

        self.clear_screen()
        
        # Create the main music interface
        cassette_art = self.get_next_cassette_frame()
        
        # Song info section
        if current_song:
            song_title = current_song[:35] + "..." if len(current_song) > 35 else current_song
            song_info = f"🎵 Now Playing: {song_title}\n🎤 Artist: AI Generated\n⏱️ 2:30 / 3:45"
        else:
            song_info = "🎵 No song playing\n🎤 Select a track\n⏱️ 0:00 / 0:00"
        
        # Progress bar
        progress_filled = int(20 * 0.6)  # 60% progress for demo
        progress_bar = "█" * progress_filled + "░" * (20 - progress_filled)
        
        # Volume bar
        volume_filled = int(20 * volume)
        volume_bar = "█" * volume_filled + "░" * (20 - volume_filled)
        
        # Controls
        controls = [
            "⏮️  Previous    ⏸️  Pause    ⏭️  Next    🔀 Shuffle",
            "🔊 Volume: " + volume_bar + f" {int(volume * 100)}%",
            "Progress: " + progress_bar,
            "",
            "Commands: p(previous) | space(pause) | n(next) | q(quit)"
        ]
        
        # Main player panel
        player_content = f"{cassette_art}\n\n{song_info}\n\n" + "\n".join(controls)
        
        player_panel = Panel(
            Align.center(Text(player_content, style="bright_green")),
            box=box.HEAVY,
            border_style="bright_green",
            title="🎵 Spotify AI Edition 🎵",
            padding=(1, 2)
        )
        
        self.console.print(player_panel)

    def clear_screen(self):
        """Clear screen and reset layout"""
        if RICH_AVAILABLE:
            self.console.clear()
            self.setup_layout()

    def show_voice_settings(self, current_voice, available_voices):
        """Show enhanced character selection menu with animations"""
        if not RICH_AVAILABLE:
            print("\n=== Character Selection ===")
            for key, (voice_id, desc) in available_voices.items():
                status = "✓" if voice_id == current_voice else " "
                print(f"{key}. [{status}] {desc}")
            return self.get_user_input("\nSelect character (or 'back')")
            
        self.clear_screen()
        
        voice_table = Table(
            title="✨ Choose Your Companion ✨",
            show_header=True,
            header_style="bold bright_green",
            border_style="bright_green",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        
        voice_table.add_column("Option", style="cyan")
        voice_table.add_column("Character", style="white")
        voice_table.add_column("Status", style="bright_green bold")
        
        for key, (voice_id, description) in available_voices.items():
            status = "💫 Current" if voice_id == current_voice else ""
            voice_table.add_row(f"🎭 {key}", description, status)
            
        self.console.print(Panel(
            voice_table,
            border_style="bright_green",
            box=box.ROUNDED,
            title="Character Selection"
        ))
        
        return self.get_user_input("\n✨ Select character (or 'back')")

    def print_fancy(self, message, style="bright_cyan", panel_title=None):
        """Enhanced printing with animations and effects"""
        if not RICH_AVAILABLE:
            print(message)
            return
            
        if panel_title:
            panel = Panel(
                Text(message, style=style), 
                title=f"✨ {panel_title} ✨",
                border_style=self.get_theme_color(),
                box=box.ROUNDED
            )
            self.console.print(panel)
        else:
            self.animate_text(message, style=style)

    def get_user_input(self, prompt="Enter command"):
        """Get enhanced user input with animations"""
        if RICH_AVAILABLE:
            return Prompt.ask(
                Text(f"✨ {prompt}", style="bold bright_green"),
                show_default=False
            ).strip()
        else:
            return input(f"{prompt}: ").strip()

    def confirm_action(self, prompt_text):
        """Get user confirmation with animated styling"""
        if RICH_AVAILABLE:
            return Confirm.ask(
                Text(f"💫 {prompt_text}", style="bold bright_green")
            )
        else:
            return input(f"{prompt_text} (y/n): ").lower().startswith('y')
