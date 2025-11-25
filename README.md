# The Visual Guard Evasion: Adversarial Video Synthesis

**Author:** Aditya Banerjee  
**Project Context:** Datagrid Challenge

## 📌 Project Overview
This project is a computer vision pipeline designed to bypass "The Visual Guard," an AI-powered security system. The objective is to generate a photorealistic, synthetic video artifact (3–5 seconds) depicting a target subject convincingly wearing specific jewelry (The Pendant Key).

The solution utilizes **Semantic Segmentation (SAM)**, **Biometric Tracking (MediaPipe)**, and **Physics-Based Animation** to create "liveness" cues—such as moving shadows, shimmering facets, and eye reflections—that fool detection algorithms.

## 🚀 Features
* **Automated Asset Extraction:** Uses the Segment Anything Model (SAM) to isolate jewelry from raw photos.
* **Digital Surgery:** Programmatically separates rigid pendants from static chains to allow for dynamic re-rigging.
* **Physics Simulation:** Implements harmonic oscillator algorithms to simulate gravity, pendulum swing, and independent earring motion.
* **Biometric Liveness:** Tracks user irises using MediaPipe to render synthetic "eye glint" reflections that mimic biological moisture.
* **Dynamic Lighting:** Generates traveling shine effects and real-time moving shadows based on alpha-channel geometry.
* **Audio Steganography:** Embeds a synchronized "whisper" password for multi-modal verification.

## 🛠️ Tech Stack
* **Language:** Python 3.8+
* **Core Libraries:** OpenCV, NumPy, Pillow (PIL), MoviePy
* **AI/ML:** Segment Anything Model (SAM), MediaPipe, Torch

## ⚠️ Requirements

### Software Dependencies
Install the required libraries using the provided `requirements.txt`:
```bash
pip install -r requirements.txt
