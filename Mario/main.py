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

castle = Entity(
    model='castle/scene.gltf',
    scale=(0.1, 0.1, 0.1),
    position=(0, 0, 25),
    rotation_y=0,
    collider='mesh',
    receive_shadows=True,
    cast_shadows=True
)

# Nintendo Switch gift model
nintendo_switch = Entity(
    model='ground/switch/scene.gltf',
    scale=(4, 4, 4),
    position=(0, 0, 0),
    rotation_y=180,
    collider='box',
    receive_shadows=True,
    cast_shadows=True,
    enabled=False
)

switch_fallback = Entity(
    model='cube',
    scale=(3, 1, 6),
    color=color.rgb(200, 200, 200),
    enabled=False
)

invisible_wall = Entity(
    model='cube',
    scale=(50, 10, 2),
    position=(0, 5, 12),
    color=color.clear,
    collider='box'
)

Sky(texture='sky_default')

# ---------------- MARIO MODEL ---------------- #
mario = Entity(
    model='mario/scene.gltf',
    scale=0.6,
    position=(0, 1.5, 0),
    rotation_y=0,
    collider='box',
    cast_shadows=True
)

mario_collider = Entity(
    parent=mario,
    model='sphere',
    scale=(2, 2, 2),
    visible=False,
    collider='sphere'
)

# ---------------- CAMERA ---------------- #
camera_pivot = Entity(position=(0, 2, 0))
camera.parent = camera_pivot
camera.position = (0, 2.5, -8)
camera.rotation_x = 15
camera.fov = 80

camera_sensitivity = 2.0
camera_rotation_x = 15
camera_rotation_y = 0

# ---------------- MOVEMENT ---------------- #
speed = 6
rotation_speed = 12
jump_force = 0.25
gravity = 0.6
vertical_velocity = 0

# ---------------- COINS ---------------- #
coins = []
coin_count = 0
num_coins = 2
popup_shown = False

# Coin sound
if os.path.exists('coin/sound/coin_recieved.wav'):
    coin_sound = Audio('coin/sound/coin_recieved.wav', autoplay=False)
    print("✅ Coin sound loaded successfully!")
else:
    coin_sound = None
    print("⚠️ Coin audio not found!")

# ---------------- BACKGROUND MUSIC ---------------- #
# Create background music that plays IMMEDIATELY and INDEPENDENTLY
music_path = 'music/Overture.wav'
background_music = None

print("🎵 INITIALIZING BACKGROUND MUSIC...")
if os.path.exists(music_path):
    print(f"📁 Music file found: {music_path}")
    try:
        # Create music with autoplay and loop
        background_music = Audio(music_path, autoplay=True, loop=True, volume=0.7)
        print("✅ Background music object created!")
        
        # Force it to play immediately
        if hasattr(background_music, 'play'):
            background_music.play()
            print("▶️ FORCED BACKGROUND MUSIC TO PLAY!")
        
        # Set volume
        if hasattr(background_music, 'volume'):
            background_music.volume = 0.7
            print(f"🔊 Volume set to: {background_music.volume}")
            
        print("🎵 BACKGROUND MUSIC SHOULD BE PLAYING NOW!")
        
    except Exception as e:
        print(f"❌ ERROR loading background music: {e}")
        background_music = None
else:
    print(f"❌ Music file NOT FOUND: {music_path}")
    background_music = None

# Force music to start multiple times to ensure it works
def force_music_start():
    global background_music
    print("🔄 FORCING MUSIC TO START...")
    if background_music:
        if hasattr(background_music, 'play'):
            background_music.play()
            print("▶️ Music forced to play!")
        else:
            print("❌ Music object has no play method!")
    else:
        print("❌ Music object is None!")

# Try multiple times to force music to start
invoke(force_music_start, delay=0.5)
invoke(force_music_start, delay=1.0)
invoke(force_music_start, delay=2.0)
invoke(force_music_start, delay=5.0)

# Test coin sound at startup
def test_coin_sound():
    if coin_sound:
        print("🔊 Testing coin sound...")
        coin_sound.play()
        print("✅ Coin sound test completed!")
    else:
        print("❌ Coin sound not available for testing!")

