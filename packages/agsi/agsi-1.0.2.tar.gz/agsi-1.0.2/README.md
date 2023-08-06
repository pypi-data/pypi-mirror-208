## Installation

Use the requirements.text file to install dependencies

## Directory Structure used to store files and images

Project_folder>DroneAssets>geodata>images

Project_folder>DroneAssets>geodata>shp_files_drone


## Usage
Using the config file
```python

data_config={
"crs":"epsg:32644",    #Provide crs corresponding to the images for conversions.
"main_shp_file_path":"./assets/DroneAssets/geo_data/gpd_main.shp", #Path for geopandas to read the concatenated shp files
"full_image_directory":"./assets/DroneAssets/geo_data/images", #Path to the directory containing images
"full_image_path":"./assets/DroneAssets/geo_data/images/3b_orthomosaic.rgb.tif", #Path to the particular drone stitched image you want to extract blocks/chips out of
"block_name":"3b", #Name of the block you want to extract from the full stitched image
"chip_directory":"./assets/DroneAssets/geo_data/chips", #Directory path to store the chips into
"full_image_iterator":False, #If true ,launch an iterator to iterate over all the stitched images in the full_image_directory
"block_iterator":False, #If true ,launch an iterator to iterate over all the blocks contained in full_image_path stitched image
"tile_iterator":True, #If true ,launch an iterator to iterate over all the chips created from the block_name image
}

shp_config={
"main_directory":"./assets/DroneAssets/geo_data", #Path to the directory to store the concatenated shp file
"shp_files_directory":"./assets/DroneAssets/geo_data/shap_files_drone" #Path to the directory to fetch all the shp files
}

```

```python

import torch
import os
from torch.utils.data import DataLoader
from data.DroneData import DroneData
from config import shp_config
from data.utils import get_combined_gpd


if __name__ == '__main__':
    # Example usage
    if not os.path.isfile(f"{shp_config['main_directory']}/gpd_main.shp"):
        print("Creating shp_file")
        get_combined_gpd(shp_config["shp_files_directory"],shp_config["main_directory"])

    droneobj=DroneData()
    myiter = iter(droneobj)
    print(next(myiter).profile)

```