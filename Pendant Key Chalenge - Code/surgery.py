import cv2
import numpy as np

def prepare_assets():
    # 1. CLEAN THE BODY
    # Load the original perfect pendant (Fox + Short Chain)
    full_pendant = cv2.imread("final_pendant.png", cv2.IMREAD_UNCHANGED)
    
    if full_pendant is None:
        print("Error: Could not find 'final_pendant.png'")
        return

    # We will "crop" the top of the image to remove the old chain.
    # The fox head starts roughly 25% down the image.
    h, w, _ = full_pendant.shape
    
    # Cutoff point: Keep everything BELOW this Y-pixel.
    # Adjust '0.20' if it cuts the ears. 0.20 means top 20% is deleted.
    cutoff_y = int(h * 0.20) 
    
    # Create body_only by slicing
    body_only = full_pendant.copy()
    # Set the top section to transparent (0 alpha)
    body_only[0:cutoff_y, :, 3] = 0 
    
    cv2.imwrite("body_only.png", body_only)
    print("Success: Created 'body_only.png' (Old chain removed).")

    # 2. PREPARE THE CHAIN
    # Load the new SAM chain output
    chain_raw = cv2.imread("chain_raw.png", cv2.IMREAD_UNCHANGED)
    
    if chain_raw is None:
        print("Error: Could not find 'chain_raw.png'. Rename your uploaded file!")
        return
        
    cv2.imwrite("chain_only.png", chain_raw)
    print("Success: Created 'chain_only.png'.")

if __name__ == "__main__":
    prepare_assets()