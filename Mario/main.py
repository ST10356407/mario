from ursina import *
from math import atan2, degrees
import random
import os

app = Ursina()

# ---------------- WINDOW SETUP ---------------- #
window.title = "Super Mario 3D Adventure"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = True
window.fps_counter.enabled = True
window.vsync = True

# ---------------- LIGHTING ---------------- #
sun = DirectionalLight(shadows=True, rotation=(45, -45, 0))
AmbientLight(color=color.rgb(180, 180, 180))

# ---------------- SCENE SETUP ---------------- #
ground = Entity(
    model='ground/scene.gltf',
    scale=(50, 1, 50),
    position=(0, 0, 0),
    collider='box',
    receive_shadows=True
)

Sky(texture='sky_default')

# ---------------- MARIO MODEL ---------------- #
mario = Entity(
    model='mario/scene.gltf',
    scale=0.6,
    position=(0, 1, 0),
    rotation_y=0,
    collider='box',
    cast_shadows=True
)

# ---------------- CAMERA SETUP ---------------- #
camera_pivot = Entity(position=(0, 2, 0))
camera.parent = camera_pivot
camera.position = (0, 2.5, -6)
camera.rotation_x = 15
camera.fov = 80

# ---------------- MOVEMENT VARIABLES ---------------- #
speed = 6
rotation_speed = 12
jump_force = 0.25
gravity = 0.6
vertical_velocity = 0

# ---------------- COINS SETUP ---------------- #
coins = []
coin_count = 0
num_coins = 26
popup_shown = False  # Flag to prevent multiple popup triggers

# Load coin audio safely
if os.path.exists('coin/sound/coin_recieved.wav'):
    coin_sound = Audio('coin/sound/coin_recieved.wav', autoplay=False)
elif os.path.exists('sounds/coin_received.wav'):
    coin_sound = Audio('sounds/coin_received.wav', autoplay=False)
elif os.path.exists('coin_received.wav'):
    coin_sound = Audio('coin_received.wav', autoplay=False)
else:
    coin_sound = None
    print("Warning: Coin audio file not found! Make sure coin_recieved.wav exists.")

# Create 10 coins at random positions
for i in range(num_coins):
    x = random.uniform(-20, 20)
    z = random.uniform(-20, 20)
    coin = Entity(
        model='coin/scene.gltf',
        scale=0.6,
        position=(x, 0.5, z),
        collider='box',
        cast_shadows=True
    )
    coins.append(coin)

# ---------------- UI: Aesthetic Coin Counter ---------------- #
# Coin counter background
coin_counter_bg = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 120),  # Semi-transparent dark background
    scale=(0.25, 0.08),
    position=(0.75, 0.45),
    alpha=0.8
)

# Coin counter border
coin_counter_border = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(255, 215, 0, 150),  # Gold border
    scale=(0.26, 0.09),
    position=(0.75, 0.45),
    alpha=0.6
)

# Coin icon (using a simple circle)
coin_icon = Entity(
    parent=camera.ui,
    model='circle',
    color=color.rgba(255, 215, 0, 255),  # Gold color
    scale=(0.03, 0.03),
    position=(0.65, 0.45),
    alpha=0.9
)

# Coin counter text
coin_counter_text = Text(
    parent=camera.ui,
    text='0 / 26',
    position=(0.75, 0.45),
    scale=1.5,
    color=color.white,
    origin=(0, 0)
)

# Aesthetic winning popup
win_popup_bg = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 150),  # More transparent black
    scale=(0.7, 0.5),
    position=(0, 0),
    alpha=0.8,
    enabled=False
)

# Decorative border
win_popup_border = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(255, 255, 255, 100),  # White border
    scale=(0.72, 0.52),
    position=(0, 0),
    alpha=0.6,
    enabled=False
)

win_popup_title = Text(
    parent=camera.ui,
    text='VICTORY!',
    position=(0, 0.15),
    scale=3.0,
    color=color.white,  # White text
    origin=(0, 0),
    enabled=False
)

win_popup_subtitle = Text(
    parent=camera.ui,
    text='You collected all 26 coins!',
    position=(0, 0.05),
    scale=1.8,
    color=color.white,
    origin=(0, 0),
    enabled=False
)

