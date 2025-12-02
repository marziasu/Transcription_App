import subprocess

def read_audio_as_bytes(file_path: str) -> bytes:
    try:
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-loglevel", "error",
                "-i", file_path,
                "-ac", "1",
                "-ar", "16000",
                "-f", "s16le",
                "pipe:1"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        audio_bytes, err = process.communicate()

        if err:
            print("FFmpeg Error:", err.decode())

        return audio_bytes

    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found! Install FFmpeg and add to PATH.")
