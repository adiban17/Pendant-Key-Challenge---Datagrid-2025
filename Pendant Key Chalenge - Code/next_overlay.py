# Importing required libraries
from PIL import Image

# define file paths
BACKGROUND_FILE = 'result.png'
OVERLAY_FILE = 'body_only.png'
OUTPUT_FILE = 'result_v2.png'

# The cooradinates (x,y) is where the top-left coordinates of the overlay image wil be placed
POSITION = (745,1100)

try:
    with Image.open(BACKGROUND_FILE).convert('RGBA') as background:
        with Image.open(OVERLAY_FILE).convert('RGBA') as overlay:

            # Scaling down the Image
            height = 272
            width = 272
            original_img = overlay.copy()
            scaled_down_img = original_img.resize((height, width), resample=Image.Resampling.LANCZOS) # Use a high-quality filter for shrinking

            # Rotating the Image
            rotated_img = scaled_down_img.rotate(13, expand=True)

            # Paste the overlay into the background
            background.paste(rotated_img, POSITION, mask = rotated_img)

            # Save the final image
            background.convert('RGB').save(OUTPUT_FILE)

            print(f"Successfully Created : {OUTPUT_FILE}")

except Exception as e:
    print(e)

except FileNotFoundError:
    print('The file you are trying to input does not exist')
