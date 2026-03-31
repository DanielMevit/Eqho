"""Diagnose what's messing with system volume when the mic opens."""

import time
import winreg

print("=" * 60)
print("EKHO AUDIO DIAGNOSTIC")
print("=" * 60)

# 1. Check Windows Communications ducking setting
print("\n[1] Windows Communications Activity setting:")
try:
    key_path = r"SOFTWARE\Microsoft\Multimedia\Audio"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
        val, _ = winreg.QueryValueEx(key, "UserDuckingPreference")
        labels = {0: "Mute other sounds", 1: "Reduce by 80%", 2: "Reduce by 50%", 3: "Do nothing"}
        print(f"    UserDuckingPreference = {val} ({labels.get(val, 'unknown')})")
except FileNotFoundError:
    print("    Registry key not found (using Windows default)")
except Exception as e:
    print(f"    Error: {e}")

# 2. Figure out pycaw API
print("\n[2] Testing pycaw volume control:")
vol_ctl = None
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    speakers = AudioUtilities.GetSpeakers()
    print(f"    GetSpeakers() type: {type(speakers)}")
    print(f"    GetSpeakers() dir: {[x for x in dir(speakers) if not x.startswith('_')]}")

    # Try different API approaches
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol_ctl = cast(interface, POINTER(IAudioEndpointVolume))
        print(f"    Method 1 (Activate) works!")
    except Exception as e1:
        print(f"    Method 1 (Activate) failed: {e1}")
        try:
            # Some pycaw versions wrap differently
            vol_ctl = speakers.QueryInterface(IAudioEndpointVolume)
            print(f"    Method 2 (QueryInterface) works!")
        except Exception as e2:
            print(f"    Method 2 (QueryInterface) failed: {e2}")

    if vol_ctl:
        v = vol_ctl.GetMasterVolumeLevelScalar()
        print(f"    Current master volume: {v:.4f} ({v*100:.1f}%)")
except ImportError as e:
    print(f"    pycaw not available: {e}")
except Exception as e:
    print(f"    Error: {e}")

# 3. Volume change test
print("\n[3] Volume change test (opening mic for 3 seconds):")
try:
    import sounddevice as sd
    import numpy as np

    if vol_ctl:
        before = vol_ctl.GetMasterVolumeLevelScalar()
        print(f"    Volume BEFORE mic open: {before*100:.1f}%")
    else:
        print("    (no volume control — just testing mic open)")

    stream = sd.InputStream(samplerate=16000, channels=1, dtype="float32", blocksize=8000)
    stream.start()

    for t in [0.5, 1.5, 3.0]:
        time.sleep(0.5 if t == 0.5 else t - (0.5 if t == 1.5 else 1.5))
        if vol_ctl:
            v = vol_ctl.GetMasterVolumeLevelScalar()
            print(f"    Volume after {t}s: {v*100:.1f}%")

    stream.stop()
    stream.close()
    time.sleep(1.0)

    if vol_ctl:
        after = vol_ctl.GetMasterVolumeLevelScalar()
        print(f"    Volume after mic close: {after*100:.1f}%")
        if abs(before - after) > 0.01:
            diff = ((after - before) / before) * 100
            print(f"    *** VOLUME CHANGED by {diff:+.1f}%!")
        else:
            print(f"    Volume stayed stable.")
except Exception as e:
    print(f"    Error: {e}")

# 4. Active audio sessions
print("\n[4] Active audio sessions:")
try:
    sessions = AudioUtilities.GetAllSessions()
    for s in sessions:
        if s.Process:
            sv = s.SimpleAudioVolume
            print(f"    {s.Process.name():30s} vol={sv.GetMasterVolume():.2f} mute={sv.GetMute()}")
except Exception as e:
    print(f"    Error: {e}")

# 5. List audio devices
print("\n[5] Audio input devices:")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            default = " (DEFAULT)" if i == sd.default.device[0] else ""
            print(f"    [{i}] {d['name']}{default}")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
