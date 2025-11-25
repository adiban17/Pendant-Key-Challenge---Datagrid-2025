import cv2
import numpy as np
import torch
import os
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

def generate_candidate_masks(image_path, output_folder, checkpoint="sam_vit_h_4b8939.pth"):
    # 1. Setup
    filename = os.path.basename(image_path).split('.')[0]
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Processing {image_path} using AutoGenerator... (This may take a minute)")
    
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 2. Load SAM with Automatic Generator
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sam = sam_model_registry["vit_h"](checkpoint=checkpoint)
    sam.to(device=device)
    
    # Tunable parameters:
    # points_per_side=32: scans a 32x32 grid of points across the image
    # pred_iou_thresh=0.9: only keep high-confidence masks
    mask_generator = SamAutomaticMaskGenerator(
        model=sam,
        points_per_side=32,
        pred_iou_thresh=0.86,
        stability_score_thresh=0.92,
        crop_n_layers=1,
        crop_n_points_downscale_factor=2,
        min_mask_region_area=1000,  # Filter out tiny dots/noise
    )
    
    # 3. Generate All Masks
    masks = mask_generator.generate(image_rgb)
    print(f"Found {len(masks)} potential segments.")

    # 4. Sort and Save the Best Ones
    # We sort by area (largest to smallest) to find the main objects
    sorted_masks = sorted(masks, key=lambda x: x['area'], reverse=True)
    
    for i, mask_data in enumerate(sorted_masks[:10]): # Save top 10 candidates
        seg_map = mask_data['segmentation'] # This is the boolean mask
        
        # Convert to RGBA
        image_bgr = image.copy()
        b, g, r = cv2.split(image_bgr)
        
        # Create Alpha channel: 255 where mask is True, 0 otherwise
        alpha = seg_map.astype(np.uint8) * 255
        
        rgba = cv2.merge([b, g, r, alpha])
        
        # Save
        save_path = f"{output_folder}/{filename}_candidate_{i}.png"
        cv2.imwrite(save_path, rgba)
        print(f"Saved {save_path}")

if __name__ == "__main__":
    # Ensure checkpoint is in folder!
    generate_candidate_masks("pendant.jpg", "candidates_pendant")
    generate_candidate_masks("Earring.jpg", "candidates_earring")