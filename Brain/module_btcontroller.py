import evdev
from datetime import datetime
import time

from evdev import InputDevice, list_devices, ecodes, categorize
global gamepad_path

def find_controller(controller_name):
    global gamepad_path
    """
    Search for a controller by its name.
    """
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if controller_name.lower() in device.name.lower():
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: Controller found: {device.name} at {device.path}")
            gamepad_path = device.path
            return device
    print(f"No controller found with name: {controller_name}")
    return None

def monitor_controller_events(device):
    """
    Monitor and print events from the selected controller.
    """
    print(f"Monitoring events for {device.name} at {device.path}")
    try:
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                print(categorize(event))
            elif event.type == ecodes.EV_ABS:
                abs_event = categorize(event)
                print(f"Absolute event: {abs_event}")
    except KeyboardInterrupt:
        print("\nExiting event monitoring.")


controller_name = "8BitDo"  # Replace with part of your controller's name
device = find_controller(controller_name)

#if device:
    #monitor_controller_events(device)


def start_controls():
    # Retry loop for detecting the gamepad
    gamepad = None
    while gamepad is None:
        try:
            # Try to connect to the gamepad
            gamepad = evdev.InputDevice(gamepad_path)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: {gamepad.name} connected.")
        except FileNotFoundError:
            #print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: Gamepad not found at {gamepad_path}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait before retrying

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

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOAD: Controls Listening...")
    try:
        for event in gamepad.read_loop():
            if event.type == evdev.ecodes.EV_KEY:  # Button press/release
                button_name = button_map.get(event.code, f"Unknown Button {event.code}")
                if event.value == 1:  # Button pressed
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MOVE: Button Pressed: {button_name}")
                elif event.value == 0:  # Button released
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MOVE: Button Released: {button_name}")
            elif event.type == evdev.ecodes.EV_ABS:  # Analog stick or D-pad movement
                axis_name = analog_map.get(event.code, f"Unknown Axis {event.code}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MOVE: {axis_name} moved to {event.value}")
            elif event.type == evdev.ecodes.EV_SYN:  # Synchronization event (optional)
                pass  # Ignore synchronization events
    except KeyboardInterrupt:
        print("\nExiting...")

    # Clean up
    gamepad.close()
