from functools import cmp_to_key
import itertools
from pymongo import MongoClient
import getpass
import numpy as np
import re
import pandas as pd
import os
import sys
import json



prev_y = 0
prev_x = 0
num_cols= 1

#custom compare function to sort list containing words in one column
def compare(word1,word2):
    y1_value = int(word1[3])
    x1_value_l = int(word1[1])
    y2_value = int(word2[3])
    x2_value_l = int(word2[1])
    
    #arbitrary value to decide if words are on same line
    if(abs(y1_value-y2_value) < 80 ):
        return x1_value_l - x2_value_l
    
    else:
        return y1_value-y2_value


def sort_companies(comp):
    return comp(0)

def find_bucket(row):
    global prev_y
    global prev_x
    y_value = int(row[3])
    x_value_l = int(row[1])
    x_value_r = int(row[2])
    word = row[-2]
    res = ''
    if(abs(y_value-prev_y) < 80 ):
        if(abs(x_value_l-prev_x) < 300):
            res = word
        else:
            res = '\t' + word
            
    else:
        res= '\n'+word
    
    prev_y = y_value
    prev_x = x_value_r
    return res
        
            
###for .day only     
def organize_day(images):
    x = 0
    global prev_y
    global prev_x
    prev_x = 0
    prev_y = 0
    #create an array of dictionaries, each element the text from given brightness level
    brightness_level = [{} for sub in range(200)]
    for i in range(len(images)): 
        num_cols = 1
        image = images[i]
        #if image contains no information, skip to next iteration

        if image == '':
            continue
        else:
            try:
                words = image.strip()
                words = words.split('\n')
                dfWords = pd.DataFrame([sub.split(",") for sub in words])
             # find delta y between words to find new column markers
                dfWords = dfWords.astype({3:'int'})
                dfWords['yDif'] = dfWords[3].diff()
                col_breaks = dfWords.loc[dfWords['yDif'] < -9000].index.values
                    
                #if there are > 1 column, take each column, and sort it
                res = []
                if(len(col_breaks)>0):
                    prev = 0
                    for c in col_breaks:
                        holder = []
                        col = dfWords.iloc[prev:c].values.tolist()
                        colDF = pd.DataFrame(sorted(col, key=cmp_to_key(compare)))
                        colDF.apply(lambda x: holder.append(find_bucket( x.to_list()))  , axis = 1)
                        res.append(holder)
                        prev = c

                    holder = []
                    col = dfWords.iloc[col_breaks[-1]:].values.tolist()
                    colDF = pd.DataFrame(sorted(col, key=cmp_to_key(compare)))
                    colDF.apply(lambda x: holder.append(find_bucket( x.to_list()))  , axis = 1)
                    res.append(holder)
                else:
                    dfWords.apply(lambda x: res.append(find_bucket( x.to_list()))  , axis = 1)
                brightness_level[x] = res
                x+=1

            except Exception as e:
                z = 1

                
    return brightness_level


####for .dat files
def organize_dat(images):
    x = 0
    global prev_y
    global prev_x
    prev_x = 0
    prev_y = 0
    #create an array of dictionaries, each element the text from given brightness level
    brightness_level = [{} for sub in range(200)]
    for i in range(len(images)): 
        num_cols = 1
        image = images[i]
        #if image contains no information, skip to next iteration

        if image == '':
            continue
        else:

            #split current image info with line boundaries and word boundaries
            info = re.split('[\/[A-Za-z0-9-.]+\/*\.day', image)
            try:
                lines = info[0].strip()
                words = info[1].strip()
                if(lines != ''):
                    num_lines = lines.count('\n')+1
                    lines = lines.split('\n')
                    words = words.split('\n')
                    words = [sub.split(",") for sub in words]
                    dfWords = pd.DataFrame(words)
                    
                    # find delta y between words to find new column markers
                    dfWords = dfWords.astype({3:'int'})
                    dfWords['yDif'] = dfWords[3].diff()
                    col_breaks = dfWords.loc[dfWords['yDif'] < -9000].index.values
                    
                    #if there are > 1 column, take each column, and sort it
                    res = []
                    if(len(col_breaks)>0):
                        prev = 0
                        for c in col_breaks:
                            holder = []
                            col = dfWords.iloc[prev:c].values.tolist()
                            colDF = pd.DataFrame(sorted(col, key=cmp_to_key(compare)))
                            colDF.apply(lambda x: holder.append(find_bucket( x.to_list()))  , axis = 1)
                            res.append(holder)
                            prev = c

                        holder = []
                        col = dfWords.iloc[col_breaks[-1]:].values.tolist()
                        colDF = pd.DataFrame(sorted(col, key=cmp_to_key(compare)))
                        colDF.apply(lambda x: holder.append(find_bucket( x.to_list()))  , axis = 1)
                        res.append(holder)
                    else:
                        dfWords.apply(lambda x: res.append(find_bucket( x.to_list()))  , axis = 1)



                    #go through word df and append word data to bucket it is closest to
                    brightness_level[x] = res
                    x+=1

            except Exception as e:
                z = 1
                
    return brightness_level

                
       



