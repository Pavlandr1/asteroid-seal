import random
import pygame
import sys
from asteroidfield import AsteroidField
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_RESPAWN_PAUSE_SECONDS,
    POWERUP_SPEED_SCORE_THRESHOLD,
    POWERUP_SHIELD_SCORE_THRESHOLD,
    POWERUP_SPEED_SPAWN_MIN_SECONDS,
    POWERUP_SPEED_SPAWN_MAX_SECONDS,
    POWERUP_SHIELD_SPAWN_MIN_SECONDS,
    POWERUP_SHIELD_SPAWN_MAX_SECONDS,
    POWERUP_BOMB_SCORE_INTERVAL,
    POWERUP_BOMB_BLAST_RADIUS_MULTIPLIER,
)
from logger import log_state
from player import Player
from asteroid import Asteroid
from powerup import PowerUp
from scoreboard import Scoreboard
from shot import Shot


def spawn_powerup(kind, player):
    margin = 80
    spawn_position = pygame.Vector2(
        random.uniform(margin, SCREEN_WIDTH - margin),
        random.uniform(margin, SCREEN_HEIGHT - margin),
    )
    attempts = 0
    while attempts < 8 and spawn_position.distance_to(player.position) < 140:
        spawn_position.update(
            random.uniform(margin, SCREEN_WIDTH - margin),
            random.uniform(margin, SCREEN_HEIGHT - margin),
        )
        attempts += 1

    PowerUp(spawn_position.x, spawn_position.y, kind)


def detonate_mega_bomb(player, asteroids):
    blast_radius = player.radius * POWERUP_BOMB_BLAST_RADIUS_MULTIPLIER
    cleared = 0
    for asteroid in list(asteroids):
        if player.position.distance_to(asteroid.position) <= blast_radius + asteroid.radius:
            player.add_score(asteroid.points)
            asteroid.hit_sound.play()
            asteroid.kill()
            cleared += 1
    return cleared


def format_duration(total_seconds):
    total_seconds = max(0, int(total_seconds))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def show_game_over(screen, clock, score, run_duration_seconds):
    title_font = pygame.font.SysFont("arial", 64, bold=True)
    body_font = pygame.font.SysFont("arial", 36)
    hint_font = pygame.font.SysFont("arial", 28)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return

        screen.blit(overlay, (0, 0))
        title = title_font.render("Game Over", True, (255, 120, 120))
        score_text = body_font.render(f"Total Score: {score}", True, "white")
        duration_text = body_font.render(
            f"Run Duration: {format_duration(run_duration_seconds)}", True, "white"
        )
        hint = hint_font.render("Press Enter or Space to exit", True, (200, 200, 200))

        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 90)))
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
        screen.blit(duration_text, duration_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 45)))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120)))
        pygame.display.flip()
        clock.tick(60)


def main():
    print(f"Starting Asteroids with pygame version:{pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    pygame.init()
    pygame.mixer.init() 
    pygame.mixer.music.load('sound_effects/freesound_community-space-72679.mp3')
    pygame.mixer.music.play(-1)  # Loop the music indefinitely
    clock = pygame.time.Clock()
    dt = 0
    respawn_pause = 0
    run_start_time = pygame.time.get_ticks()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pause_font = pygame.font.SysFont("arial", 36)
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    AsteroidField.containers = (updatable)
    asteroidField = AsteroidField()
    Asteroid.containers = (updatable, drawable, asteroids)
    Player.containers = (updatable, drawable)
    player = Player(x, y)
    Shot.containers = (updatable, drawable, shots)
    PowerUp.containers = (updatable, drawable, powerups)
    Scoreboard.containers = (drawable)
    scoreboard = Scoreboard(20, 20, player)
    shield_spawn_timer = random.uniform(
        POWERUP_SHIELD_SPAWN_MIN_SECONDS, POWERUP_SHIELD_SPAWN_MAX_SECONDS
    )
    speed_spawn_timer = random.uniform(
        POWERUP_SPEED_SPAWN_MIN_SECONDS, POWERUP_SPEED_SPAWN_MAX_SECONDS
    )
    next_bomb_score = POWERUP_BOMB_SCORE_INTERVAL
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")

        if player.score >= POWERUP_SPEED_SCORE_THRESHOLD:
            speed_spawn_timer = max(0, speed_spawn_timer - dt)
            if (
                speed_spawn_timer <= 0
                and player.speed_timer <= 0
                and not any(powerup.kind == "speed" for powerup in powerups)
            ):
                spawn_powerup("speed", player)
                speed_spawn_timer = random.uniform(
                    POWERUP_SPEED_SPAWN_MIN_SECONDS,
                    POWERUP_SPEED_SPAWN_MAX_SECONDS,
                )

        if player.score >= POWERUP_SHIELD_SCORE_THRESHOLD:
            shield_spawn_timer = max(0, shield_spawn_timer - dt)
            if (
                shield_spawn_timer <= 0
                and player.shield_timer <= 0
                and not any(powerup.kind == "shield" for powerup in powerups)
            ):
                spawn_powerup("shield", player)
                shield_spawn_timer = random.uniform(
                    POWERUP_SHIELD_SPAWN_MIN_SECONDS,
                    POWERUP_SHIELD_SPAWN_MAX_SECONDS,
                )

        while player.score >= next_bomb_score:
            if player.mega_bombs < 1 and not any(powerup.kind == "bomb" for powerup in powerups):
                spawn_powerup("bomb", player)
            next_bomb_score += POWERUP_BOMB_SCORE_INTERVAL

        if respawn_pause > 0:
            respawn_pause = max(0, respawn_pause - dt)
            player.invulnerable_timer = max(0, player.invulnerable_timer - dt)
            player.speed_timer = max(0, player.speed_timer - dt)
            player.shot_cooldown -= dt
            for item in drawable:
                item.draw(screen)
            pause_text = pause_font.render("Respawning...", True, "yellow")
            screen.blit(pause_text, (x - 110, y + 60))
            pygame.display.flip()
            time_passed_ms = clock.tick(60)
            dt = time_passed_ms / 1000
            continue

        updatable.update(dt)

        if player.consume_bomb_trigger():
            detonate_mega_bomb(player, asteroids)

        for powerup in list(powerups):
            if player.collides_with(powerup):
                if player.apply_powerup(powerup.kind):
                    powerup.kill()

        for asteroid in list(asteroids):
            if player.collides_with(asteroid):
                hit_result = player.player_hit()
                if hit_result == "shielded":
                    asteroid.split()
                    break
                if hit_result == "invulnerable":
                    continue

                if player.lives <= 0:
                    run_duration_seconds = (pygame.time.get_ticks() - run_start_time) / 1000
                    show_game_over(screen, clock, player.score, run_duration_seconds)
                    pygame.quit()
                    return

                player.position = pygame.math.Vector2(x, y)
                player.velocity = pygame.Vector2(0, 0)
                player.set_spawn_invulnerability()
                respawn_pause = PLAYER_RESPAWN_PAUSE_SECONDS
                break
            for s in list(shots):
                if asteroid.collides_with(s):
                    player.add_score(asteroid.points)
                    asteroid.split()
                    s.kill()
                    break
        for item in drawable:
            item.draw(screen)
        pygame.display.flip()
        time_passed_ms = clock.tick(60)
        dt = time_passed_ms/1000


if __name__ == "__main__":
    main()
