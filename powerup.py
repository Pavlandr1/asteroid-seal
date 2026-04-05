import math
import random

import pygame

from circleshape import CircleShape
from constants import LINE_WIDTH, POWERUP_RADIUS


class PowerUp(CircleShape):
    STYLES = {
        "shield": {"label": "d", "color": (120, 255, 140)},
        "speed": {"label": "s", "color": (120, 170, 255)},
        "bomb": {"label": "m", "color": (255, 165, 110)},
    }

    def __init__(self, x, y, kind):
        super().__init__(x, y, POWERUP_RADIUS)
        self.kind = kind
        self.base_position = pygame.Vector2(x, y)
        self.phase = random.uniform(0, math.tau)

    def update(self, dt):
        self.phase += dt * 2
        self.position.y = self.base_position.y + math.sin(self.phase) * 4

    def draw(self, screen):
        style = self.STYLES[self.kind]
        bubble_surface = pygame.Surface(
            (int(self.radius * 4), int(self.radius * 5)), pygame.SRCALPHA
        )
        bubble_rect = pygame.Rect(0, 0, int(self.radius * 1.4), int(self.radius * 1.9))
        bubble_rect.center = (bubble_surface.get_width() // 2, bubble_surface.get_height() // 2)

        for inflate, alpha in ((10, 35), (4, 55)):
            glow_rect = bubble_rect.inflate(inflate, inflate)
            pygame.draw.ellipse(bubble_surface, (*style["color"], alpha), glow_rect, 0)

        pygame.draw.ellipse(bubble_surface, (*style["color"], 170), bubble_rect, LINE_WIDTH)
        highlight = bubble_rect.inflate(-int(self.radius * 0.9), -int(self.radius * 1.2))
        highlight.move_ip(-3, -4)
        pygame.draw.ellipse(bubble_surface, (255, 255, 255, 140), highlight, 1)

        font = pygame.font.SysFont("arial", 20, bold=True)
        text = font.render(style["label"], True, style["color"])
        text_rect = text.get_rect(center=bubble_rect.center)
        bubble_surface.blit(text, text_rect)

        screen.blit(
            bubble_surface,
            bubble_surface.get_rect(center=(int(self.position.x), int(self.position.y))),
        )
