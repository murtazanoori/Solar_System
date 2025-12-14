#tiktok QuantumWebb
#Youtube QuantumWeb6

import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Sun properties
SUN_X, SUN_Y = WIDTH // 2, HEIGHT // 2
SUN_RADIUS = 30
SUN_COLOR = (255, 220, 100)
SUN_GLOW = (255, 200, 50)

class Star:
    def __init__(self, layer=0):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.base_brightness = random.randint(30, 255)
        self.brightness = self.base_brightness
        self.size = random.choice([1, 1, 1, 2]) if layer == 0 else 1
        self.layer = layer
        self.twinkle_speed = random.uniform(0.01, 0.05)
        self.twinkle_offset = random.uniform(0, 2 * math.pi)
        self.parallax_speed = random.uniform(0.01, 0.03) if layer > 0 else 0

class Moon:
    def __init__(self, planet, distance, radius, color):
        self.planet = planet
        self.distance = distance
        self.radius = radius
        self.color = color
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.05, 0.15)
        self.trail = []
        self.max_trail_length = 15

class Asteroid:
    def __init__(self, min_dist, max_dist):
        self.distance = random.uniform(min_dist, max_dist)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.002, 0.008)
        self.size = random.choice([1, 1, 2])
        self.brightness = random.randint(100, 200)

