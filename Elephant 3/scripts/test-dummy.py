import os

import pandas as pd

os.path.abspath(os.curdir)
os.chdir("..")
main_dir_path = os.path.abspath(os.curdir)

targets = ['\\rw']

string_path = main_dir_path + '\\Results\\Location Strings' + targets[0]+ '\Strings_' + targets[0][1:]+'.xlsx'

print(main_dir_path)
results_path = main_dir_path+ '\\Results\Clustered Location Strings'
df = pd.read_excel(string_path)


print(string_path)
print(results_path+ targets[0]+ '\Strings_' + targets[0][1:]+'_cluster'+str(3)+'.xlsx')