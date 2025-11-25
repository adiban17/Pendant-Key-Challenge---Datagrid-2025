from PIL import Image

def _process_and_overlay(background_path, overlay_path, output_path, position, size=None, angle=0):
    
    try:
        # loading background and overlay images
        with Image.open(background_path).convert('RGBA') as background:
            with Image.open(overlay_path).convert('RGBA') as overlay:
                
                # Copy the background image to work on, preserving the original for subsequent pastes
                working_background = background.copy()
                
                # Scaling the Image (if size is provided)
                processed_img = overlay.copy()
                if size:
                    processed_img = processed_img.resize(size, resample=Image.Resampling.LANCZOS)
                
                # Rotating the Image (if angle is not 0)
                if angle != 0:
                    # expand=True ensures the canvas is large enough for the rotated image
                    processed_img = processed_img.rotate(angle, expand=True)

                # Paste the processed overlay onto the background
                # We use the processed image itself as the mask for correct transparency handling
                working_background.paste(processed_img, position, mask=processed_img)

                # Saving the final image
                working_background.convert('RGB').save(output_path)
                
                print(f"✅ Successfully processed {overlay_path} and saved to: {output_path}")

    except FileNotFoundError:
        print(f" Error: One or both files not found: {background_path} or {overlay_path}")
    except Exception as e:
        print(f" An unexpected error occurred: {e}")


# Main Logic
def plot_pendant():
    """
    Executes the sequence of image overlays using a reusable helper function.
    """
    BACKGROUND_FILE = 'Model.png'
    OUTPUT_FILE = 'result.png'
    
    # Plotting the Earring/Pendant
    _process_and_overlay(
        background_path=BACKGROUND_FILE,
        overlay_path='final_earring.png',
        output_path=OUTPUT_FILE,
        position=(531, 570),
        size=(80, 80),  # (width, height)
        angle=0
    )

    # Plotting the Chain
    _process_and_overlay(
        background_path=OUTPUT_FILE, # Use the previously saved file as the new background
        overlay_path='chain_only.png',
        output_path=OUTPUT_FILE,
        position=(570, 990),
        size=(600, 600), # (width, height)
        angle=13
    )

if __name__ == '__main__':
    plot_pendant()