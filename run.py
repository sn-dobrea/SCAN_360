import argparse
from Python.sample import Sample
from Python.common import *
from Python.uart import UART

def start_scan():
    """
    Starts the scanning process by iterating through predefined angles.
    - Initializes the UART connection.
    - Iterates over all predefined angles in the ANGLES dictionary.
    - Sends commands to perform scanning for each angle.
    """
    print("Starting the scan...")
    try:
        UART.ser.close()
    except:
        pass
    
    UART.init(port=COM, baud_rate=BAUT_RATE)
    sample = Sample(UART)
    for angle in ANGLES.keys():
        print("ANGLE",angle)
        sample.start(angle)
    UART.close()


def sample_scan(angle):
    """
    Performs a scan operation for a specific angle.
    - Validates the provided angle (must be between 0 and 180).
    - Initializes the UART connection.
    - Commands the scanner to scan at the specified angle.
    """
    UART.init(port=COM, baud_rate=BAUT_RATE)
    if (angle > 180) or (angle < 0):
        print("Error: Angle must be between 0 and 180 degrees.")
    else:
        print(f"Running sample scan with angle: {angle} degrees")
    sample = Sample(UART)
    print("angle",angle)
    sample.start(angle)
    UART.close()
        
        
def valid_angle(value):
    """
    Validates that the provided angle is between 0 and 180.
    - Raises an `argparse.ArgumentTypeError` if the angle is outside the valid range.
    """
    ivalue = int(value)
    if ivalue < 0 or ivalue > 180:
        raise argparse.ArgumentTypeError("Angle must be between 0 and 180.")
    return ivalue


def help():
    """
    Displays a help message with available commands.
    - Describes the purpose of each command and its usage.
    """
    print("Available commands:")
    print("start_scan     - Start the scan operation.")
    print("sample_scan    - Perform a sample scan with a specified angle (0-180).")
    print("help           - Show this help message.")



if __name__ == "__main__":
    """
    Main entry point for the script.
    - Parses command-line arguments to determine the desired operation.
    - Maps commands to their corresponding functions.
    - Executes the selected command, optionally passing arguments (e.g., angle).
    """
    parser = argparse.ArgumentParser(description="Control scan operations.")
    parser.add_argument("command", choices=["start_scan", "sample_scan", "help"], help="The command to execute")
    parser.add_argument("--angle", type=valid_angle, help="The angle for the sample scan (between 0 and 180 degrees)", default=None)
    args = parser.parse_args()
    commands = {
        "start_scan": start_scan,
        "sample_scan": sample_scan,
        "help": help,
    }
    if args.command == "sample_scan" and args.angle is None:
        print("Error: The 'sample_scan' command requires an '--angle' argument.")
    else:
        command_function = commands.get(args.command)
        if command_function:
            if args.command == "sample_scan":
                command_function(args.angle)  # Pass the angle argument to the function
            else:
                command_function()
        else:
            print("Invalid command.")