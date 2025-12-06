import sys
import math
import random

import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_a, K_d, K_SPACE, K_s, K_DOWN, K_RETURN, K_r, K_i

from OpenGL.GL import *
from OpenGL.GLU import *


# Window / timing
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# 3D projection / camera
FOV = 70.0
NEAR_PLANE = 0.1
FAR_PLANE = 200.0

# Lane system (X positions in world space)
LANE_POSITIONS = [-2.0, 0.0, 2.0]
LANE_SWITCH_SPEED = 8.0  # units per second

# Player
PLAYER_SIZE = 0.8
PLAYER_WIDTH = 0.8
PLAYER_HEIGHT = 1.6
PLAYER_HEIGHT_SLIDE = 0.6
PLAYER_DEPTH = 1.0
PLAYER_START_Y = 0.5
PLAYER_START_Z = 0.0

# Jump & slide
JUMP_FORCE = 9.0
GRAVITY = -24.0
SLIDE_DURATION = 0.6

# Camera
CAMERA_OFFSET_Y = 3.0
CAMERA_OFFSET_Z = 8.0
CAMERA_FOLLOW_STIFFNESS = 10.0  # higher = snappier

# Runner movement
BASE_FORWARD_SPEED = 10.0      # units per second
MAX_FORWARD_SPEED = 20.0
FORWARD_ACCEL_PER_SEC = 0.2

GRID_LENGTH = 80.0             # how far in Z we draw floor
GRID_STEP_Z = 2.0
GRID_STEP_X = 2.0

# Obstacles
OBSTACLE_SPAWN_DISTANCE_Z = -80.0
OBSTACLE_DESPAWN_Z = 5.0
OBSTACLE_MIN_GAP_Z = 8.0
OBSTACLE_MAX_GAP_Z = 16.0

OBSTACLE_HIGH_HEIGHT = 3.0   # must be avoided by lane
OBSTACLE_MID_HEIGHT = 2.0    # must jump over
OBSTACLE_LOW_HEIGHT = 1.0    # must slide under
OBSTACLE_WIDTH = 1.4
OBSTACLE_DEPTH = 2.0

# Collectibles (orbs)
ORB_SPAWN_DISTANCE_Z = -80.0
ORB_DESPAWN_Z = 5.0
ORB_MIN_GAP_Z = 4.0
ORB_MAX_GAP_Z = 12.0
ORB_RADIUS = 0.3
ORB_Y = 1.5
ORB_SCORE_VALUE = 10.0

# Shield
SHIELD_DURATION = 4.0

# Screen shake
SHAKE_DURATION = 0.3
SHAKE_INTENSITY = 0.3

# Difficulty
DIFFICULTY_RAMP_INTERVAL = 100.0  # increase difficulty every 100 units
OBSTACLE_SPAWN_RAMP = 0.05  # decrease gap by this amount per interval
SPEED_RAMP = 0.5  # additional speed per interval


# Pygame / timing
clock = None

# Player state
current_lane_index = 1  # 0=left, 1=center, 2=right
target_lane_index = 1

player_x = LANE_POSITIONS[current_lane_index]
player_y = PLAYER_START_Y
player_z = PLAYER_START_Z

lane_switching = False

# Jump & slide state
player_vertical_velocity = 0.0
is_jumping = False
is_grounded = True
is_sliding = False
slide_timer = 0.0

# Camera
camera_x = 0.0
camera_y = CAMERA_OFFSET_Y
camera_z = CAMERA_OFFSET_Z

# Forward motion
forward_speed = BASE_FORWARD_SPEED
distance_travelled = 0.0

floor_scroll_z = 0.0  # offset to make grid "move"

# Obstacles
obstacles = []          # list of dicts
last_obstacle_z = OBSTACLE_SPAWN_DISTANCE_Z

# Collectibles
orbs = []               # list of dicts
last_orb_z = ORB_SPAWN_DISTANCE_Z
orbs_collected = 0

# Shield
shield_active = False
shield_timer = 0.0

# Screen shake
shake_timer = 0.0
shake_intensity = 0.0

# Score
score = 0.0

# Game state
game_state = "menu"  # "menu", "running", "game_over", "instructions"

# Fonts
font_small = None
font_large = None

# Audio
music = None
sounds = {}

running = True


