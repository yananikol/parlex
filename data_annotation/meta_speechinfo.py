from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os
import argparse
import re
from tqdm import tqdm
import string

def open_xml(path):
    "Opens file and creates soup."
    with open(path, 'r') as doc:
        file = doc.read()
    soup = BeautifulSoup(file, 'xml')
    return soup

def create_dict(filepath):
    "For DK: Creates and returns dictionary of topic titles (keys) and speech id's (values)."
    "For BG: Creates and returns dictionaryof speech ids (keys) and speeches (values) from .txt file"

    if args.lang == "dk":
        speech_dict = {}
        soup = open_xml(filepath) #create soup
        for el in soup.TEI.body.find_all('div'):
            for child in el.children:
                if child.name == 'head': #find speech topics
                    key_name = child.contents[0]
                elif child.name == 'u': #find speech ids under each topic 
                    speech_dict[key_name] = speech_dict.get(key_name, []) + [child.attrs['xml:id']]
                else:
                    continue
        
        return speech_dict
    
    elif args.lang == "bg":
        with open(filepath, 'r') as file: #open txt file
            lines = file.readlines()
        ids = [line.split('\t')[0] for line in lines] #get ids
        speeches = [line.split('\t')[1] for line in lines] #get speeches
        speechdict = dict(zip(ids, speeches))

        return speechdict

def new_meta_dk(textfile, metafile):
    "Converts speech dictionary to dataframe with annotation"
    dictionary = create_dict(textfile)
    meta = pd.read_csv(metafile, delimiter = "\t")
    df = pd.Series(dictionary, name = "Speech_id").rename_axis("Topic_title").explode().reset_index()
    df["Debate"] = df['Topic_title'].str.contains("behandling") + df['Topic_title'].str.contains("afstemning") #add debate annotation
    df["Question"] = df['Topic_title'].str.contains("spørgetime") + df['Topic_title'].str.contains("Spm.") #add question annotation
    new_meta = meta.join(df.set_index("Speech_id"), on = 'ID' ) #merge dataframes

    return new_meta

def create_chairlist(metadf):
    "Opens meta file and extracts list of chairperson speeches"
    chairlist = list(metadf[metadf["Speaker_role"] == "Chairperson"]["ID"])

    return chairlist


def find_matches(text):
    matchlist = []
    match = []

    curr_token = False
    for word in text.split():
        if word.isupper():
            match.append(word)
            curr_token = True
        else:
            if curr_token == True and word.strip(string.punctuation).isalpha() == False:
                match.append(word)
                curr_token = True
            else:
                if len(match) > 0:
                    match = " ".join(match)
                    match = match.rstrip("C")
                    matchlist.append(match)
                    match = []
                curr_token = False
    return matchlist

def bg_annotate(textfile, metadf):
    "Annotates speeches in document by Debate or Question based on string-matching the Speaker/Chairperson's speeches and returns dictionary"
    chairlist = create_chairlist(metadf) #list of chairperson speeches
    speechdict = create_dict(textfile) #dictionary of speech ids to speeches
    
    matchdict = dict() #creates a dictionary in the format {matched string: (index, speech type)}
    spisuk = ["ГЛАСУВАНЕ", "ЧЕТЕНЕ", "КОНТРОЛ", "ПРОЕКТ", "ПРОЕКТИ", "ЗАКОНОПРОЕКТ", "РЕШЕНИЕ",  "ДОКЛАД", "ИЗБОР", 
                "ИЗСЛУШВАНЕ", "ОТЧЕТ", 'НАДЗОР', 'ПРОМЕНИ', 'ПРЕДСТАВЯНЕ', 'ОТНОСНО', 'РАЗИСКВАНИЯ', 'ОСТАВКА', 
                'ИЗПЪЛНЕНИЕ']
        

    for id in chairlist:
        index = int(id.split('u')[1])
        speech = speechdict[id]
        matches = find_matches(speech) #search uppercase strings
        for match in matches:
            if len(match) > 10:
                for word in match.split():
                    if word in spisuk:
                        matchdict[match] = (index, word)
                        break

    return matchdict, speechdict


def new_meta_bg(textfile, metafile):
    "Creates array of ids, titles and booleans based on annotation dictionary"
    
    meta = pd.read_csv(metafile, delimiter = "\t")
    matchdict, speechdict = bg_annotate(textfile, meta)
    ids = list(speechdict.keys())
    speecharray = np.empty((len(ids), 3), dtype = object) #create array
    speecharray[:, 0] = np.array(ids) #insert speech ids
    items = list(matchdict.items())

    for i, item in enumerate(items):
        key = item[0]
        index, annot = item[1]
        
        try: #get next id
            next_index = items[i+1][1][0]
        except: #if not, get last id
            next_index = int(ids[-1].split('u')[1])
            
        #adds topic title
        speecharray[index:next_index, 1] = key

        #add meeting type
        speecharray[index:next_index, 2] = annot

    #create dataframe    
    df = pd.DataFrame(speecharray, columns = ["Speech_id", "Topic_title", "Meeting_type"])
    new_meta = meta.join(df.set_index("Speech_id"), on = 'ID' )
    return new_meta    


def main():
    "Loops over files in directory and converts them, creating new CSV directory"


    for root, dirs, files in os.walk(args.dir, topdown=True):

        if args.lang == "bg":
            for name in tqdm(files):
                if name.endswith('.txt') and name != "00README.txt":
                    textfile = os.path.join(root, name)
                    metafile = os.path.join(root, os.path.splitext(name)[0] + "-meta.tsv")

                    new_meta = new_meta_bg(textfile, metafile)
                    new_meta.to_csv(os.path.splitext(metafile)[0] + ".csv", sep = '\t')

        elif args.lang == "dk":
            for name in files:
                if name.endswith('.ana.xml') and len(name) >33 :
                    print(name)
                    textfile = os.path.join(root, name)
                    metaroot = "ParlaMint-DK.txt"
                    year = os.path.split(root)[1]
                    metafile = os.path.join(metaroot, year, name.rstrip("ana.xml") + "-meta.tsv")
                    
                    new_meta = new_meta_dk(textfile, metafile)
                    new_meta.to_csv(os.path.splitext(metafile)[0] + ".csv", sep = '\t')
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, required=True)
    #parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--lang', type=str, required=True)
    args = parser.parse_args()
    
    main()