import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import math
import cv2
import mediapipe as mp

try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy.video.VideoClip import VideoClip

# Configuring Coordinates
EARRING_POS = (585, 600)
PENDANT_POS = (878, 1130) 
CHAIN_POS = (570, 990)
EARRING_SIZE = (80, 80)
PENDANT_SIZE = (300, 300)
CHAIN_SIZE = (600, 600)

DURATION = 4
FPS = 30

# FIle Handling
print("Loading assets...")
bg_base = Image.open('Model.png').convert('RGBA')
earring_raw = Image.open('final_earring.png').convert('RGBA').resize(EARRING_SIZE, Image.Resampling.LANCZOS)
pendant_raw = Image.open('body_only.png').convert('RGBA').resize(PENDANT_SIZE, Image.Resampling.LANCZOS)
chain_img = Image.open('chain_only.png').convert('RGBA').resize(CHAIN_SIZE, Image.Resampling.LANCZOS)
chain_img = chain_img.rotate(13, expand=True, resample=Image.Resampling.BICUBIC)

# Detecting eye position
print("Detecting eyes for 'Alive' effect...")
mp_face_mesh = mp.solutions.face_mesh
eye_coords = []

with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as mesh:
    open_cv_image = cv2.cvtColor(np.array(bg_base), cv2.COLOR_RGBA2BGR)
    results = mesh.process(open_cv_image)
    
    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        h, w = bg_base.size[1], bg_base.size[0]
        # 468=Left Iris, 473=Right Iris
        left_iris = (int(lm[468].x * w), int(lm[468].y * h))
        right_iris = (int(lm[473].x * w), int(lm[473].y * h))
        eye_coords = [left_iris, right_iris]
        print(f" Eyes found at: {eye_coords}")
    else:
        print("⚠️ Warning: Could not detect eyes.")

# --- 4. HELPER FUNCTIONS ---

def rotate_around_pivot(img, angle, pivot):
    rgba = img.convert('RGBA')
    w, h = rgba.size
    px, py = pivot
    canvas_w, canvas_h = w * 2, h * 2
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    paste_x = w - px
    paste_y = h - py
    canvas.paste(rgba, (paste_x, paste_y))
    rotated_canvas = canvas.rotate(angle, resample=Image.Resampling.BICUBIC)
    return rotated_canvas, w, h

def create_shadow(img, offset=(5, 5), opacity=100, blur_radius=5):
    mask = img.split()[3]
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, opacity), (0, 0), mask=mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return shadow

def apply_traveling_shine(img, t):
    period = 3.25 
    phase = (t % period) / 1.0
    arr = np.array(img)
    alpha = arr[:, :, 3].astype(float) / 255.0 
    rows, cols = arr.shape[:2]
    x = np.arange(cols)
    y = np.arange(rows)
    xv, yv = np.meshgrid(x, y)
    total_dist = cols + rows
    current_pos = total_dist * phase * 1.8 - (total_dist * 0.4) 
    dist = np.abs((xv + yv) - current_pos)
    band_width = 50.0
    intensity = np.exp(-(dist**2) / (2 * (band_width**2)))
    shine_layer = np.zeros_like(arr)
    shine_layer[:, :, 0:3] = 255
    shine_alpha = (intensity * alpha * 100).astype(np.uint8)
    shine_layer[:, :, 3] = shine_alpha
    img_pil = Image.fromarray(arr)
    shine_pil = Image.fromarray(shine_layer)
    return Image.alpha_composite(img_pil, shine_pil)

