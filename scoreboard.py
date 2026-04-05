import pygame


class Scoreboard(pygame.sprite.Sprite):

    def __init__(self, x, y, player):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.math.Vector2(x, y)
        self.player = player

    def draw(self, screen):
        font = pygame.font.SysFont("arial", 36)
        lives_text = font.render(f"Lives: {self.player.lives}", True, "white")
        score_text = font.render(f"Score: {self.player.score}", True, "white")
        bomb_text = font.render(f"Bomb: {self.player.mega_bombs} [LSHIFT]", True, "white")
        screen.blit(lives_text, (self.position.x, self.position.y))
        screen.blit(score_text, (self.position.x, self.position.y + 40))
        screen.blit(bomb_text, (self.position.x, self.position.y + 80))