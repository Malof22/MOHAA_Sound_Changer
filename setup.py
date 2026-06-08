from cx_Freeze import setup, Executable
import sys
base = "Win32GUI" if sys.platform == "win32" else None

executables = [Executable("SoundChanger.py", base=base)]

packages = ["numpy", "PyQt6", "sounddevice", "soundfile"]
options = {
    'build_exe': {
        'packages':packages,
        "include_files": ["icons"]
    },
}

setup(
    name = "MOHAA Sound Changer",
    options = options,
    version = "1.0",
    description = 'Change MOHAA sounds',
    executables = executables
)