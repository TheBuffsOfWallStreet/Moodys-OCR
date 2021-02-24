import numpy as np
import re
import pandas as pd
from functools import cmp_to_key
import itertools



start = '/scratch/summit/diga9728/Moodys/Industrials/OCRrun1944/'
zay = '/194/OCR.micro.19440021-0035.zay'


#open page file and split images at lines containing .day
file = open(start + zay, 'r').read()
if(len(re.findall('[\/[A-Za-z0-9-._]+\/*\.dat', file)) > 1):
    images = re.split('[\/[A-Za-z0-9-._]+\/*\.dat', file)
    brightness_levels = organize_dat(images)


else:
    images = re.split('[\/[A-Za-z0-9-._]+\/*\.day', file)
    brightness_levels = organize_day(images)

term_dict,res = assemble(brightness_levels)
find_opt(res,term_dict)




#global vars for previous word coords
prev_y = 0
prev_x = 0

def compare(word1,word2):
    y1_value = int(word1[3])
    x1_value_l = int(word1[1])
    y2_value = int(word2[3])
    x2_value_l = int(word2[1])
    if(abs(y1_value-y2_value) < 80 ):
        return x1_value_l - x2_value_l

    else:
        return y1_value-y2_value

###for .day only
prev_y = 0
prev_x = 0
num_cols= 1




def find_bucket(row):
    global prev_y
    global num_cols
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



def organize_day(images):
    x = 0
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
                print(e)


    return brightness_level





def organize_dat(images):
    x = 0
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


                    #create dictionary where keys are the lines y1 values

                    #go through word df and append word data to bucket it is closest to
                    brightness_level[x] = res
                    x+=1

            except Exception as e:
                print(e)

    return brightness_level





def assemble(brightness_level):
    res = []
    term_dict = {}
    for count, blocks in enumerate(brightness_level):
        blob_set = set()
        try:
            if(blocks != None):
                blob = ' '.join(blocks)
                for x in range(len(blocks)-1):
                    ngram = blocks[x]+blocks[x+1]
                    blob_set.add(ngram)
                    if ngram in term_dict:
                        term_dict[ngram] +=1
                    else:
                        term_dict[ngram] = 1

                res.append((blob,blob_set))
        except Exception as e:
            print(e)

    return term_dict, res



def find_opt(res, term_dict):
    total = 0
    optimum = ''
    opt_brightnes = -1
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

    print(opt_brightness)
    print(optimum)
