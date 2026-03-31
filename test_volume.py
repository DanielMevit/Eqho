"""Quick test of pycaw volume control for Eqho."""
from pycaw.pycaw import AudioUtilities

speakers = AudioUtilities.GetSpeakers()
vol = speakers.EndpointVolume
print(f"Type: {type(vol)}")
print(f"Methods: {[x for x in dir(vol) if not x.startswith('_') and 'aster' in x or 'ute' in x.lower()]}")
print(f"All: {[x for x in dir(vol) if not x.startswith('_')]}")

# Test get
try:
    s = vol.GetMasterVolumeLevelScalar()
    print(f"\nGetMasterVolumeLevelScalar() = {s:.4f} ({s*100:.1f}%)")
except Exception as e:
    print(f"GetMasterVolumeLevelScalar failed: {e}")

try:
    d = vol.GetMasterVolumeLevel()
    print(f"GetMasterVolumeLevel() = {d:.2f} dB")
except Exception as e:
    print(f"GetMasterVolumeLevel failed: {e}")

try:
    m = vol.GetMute()
    print(f"GetMute() = {m}")
except Exception as e:
    print(f"GetMute failed: {e}")

# Test set to 50% of current then restore
import time
try:
    current = vol.GetMasterVolumeLevelScalar()
    print(f"\nSetting to {current*50:.1f}% (50% of {current*100:.1f}%)...")
    vol.SetMasterVolumeLevelScalar(current * 0.5)
    time.sleep(2)
    print(f"Current now: {vol.GetMasterVolumeLevelScalar()*100:.1f}%")
    print("Restoring...")
    vol.SetMasterVolumeLevelScalar(current)
    print(f"Restored to: {vol.GetMasterVolumeLevelScalar()*100:.1f}%")
except Exception as e:
    print(f"Set scalar failed: {e}")

# Test mute
try:
    print(f"\nTesting mute...")
    vol.SetMute(True)
    print(f"Muted: {vol.GetMute()}")
    time.sleep(2)
    vol.SetMute(False)
    print(f"Unmuted: {vol.GetMute()}")
except Exception as e:
    print(f"Mute failed: {e}")

print("\nDone!")
