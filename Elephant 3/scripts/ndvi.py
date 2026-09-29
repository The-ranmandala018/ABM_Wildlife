import earthaccess
import os

# Define study area (Etosha bounding box: min_lon, min_lat, max_lon, max_lat)
bounding_box = (14.5, -19.3, 16.8, -18.2)

# Define time period
start_date = '2008-01-01'
end_date = '2014-12-31'

# Output directory
output_dir = '../etosha_modis_ndvi'  # Change as needed
os.makedirs(output_dir, exist_ok=True)

# Authenticate (uses ~/.netrc file)
earthaccess.login(strategy="netrc")

# Search for MOD13Q1 granules (version 6)
granules = earthaccess.search_data(
    short_name='MOD13Q1',
    version='006',
    bounding_box=bounding_box,
    temporal=(start_date, end_date),
    count=1000  # Increase if needed; default is 10
)

print(f"Found {len(granules)} granules matching criteria.")

# Get download links (on-prem for direct HTTP access)
data_links = [granule.data_links(access='onprem') for granule in granules]

# Download with threading (adjust threads for your bandwidth)
earthaccess.download(
    data_links, 
    local_path=output_dir, 
    threads=4  # Parallel downloads; max ~10
)

print(f"Downloaded to {output_dir}")