def init_pygame():
    global clock, font_small, font_large, music, sounds
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        DOUBLEBUF | OPENGL
    )
    pygame.display.set_caption("Temple Run 3D - Phase 8")
    clock = pygame.time.Clock()
    font_small = pygame.font.Font(None, 36)
    font_large = pygame.font.Font(None, 72)
    
    # Try to load audio files (fail gracefully if they don't exist)
    try:
        pygame.mixer.music.load("music_loop.ogg")
        music = True  # Flag that music is loaded
        sounds["jump"] = pygame.mixer.Sound("jump.wav")
        sounds["slide"] = pygame.mixer.Sound("slide.wav")
        sounds["orb"] = pygame.mixer.Sound("orb.wav")
        sounds["hit"] = pygame.mixer.Sound("hit.wav")
        sounds["shield"] = pygame.mixer.Sound("shield.wav")
    except:
        music = None  # Audio files not found, continue without audio


def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    glClearColor(0.02, 0.02, 0.05, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = WINDOW_WIDTH / float(WINDOW_HEIGHT)
    gluPerspective(FOV, aspect, NEAR_PLANE, FAR_PLANE)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def setup_camera():
    global shake_timer, shake_intensity
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Apply screen shake
    cam_x = camera_x
    cam_y = camera_y
    if shake_timer > 0.0:
        offset_x = (random.random() - 0.5) * shake_intensity
        offset_y = (random.random() - 0.5) * shake_intensity
        cam_x += offset_x
        cam_y += offset_y
        shake_timer -= (1.0 / FPS)
        if shake_timer <= 0.0:
            shake_timer = 0.0
            shake_intensity = 0.0
    
    gluLookAt(
        cam_x, cam_y, camera_z,
        0.0, 0.0, 0.0,
        0.0, 1.0, 0.0
    )


def create_orb(lane_index, z, is_shield=False):
    x = LANE_POSITIONS[lane_index]
    return {
        "x": x,
        "y": ORB_Y,
        "z": z,
        "radius": ORB_RADIUS,
        "active": True,
        "is_shield": is_shield,
    }


def create_obstacle(lane_index, z, obstacle_type):
    x = LANE_POSITIONS[lane_index]

    if obstacle_type == "high":
        height = OBSTACLE_HIGH_HEIGHT
        y = height / 2.0
    elif obstacle_type == "mid":
        height = OBSTACLE_MID_HEIGHT
        y = height / 2.0
    else:
        height = OBSTACLE_LOW_HEIGHT
        y = height / 2.0

    return {
        "type": obstacle_type,
        "lane_index": lane_index,
        "x": x,
        "y": y,
        "z": z,
        "width": OBSTACLE_WIDTH,
        "height": height,
        "depth": OBSTACLE_DEPTH,
        "active": True,
    }


def maybe_spawn_obstacles():
    global last_obstacle_z, obstacles

    # We spawn based on "virtual" distance travelled along Z
    # Place next obstacle further down negative Z axis
    # More negative = further away.

    # If the last obstacle is too close to spawn distance, do nothing
    if last_obstacle_z - OBSTACLE_SPAWN_DISTANCE_Z > -OBSTACLE_MIN_GAP_Z:
        return

    # Difficulty-based gap (closer obstacles as distance increases)
    difficulty_level = int(distance_travelled / DIFFICULTY_RAMP_INTERVAL)
    gap_reduction = difficulty_level * OBSTACLE_SPAWN_RAMP
    min_gap = max(OBSTACLE_MIN_GAP_Z - gap_reduction, 3.0)
    max_gap = max(OBSTACLE_MAX_GAP_Z - gap_reduction, 5.0)
    
    # Decide random gap
    gap = random.uniform(min_gap, max_gap)
    last_obstacle_z -= gap

    lane_index = random.randint(0, len(LANE_POSITIONS) - 1)
    obstacle_type = random.choice(["high", "mid", "low"])

    obstacle = create_obstacle(lane_index, last_obstacle_z, obstacle_type)
    obstacles.append(obstacle)


def maybe_spawn_orbs():
    global last_orb_z, orbs

    # If the last orb is too close to spawn distance, do nothing
    if last_orb_z - ORB_SPAWN_DISTANCE_Z > -ORB_MIN_GAP_Z:
        return

    # Decide random gap
    gap = random.uniform(ORB_MIN_GAP_Z, ORB_MAX_GAP_Z)
    last_orb_z -= gap

    lane_index = random.randint(0, len(LANE_POSITIONS) - 1)
    # 10% chance for shield orb
    is_shield = random.random() < 0.1

    orb = create_orb(lane_index, last_orb_z, is_shield)
    orbs.append(orb)


def update_obstacles(delta_time):
    global obstacles

    speed = forward_speed

    for obstacle in obstacles:
        obstacle["z"] += speed * delta_time

    # Remove obstacles that passed the camera
    new_obstacles = []
    for o in obstacles:
        if o["z"] < OBSTACLE_DESPAWN_Z:
            new_obstacles.append(o)
    obstacles = new_obstacles


def update_orbs(delta_time):
    global orbs

    speed = forward_speed

    for orb in orbs:
        orb["z"] += speed * delta_time

    # Remove orbs that passed the camera
    new_orbs = []
    for o in orbs:
        if o["z"] < ORB_DESPAWN_Z:
            new_orbs.append(o)
    orbs = new_orbs


def draw_cube(size):
    half = size / 2.0

    glBegin(GL_QUADS)

    # Front (z+)
    glColor3f(0.2, 0.8, 1.0)
    glVertex3f(-half, -half, half)
    glVertex3f(half, -half, half)
    glVertex3f(half, half, half)
    glVertex3f(-half, half, half)

    # Back (z-)
    glColor3f(0.1, 0.3, 0.8)
    glVertex3f(-half, -half, -half)
    glVertex3f(-half, half, -half)
    glVertex3f(half, half, -half)
    glVertex3f(half, -half, -half)

    # Left (x-)
    glColor3f(0.4, 0.1, 0.6)
    glVertex3f(-half, -half, -half)
    glVertex3f(-half, -half, half)
    glVertex3f(-half, half, half)
    glVertex3f(-half, half, -half)

    # Right (x+)
    glColor3f(0.8, 0.1, 0.4)
    glVertex3f(half, -half, -half)
    glVertex3f(half, half, -half)
    glVertex3f(half, half, half)
    glVertex3f(half, -half, half)

    # Top (y+)
    glColor3f(0.8, 0.8, 1.0)
    glVertex3f(-half, half, -half)
    glVertex3f(-half, half, half)
    glVertex3f(half, half, half)
    glVertex3f(half, half, -half)

    # Bottom (y-)
    glColor3f(0.0, 0.0, 0.0)
    glVertex3f(-half, -half, -half)
    glVertex3f(half, -half, -half)
    glVertex3f(half, -half, half)
    glVertex3f(-half, -half, half)

    glEnd()


def update_player(delta_time):
    global player_x, current_lane_index

    target_x = LANE_POSITIONS[target_lane_index]

    # Move toward target_x smoothly
    dx = target_x - player_x
    max_step = LANE_SWITCH_SPEED * delta_time

    if abs(dx) <= max_step:
        player_x = target_x
        current_lane_index = target_lane_index
    else:
        if dx > 0:
            player_x += max_step
        else:
            player_x -= max_step


def update_vertical_motion(delta_time):
    global player_y, player_vertical_velocity, is_jumping, is_grounded, is_sliding, slide_timer

    # Update slide timer
    if is_sliding:
        slide_timer -= delta_time
        if slide_timer <= 0.0:
            is_sliding = False

    # Update jump physics
    if is_jumping:
        player_vertical_velocity += GRAVITY * delta_time
        player_y += player_vertical_velocity * delta_time

        # Clamp at ground
        if player_y <= PLAYER_START_Y:
            player_y = PLAYER_START_Y
            player_vertical_velocity = 0.0
            is_jumping = False
            is_grounded = True


def update_shield(delta_time):
    global shield_active, shield_timer

    if shield_active:
        shield_timer -= delta_time
        if shield_timer <= 0.0:
            shield_active = False


def update_score():
    global score
    score = distance_travelled + (orbs_collected * ORB_SCORE_VALUE)


def update_camera(delta_time):
    global camera_x, camera_y, camera_z

    # Desired camera X is player's lane X
    target_cam_x = player_x

    dx = target_cam_x - camera_x
    camera_x += dx * CAMERA_FOLLOW_STIFFNESS * delta_time

    camera_y = CAMERA_OFFSET_Y
    camera_z = CAMERA_OFFSET_Z


def update_forward_motion(delta_time):
    global forward_speed, distance_travelled, floor_scroll_z

    # Difficulty-based speed ramp
    difficulty_level = int(distance_travelled / DIFFICULTY_RAMP_INTERVAL)
    base_max_speed = MAX_FORWARD_SPEED + (difficulty_level * SPEED_RAMP)
    
    forward_speed += FORWARD_ACCEL_PER_SEC * delta_time
    if forward_speed > base_max_speed:
        forward_speed = base_max_speed

    distance_travelled += forward_speed * delta_time

    # Scroll the floor so it looks like we move along -Z
    floor_scroll_z += forward_speed * delta_time

    # Wrap scroll to avoid huge values
    grid_period = GRID_STEP_Z
    if floor_scroll_z >= grid_period:
        floor_scroll_z -= grid_period


def draw_neon_floor():
    glPushMatrix()

    glColor3f(0.0, 0.9, 0.9)

    glBegin(GL_LINES)

    # Z lines (parallel to Z axis) – lane-ish guides
    z_start = -GRID_LENGTH - floor_scroll_z
    z_end = floor_scroll_z

    x = -10.0
    while x <= 10.0:
        z = z_start
        glVertex3f(x, 0.0, z)
        glVertex3f(x, 0.0, z_end)
        x += GRID_STEP_X

    # X lines (across track)
    x_min = -10.0
    x_max = 10.0

    z = z_start
    while z <= z_end:
        glVertex3f(x_min, 0.0, z)
        glVertex3f(x_max, 0.0, z)
        z += GRID_STEP_Z

    glEnd()
    glPopMatrix()


def draw_obstacle(obstacle):
    x = obstacle["x"]
    y = obstacle["y"]
    z = obstacle["z"]
    width = obstacle["width"]
    height = obstacle["height"]
    depth = obstacle["depth"]

    glPushMatrix()
    glTranslatef(x, y, z)

    # Use different color for different obstacle types
    if obstacle["type"] == "high":
        glColor3f(1.0, 0.2, 0.2)
    elif obstacle["type"] == "mid":
        glColor3f(1.0, 0.4, 0.0)
    else:
        glColor3f(1.0, 0.6, 0.0)

    # Scale cube-like primitive
    glScalef(width, height, depth)
    draw_cube(1.0)
    glPopMatrix()


def draw_obstacles():
    for obstacle in obstacles:
        draw_obstacle(obstacle)


def draw_orb(orb):
    glPushMatrix()
    glTranslatef(orb["x"], orb["y"], orb["z"])

    if orb["is_shield"]:
        glColor3f(0.5, 0.8, 1.0)  # Blue for shield
    else:
        glColor3f(1.0, 0.9, 0.2)  # Yellow for normal orb

    # Draw as a sphere-like shape (using scaled cube for simplicity)
    glScalef(ORB_RADIUS * 2, ORB_RADIUS * 2, ORB_RADIUS * 2)
    draw_cube(1.0)
    glPopMatrix()


def draw_orbs():
    for orb in orbs:
        if orb["active"]:
            draw_orb(orb)


def draw_player():
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    
    # Scale down visually when sliding
    if is_sliding:
        glScalef(1.0, PLAYER_HEIGHT_SLIDE / PLAYER_HEIGHT, 1.0)
    
    # Shield glow effect
    if shield_active:
        # Draw outer glow
        glPushMatrix()
        glScalef(1.3, 1.3, 1.3)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.3, 0.6, 1.0, 0.3)
        draw_cube(PLAYER_SIZE)
        glDisable(GL_BLEND)
        glPopMatrix()
    
    draw_cube(PLAYER_SIZE)
    glPopMatrix()


