import serial
import threading
import struct

class UART:
    """
    A static class for managing UART (Universal Asynchronous Receiver-Transmitter) communication.
    Handles serial port initialization, sending, receiving, and closing operations.
    """
    ser = None
    _stop_thread = False
    data = []
    receiver_thread = None


    @staticmethod
    def init(port, baud_rate):
        """
        Initializes the UART connection with the specified port and baud rate.
        - If the connection is already initialized, it avoids reinitializing.
        - Starts a background thread to continuously receive data.
        
        Args:
            port (str): The name of the serial port (e.g., "COM3" or "/dev/ttyUSB0").
            baud_rate (int): The communication speed in bits per second.
        """
        if UART.ser is None:
            UART.ser = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
            print(f"Serial connection established on {port} at {baud_rate} baud.")

            # Pornim thread-ul de recepție o singură dată
            UART._stop_thread = False
            UART.receiver_thread = threading.Thread(target=UART.receive)
            UART.receiver_thread.start()
        else:
            print("Serial connection already initialized.")


    @staticmethod
    def send(hex_data):
        """
        Sends data in hexadecimal format over the UART connection.
        - Converts the data into binary before transmission.
        
        Args:
            hex_data (list[int]): A list of integers representing the data to send in hexadecimal format.
        
        Example:
            UART.send([0xA5, 0x20])  # Sends two bytes: 0xA5 and 0x20.
        """
        if UART.ser is not None:
            try:
                # Convertim fiecare număr din lista la un byte
                byte_data = struct.pack(f"{len(hex_data)}B", *hex_data)
                UART.ser.write(byte_data)  # Trimiterea datelor
                print(f"Sent (hex): {byte_data}")
            except (ValueError, struct.error) as e:
                print(f"Invalid data format: {e}")
        else:
            print("Serial connection is not initialized.")


    @staticmethod
    def receive():
        """
        Continuously receives data from the serial port and stores it in the `data` list.
        - Runs as a background thread.
        - Stops gracefully when `_stop_thread` is set to True.
        """
        while not UART._stop_thread:
            if UART.ser:
                byte_data = UART.ser.read(UART.ser.in_waiting or 1)
                if byte_data:
                    for byte in byte_data:
                        UART.data.append(hex(byte))


    @staticmethod
    def close():
        """
        Closes the UART connection and stops the receiver thread.
        - Ensures that all resources are released properly.
        """
        UART._stop_thread = True
        if UART.receiver_thread:
            UART.receiver_thread.join()
        if UART.ser is not None:
            UART.ser.close()
            UART.ser = None
            print("Serial connection closed.")
