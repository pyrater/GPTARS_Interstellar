import pygame
from moviepy import VideoFileClip
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def play_video_fullscreen(video_path, rotation_angle=0):
    """
    Play a video in fullscreen mode using Pygame while maintaining aspect ratio.

    Parameters:
    - video_path (str): Path to the video file to play.
    - rotation_angle (int): Angle to rotate the video, default is 0.
    """

    # Create the full path to the video
    clip_path = os.path.join(BASE_DIR, video_path)


    # Initialize Pygame
    pygame.init()

    # Set up the screen in fullscreen mode
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()

    # Load the video file

    clip_path = os.path.join(BASE_DIR, video_path)
    
    clip = VideoFileClip(clip_path)

    # Rotate the video if necessary
    clip = clip.rotated(rotation_angle)

    # Get video dimensions
    video_width, video_height = clip.size

    # Calculate scaling factor to fit the video to the screen while maintaining aspect ratio
    scale_factor = min(screen_width / video_width, screen_height / video_height)
    scaled_width = int(video_width * scale_factor) / 2
    scaled_height = int(video_height * scale_factor)

    # Calculate offsets to center the video on the screen
    x_offset = (screen_width - scaled_width) // 2
    y_offset = (screen_height - scaled_height) // 2

    # Play the video
    for frame in clip.iter_frames(fps=30, dtype="uint8"):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Convert frame to Pygame surface and resize it to maintain aspect ratio
        frame_surface = pygame.surfarray.make_surface(frame)
        frame_surface = pygame.transform.scale(frame_surface, (scaled_width, scaled_height))

        # Blit the frame surface onto the screen at the calculated position
        screen.fill((0, 0, 0))  # Clear the screen with black
        screen.blit(frame_surface, (x_offset, y_offset))
        pygame.display.update()

    # Close Pygame when the video is done
    pygame.quit()
