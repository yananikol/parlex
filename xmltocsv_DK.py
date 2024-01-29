from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('--dir', type=str, required=True)
args = parser.parse_args()

def open_file(path):
    "Opens file and creates soup."
    with open(path, 'r') as doc:
        file = doc.read()
    soup = BeautifulSoup(file, 'xml')
    return soup

def get_size(soup):
    "For DK: Gets total number of words and punctuation, corresponding to array rows."

    words = soup.TEI.encodingDesc.tagsDecl.find('tagUsage', {'gi':'w'}).attrs['occurs']
    puncts = soup.TEI.encodingDesc.tagsDecl.find('tagUsage', {'gi':'pc'}).attrs['occurs']
    total = int(words) + int(puncts)

    return total

def create_array(rows, cols = 5):
    "Initializes empty array of set size. Default is 5 cols for Danish. "

    array = np.empty((rows,cols), dtype = object)
    return array

def fill(soup):
    "Fills array with ID, token, lemma, named entity status, and morhpological data for each word."
    array = create_array(get_size(soup))

    for i, w in enumerate(soup.body.find_all(['w', 'pc'])):
        w_id = w.attrs['xml:id']
        token = w.string
        lemma = w.attrs.get('lemma', w.string).lower()
        msd = w.attrs['msd'][8:] #first element is always UPosTag
        named = str([w.parent.attrs['type'] if w.parent.name == 'name' else None])[1:-1] #removes brackets
        
        array_object = np.array([w_id, token, lemma, named, msd])
        array[i, :] = array_object       
    
    return array

def to_dataframe(array):
    "Converts array to DataFrame and splits columns, removing extra empty rows created during create_array."

    df = pd.DataFrame(array, columns = ['id','token','lemma', 'NE', 'msd'])
    df[['id','seg','sent', 'word']] = df['id'].str.split('.', expand=True) #expand id

    expansion = df['msd'].str.split('|', expand=True) #expand msd
    new_cols = len(expansion.columns) - 1 #count expanded columns excluding PoS

    col_list = ['pos']
    for col in range(new_cols): #name expanded columns
        col_list.append('msd' + str(col+1)) 

    df[col_list] = expansion #expand dataframe
    df = df.drop(['msd'], axis = 1)

    return df


def main():
    #creating new root directory for CSV corpus 
    name = args.dir[:-3]
    newdir = name + 'CSV' 
    if not os.path.exists(newdir):
        os.makedirs(newdir)

    for root, dirs, files in os.walk(args.dir, topdown=True):
        dirs[:] = [d for d in dirs if re.fullmatch('[0-9]*', d)] #include only numeric (year) direcotries
        for folder in dirs: #create new year directories for new root file
            newyear = os.path.join(newdir, folder)
            if not os.path.exists(newyear):
                os.makedirs(newyear)

        #filter out other files
        files[:] = [f for f in files if re.search("[0-9]+.ana.xml", f)]
        for name in files:
            print("Converting", name)
            filepath = os.path.join(root, name)

            #conversion
            soup = open_file(filepath)
            filled_array = fill(soup)
            dataframe = to_dataframe(filled_array)

            #save to file in new directory
            filename = soup.TEI.attrs['xml:id'] + '.csv' #get file name
            year = filepath.split(os.sep)[1] #get year
            path = os.path.join(newdir, year, filename) #create new path
            dataframe.to_csv(path, index = False, sep = '\t') #save csv to path 


if __name__ == '__main__':
    main()