import pandas as pd
import os
import glob
import string

def create_cluster_mapping(csv_files, cluster_column="Cluster_DBSCAN_0.0005_10", output_dir=None):

    # Verify openpyxl is installed
    try:
        import openpyxl
    except ImportError:
        raise ImportError("The 'openpyxl' library is required for Excel output. Install with: pip install openpyxl")
    
    # Convert single file or directory to list of files
    if isinstance(csv_files, str):
        if os.path.isdir(csv_files):
            csv_files = glob.glob(os.path.join(csv_files, "*.csv"))
        else:
            csv_files = [csv_files]
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    # Dictionary to store results
    results = {}
    
    # Generate letter mappings (A-Z, then AA, AB, ..., ZZ)
    def generate_letters(n):
        letters = []
        for i in range(n):
            if i==0:
                letters.append('Home')
            elif i > 0 and i < 26:
                # Single letters: A, B, ..., Z
                letters.append(string.ascii_uppercase[i-1])
            else:
                # Double letters: AA, AB, ..., AZ, BA, ..., ZZ
                first = string.ascii_uppercase[(i - 26) // 26]
                second = string.ascii_uppercase[(i - 26) % 26]
                letters.append(f"{first}{second}")
        return letters
    
    for csv_file in csv_files:
        try:
            # Verify input file exists
            if not os.path.isfile(csv_file):
                raise FileNotFoundError(f"Input file '{csv_file}' does not exist.")
            
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Ensure cluster column exists
            if cluster_column not in df.columns:
                raise ValueError(f"Column '{cluster_column}' not found in {csv_file}.")
            
            # Get unique cluster numbers, excluding -1 and handling non-integer values
            try:
                unique_clusters = sorted(df[cluster_column][df[cluster_column] != -1].dropna().astype(int).unique())
            except ValueError as e:
                print(f"Error in {csv_file}: Non-integer values in '{cluster_column}'. Error: {e}")
                results[csv_file] = None
                continue
            
            if not unique_clusters:
                print(f"Warning: No valid cluster numbers (excluding -1) in {csv_file}.")
                results[csv_file] = None
                continue
            
            # Generate letters for the unique clusters
            letters = generate_letters(len(unique_clusters))
            
            # Create mapping DataFrame
            mapping_df = pd.DataFrame({
                'cluster_no': unique_clusters,
                'letter': letters
            })
            
            # Determine output file path with .xlsx extension
            base_name = os.path.basename(csv_file).replace("_ClusterData.csv", "_cat.xlsx")
            output_dir = output_dir or os.path.dirname(csv_file)
            output_file = os.path.join(output_dir, base_name)
            
            # Save the mapping to Excel without headers
            mapping_df.to_excel(output_file, index=False, header=False, engine='openpyxl')
            
            print(f"Cluster mapping saved to: {output_file}")
            results[csv_file] = mapping_df
        
        except PermissionError as e:
            print(f"Error processing {csv_file}: Permission error: {e}. Check file/directory permissions.")
            results[csv_file] = None
        except FileNotFoundError as e:
            print(f"Error processing {csv_file}: {e}")
            results[csv_file] = None
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            results[csv_file] = None
    
    return results


# Example usage
if __name__ == "__main__":

    class_names = ["af", "am", "jm", "sf", "sm"]
    for class_name in class_names:

        # for class_name in class_names:
        cluster_path = f"../../clusters/{class_name}"
        output_path = f"../../catalogues/{class_name}"
        os.makedirs(output_path, exist_ok=True)
        create_cluster_mapping(cluster_path, "Cluster_DBSCAN_0.0005_10" , output_path)