def draw_speed_lines():
    # Draw speed lines when moving fast
    if forward_speed > 15.0:
        glPushMatrix()
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)
        
        num_lines = 10
        for i in range(num_lines):
            x = random.uniform(-8.0, 8.0)
            y = random.uniform(0.5, 5.0)
            z = random.uniform(-5.0, 5.0)
            
            glVertex3f(x, y, z)
            glVertex3f(x, y - 1.0, z + 2.0)
        
        glEnd()
        glPopMatrix()


def render_text_gl(text, x, y, color=(255, 255, 255), font=None):
    """Render text using OpenGL texture"""
    if font is None:
        font = font_small
    
    try:
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width, height = text_surface.get_size()
        
        if width == 0 or height == 0:
            return
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        texture_id = glGenTextures(1)
        # Handle both int and list return types
        if isinstance(texture_id, (list, tuple)):
            texture_id = texture_id[0]
        
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        # Texture coordinates: pygame images are stored top-to-bottom, OpenGL expects bottom-to-top
        # So we flip V coordinates
        glTexCoord2f(0, 0)  # Top-left of texture -> Top-left of screen
        glVertex2f(x, y)
        glTexCoord2f(1, 0)  # Top-right of texture -> Top-right of screen
        glVertex2f(x + width, y)
        glTexCoord2f(1, 1)  # Bottom-right of texture -> Bottom-right of screen
        glVertex2f(x + width, y + height)
        glTexCoord2f(0, 1)  # Bottom-left of texture -> Bottom-left of screen
        glVertex2f(x, y + height)
        glEnd()
        
        glDeleteTextures(1, [texture_id])
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
    except Exception as e:
        # Fallback: just draw a rectangle if text rendering fails
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + 200, y)
        glVertex2f(x + 200, y + 30)
        glVertex2f(x, y + 30)
        glEnd()


