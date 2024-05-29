import osmnx as ox
import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import box

import tkinter as tk
from tkinter import *
from functools import partial

def model(city, threshold, listbox, line_number):
    # Fetch the boundary coordinates of the specified town/city
    place = ox.geocode_to_gdf(city)
    bbox = place.geometry.total_bounds

    # Create a GeoDataFrame with a rectangular polygon representing the area
    bbox_gdf = gpd.GeoDataFrame(geometry=[box(*bbox)], crs="EPSG:4326")

    # Fetch OSM street network within the bounding box
    graph = ox.graph_from_polygon(bbox_gdf.geometry[0], network_type='all')

    # Building footprints
    buildings = ox.geometries_from_polygon(bbox_gdf.geometry[0], tags={'building': True})

    # Reproject the geometry column to a projected CRS
    buildings = buildings.to_crs("EPSG:3857")

    # Calculate the area of each building
    buildings['area'] = buildings['geometry'].area

    # Filter buildings larger than or equal to the threshold
    large_buildings = buildings[buildings['area'] >= threshold]

    # Graph to GeoDataFrame
    nodes, edges = ox.graph_to_gdfs(graph)

    nodes.head()
    edges.head()

    # Plotting data
    fig, ax = plt.subplots(figsize=(12, 8))

    # Set the title of the plot to the selected city
    ax.set_title(city)

    # Plot the outline of the place
    bbox_gdf.to_crs("EPSG:3857").plot(ax=ax, linewidth=2, edgecolor='red')

    # Plot street edges
    edges.to_crs("EPSG:3857").plot(ax=ax, linewidth=1, edgecolor='#BC8F8F')

    # Plot buildings larger than or equal to the threshold with a red outline
    large_buildings.plot(ax=ax, color='red', linewidth=2)

    # Plot all buildings
    buildings[~buildings['geometry'].isin(large_buildings['geometry'])].plot(ax=ax, facecolor='khaki', alpha=0.7)

    # Add building area annotations
    for idx, building in large_buildings.iterrows():
        x, y = building.geometry.centroid.x, building.geometry.centroid.y
        plt.text(x, y, f"{building['area']:.2f} sqm", color='black', fontsize=8,
                 ha='center', va='center', weight='bold')

    plt.tight_layout()
    plt.show()

    # Output the total number of buildings larger than or equal to the threshold
    total_large_buildings = len(large_buildings)
    info = f"Total number of buildings larger than or equal to {threshold} sqm: {total_large_buildings}"

    # Insert the line number and building information into the listbox
    listbox.insert(END, f"{line_number}. {info}")

def clear(entry):
    entry.delete(0, END)

def apply_button_clicked(entry, threshold_entry, listbox):
    selected_city = entry.get()
    threshold = float(threshold_entry.get())
    print("Selected city:", selected_city)
    print("Threshold:", threshold)

    # Get the current number of lines in the listbox
    line_number = listbox.size()
    line_number += 1
    model(selected_city, threshold, listbox, line_number)

def interface():
    root = tk.Tk()
    root.title("Map Display")
    icon = tk.PhotoImage(file="icon.png")
    root.iconphoto(False, icon)
    root.geometry("600x400")

    label = tk.Label(text="Enter the city")
    label.pack()

    entry = tk.Entry()
    entry.pack(anchor=NW, padx=6, pady=6)
    entry.insert(0, "Exeter")

    label_threshold = tk.Label(text="Enter the building area threshold (sqm)")
    label_threshold.pack()

    threshold_entry = tk.Entry()
    threshold_entry.pack(anchor=NW, padx=6, pady=6)
    threshold_entry.insert(0, "5000")

    # Create a listbox to display the building information
    listbox = tk.Listbox(root)
    listbox.pack(fill=BOTH, expand=True)

    # Create a frame for buttons
    button_frame = tk.Frame(root)
    button_frame.pack(side=BOTTOM, padx=6, pady=6)

    apply_button = tk.Button(button_frame, text="Apply", command=partial(apply_button_clicked, entry, threshold_entry, listbox))
    apply_button.pack(side=LEFT)

    clear_button = tk.Button(button_frame, text="Clear", command=partial(clear, entry))
    clear_button.pack(side=LEFT)

    root.mainloop()

if __name__ == '__main__':
    interface()
