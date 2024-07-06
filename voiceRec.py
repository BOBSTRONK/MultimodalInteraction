import os
import subprocess
import tempfile
import wave
import sounddevice as sd


# input_filename: file paths for the input audio
# output_filename: output text file
def transcribe_to_txt(input_filename: str, output_filename: str):
    print("Running whisper transcription...")
    # Compose the command of all components
    # necessary command-line arguments to run the transcription tool
    command = [
        # executable
        "whisper.cpp/main",
        "-m",
        "whisper.cpp/models/ggml-medium.en.bin",
        "-f",
        input_filename,
        "-otxt",
        "-of",
        output_filename,
        "-np",
    ]

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)
    # Print the output and error messages for debugging


# indata: the audiodata
# frames: The number of frames in the audio data
# time: timing information
# status: the status of audio stream
def callback(indata, frames, time, status):
    # Raise for status if required
    if status:
        print(status)
    
    # Create a tempfile to save the audio to, with autodeletion
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav', prefix='audio_', dir='.') as tmpfile:
        # Save the 5 second audio to a .wav file
        with wave.open(tmpfile.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(16000)  # Sample rate
            wav_file.writeframes(indata)
        
        # Prepare the output filename
        output_filename = tmpfile.name.replace('.wav', '')
        
        # Transcribe the audio to text using our whisper.cpp wrapper
        transcribe_to_txt(tmpfile.name, output_filename)

        # Print the transcribed text
        with open(output_filename + '.txt', 'r') as file:
            print(file.read())
        
        # Clean up temporary files
        os.remove(output_filename + '.txt')

# sd.InputStream is used to open an input audio stream
# callback specifies a callback function that processes chunks of audio data
# dtype = 'int16' sets the data type of the audio stream
# 'channels = 1' indicates that the audio is mono (single channel, same sound being hear from all direction)
# 'samplerate = 1600' sets the sampling rate (16000 hz) of the audiot stream
# sample rate = sample of the audio signal taken per second. determines the quality and frequence range of the audio, higher = better quality
# with sd.InputStream(callback=callback, dtype='int16', channels=1, samplerate=16000, blocksize=16000*5):

try:
    # Start recording with a rolling 5-second buffer
    with sd.InputStream(
        callback=callback,
        dtype="int16",
        channels=1,
        samplerate=16000,
        blocksize=16000 * 3,
    ):
        print("Recording... Press Ctrl+C to stop.")
        while True:
            pass
except KeyboardInterrupt:
    print("Recording stopped.")
