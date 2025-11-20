"""Audio utility functions for music and sound effects"""

import pygame

# Global music tracking
current_track = None


def play_music(track):
    """Play background music, avoiding reload if same track is already playing
    
    Args:
        track: Path to music file (relative to project root)
    """
    global current_track
    if current_track == track:
        return  # Don't reload if already playing this track
    
    try:
        current_track = track
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        print(f"🎵 Now playing: {track}")
    except pygame.error as e:
        print(f"⚠️ Could not load music '{track}': {e}")


def stop_music():
    """Stop currently playing music"""
    global current_track
    pygame.mixer.music.stop()
    current_track = None


def set_music_volume(volume):
    """Set music volume
    
    Args:
        volume: Float between 0.0 and 1.0
    """
    pygame.mixer.music.set_volume(volume)