class Planet:
    def __init__(self, name, distance, radius, color, speed_variation=0, ellipse_factor=1.0):
        self.name = name
        self.distance = distance
        self.radius = radius
        self.color = color
        self.base_speed = 1.0 / (distance / 150)
        self.speed = self.base_speed * (1 + speed_variation)
        self.angle = random.uniform(0, 2 * math.pi)
        self.trail = []
        self.max_trail_length = 50
        self.ellipse_a = distance
        self.ellipse_b = distance * ellipse_factor
        self.rotation_angle = 0
        self.rotation_speed = random.uniform(0.01, 0.03)
        self.moons = []
        self.gradient_colors = self._generate_gradient_colors()

    def _generate_gradient_colors(self):
        colors = []
        for i in range(3):
            factor = 1.0 - (i * 0.15)
            colors.append(tuple(min(255, int(c * (1 + (1 - factor) * 0.3))) for c in self.color))
        return colors

    def add_moon(self, moon):
        self.moons.append(moon)

    def update(self, time):
        # Update orbital angle with tiny random variation
        speed_variation = math.sin(time * 0.001 + self.angle) * 0.0001
        self.angle += (self.speed + speed_variation) * 0.01
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

        # Update rotation
        self.rotation_angle += self.rotation_speed

        # Calculate elliptical orbit position
        x = SUN_X + self.ellipse_a * math.cos(self.angle)
        y = SUN_Y + self.ellipse_b * math.sin(self.angle)

        # Update trail
        self.trail.append((x, y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Update moons
        for moon in self.moons:
            moon.angle += moon.speed * 0.01
            moon_x = x + moon.distance * math.cos(moon.angle)
            moon_y = y + moon.distance * math.sin(moon.angle)
            moon.trail.append((moon_x, moon_y))
            if len(moon.trail) > moon.max_trail_length:
                moon.trail.pop(0)

        return x, y

    def draw(self, screen, font):
        if not self.trail:
            return

        x, y = self.trail[-1]

        # Draw planet trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = i / len(self.trail)
                trail_color = tuple(int(c * alpha * 0.5) for c in self.color)
                trail_radius = max(1, int(self.radius * alpha * 0.7))
                pygame.draw.circle(screen, trail_color, 
                                 (int(self.trail[i][0]), int(self.trail[i][1])), 
                                 trail_radius)

        # Draw planet with gradient layers
        for i, color in enumerate(reversed(self.gradient_colors)):
            layer_radius = self.radius - i * 2
            if layer_radius > 0:
                pygame.draw.circle(screen, color, (int(x), int(y)), layer_radius)

        # Draw moons
        for moon in self.moons:
            if moon.trail:
                # Draw moon trail
                for i in range(len(moon.trail) - 1):
                    alpha = i / len(moon.trail)
                    trail_color = tuple(int(c * alpha * 0.3) for c in moon.color)
                    pygame.draw.circle(screen, trail_color,
                                     (int(moon.trail[i][0]), int(moon.trail[i][1])), 1)

                # Draw moon
                moon_x, moon_y = moon.trail[-1]
                pygame.draw.circle(screen, moon.color, (int(moon_x), int(moon_y)), moon.radius)

        # Draw name tag with glow effect
        text = font.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=(int(x), int(y - self.radius - 15)))
        
        # Draw text shadow/glow
        glow_text = font.render(self.name, True, (50, 50, 50))
        for dx, dy in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            screen.blit(glow_text, (text_rect.x + dx, text_rect.y + dy))
        screen.blit(text, text_rect)

def draw_stars(screen, stars, time):
    for star in stars:
        # Twinkle effect
        twinkle = math.sin(time * star.twinkle_speed + star.twinkle_offset) * 0.3 + 0.7
        brightness = int(star.base_brightness * twinkle)
        color = (brightness, brightness, brightness)
        
        # Parallax movement for distant stars
        if star.layer > 0:
            star.x += star.parallax_speed
            if star.x > WIDTH:
                star.x = 0
            elif star.x < 0:
                star.x = WIDTH
        
        pygame.draw.circle(screen, color, (int(star.x), int(star.y)), star.size)

def draw_sun(screen, font, time):
    # Pulsating glow effect
    pulse = math.sin(time * 0.003) * 15

    # Draw multiple glow layers
    glow_layers = [
        (SUN_RADIUS + 60 + pulse, 0.08, (255, 180, 50)),
        (SUN_RADIUS + 45 + pulse * 0.8, 0.12, (255, 200, 70)),
        (SUN_RADIUS + 30 + pulse * 0.6, 0.18, (255, 210, 85)),
        (SUN_RADIUS + 20 + pulse * 0.4, 0.25, (255, 215, 95)),
        (SUN_RADIUS + 10 + pulse * 0.2, 0.35, (255, 218, 98)),
    ]

    for radius, alpha, color in glow_layers:
        glow_color = tuple(int(c * alpha) for c in color)
        pygame.draw.circle(screen, glow_color, (SUN_X, SUN_Y), int(radius))

    # Draw sun with gradient
    sun_layers = [
        (SUN_RADIUS, SUN_COLOR),
        (SUN_RADIUS - 5, (255, 230, 120)),
        (SUN_RADIUS - 10, (255, 240, 140)),
    ]
    
    for radius, color in sun_layers:
        if radius > 0:
            pygame.draw.circle(screen, color, (SUN_X, SUN_Y), radius)

    # Draw sun name tag with glow
    text = font.render("Sun", True, WHITE)
    text_rect = text.get_rect(center=(SUN_X, SUN_Y - SUN_RADIUS - 20))
    
    # Draw text glow
    glow_text = font.render("Sun", True, (100, 80, 30))
    for dx, dy in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        screen.blit(glow_text, (text_rect.x + dx, text_rect.y + dy))
    screen.blit(text, text_rect)

def draw_asteroid_belt(screen, asteroids):
    for asteroid in asteroids:
        x = SUN_X + asteroid.distance * math.cos(asteroid.angle)
        y = SUN_Y + asteroid.distance * math.sin(asteroid.angle)
        color = (asteroid.brightness, asteroid.brightness, asteroid.brightness)
        pygame.draw.circle(screen, color, (int(x), int(y)), asteroid.size)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Solar System - Cinematic")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # Create stars in multiple layers
    stars = []
    for _ in range(75):
        stars.append(Star(layer=0))
    for _ in range(50):
        stars.append(Star(layer=1))

    # Create planets
    planets = [
        Planet("Mercury", 95, 5, (180, 180, 180), 0.15, 0.96),
        Planet("Venus", 135, 9, (255, 220, 120), 0.08, 0.98),
        Planet("Earth", 185, 10, (100, 150, 255), 0.05, 1.0),
        Planet("Mars", 235, 8, (255, 120, 80), -0.03, 0.97),
        Planet("Jupiter", 320, 22, (255, 200, 140), 0.02, 1.05),
        Planet("Saturn", 400, 19, (230, 210, 160), -0.01, 1.08),
        Planet("Uranus", 480, 14, (160, 200, 255), 0.03, 1.02),
        Planet("Neptune", 540, 13, (80, 120, 255), -0.02, 1.01),
    ]

    # Add moons to Earth and Jupiter
    planets[2].add_moon(Moon(planets[2], 18, 3, (200, 200, 200)))
    planets[4].add_moon(Moon(planets[4], 30, 4, (220, 220, 220)))
    planets[4].add_moon(Moon(planets[4], 40, 3, (180, 180, 180)))

    # Create asteroid belt between Mars and Jupiter
    asteroids = []
    for _ in range(50):
        asteroids.append(Asteroid(260, 300))

    running = True
    zoom = 1.0
    zoom_direction = 1
    pan_offset_x = 0
    pan_offset_y = 0
    time_counter = 0

    while running:
        time_counter += clock.get_time()
        current_time = time_counter

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill(BLACK)

        # Cinematic zoom and pan
        zoom += 0.0003 * zoom_direction
        if zoom > 1.04 or zoom < 0.96:
            zoom_direction *= -1

        pan_offset_x = math.sin(current_time * 0.0002) * 30
        pan_offset_y = math.cos(current_time * 0.00015) * 15

        # Create temporary surface for transformations
        temp_surface = pygame.Surface((WIDTH, HEIGHT))
        temp_surface.fill(BLACK)

        # Draw everything on temp surface
        draw_stars(temp_surface, stars, current_time)
        draw_asteroid_belt(temp_surface, asteroids)
        draw_sun(temp_surface, font, current_time)

        for planet in planets:
            planet.update(current_time)
            planet.draw(temp_surface, font)

        # Apply transformations and blit to main screen
        scaled_surface = pygame.transform.scale(temp_surface, 
                                             (int(WIDTH * zoom), int(HEIGHT * zoom)))
        screen.blit(scaled_surface, 
                   (pan_offset_x - (WIDTH * zoom - WIDTH) // 2, 
                    pan_offset_y - (HEIGHT * zoom - HEIGHT) // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
