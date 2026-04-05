import pygame
from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SPEED,
    PLAYER_ACCELERATION,
    PLAYER_DRAG,
    PLAYER_TURN_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_LIVES,
    PLAYER_SCORE,
    PLAYER_SPEED_BOOST_MULTIPLIER,
    PLAYER_ACCELERATION_BOOST_MULTIPLIER,
    PLAYER_SPAWN_INVULNERABILITY_SECONDS,
    POWERUP_SPEED_DURATION_SECONDS,
    POWERUP_SHIELD_DURATION_SECONDS,
    POWERUP_BOMB_BLAST_DURATION_SECONDS,
    POWERUP_BOMB_BLAST_RADIUS_MULTIPLIER,
)
from logger import log_event
from shot import Shot


class Player(CircleShape):

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        pygame.mixer.init()
        self.player_hit_sound = pygame.mixer.Sound('sound_effects/soundreality-explosion-fx-343683.mp3')
        self.mega_bomb_sound = pygame.mixer.Sound('sound_effects/daviddumaisaudio-sci-fi-explosion-09-190268.mp3')
        self.speed_powerup_sound = pygame.mixer.Sound('sound_effects/freesound_community-boost-100537.mp3')
        self.shield_powerup_sound = pygame.mixer.Sound('sound_effects/ribhavagrawal-power-up-type-2-230549.mp3')
        self.rotation = 0
        self.shot_cooldown = 0
        self.lives = PLAYER_LIVES
        self.score = PLAYER_SCORE
        self.shield_timer = 0
        self.speed_timer = 0
        self.invulnerable_timer = 0
        self.mega_bombs = 1
        self.bomb_blast_timer = 0
        self.pending_bomb_trigger = False
        self.set_spawn_invulnerability()

    # in the Player class
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        if self.bomb_blast_timer > 0:
            self._draw_bomb_blast(screen)
        if self.invulnerable_timer > 0:
            self._draw_glow(screen, (255, 230, 120))
        if self.speed_timer > 0:
            self._draw_glow(screen, (90, 170, 255))
        if self.shield_timer > 0:
            self._draw_glow(screen, (90, 255, 140))
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def _draw_bomb_blast(self, screen):
        progress = 1 - (self.bomb_blast_timer / POWERUP_BOMB_BLAST_DURATION_SECONDS)
        max_radius = int(self.radius * POWERUP_BOMB_BLAST_RADIUS_MULTIPLIER)
        blast_radius = max(self.radius, int(max_radius * progress))
        pygame.draw.circle(screen, (255, 170, 80), self.position, blast_radius, 3)

    def _draw_glow(self, screen, color):
        glow_surface = pygame.Surface((self.radius * 6, self.radius * 6), pygame.SRCALPHA)
        center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
        for scale, alpha in ((2.2, 35), (1.8, 55), (1.45, 80)):
            pygame.draw.circle(
                glow_surface,
                (*color, alpha),
                center,
                int(self.radius * scale),
            )
        screen.blit(
            glow_surface,
            glow_surface.get_rect(center=(int(self.position.x), int(self.position.y))),
        )

    def rotate(self, dt):
        self.rotation += dt * PLAYER_TURN_SPEED
    
    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        acceleration = PLAYER_ACCELERATION
        max_speed = PLAYER_SPEED
        if self.speed_timer > 0:
            acceleration *= PLAYER_ACCELERATION_BOOST_MULTIPLIER
            max_speed *= PLAYER_SPEED_BOOST_MULTIPLIER

        self.velocity += forward * dt * acceleration
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.shot_cooldown -= dt
        self.speed_timer = max(0, self.speed_timer - dt)
        self.shield_timer = max(0, self.shield_timer - dt)
        self.invulnerable_timer = max(0, self.invulnerable_timer - dt)
        self.bomb_blast_timer = max(0, self.bomb_blast_timer - dt)

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move(dt)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move(-dt)

        self.position += self.velocity * dt
        self.velocity *= PLAYER_DRAG ** (dt * 60)
        if self.velocity.length_squared() < 0.01:
            self.velocity = pygame.Vector2(0, 0)
        self.wrap_position()

        if keys[pygame.K_SPACE]:
            self.shoot()
        if keys[pygame.K_LSHIFT]:
            self.use_mega_bomb()

    def shoot(self):
        if self.shot_cooldown > 0:
            return
        else:
            self.shot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
            
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED

    def player_hit(self):
        if self.invulnerable_timer > 0:
            log_event("spawn_invulnerability_blocked_hit")
            return "invulnerable"

        if self.shield_timer > 0:
            log_event("shield_blocked_hit")
            return "shielded"

        self.lives -= 1
        self.player_hit_sound.play()
        log_event("player_hit")
        return "damaged"

    def add_score(self, points):
        self.score += points
        log_event("asteroid_shot")

    def set_spawn_invulnerability(self):
        self.invulnerable_timer = PLAYER_SPAWN_INVULNERABILITY_SECONDS

    def use_mega_bomb(self):
        if self.mega_bombs <= 0 or self.pending_bomb_trigger:
            return False

        self.mega_bombs -= 1
        self.pending_bomb_trigger = True
        self.bomb_blast_timer = POWERUP_BOMB_BLAST_DURATION_SECONDS
        self.mega_bomb_sound.play()
        log_event("mega_bomb_used")
        return True

    def consume_bomb_trigger(self):
        if not self.pending_bomb_trigger:
            return False

        self.pending_bomb_trigger = False
        return True

    def apply_powerup(self, kind):
        if kind == "shield":
            self.shield_timer = POWERUP_SHIELD_DURATION_SECONDS
            self.shield_powerup_sound.play()
            log_event("shield_powerup_collected")
            return True
        if kind == "speed":
            self.speed_timer = POWERUP_SPEED_DURATION_SECONDS
            self.speed_powerup_sound.play()
            log_event("speed_powerup_collected")
            return True
        if kind == "bomb":
            if self.mega_bombs >= 1:
                return False
            self.mega_bombs = 1
            log_event("mega_bomb_collected")
            return True
        return False