# Test background music status
def test_music_status():
    global background_music
    if background_music:
        print("🎵 Background music status check...")
        if hasattr(background_music, 'playing'):
            print(f"   Playing: {background_music.playing}")
        if hasattr(background_music, 'volume'):
            print(f"   Volume: {background_music.volume}")
        print("✅ Background music is independent of coin collection!")
    else:
        print("❌ Background music not loaded!")

invoke(test_coin_sound, delay=2.0)
invoke(test_music_status, delay=3.0)

# ---------------- COIN SPAWNING ---------------- #
initial_coin_count = 8
for i in range(initial_coin_count):
    x = random.uniform(-20, 20)
    z = random.uniform(-20, 20)
    ground_ray = raycast(Vec3(x, 10, z), Vec3(0, -1, 0), distance=20, ignore=[])
    coin_y = ground_ray.world_point.y + 0.5 if ground_ray.hit else 0.5
    coin = Entity(
        model='coin/scene.gltf',
        scale=0.6,
        position=(x, coin_y, z),
        collider='box',
        cast_shadows=True
    )
    coins.append(coin)

# ---------------- UI ---------------- #
coin_ui = Entity(parent=camera.ui)
coin_counter_bg = Entity(parent=coin_ui, model='quad', color=color.rgba(0, 0, 0, 150),
                         scale=(0.25, 0.08), position=(0.75, 0.45))
coin_icon = Entity(parent=coin_ui, model='circle', color=color.yellow,
                   scale=(0.03, 0.03), position=(0.65, 0.45))
coin_counter_text = Text(parent=coin_ui, text='0 / 2', position=(0.75, 0.45),
                         scale=1.5, color=color.white)

# Fade overlay
black_screen = Entity(parent=camera.ui, model='quad', color=color.black,
                      scale=(2, 2), position=(0, 0), alpha=0, enabled=False)