def draw_hud():
    # Score
    render_text_gl(f"Score: {int(score)}", 10, 10, (255, 255, 255), font_small)
    
    # Distance
    render_text_gl(f"Distance: {int(distance_travelled)}", 10, 50, (255, 255, 255), font_small)
    
    # Speed
    render_text_gl(f"Speed: {int(forward_speed)}", 10, 90, (255, 255, 255), font_small)
    
    # Shield indicator
    if shield_active:
        render_text_gl(f"SHIELD: {int(shield_timer)}s", 10, 130, (100, 200, 255), font_small)
    
    # Difficulty level
    difficulty_level = int(distance_travelled / DIFFICULTY_RAMP_INTERVAL)
    render_text_gl(f"Level: {difficulty_level + 1}", 10, 170, (255, 200, 100), font_small)


def draw_menu():
    # Calculate title position
    title_width = font_large.size("TEMPLE RUN 3D")[0]
    title_height = font_large.size("TEMPLE RUN 3D")[1]
    title_x = (WINDOW_WIDTH - title_width) // 2
    title_y = WINDOW_HEIGHT // 2 - 100
    render_text_gl("TEMPLE RUN 3D", title_x, title_y, (255, 255, 255), font_large)

    # Calculate start button position
    start_width = font_small.size("Press ENTER to Start")[0]
    start_height = font_small.size("Press ENTER to Start")[1]
    start_x = (WINDOW_WIDTH - start_width) // 2
    start_y = WINDOW_HEIGHT // 2
    render_text_gl("Press ENTER to Start", start_x, start_y, (200, 200, 200), font_small)

    # Calculate instructions position
    inst_width = font_small.size("Press I for Instructions")[0]
    inst_height = font_small.size("Press I for Instructions")[1]
    inst_x = (WINDOW_WIDTH - inst_width) // 2
    inst_y = WINDOW_HEIGHT // 2 + 50
    render_text_gl("Press I for Instructions", inst_x, inst_y, (200, 200, 200), font_small)


