from subprocess import call
from sys import argv
import pandas as pd
def transform(filename):
    call(["pdftotext","-layout",filename])
    return filename.split(".")[0] + ".txt"

def segment(contents):
    relevant = []
    start = False
    for line in contents:
        if "Population" in line:
            start = True
        if "www.coalitionforthehomeless.org" in line:
            start = False
        if start:
            relevant.append(line)
    return relevant

def parse(relevant):
    tmp = {}
    df = pd.DataFrame()
    count = 0
    for ind,line in enumerate(relevant):
        split_up = line.split(" ")
        sp = [elem for elem in split_up if elem !='']
        if len(split_up) == 1: continue 
        if len(sp) == 11:
            keys = ["month","year","total_population","total_families",
                    "total_persons_in_families","children","adults_in_families",
                    "single_adults","single_men","single_women","average_shelter_stays_for_families"]
            for ind,elem in enumerate(sp):
                try:
                    tmp[keys[ind]] = str(elem)
                except IndexError:
                    print split_up
            df = df.append(tmp,ignore_index=True)
    return df

if __name__ == '__main__':
    txt_file = transform(argv[1])
    text = open(txt_file,"r").read().decode("ascii","ignore")
    contents = text.split("\n")
    relevant = segment(contents)
    df = parse(relevant)
    df.to_csv("homeless_data.csv")