win_popup_message = Text(
    parent=camera.ui,
    text='Well done Veeasha!',
    position=(0, -0.05),
    scale=1.4,
    color=color.white,
    origin=(0, 0),
    enabled=False
)

win_popup_footer = Text(
    parent=camera.ui,
    text='Press ESC to exit',
    position=(0, -0.15),
    scale=1.0,
    color=color.white,
    origin=(0, 0),
    enabled=False
)

# ---------------- UPDATE LOOP ---------------- #
def update():
    global vertical_velocity, coin_count, popup_shown

    # Movement input
    move_dir = Vec3(
        held_keys['d'] - held_keys['a'],
        0,
        held_keys['w'] - held_keys['s']
    )

    if move_dir != Vec3(0, 0, 0):
        move_dir = move_dir.normalized()
        forward = Vec3(camera.forward.x, 0, camera.forward.z).normalized()
        right = Vec3(camera.right.x, 0, camera.right.z).normalized()
        direction = forward * move_dir.z + right * move_dir.x

        mario.rotation_y = lerp(
            mario.rotation_y,
            degrees(atan2(-direction.x, -direction.z)),
            time.dt * rotation_speed
        )

        mario.position += direction * speed * time.dt

    # Gravity & Jump
    ray = raycast(mario.world_position + (0, 0.5, 0), Vec3(0, -1, 0), distance=1.1, ignore=(mario,))
    on_ground = ray.hit

    if on_ground:
        if held_keys['space']:
            vertical_velocity = jump_force
        else:
            vertical_velocity = 0
    else:
        vertical_velocity -= gravity * time.dt

    mario.y += vertical_velocity

    # Camera follow
    target_pos = mario.world_position + Vec3(0, 2, 0)
    camera_pivot.position = lerp(camera_pivot.position, target_pos, time.dt * 5)
    camera.look_at(mario.position + Vec3(0, 1, 0))

    # Check for coin collection
    for coin in coins:
        if coin.enabled and mario.intersects(coin).hit:
            coin_count += 1
            if coin_sound:
                coin_sound.play()
            
            # Update coin counter with animation
            coin_counter_text.text = f'{coin_count} / {num_coins}'
            
            # Add pulsing effect to coin counter
            coin_counter_bg.animate_scale((0.25, 0.08), duration=0.2)
            coin_icon.animate_scale((0.03, 0.03), duration=0.2)
            
            print(f"Coins collected: {coin_count}/{num_coins}")
            # Move coin to a new random position instead of disabling it
            x = random.uniform(-20, 20)
            z = random.uniform(-20, 20)
            coin.position = (x, 0.5, z)

    # Show victory popup when all 26 coins are collected
    if coin_count >= num_coins and not popup_shown:
        popup_shown = True  # Prevent multiple triggers
        
        # Show all popup elements with animation
        win_popup_bg.enabled = True
        win_popup_border.enabled = True
        win_popup_title.enabled = True
        win_popup_subtitle.enabled = True
        win_popup_message.enabled = True
        win_popup_footer.enabled = True
        
        # Add entrance animation
        win_popup_bg.animate_scale((0.7, 0.5), duration=0.6, curve=curve.out_bounce)
        win_popup_border.animate_scale((0.72, 0.52), duration=0.6, curve=curve.out_bounce)
        win_popup_title.animate_scale((3.0, 3.0), duration=0.8, curve=curve.out_elastic)
        
        # Add celebration effect to coin counter
        coin_counter_bg.color = color.rgba(0, 255, 0, 200)  # Green for victory
        coin_counter_border.color = color.rgba(255, 255, 0, 200)  # Yellow border
        coin_icon.color = color.rgba(255, 255, 0, 255)  # Yellow coin

# ---------------- CAMERA ROTATION ---------------- #
def input(key):
    if key == 'right mouse down':
        camera_pivot.animate_rotation_y(camera_pivot.rotation_y + 30, duration=0.2)
    elif key == 'left mouse down':
        camera_pivot.animate_rotation_y(camera_pivot.rotation_y - 30, duration=0.2)

# ---------------- UI ---------------- #
Text(
    text="WASD: Move | SPACE: Jump | Click Mouse: Rotate Camera | ESC: Exit",
    origin=(-0.5, -0.85),
    scale=1,
    color=color.azure
)

# ---------------- RUN GAME ---------------- #
app.run()