def draw_instructions():
    title_surface = font_large.render("INSTRUCTIONS", True, (255, 255, 255))
    title_width, title_height = title_surface.get_size()
    title_x = (WINDOW_WIDTH - title_width) // 2
    render_text_gl("INSTRUCTIONS", title_x, 100, (255, 255, 255), font_large)
    
    y_offset = 200
    controls = [
        "A / LEFT ARROW: Move Left",
        "D / RIGHT ARROW: Move Right",
        "SPACE: Jump",
        "S / DOWN ARROW: Slide",
        "",
        "Avoid obstacles by:",
        "- Switching lanes",
        "- Jumping over mid obstacles",
        "- Sliding under low obstacles",
        "",
        "Collect yellow orbs for points",
        "Blue orbs give temporary shield",
        "",
        "Press ESC to go back"
    ]
    
    for line in controls:
        if line:  # Skip empty lines
            text_width = font_small.size(line)[0]
            text_x = (WINDOW_WIDTH - text_width) // 2
            render_text_gl(line, text_x, y_offset, (255, 255, 255), font_small)
        y_offset += 40


def draw_game_over():
    title_width = font_large.size("GAME OVER")[0]
    title_x = (WINDOW_WIDTH - title_width) // 2
    title_y = WINDOW_HEIGHT // 2 - 100
    render_text_gl("GAME OVER", title_x, title_y, (255, 0, 0), font_large)

    score_str = f"Final Score: {int(score)}"
    score_width = font_small.size(score_str)[0]
    score_x = (WINDOW_WIDTH - score_width) // 2
    score_y = WINDOW_HEIGHT // 2
    render_text_gl(score_str, score_x, score_y, (255, 255, 255), font_small)

    restart_width = font_small.size("Press R to Restart")[0]
    restart_x = (WINDOW_WIDTH - restart_width) // 2
    restart_y = WINDOW_HEIGHT // 2 + 50
    render_text_gl("Press R to Restart", restart_x, restart_y, (200, 200, 200), font_small)

    quit_width = font_small.size("Press ESC to Quit")[0]
    quit_x = (WINDOW_WIDTH - quit_width) // 2
    quit_y = WINDOW_HEIGHT // 2 + 100
    render_text_gl("Press ESC to Quit", quit_x, quit_y, (200, 200, 200), font_small)


