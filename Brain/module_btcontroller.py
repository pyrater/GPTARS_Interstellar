
import evdev
from datetime import datetime
#MAIN FUNCTION
# Set the path to your gamepad
gamepad_path = '/dev/input/event6'

def start_controls():
# Main loop to read events
    try:
        # Connect to the gamepad
        gamepad = evdev.InputDevice(gamepad_path)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: {gamepad.name} connected.")
    except FileNotFoundError:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: Gamepad not found at {gamepad_path}")
        return
        exit()

    # Define mappings for button events
    button_map = {
        evdev.ecodes.BTN_SOUTH: "A Button",
        evdev.ecodes.BTN_EAST: "B Button",
        evdev.ecodes.BTN_NORTH: "X Button",
        evdev.ecodes.BTN_WEST: "Y Button",
        evdev.ecodes.BTN_TL: "Left Bumper",
        evdev.ecodes.BTN_TR: "Right Bumper",
        evdev.ecodes.BTN_SELECT: "Select",
        evdev.ecodes.BTN_START: "Start",
        evdev.ecodes.BTN_MODE: "Home",
        evdev.ecodes.BTN_THUMBL: "Left Stick Press",
        evdev.ecodes.BTN_THUMBR: "Right Stick Press",
        313: "R2 Button",  # Example label for Unknown Button 313
        312: "L2 Button",
        306: "Bottom Button",
    }

    # Define mappings for analog events
    analog_map = {
        evdev.ecodes.ABS_X: "Left Stick X",
        evdev.ecodes.ABS_Y: "Left Stick Y",
        evdev.ecodes.ABS_Z: "Right Stick X",
        evdev.ecodes.ABS_RZ: "Right Stick Y",
        evdev.ecodes.ABS_HAT0X: "D-Pad X",
        evdev.ecodes.ABS_HAT0Y: "D-Pad Y",
        9: "Trigger Axis",  # Example label for Unknown Axis 9
    }
    #print("Listening for events... (Press Ctrl+C to exit)")
    try:
        for event in gamepad.read_loop():
            if event.type == evdev.ecodes.EV_KEY:  # Button press/release
                button_name = button_map.get(event.code, f"Unknown Button {event.code}")
                if event.value == 1:  # Button pressed
                    print(f"Button Pressed: {button_name}")
                elif event.value == 0:  # Button released
                    print(f"Button Released: {button_name}")
            elif event.type == evdev.ecodes.EV_ABS:  # Analog stick or D-pad movement
                axis_name = analog_map.get(event.code, f"Unknown Axis {event.code}")
                print(f"{axis_name} moved to {event.value}")
            elif event.type == evdev.ecodes.EV_SYN:  # Synchronization event (optional)
                pass  # Ignore synchronization events
    except KeyboardInterrupt:
        print("\nExiting...")

    # Clean up
    gamepad.close()