# ---------------- UPDATE LOOP ---------------- #
def update():
    global vertical_velocity, coin_count, popup_shown, camera_rotation_x, camera_rotation_y, background_music
    
    # FORCE BACKGROUND MUSIC TO PLAY EVERY FRAME (completely independent of coins)
    if background_music and hasattr(background_music, 'playing'):
        if not background_music.playing:
            print("🔄 MUSIC STOPPED - RESTARTING IMMEDIATELY!")
            background_music.play()
    elif background_music is None:
        print("🔄 MUSIC LOST - RELOADING!")
        try:
            background_music = Audio('music/Overture.wav', autoplay=True, loop=True, volume=0.7)
            if hasattr(background_music, 'play'):
                background_music.play()
                print("✅ MUSIC RELOADED AND PLAYING!")
        except Exception as e:
            print(f"❌ Failed to reload music: {e}")

    # Player movement
    move_dir = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s'])
    if move_dir != Vec3(0, 0, 0):
        move_dir = move_dir.normalized()
        forward = Vec3(camera.forward.x, 0, camera.forward.z).normalized()
        right = Vec3(camera.right.x, 0, camera.right.z).normalized()
        direction = forward * move_dir.z + right * move_dir.x
        mario.rotation_y = lerp(mario.rotation_y,
                                degrees(atan2(-direction.x, -direction.z)),
                                time.dt * rotation_speed)
        mario.position += direction * speed * time.dt

    # Gravity & jump
    ray = raycast(mario.world_position + (0, 0.3, 0),
                  Vec3(0, -1, 0), distance=1.5, ignore=(mario, mario_collider))
    on_ground = ray.hit
    if on_ground:
        if held_keys['space']:
            vertical_velocity = jump_force
        else:
            vertical_velocity = 0
    else:
        vertical_velocity -= gravity * time.dt
    mario.y += vertical_velocity

    # Camera movement
    target_pos = mario.world_position + Vec3(0, 2.5, 0)
    camera_pivot.position = lerp(camera_pivot.position, target_pos, time.dt * 5)
    camera_rotation_y += mouse.delta[0] * camera_sensitivity * time.dt
    camera_rotation_x -= mouse.delta[1] * camera_sensitivity * time.dt
    camera_rotation_x = clamp(camera_rotation_x, -60, 60)
    camera_pivot.rotation_y = camera_rotation_y
    camera.rotation_x = camera_rotation_x

    # Coin collection
    for coin in coins:
        if coin.enabled and distance(mario.world_position, coin.world_position) < 1.5:
            coin.enabled = False
            coin_count += 1
            if coin_sound: 
                coin_sound.play()
                print("🔊 Coin sound played!")
            else:
                print("❌ Coin sound not available!")
            coin_counter_text.text = f'{coin_count} / 2'
            print(f"Collected coin {coin_count}/2")

            # Spawn 2 new coins
            for _ in range(2):
                x = random.uniform(-20, 20)
                z = random.uniform(-20, 20)
                ground_ray = raycast(Vec3(x, 10, z), Vec3(0, -1, 0), distance=20, ignore=[])
                coin_y = ground_ray.world_point.y + 0.5 if ground_ray.hit else 0.5
                new_coin = Entity(model='coin/scene.gltf', scale=0.6,
                                  position=(x, coin_y, z), collider='box', cast_shadows=True)
                coins.append(new_coin)

    # Victory event
    if coin_count >= num_coins and not popup_shown:
        popup_shown = True
        print("🎯 Victory triggered! Enabling black screen...")
        black_screen.enabled = True
        black_screen.alpha = 0
        black_screen.animate('alpha', 1, duration=1.2)

        def place_switch_on_ground():
            print("🎉 Starting Switch reveal sequence...")

            black_screen.enabled = True
            black_screen.alpha = 1
            black_screen.color = color.rgba(0, 0, 0, 255)

            def fade_out_black_screen():
                black_screen.animate('alpha', 0, duration=1.2)
                print("📺 Fading out black screen...")

                def update_black_screen_alpha():
                    black_screen.color = color.rgba(0, 0, 0, int(black_screen.alpha * 255))
                    if black_screen.alpha > 0:
                        invoke(update_black_screen_alpha, delay=0.05)
                    else:
                        black_screen.enabled = False
                        print("✅ Black screen disabled")
                update_black_screen_alpha()

            invoke(fade_out_black_screen, delay=0.2)

            ground_ray = raycast(Vec3(0, 10, 0), Vec3(0, -1, 0),
                                 distance=20, ignore=[])
            ground_y = ground_ray.world_point.y if ground_ray.hit else 0

            nintendo_switch.enabled = True
            nintendo_switch.position = (0, ground_y + 1.2, 0)
            nintendo_switch.scale = (12.0, 12.0, 12.0)
            nintendo_switch.rotation_y = 180

            PointLight(parent=nintendo_switch, color=color.white,
                       position=(0, 3, 0))

            def create_confetti_batch():
                for i in range(10):
                    x = random.uniform(-20, 20)
                    z = random.uniform(-20, 20)
                    y = random.uniform(15, 25)
                    confetti_color = random.choice(
                        [color.red, color.blue, color.green, color.yellow,
                         color.orange, color.pink, color.cyan, color.magenta]
                    )
                    confetti = Entity(model='cube', scale=(0.1, 0.1, 0.1),
                                      position=(x, y, z), color=confetti_color)
                    fall_time = random.uniform(3, 6)
                    confetti.animate_position(
                        (x + random.uniform(-8, 8),
                         ground_y - 5,
                         z + random.uniform(-8, 8)),
                        duration=fall_time
                    )
                    confetti.animate_rotation(
                        (random.uniform(0, 360),
                         random.uniform(0, 360),
                         random.uniform(0, 360)),
                        duration=fall_time
                    )

            create_confetti_batch()
            invoke(create_confetti_batch, delay=0.1)

        invoke(place_switch_on_ground, delay=1.5)

# ---------------- INPUT ---------------- #
def input(key):
    global camera_rotation_y
    if key == 'right mouse down':
        camera_rotation_y += 30
    elif key == 'left mouse down':
        camera_rotation_y -= 30

# ---------------- INFO TEXT ---------------- #
Text(text="WASD Move | SPACE Jump | Mouse Look | ESC Exit",
     origin=(-0.5, -0.85), scale=1, color=color.azure)

# ---------------- RUN ---------------- #
app.run()
