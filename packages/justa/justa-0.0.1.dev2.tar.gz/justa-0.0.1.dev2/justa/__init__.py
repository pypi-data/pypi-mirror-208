from justa.body import       *
from justa.core import       *
from justa.math_utils import *
from justa.clip import       *
import pygame

def load2screen(screen = pygame.Surface, file_name = "result.png"):
    bg = pygame.image.load(file_name).convert()
    screen.blit(bg, (0, 0))
    pygame.display.flip()
