from Python.common import *
import time
import csv
import numpy as np


class Sample:
    """
    A class to handle scanning operations using a UART connection.
    Includes methods to start the scan process, process received data, and save results to a CSV file.

    Attributes:
        uart (object): The UART object used for communication.
        angle_dec (int): The current angle in decimal format.
    """
    
    
    def __init__(self, uart):
        """
        Initializes the Sample object.

        Args:
            uart (object): The UART object for communication.
        """
        self.uart = uart
        self.angle_dec = None


    def start(self, angle):
        """
        Starts the scanning process for a specific angle.
        - Continuously retries the process if no valid data is received.
        - Sends commands to reset, start, and stop scanning.
        - Processes received data and saves it to a CSV file.

        Args:
            angle (int): The angle to scan (in degrees).
        """
        self.angle_dec = angle

        while True:  # Buclă infinită până când datele sunt valide
            try:
                # Resetăm bufferul UART și trimitem comenzile
                self.uart.ser.reset_input_buffer()
                print("GET_LIDAR_CONF", GET_HEALTH_STATUS)
                self.send_package(self.uart, self.angle_dec, GET_HEALTH_STATUS)
                time.sleep(1)

                print("START_SCAN")
                self.send_package(self.uart, self.angle_dec, START_SCAN)
                time.sleep(5)

                print("STOP_SCAN")
                self.send_package(self.uart, self.angle_dec, STOP_SCAN)
                time.sleep(1)

                # Verificăm dacă datele sunt goale
                if len(self.uart.data) == 0:
                    print("No data received. Retrying...")
                    continue  # Reîncepe bucla dacă nu sunt date
                
                # Procesăm datele și salvăm
                print(len(self.uart.data), "<-self.uart.data")
                self.save_hex_list_to_csv(
                    self.extract_angel_and_distance(self.extract_data(self.uart.data)),
                    FILE_NAME
                )
                print("Scan completed successfully!")
                break  # Ieșim din buclă dacă totul este în regulă

            except KeyboardInterrupt:
                print("\nProgram interrupted by user.")
                break  # Ieșim din buclă dacă utilizatorul oprește manual programul

            finally:
                self.uart.data.clear()
                print("________________ALL DONE___________________")


    def send_package(self, uart_comunication, angle, command):
        """
        Sends a command package over UART.

        Args:
            uart_comunication (object): The UART object.
            angle (int): The angle for the scan.
            command (int): The command to send (e.g., START_SCAN).
        """
        # MESSAGE = [angle, command] if angle is not None else [command]
        MESSAGE = [angle, command]
        print("MESSAGE", MESSAGE)
        uart_comunication.send(MESSAGE)

    
    def save_hex_list_to_csv(self, angle_distance, file_name):
        """
        Saves angle-distance data to a CSV file.

        Args:
            angle_distance (dict or list): The processed angle-distance data.
            file_name (str): The base name of the CSV file.
        """
        print(self.angle_dec, type(self.angle_dec))
        print(file_name, type(file_name))
        file_name = file_name + "_" + str(self.angle_dec)
        print(file_name)
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Scrie antetul CSV (opțional)
            writer.writerow(["Key", "Value"])
            # Scrie fiecare pereche cheie-valoare pe un rând nou
            if isinstance(angle_distance, dict):
                for key, value in angle_distance.items():
                    writer.writerow([key, value])
            elif isinstance(angle_distance, list):
                count = 0
                for item in angle_distance:
                    if count <=99:
                        count += 1
                        try:
                            # Convertim item la int înainte de a aplica hex()
                            int_item = int(item, 16) if isinstance(item, str) and item.startswith("0x") else int(item)
                            writer.writerow([hex(int_item)])
                        except ValueError:
                            print(f"Eroare: '{item}' nu poate fi convertit în hex!")
        
    
    def extract_data(self, data_hex):
        """
        Extracts valid data from a received hex list by removing headers.

        Args:
            data_hex (list): The raw data received from the LIDAR in hexadecimal format.

        Returns:
            list: The extracted data.
        """
        print("data_hex",len(data_hex))
        data_hex = [int(x, 16) for x in data_hex]
        start_index = -1
        result = []
        
        for i in range(len(data_hex) - len(START_SCAN_RESP) + 1):
            if data_hex[i:i+len(START_SCAN_RESP)] == START_SCAN_RESP:
                start_index = i + len(START_SCAN_RESP)
                break

        # Extrage valorile ulterioare dacă secvența a fost găsită
        if start_index != -1:
            result = data_hex[start_index:]
        print("result",len(result))
        return result


    def extract_angel_and_distance(self, data):
        """
        Extracts angle-distance pairs from the data.

        Args:
            data (list): The raw data extracted from the LIDAR.

        Returns:
            dict: A dictionary of angles and their corresponding distances.
        """
        count = 0
        angle_distance = {key: 0 for key in range(360)}
        print("data", len(data))
        for idx in range(0, len(data), 5):
            package = data[idx:idx+5]
            if len(package) == 5:
                angle, distance = self.hex_to_angle_and_distance(package)
                angle = round(angle * 2)
                if angle == 360:
                    angle =0
                if angle_distance[angle] == 0:
                    angle_distance[angle] = distance
            count += 1
         
        return self.interpolate_missing_distances(angle_distance)
    
       
    def hex_to_angle_and_distance(self, packet):
        """
        Converts a raw 5-byte packet into angle and distance.

        Args:
            packet (list): A 5-byte data packet.

        Returns:
            tuple: (angle, distance).
        """
        if len(packet) != 5:
            raise ValueError("Pachet invalid! Lungimea trebuie să fie exact 5 bytes.")
        
        angle_q6 = ((packet[1] >> 2) & 0x3F) | (packet[2] << 6)
        angle = angle_q6 / 64.0

        distance_q2 = packet[3] | (packet[4] << 8)
        distance = distance_q2 / 4.0

        return angle, distance


    def interpolate_missing_distances(self, data):
        """
        Interpolates missing distances (values equal to 0) in the data.

        Args:
            data (dict): A dictionary with angles as keys and distances as values.

        Returns:
            dict: The dictionary with interpolated distances.
        """
        # Extragem unghiurile și valorile
        angles = np.array(list(data.keys()))
        distances = np.array(list(data.values()))
        
        # Identificăm indicii pentru valori nenule
        non_zero_indices = np.where(distances > 0)[0]
        non_zero_angles = angles[non_zero_indices]
        non_zero_distances = distances[non_zero_indices]
        
        # Interpolăm valorile lipsă
        interpolated_distances = np.interp(angles, non_zero_angles, non_zero_distances)
        
        # Înlocuim valorile în dicționar
        for i, angle in enumerate(angles):
            data[angle] = round(interpolated_distances[i], 1)
        
        return data