from nlptools.morphology import settings 
import pickle
from nlptools.DataDownload import downloader
import os 


filename = 'ALMA27012000.pickle'
path =downloader.get_appdatadir()
file_path = os.path.join(path, filename)
with open(file_path, 'rb') as f:
       #Load the serialized data from the file
    settings.div_dic = pickle.load(f)
       #print(ALMA_dic)