def assemble(brightness_level):
    res = []
    term_dict = {}
    
    #contents of one page
    for count, blocks in enumerate(brightness_level):
        blob_set = set()
        if(blocks != None):
            try:
                cols = []
                full_text = []
                
                #if multiple columns
                if(len(blocks) < 10):
                    for col in blocks : 
                        cols.append(' '.join(col))
                        full_text.extend(col)

                    blob = '\n\n'.join(cols)
                else:
                    blob = ' '.join(blocks)
                    
                #counts bigrams in blob and adds count to bigram dictionary
                for x in range(len(full_text)-1):
                    ngram = full_text[x]+full_text[x+1]
                    blob_set.add(ngram)
                    if ngram in term_dict:
                        term_dict[ngram] +=1
                    else:
                        term_dict[ngram] = 1
                
        
                res.append((blob,blob_set))
            except Exception as e:
                z= 1
                
    #returns put together text blob and also its word dictionary
    return term_dict, res



#finds text blob that has highest score of bigrams 
def find_opt(res, term_dict):
    total = 0
    optimum = ''
    opt_brightness = -1
    for brightness,blocks in enumerate(res):
        blob_total = 0
        blob_set = blocks[1]
        blob = blocks[0]
        for ngram in blob_set:
            blob_total += term_dict[ngram]
        if(blob_total > total):
            total = blob_total
            optimum = blob
            opt_brightness = brightness

    return opt_brightness,optimum
        
    

#parameter of all capital strings in page, throws out ones that do not contain company endings
#should probably go to stop words and throw out all companies that don't contain a stop word
#returns company names
def find_caps(text):
    company_words = {' INC ', ' CO ', ' CORP ', ' LTD ', 'PRODUCTIONS', 'LLC'}
    all_caps = re.findall(r'((?:[A-Z]{2,} *){2,})', optimum)
    companies = set()

    for w in company_words:
        for name in all_caps:
            if(w in name):
                companies.add(name)
                continue
                
    return list(companies)


if __name__ == "__main__":
    
    year = str(sys.argv[1])
    #pwd = getpass.getpass("Password: ")
    # db = MongoClient(host="royceschultz.com", port=27017, username="finlab_beta", password=pwd,   authSource="users").finlab_dev.trevino_MoodysOCR
    fout = open('1930.json', 'w')
    output = []

    #get directory and parse all pages in directory
    path = r'/scratch/summit/diga9728/Moodys/Industrials/OCRrun'+year
    print(path)

    #dictionaries to store company/page info
    comp_dict = {}
    page_dict = {}

    #dirs is path to OCRrunXXXX
    dirs = os.listdir(path)
    sub_dirs = []

    #find all subdirs that contain only 3 numbers which are page scans
    for d in dirs:
        match = re.fullmatch('[0-9]{3}', d)
        if match:
            sub_dirs.append(match.group(0))

    sub_dirs = sorted(sub_dirs)
    page_counter = 1

    #create paths by joining orignal path and then subdirectory then scan all files in that subdirectory
    for d in sub_dirs:
        sub_path = os.path.join(path, d)
        for entry in os.scandir(sub_path):
            print(page_counter, end='\r')
            curr_path = entry.path
            ident = curr_path[-17:-4]
            #check if page has been processed before
            # if (db.count_documents({'_id': ident}) == 0):
            year = int(year)

            #open page file and split images at lines containing .day
            file = open(curr_path, 'r').read()

            #some files have line info, so we have two different methods to read depending on file contents
            if(len(re.findall('[\/[A-Za-z0-9-._]+\/*\.dat', file)) > 1):
                images = re.split('[\/[A-Za-z0-9-._]+\/*\.dat', file)
                brightness_levels = organize_dat(images)
            else:
                images = re.split('[\/[A-Za-z0-9-._]+\/*\.day', file)
                brightness_levels = organize_day(images)

            #get all ngrams from the 99 iterations and each text blob from the 99 iterations
            term_dict,res = assemble(brightness_levels)

            #find optimum brightness and correlating blob
            opt_brightness,optimum = find_opt(res,term_dict)

            #identify company names
            companies = find_caps(optimum)


            entry = {'_id': ident,'optimum_brightness': opt_brightness, 'text_blob': optimum, 'companies': companies, 'year': year, 'page': page_counter}
            # db.insert_one(entry)
            output.append(entry)
                
            page_counter+=1

    json.dump(output, fout)


    # #find companies by words that are in all caps
    # companies = find_caps(optimum)

    # #get indices of company names in text string
    # companies = sorted([(optimum.find(x),x) for x in companies])
    # companies.append((len(optimum),'holder'))

    # #try to parse for history and officers section of multiple companies on page
    # if(len(companies) > 1):
    #     for x in range(len(companies)-1):
    #         first = companies[x]
    #         second = companies[x+1]
    #         company_text = optimum[first[0]: second[0]]
    #         history = company_text[company_text.find('History'):company_text.find('Officers')]
    #         officers = company_text[company_text.find('Officers'):company_text.find('Directors')]
    #         comp_dict[first[1].strip()] = {'history': history, 'officers':officers}

    # #only one company found on page
    # elif(len(companies) == 2):
    #     first = companies[0]
    #     comp_dict[first[1]] = optimum[first[0]: len(optimum)]

        
    



    
