import os

path = '../../Results/time split Location Strings'

def find_file(path, given_profession, given_minute):
    folders = os.listdir(path)
    for folder in folders:
        subfolder_path = os.path.join(path, folder)
        subfolders = os.listdir(subfolder_path)

        for subfolder in subfolders:
            stem = os.path.splitext(subfolder)[0]      # → "Strings_af_0_239"

            parts = stem.split('_')
            profession = parts[1]
            starting_num = int(parts[-2])
            ending_num = int(parts[-1])
            if profession == given_profession:
                for num in range(starting_num, ending_num+1):
                    if num == given_minute:
                        print(subfolder)

find_file(path, 'am', 21)