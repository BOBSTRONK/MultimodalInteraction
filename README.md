# Multimodal Interaction

This repository explores multimodal interaction techniques, utilizing tools and frameworks for gesture recognition, voice commands, and other input modalities.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Folder Structure](#folder-structure)
5. [Installation](#installation)
6. [Usage](#usage)

## Overview

Multimodal interaction combines various input methods (e.g., gestures, voice, and touch) to create a seamless user experience. This project implements gesture recognition using machine learning and integrates with tools such as `whisper.cpp` for voice processing.

## Features

- **Gesture Recognition**: Models to detect and classify hand gestures using MediaPipe.
- **Voice Interaction**: Supports speech-to-text functionality using `whisper.cpp`.
- **Extensible Design**: Easily integrates new input modalities or interaction models.

## Requirements

- Python 3.11 or later.
- [MediaPipe](https://mediapipe.dev): A cross-platform framework for building multimodal machine learning pipelines.
- [Whisper CPP](https://github.com/ggerganov/whisper.cpp): A lightweight, C++ implementation of OpenAI’s Whisper, an automatic speech recognition (ASR) model. It’s an open-source project creating a buzz among AI enthusiasts.

## Folder Structure

The repository is organized as follows:

- **`Gesture/`**: Code and models for gesture recognition.
- **`Models/`**: Pre-trained models and utilities for multimodal tasks.
- **`images/`**: Reference images and visualization assets.
- **`test/`**: Unit tests and example scripts.
- **`whisper.cpp`**: A C++ library for speech-to-text processing.
- **`app.py`**: The main Python application to run multimodal interactions.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BOBSTRONK/MultimodalInteraction.git
   ```
2. Navigate to the project directory:
   ```bash
   cd MultimodalInteraction
   ```
3. Ensure Python 3.11 or later is installed on your system.

## Usage

Run the main application with:
```bash
python app.py
```

This script initializes the multimodal interaction system, allowing you to test gesture and voice input.