def trigger_screen_shake(intensity):
    global shake_timer, shake_intensity
    shake_timer = SHAKE_DURATION
    shake_intensity = intensity


def check_player_obstacle_collisions():
    # Skip collision if shield is active (but trigger screen shake)
    if shield_active:
        trigger_screen_shake(0.2)
        if "hit" in sounds:
            sounds["hit"].play()
        return False

    player_min_x = player_x - PLAYER_WIDTH / 2.0
    player_max_x = player_x + PLAYER_WIDTH / 2.0
    
    # Use sliding height if sliding
    if is_sliding:
        effective_height = PLAYER_HEIGHT_SLIDE
        player_min_y = player_y - effective_height / 2.0
        player_max_y = player_y + effective_height / 2.0
    else:
        player_min_y = player_y - PLAYER_HEIGHT / 2.0
        player_max_y = player_y + PLAYER_HEIGHT / 2.0
    
    player_min_z = player_z - PLAYER_DEPTH / 2.0
    player_max_z = player_z + PLAYER_DEPTH / 2.0

    for obstacle in obstacles:
        half_w = obstacle["width"] / 2.0
        half_h = obstacle["height"] / 2.0
        half_d = obstacle["depth"] / 2.0

        ox = obstacle["x"]
        oy = obstacle["y"]
        oz = obstacle["z"]

        obs_min_x = ox - half_w
        obs_max_x = ox + half_w
        obs_min_y = oy - half_h
        obs_max_y = oy + half_h
        obs_min_z = oz - half_d
        obs_max_z = oz + half_d

        overlap_x = (player_min_x <= obs_max_x) and (player_max_x >= obs_min_x)
        overlap_y = (player_min_y <= obs_max_y) and (player_max_y >= obs_min_y)
        overlap_z = (player_min_z <= obs_max_z) and (player_max_z >= obs_min_z)

        if overlap_x and overlap_y and overlap_z:
            trigger_screen_shake(SHAKE_INTENSITY)
            if "hit" in sounds:
                sounds["hit"].play()
            return True

    return False


def check_player_orb_collisions():
    global orbs, orbs_collected, shield_active, shield_timer

    player_center_x = player_x
    player_center_y = player_y
    player_center_z = player_z

    # Simple sphere vs AABB collision
    for orb in orbs:
        if not orb["active"]:
            continue

        dx = orb["x"] - player_center_x
        dy = orb["y"] - player_center_y
        dz = orb["z"] - player_center_z
        dist_sq = dx * dx + dy * dy + dz * dz
        collision_dist = ORB_RADIUS + max(PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_DEPTH) / 2.0
        collision_dist_sq = collision_dist * collision_dist

        if dist_sq < collision_dist_sq:
            orb["active"] = False
            orbs_collected += 1

            if orb["is_shield"]:
                shield_active = True
                shield_timer = SHIELD_DURATION
                if "shield" in sounds:
                    sounds["shield"].play()
            else:
                if "orb" in sounds:
                    sounds["orb"].play()


def handle_jump_input():
    global player_vertical_velocity, is_jumping, is_grounded

    if is_grounded and not is_sliding:
        player_vertical_velocity = JUMP_FORCE
        is_jumping = True
        is_grounded = False
        if "jump" in sounds:
            sounds["jump"].play()


