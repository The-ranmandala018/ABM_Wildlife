# import xml.etree.ElementTree as ET
# import csv

# def kml_to_csv(kml_file_path, csv_file_path):
#     """
#     Converts a KML file containing point coordinates to a CSV file with Longitude and Latitude columns.
    
#     This script assumes a standard KML structure with Placemarks containing Points.
#     It extracts longitude and latitude from <coordinates> tags (format: lon,lat,alt).
    
#     Args:
#     kml_file_path (str): Path to the input KML file.
#     csv_file_path (str): Path to the output CSV file.
#     """
#     # Parse the KML file
#     tree = ET.parse(kml_file_path)
#     root = tree.getroot()
    
#     # KML namespace
#     ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
#     # List to hold coordinates
#     coordinates = []
    
#     # Find all Placemarks
#     for placemark in root.findall('.//kml:Placemark', ns):
#         # Look for Point elements
#         point = placemark.find('.//kml:Point/kml:coordinates', ns)
#         if point is not None:
#             # Extract text and split by comma
#             coord_text = point.text.strip()
#             if coord_text:
#                 parts = coord_text.split(',')
#                 if len(parts) >= 2:
#                     lon = parts[0].strip()
#                     lat = parts[1].strip()
#                     coordinates.append((lon, lat))
    
#     # Write to CSV
#     with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Longitude', 'Latitude'])
#         writer.writerows(coordinates)
    
#     print(f"Conversion complete! {len(coordinates)} points exported to {csv_file_path}")

# # Usage with your file path
# kml_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\Waterholes.kml"
# csv_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\Waterholes.csv"  # Adjust output path as needed
# kml_to_csv(kml_path, csv_path)

import xml.etree.ElementTree as ET
import csv

def kml_to_csv(kml_file_path, csv_file_path):
    """
    Converts a KML file containing point coordinates to a CSV file with Name, Longitude, and Latitude columns.
    
    This script assumes a standard KML structure with Placemarks containing Points and Names.
    It extracts the Placemark name, and longitude and latitude from <coordinates> tags (format: lon,lat,alt).
    
    Args:
    kml_file_path (str): Path to the input KML file.
    csv_file_path (str): Path to the output CSV file.
    """
    # Parse the KML file
    tree = ET.parse(kml_file_path)
    root = tree.getroot()
    
    # KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    # List to hold data
    data = []
    
    # Find all Placemarks
    for placemark in root.findall('.//kml:Placemark', ns):
        # Extract name
        name_elem = placemark.find('.//kml:name', ns)
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else 'Unknown'
        
        # Look for Point elements
        point = placemark.find('.//kml:Point/kml:coordinates', ns)
        if point is not None:
            # Extract text and split by comma
            coord_text = point.text.strip()
            if coord_text:
                parts = coord_text.split(',')
                if len(parts) >= 2:
                    lon = parts[0].strip()
                    lat = parts[1].strip()
                    data.append((name, lon, lat))
    
    # Write to CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Longitude', 'Latitude'])
        writer.writerows(data)
    
    print(f"Conversion complete! {len(data)} points exported to {csv_file_path}")

# Usage with your file path
kml_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\Waterholes.kml"
csv_path = r"G:\Work (UoP)\MARC\ABM\Animal\ai4covid_clustering-dev - Elephants - Pure Markov\data\Waterholes.csv"  # Adjust output path as needed
kml_to_csv(kml_path, csv_path)