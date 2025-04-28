import glob
import os

for file in glob.glob('shared/*/*.flent.gz'):
    print(f'Removing file: {file}')
    os.remove(file)