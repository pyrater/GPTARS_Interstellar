import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import os

# Initialize I2C bus.
i2c = busio.I2C(SCL, SDA)

# Initialize PCA9685.
pca = PCA9685(i2c)
pca.frequency = 50  # Set the PWM frequency to 50Hz for servos.

# Constants
MIN_ANGLE = 0
MAX_ANGLE = 180
MIN_SERVO = 0
MAX_SERVO = 11

# Initialize servo positions (default to 0 degrees).
servo_positions = [0] * 12

# Function to set the servo angle.
def set_servo_angle(channel, angle):
    """
    Set the angle of the servo on the specified channel.
    """
    pulse_min = 500
    pulse_max = 2500
    pulse_length = (pulse_max - pulse_min) * (angle / 180) + pulse_min
    pwm_value = int(pulse_length / (1000000 / pca.frequency) * 0xFFFF)
    pca.channels[channel].duty_cycle = pwm_value
    servo_positions[channel] = angle  # Update the position in the list.

# Function to display the current positions of all servos.
def display_servo_positions():
    """
    Clear the screen and display the current positions of all servos.
    """
    os.system("clear")  # Clear the terminal screen.
    print("Servo Positions:")
    print("----------------")
    for i in range(MIN_SERVO, MAX_SERVO + 1):
        print(f"Servo {i}: {servo_positions[i]} degrees")
    print("----------------")

# Get validated integer input.
def get_valid_input(prompt, min_value, max_value):
    """
    Prompt the user for input and validate it within the specified range.
    """
    while True:
        user_input = input(prompt).strip()
        if user_input.isdigit():
            value = int(user_input)
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Error: Please enter a number between {min_value} and {max_value}.")
        else:
            print("Error: Please enter a valid number.")

# Menu to control servos.
def servo_control_menu():
    selected_servo = None
    print("\nWelcome to the Servo Control Program!")
    print("Use this menu to control up to 12 servos (channels 0-11).")
    print("Press Ctrl+C at any time to exit.")

    while True:
        try:
            # Display current positions before showing the menu.
            display_servo_positions()

            print("Servo Control Menu")
            print("1. Select a Servo (0-11) and Set Position")
            print("2. Set Position of Currently Selected Servo")
            print("3. Exit")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                # Select Servo and set position immediately.
                selected_servo = get_valid_input("Enter the servo number (0-11): ", MIN_SERVO, MAX_SERVO)
                position = get_valid_input(f"Enter position for Servo {selected_servo} (0-180 degrees): ", MIN_ANGLE, MAX_ANGLE)
                set_servo_angle(selected_servo, position)

            elif choice == "2":
                # Set position of currently selected servo.
                if selected_servo is not None:
                    position = get_valid_input(f"Enter position for Servo {selected_servo} (0-180 degrees): ", MIN_ANGLE, MAX_ANGLE)
                    set_servo_angle(selected_servo, position)
                else:
                    print("Error: No servo selected. Please select a servo first (option 1).")

            elif choice == "3":
                print("Exiting servo control. Goodbye!")
                break

            else:
                print("Error: Invalid choice. Please select a valid option.")

        except KeyboardInterrupt:
            print("\nProgram interrupted by user. Exiting gracefully.")
            break

# Run the menu.
try:
    servo_control_menu()
finally:
    pca.deinit()  # Safely reset the PCA9685 module.
