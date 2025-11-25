import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

try:
    from moviepy.editor import VideoClip
except ImportError:
    from moviepy.video.VideoClip import VideoClip


# Coordinate Configuration
EARRING_POS = (585, 600)
PENDANT_POS = (878, 1130) 
CHAIN_POS = (570, 990)

# Dimensions
EARRING_SIZE = (80, 80)
PENDANT_SIZE = (300, 300)
CHAIN_SIZE = (600, 600)

# Video Settings
DURATION = 4  # Seconds
FPS = 30

# Load and Prepare Files
print("Loading assets...")
bg_base = Image.open('Model.png').convert('RGBA')
earring_raw = Image.open('final_earring.png').convert('RGBA')
earring_raw = earring_raw.resize(EARRING_SIZE, Image.Resampling.LANCZOS)
pendant_raw = Image.open('body_only.png').convert('RGBA')
pendant_raw = pendant_raw.resize(PENDANT_SIZE, Image.Resampling.LANCZOS)
chain_img = Image.open('chain_only.png').convert('RGBA')
chain_img = chain_img.resize(CHAIN_SIZE, Image.Resampling.LANCZOS)

# Apply the static 13-degree rotation to the chain immediately
chain_img = chain_img.rotate(13, expand=True, resample=Image.Resampling.BICUBIC)



def rotate_around_pivot(img, angle, pivot):
    """
    Rotates an image around a specific pivot point (px, py).
    Returns the rotated canvas and the centering offsets (cw, ch).
    """
    rgba = img.convert('RGBA')
    w, h = rgba.size
    px, py = pivot
    
    # Create a large canvas (2x size) to prevent clipping during rotation
    canvas_w, canvas_h = w * 2, h * 2
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # Paste so pivot aligns with canvas center
    paste_x = w - px
    paste_y = h - py
    canvas.paste(rgba, (paste_x, paste_y))
    
    # Rotate the canvas
    rotated_canvas = canvas.rotate(angle, resample=Image.Resampling.BICUBIC)
    
    return rotated_canvas, w, h


def create_shadow(img, offset=(5, 5), opacity=100, blur_radius=5):
    """
    Creates a realistic blurred drop shadow from an image's alpha channel.
    """
    # Extract alpha mask
    mask = img.split()[3]
    
    # Create black silhouette
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, opacity), (0, 0), mask=mask)
    
    # Apply Gaussian Blur for softness
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    return shadow


def apply_shimmer(img, t):
    """
    Adds a subtle moving white glint to the diamonds.
    """
    # Cycle every 2 seconds
    cycle = t % 2.0
    
    # Active only between 0.8s and 1.2s
    if 0.8 < cycle < 1.2:
        shimmer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        mask = img.split()[3]
        
        # Intensity fades in/out like a sine wave
        intensity = int(80 * np.sin((cycle - 0.8) * 3.14 / 0.4))
        intensity = max(0, min(255, intensity))
        
        shimmer.putalpha(intensity)
        
        # Composite and blend
        out = Image.composite(shimmer, img, mask)
        return Image.blend(img, out, 0.3)
        
    return img


# Main Render Loop
def make_frame(t):
    frame_bg = bg_base.copy()
    
    # Pendulum Motion
    angle_earring = 3 * np.sin(3 * t)
    angle_pendant = 13 + (2 * np.sin(2 * t)) # Oscillates around 13 degrees

    # Shadow
    shadow_e_raw = create_shadow(earring_raw, opacity=60, blur_radius=5) 
    shadow_p_raw = create_shadow(pendant_raw, opacity=100, blur_radius=8) 
    chain_shadow = create_shadow(chain_img, opacity=200, blur_radius=8)
    frame_bg.paste(chain_shadow, (CHAIN_POS[0]+5, CHAIN_POS[1]+5), chain_shadow)
    frame_bg.paste(chain_img, CHAIN_POS, chain_img)

    # Apply Shimmer
    shimmer_e = apply_shimmer(earring_raw, t)
    
    # Rotate Earring AND its Shadow around the same pivot
    pivot_e = (EARRING_SIZE[0] // 2, 5)
    r_earring, cw, ch = rotate_around_pivot(shimmer_e, angle_earring, pivot_e)
    r_shadow_e, _, _ = rotate_around_pivot(shadow_e_raw, angle_earring, pivot_e)
    
    # Calculate Placement
    pos_e = (EARRING_POS[0] - cw, EARRING_POS[1] - ch)
    shadow_pos_e = (pos_e[0] + 5, pos_e[1] + 5) # Shadow is 5px down/right
    
    # Paste (Shadow first, then Object)
    frame_bg.paste(r_shadow_e, shadow_pos_e, r_shadow_e)
    frame_bg.paste(r_earring, pos_e, r_earring)

    # Apply Shimmer
    shimmer_p = apply_shimmer(pendant_raw, t)
    # Rotate Pendant AND its Shadow
    pivot_p = (PENDANT_SIZE[0] // 2, 10)
    r_pendant, cw, ch = rotate_around_pivot(shimmer_p, angle_pendant, pivot_p)
    r_shadow_p, _, _ = rotate_around_pivot(shadow_p_raw, angle_pendant, pivot_p)
    # Calculate Placement
    pos_p = (PENDANT_POS[0] - cw, PENDANT_POS[1] - ch)
    shadow_pos_p = (pos_p[0] + 8, pos_p[1] + 8) # Pendant shadow is deeper (8px)
    # Paste
    frame_bg.paste(r_shadow_p, shadow_pos_p, r_shadow_p)
    frame_bg.paste(r_pendant, pos_p, r_pendant)

    return np.array(frame_bg.convert('RGB'))

# Execute
if __name__ == "__main__":
    print("Rendering final video with shadows and shimmer...")
    clip = VideoClip(make_frame, duration=DURATION)
    clip.write_videofile("final_video0.mp4", fps=FPS)
    print("✅ Video saved as 'final_video0.mp4'")