import os
import csv
import numpy as np
from stl import mesh
import math


def read_csv_to_dict(base_path, base_filename="angle_180"):
    """
    Reads CSV files for angles from 0 to 180 degrees, extracts data, and organizes it into a dictionary.

    Args:
        base_path (str): Path to the folder containing CSV files.
        base_filename (str): Base name of the CSV files (e.g., 'angle_180').

    Returns:
        dict: A dictionary where keys are angles (0–180) and values are lists of tuples (lidar_angle, distance).
    """
    results = {}

    for angle in range(0, 181):
        file_name = base_filename.replace("0", str(angle))
        file_path = os.path.join(base_path, file_name)

        # Verificăm dacă fișierul există
        if not os.path.exists(file_path):
            print(f"Fișierul {file_path} nu există. Continuăm cu următorul.")
            continue

        # Inițializăm lista pentru unghiul curent
        results[angle] = []

        # Citim datele din fișier
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                try:
                    key = int(row[0])
                    value = float(row[1])
                    results[angle].append((key, value))
                except (ValueError, IndexError):
                    print(f"Rând invalid în fișierul {file_path}: {row}")
                    continue

    return results


def convert_to_cartesian_3d(data_dict):
    """
    Converts polar coordinates (angle, distance) into Cartesian 3D coordinates.

    Args:
        data_dict (dict): A dictionary of angles and distances.

    Returns:
        list: A list of 3D points (x, y, z).
    """
    points = []
    for servo_angle, values in data_dict.items():
        servo_rad = math.radians(servo_angle)  # Unghiul servomotorului în radiani

        for lidar_angle, distance in values:
            lidar_rad = math.radians(lidar_angle)
            # Coordonate în plan XY pentru rotația LIDAR-ului
            x = distance * math.cos(lidar_rad)
            y = distance * math.sin(lidar_rad)
            # Rotim planul XY în jurul axei X pentru unghiul servomotorului
            z = y * math.sin(servo_rad)
            y = y * math.cos(servo_rad)
            points.append((x, y, z))
    return points


def generate_stl_from_points(points, output_file, points_per_layer=360):
    """
    Generates a 3D STL file from a list of 3D points.

    Args:
        points (list): A list of 3D points (x, y, z).
        output_file (str): Name of the output STL file.
        points_per_layer (int): Number of points in each layer of the scan.
    """
    vertices = np.array(points)
    faces = []

    total_points = len(vertices)
    layers = total_points // points_per_layer

    for i in range(layers - 1):  # Ne oprim înainte de ultimul strat
        for j in range(points_per_layer - 1):
            # Calculăm idx-ii punctelor
            v0 = i * points_per_layer + j
            v1 = v0 + 1
            v2 = v0 + points_per_layer
            v3 = v2 + 1

            if v3 >= total_points:  # Evităm depășirea limitei
                continue

            # Adăugăm triunghiurile
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])

    # Generăm mesh-ul STL
    stl_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            stl_mesh.vectors[i][j] = vertices[face[j]]

    stl_mesh.save(output_file)
    print(f"Fișier STL generat: {output_file}")


if __name__ == "__main__":

    base_path = r"D:\Repos\SCAN_360\data"
    base_filename = "angle_0"
    results = read_csv_to_dict(base_path, base_filename)
    
    output_file = "sala_215.stl"
    points_per_layer = 360

    # Conversie în coordonate 3D
    points = convert_to_cartesian_3d(results)

    # Generare fișier STL
    generate_stl_from_points(points, output_file, points_per_layer)