
import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS

class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x,y, SHOT_RADIUS)
        pygame.mixer.init()
        self.shot_sound = pygame.mixer.Sound('sound_effects/freesound_community-laser-zap-90575.mp3')
        self.shot_sound.play()
    
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)
    
    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()