def apply_eye_glint(bg_img, t, coords):
    """
    Adds a PROMINENT, pulsing white dot to the pupils.
    """
    if not coords: return bg_img
    
    # --- UPDATED SETTINGS FOR VISIBILITY ---
    size = 16  # Increased canvas size (was 10)
    dot_r = 2  # Radius of the dot (Diameter = 12px, much bigger)
    
    glint = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    
    # Opacity Cycle: Much brighter now
    # Oscillates between 150 (visible) and 255 (bright white)
    period = 3.25
    cycle = (math.sin((t * 2 * math.pi) / period) + 1) / 2 
    opacity = int(100 + (105 * cycle)) 
    
    # Draw sharp white circle
    # Center is (size/2, size/2) -> (8, 8)
    # Bounding box: (8-r, 8-r, 8+r, 8+r) -> (2, 2, 14, 14)
    x0, y0 = size//2 - dot_r, size//2 - dot_r
    x1, y1 = size//2 + dot_r, size//2 + dot_r
    
    # We use a draw object to make a filled circle
    from PIL import ImageDraw
    draw = ImageDraw.Draw(glint)
    draw.ellipse([x0, y0, x1, y1], fill=(255, 255, 255, opacity))
    
    # Minimal blur to keep it sharp but integrated
    glint = glint.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    # Paste onto background
    for (x, y) in coords:
        # Offset to align center of glint with center of eye
        pos = (x - size//2, y - size//2) 
        final_pos = (pos[0] + 2, pos[1] - 2) 
        bg_img.paste(glint, final_pos, glint)
        
    return bg_img

def apply_obvious_zoom(final_frame, t):
    w, h = final_frame.size
    max_zoom = 1.13
    progress = t / DURATION
    current_zoom = 1.0 + ((max_zoom - 1.0) * progress)
    new_w = int(w / current_zoom)
    new_h = int(h / current_zoom)
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    right = left + new_w
    bottom = top + new_h
    cropped = final_frame.crop((left, top, right, bottom))
    return cropped.resize((w, h), resample=Image.Resampling.BICUBIC)

# Run Main Logic

def make_frame(t):
    frame_bg = bg_base.copy()
    
    # Apply Eye Glint (Before Jewelry)
    frame_bg = apply_eye_glint(frame_bg, t, eye_coords)

    # Jewelry Rendering
    angle_earring = 3 * np.sin(3 * t)
    angle_pendant = 13 + (2 * np.sin(2 * t))

    shadow_e_raw = create_shadow(earring_raw, opacity=60, blur_radius=5) 
    shadow_p_raw = create_shadow(pendant_raw, opacity=100, blur_radius=8) 
    chain_shadow = create_shadow(chain_img, opacity=200, blur_radius=8)

    frame_bg.paste(chain_shadow, (CHAIN_POS[0]+5, CHAIN_POS[1]+5), chain_shadow)
    frame_bg.paste(chain_img, CHAIN_POS, chain_img)

    shiny_e = apply_traveling_shine(earring_raw, t)
    pivot_e = (EARRING_SIZE[0] // 2, 5)
    r_earring, cw, ch = rotate_around_pivot(shiny_e, angle_earring, pivot_e)
    r_shadow_e, _, _ = rotate_around_pivot(shadow_e_raw, angle_earring, pivot_e)
    pos_e = (EARRING_POS[0] - cw, EARRING_POS[1] - ch)
    frame_bg.paste(r_shadow_e, (pos_e[0]+5, pos_e[1]+5), r_shadow_e)
    frame_bg.paste(r_earring, pos_e, r_earring)

    shiny_p = apply_traveling_shine(pendant_raw, t + 0.5)
    pivot_p = (PENDANT_SIZE[0] // 2, 10)
    r_pendant, cw, ch = rotate_around_pivot(shiny_p, angle_pendant, pivot_p)
    r_shadow_p, _, _ = rotate_around_pivot(shadow_p_raw, angle_pendant, pivot_p)
    pos_p = (PENDANT_POS[0] - cw, PENDANT_POS[1] - ch)
    frame_bg.paste(r_shadow_p, (pos_p[0]+8, pos_p[1]+8), r_shadow_p)
    frame_bg.paste(r_pendant, pos_p, r_pendant)

    # Apply Zoom
    final_scene = apply_obvious_zoom(frame_bg, t)

    return np.array(final_scene.convert('RGB'))

# EXECUTE
if __name__ == "__main__":
    print("Rendering final video with PROMINENT EYE GLINT...")
    clip = VideoClip(make_frame, duration=DURATION)
    clip.write_videofile("final_video.mp4", fps=FPS)
    print(" Video saved as 'final_video.mp4'")