def handle_slide_input():
    global is_sliding, slide_timer

    if is_grounded and not is_jumping:
        is_sliding = True
        slide_timer = SLIDE_DURATION
        if "slide" in sounds:
            sounds["slide"].play()


def handle_lane_input(key):
    global target_lane_index

    if key in (K_LEFT, K_a):
        if target_lane_index > 0:
            target_lane_index -= 1
    elif key in (K_RIGHT, K_d):
        if target_lane_index < len(LANE_POSITIONS) - 1:
            target_lane_index += 1
    elif key == K_SPACE:
        handle_jump_input()
    elif key in (K_s, K_DOWN):
        handle_slide_input()


def reset_game():
    global player_x, player_y, player_z, current_lane_index, target_lane_index
    global player_vertical_velocity, is_jumping, is_grounded, is_sliding, slide_timer
    global forward_speed, distance_travelled, floor_scroll_z
    global obstacles, last_obstacle_z, orbs, last_orb_z, orbs_collected
    global shield_active, shield_timer, score, shake_timer, shake_intensity

    # Reset player
    current_lane_index = 1
    target_lane_index = 1
    player_x = LANE_POSITIONS[current_lane_index]
    player_y = PLAYER_START_Y
    player_z = PLAYER_START_Z
    player_vertical_velocity = 0.0
    is_jumping = False
    is_grounded = True
    is_sliding = False
    slide_timer = 0.0

    # Reset motion
    forward_speed = BASE_FORWARD_SPEED
    distance_travelled = 0.0
    floor_scroll_z = 0.0

    # Reset obstacles and orbs
    obstacles = []
    last_obstacle_z = OBSTACLE_SPAWN_DISTANCE_Z
    orbs = []
    last_orb_z = ORB_SPAWN_DISTANCE_Z
    orbs_collected = 0

    # Reset shield, score, and shake
    shield_active = False
    shield_timer = 0.0
    score = 0.0
    shake_timer = 0.0
    shake_intensity = 0.0


def handle_events():
    global running, game_state

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if game_state == "menu":
                if event.key == K_RETURN:
                    reset_game()
                    game_state = "running"
                    if music is not None:
                        try:
                            pygame.mixer.music.play(-1)  # Loop music
                        except:
                            pass
                elif event.key == K_i:
                    game_state = "instructions"
                elif event.key == K_ESCAPE:
                    running = False
            elif game_state == "instructions":
                if event.key == K_ESCAPE:
                    game_state = "menu"
            elif game_state == "game_over":
                if event.key == K_r:
                    reset_game()
                    game_state = "running"
                elif event.key == K_ESCAPE:
                    running = False
            elif game_state == "running":
                if event.key == K_ESCAPE:
                    game_state = "menu"
                else:
                    handle_lane_input(event.key)


def main():
    global running, game_state

    init_pygame()
    init_opengl()

    while running:
        delta_ms = clock.tick(FPS)
        delta_time = delta_ms / 1000.0

        handle_events()

        if game_state == "running":
            update_player(delta_time)
            update_vertical_motion(delta_time)
            update_forward_motion(delta_time)
            update_camera(delta_time)
            update_shield(delta_time)
            maybe_spawn_obstacles()
            update_obstacles(delta_time)
            maybe_spawn_orbs()
            update_orbs(delta_time)
            check_player_orb_collisions()
            update_score()

            hit = check_player_obstacle_collisions()
            if hit:
                game_state = "game_over"

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            setup_camera()
            draw_neon_floor()
            draw_speed_lines()
            draw_obstacles()
            draw_orbs()
            draw_player()
            
            # Switch to 2D mode for HUD
            glDisable(GL_DEPTH_TEST)
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            draw_hud()
            
            # Restore 3D mode
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glEnable(GL_DEPTH_TEST)
        elif game_state == "menu":
            glClearColor(0.05, 0.05, 0.1, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glDisable(GL_DEPTH_TEST)
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            draw_menu()
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glEnable(GL_DEPTH_TEST)
        elif game_state == "instructions":
            glClearColor(0.05, 0.05, 0.1, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glDisable(GL_DEPTH_TEST)
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            draw_instructions()
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glEnable(GL_DEPTH_TEST)
        elif game_state == "game_over":
            glClearColor(0.1, 0.05, 0.05, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glDisable(GL_DEPTH_TEST)
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            draw_game_over()
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glEnable(GL_DEPTH_TEST)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

