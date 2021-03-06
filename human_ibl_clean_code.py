# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 16:17:56 2022

@author:Annika Frach
"""



####TO DO => flip x axis of psychometric curve


#####import useful packages
import urllib #library to acess url links
from io import StringIO
import re # regular expressions
import pandas as pd
import seaborn as sns

def get_files(contents):
    '''function to acquire list of csv files from pavlovia gitlab'''
    actual_regular_expression = 'href="(.*?)"'
    # actual_regular_expressions=> () => group  => extract this part
    #".*" => indicates all letters should be included. ? => take letters until "
    matches = re.findall(actual_regular_expression, contents) # extract all links
    # matches =>all links that were found in href (also not CSV)
    csv_files = list(filter(lambda match: match.endswith('.csv'), matches))
    #csv_files =>  from found links, filter everything that doesnt end with a .csv extension
    raw_csv_links = list(map(lambda link: link.replace("blob", "raw"), csv_files))
    # raw_csv_ling => this is like like clicking raw link in the HTML
    downloaded_files = [] #make a list
    for file_name in raw_csv_links: # loop through each CSV file link
        with urllib.request.urlopen(f"https://gitlab.pavlovia.org/{file_name}") as url_stream:
            downloaded_files.append((file_name,
              url_stream.read().decode("UTF-8"))) # read URL into a String
    return downloaded_files
# read html code of gitlab file list
with urllib.request.urlopen("https://gitlab.pavlovia.org/Anninas/human_ibl_piloting/tree/master/data") as url_stream:
    contents = url_stream.read().decode("UTF-8")
# extract file names and file contents from gitlab
downloaded_files = get_files(contents)
# list of individual data frames per participant
to_combine = []
# loop over file name and string content of csv
for file_name, file_content in downloaded_files:
    print("looking at", file_name)
    # type(file_content) == string
    # parse string using CSV format into a Python Pandas Dataframe
    data = pd.read_csv(StringIO(file_content)) #string IO pretends to be a file handle
    # add participant dataframe to list
    to_combine.append(data)
# data not a string anymore
# Use dataframe like you would use a normal data frame
# create big dataframe from all individual participants dataframes
combined_data = pd.concat(to_combine)
print("got combined data", combined_data)
#totaltrials= len(combined_data.index)
contrast = combined_data["signed_contrast"].unique() # save all the different contrasts that we have
###create loop which counts right button presses (m) as 1 and left button presses (x) as 0 so the mean and error bars for each contrast can be displayed
percentages = []
count = []
contrasts_for_error = []
for contrast_to_check in contrast:
    contrast0 = combined_data[combined_data["signed_contrast"]==contrast_to_check]
    print(contrast0)
    totaltrials0= len(contrast0.index)
    print(totaltrials0)
    rightcount0 = contrast0["key_resp.keys"].value_counts()
    print(rightcount0)
    rightchoice0 = rightcount0["m"]
    for _ in range(0, rightchoice0):
        contrasts_for_error.append(contrast_to_check)
        count.append(1)
    rightchoice1 = rightcount0["x"]
    for _ in range(0, rightchoice1):
        contrasts_for_error.append(contrast_to_check)
        count.append(0)
    percentageright0 = (rightchoice0/totaltrials0)
    percentages.append(percentageright0)
print("result", percentages)
#####The psychometric curve
contrast_percentages = pd.DataFrame(data={"contrast_to_check": contrasts_for_error, "rightchoice0": count})
print(contrast_percentages)
sns.lineplot(data=contrast_percentages, x="contrast_to_check", y="rightchoice0", err_style = "bars")
#### RT contrast plot
sns.relplot(data=combined_data,  x="signed_contrast", y= "key_resp.rt")
#### RT trial number plot
sns.relplot(data=combined_data,  x="trials.thisN", y= "key_resp.rt")
