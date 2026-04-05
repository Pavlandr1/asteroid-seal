import random

import pygame
from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, LINE_WIDTH, ASTEROID_POINTS
from logger import log_event

class Asteroid(CircleShape):

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        pygame.mixer.init()
        self.hit_sound = pygame.mixer.Sound('sound_effects/dragon-studio-explosion-fx-425453.mp3')
        self.points = ASTEROID_POINTS[self.kind()]
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-30, 30)
        point_count = random.randint(9, 13)
        self.shape_offsets = [random.uniform(0.78, 1.22) for _ in range(point_count)]

    def draw(self, screen):
        points = []
        for index, offset in enumerate(self.shape_offsets):
            angle = self.rotation + (360 / len(self.shape_offsets)) * index
            point = self.position + pygame.Vector2(0, self.radius * offset).rotate(angle)
            points.append(point)
        pygame.draw.polygon(screen, "white", points, LINE_WIDTH)
    
    def update(self, dt):
        self.position = self.position + self.velocity * dt
        self.rotation += self.spin * dt
        self.wrap_position()
    def kind(self):
        if self.radius > 40:
            return 1
        elif self.radius > 20:
            return 2
        else:
            return 3

    def split(self):
        
        self.kill()
        self.hit_sound.play()
        if self.radius > ASTEROID_MIN_RADIUS:
            log_event("asteroid_split")
            random_angle = random.uniform(20, 50)
            new_velocity = self.velocity.rotate(random_angle)
            new_velocity2 = self.velocity.rotate(-random_angle)
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            Asteroid(self.position.x, self.position.y, new_radius).velocity = new_velocity * 1.2  # make the new asteroid a bit faster than the original one
            Asteroid(self.position.x, self.position.y, new_radius).velocity = new_velocity2
        else:
            return []