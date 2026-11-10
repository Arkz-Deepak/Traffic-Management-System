"""
AURA Hardware-in-the-Loop (HIL) Microcontroller Bridge
Maps real-time AURA traffic light states to physical LEDs via USB Serial (Arduino / ESP32 / Raspberry Pi Pico)
or terminal-rendered ASCII virtual hardware.
"""

import os
import sys
import time
import json
import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:3000/api/traffic")
SERIAL_PORT = os.environ.get("SERIAL_PORT", "/dev/ttyUSB0")
BAUD_RATE = int(os.environ.get("BAUD_RATE", "115200"))

# State to Hardware Pin Mapping:
# Phase 0: NS GREEN, EW RED
# Phase 1: NS YELLOW, EW RED
# Phase 2: NS RED, EW GREEN
# Phase 3: NS RED, EW YELLOW

PIN_MAP = {
    'NS_GREEN':  'NS_G:1,NS_Y:0,NS_R:0,EW_G:0,EW_Y:0,EW_R:1\n',
    'NS_YELLOW': 'NS_G:0,NS_Y:1,NS_R:0,EW_G:0,EW_Y:0,EW_R:1\n',
    'EW_GREEN':  'NS_G:0,NS_Y:0,NS_R:1,EW_G:1,EW_Y:0,EW_R:0\n',
    'EW_YELLOW': 'NS_G:0,NS_Y:0,NS_R:1,EW_G:0,EW_Y:1,EW_R:0\n',
    'ALL_RED':   'NS_G:0,NS_Y:0,NS_R:1,EW_G:0,EW_Y:0,EW_R:1\n'
}

def render_ascii_traffic_light(phase_name, is_preempt=False):
    ns_g = "🟢" if "NS_GREEN" in phase_name else "⚫"
    ns_y = "🟡" if "NS_YELLOW" in phase_name else "⚫"
    ns_r = "🔴" if ("EW_GREEN" in phase_name or "EW_YELLOW" in phase_name or "ALL_RED" in phase_name) else "⚫"

    ew_g = "🟢" if "EW_GREEN" in phase_name else "⚫"
    ew_y = "🟡" if "EW_YELLOW" in phase_name else "⚫"
    ew_r = "🔴" if ("NS_GREEN" in phase_name or "NS_YELLOW" in phase_name or "ALL_RED" in phase_name) else "⚫"

    preempt_badge = "🚨 [PREEMPTION WAVE ACTIVE]" if is_preempt else ""
    return (
        f"\r[HIL PHYSICAL LEDS]  North-South: [{ns_r}{ns_y}{ns_g}]  |  "
        f"East-West: [{ew_r}{ew_y}{ew_g}]  |  Phase: {phase_name:<10} {preempt_badge}"
    )

def run_hil_bridge():
    print("=" * 65)
    print("🚦 AURA HARDWARE-IN-THE-LOOP (HIL) PHYSICAL CONTROLLER BRIDGE")
    print(f"   Target Serial Port: {SERIAL_PORT} @ {BAUD_RATE} baud")
    print(f"   Telemetry Endpoint: {BACKEND_URL}")
    print("=" * 65)

    ser = None
    try:
        import serial
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print(f"✅ Hardware Connected: Successfully opened {SERIAL_PORT}")
    except Exception as e:
        print(f"ℹ️ Physical serial port not attached ({e}). Running in Virtual HIL Emulation Mode.")

    print("\nStarting live telemetry synchronization... (Press Ctrl+C to exit)\n")

    last_phase = None
    try:
        while True:
            try:
                res = requests.get(BACKEND_URL, timeout=0.5).json()
                active_signal = res.get("activeSignal", "NS_GREEN")
                sys_mode = res.get("systemMode", "AI_OPTIMIZED")
                is_preempt = "PREEMPTION" in active_signal or "GREEN WAVE" in active_signal

                if "NS" in active_signal and "YELLOW" in active_signal:
                    phase = "NS_YELLOW"
                elif "NS" in active_signal:
                    phase = "NS_GREEN"
                elif "EW" in active_signal and "YELLOW" in active_signal:
                    phase = "EW_YELLOW"
                elif "EW" in active_signal:
                    phase = "EW_GREEN"
                elif sys_mode == "POLICE_STOP":
                    phase = "ALL_RED"
                else:
                    phase = "NS_GREEN"

                if ser and ser.is_open:
                    command = PIN_MAP.get(phase, PIN_MAP['ALL_RED'])
                    ser.write(command.encode('utf-8'))

                sys.stdout.write(render_ascii_traffic_light(phase, is_preempt))
                sys.stdout.flush()

            except Exception:
                pass

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n\n🛑 HIL Bridge stopped cleanly.")
    finally:
        if ser and ser.is_open:
            ser.close()

if __name__ == '__main__':
    run_hil_bridge()
