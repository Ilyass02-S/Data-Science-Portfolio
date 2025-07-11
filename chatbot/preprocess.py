import pandas as pd
from utils import rows_to_json
# Reading the source csv and figuring out what it contains.
df = pd.read_csv("persistent/chatbot/data/Movie_Data.csv")

#droping unnecessary columns
df = df.drop(['Average_rating', "Release_year",'Owner_rating','½', '★', '★½', '★★', '★★½', '★★★',
               '★★★½', '★★★★', '★★★★½', '★★★★★','Fans', 'Spoken_languages','Description','Film_URL'], axis="columns")

#droping movies that has more than 3h
df = df[df['Runtime'] <= 160 ]
df = df.dropna()
col_list = df.columns.to_list()
print(col_list)

#distinguish movies runtime shortest to longest and the average time
shortest = df['Runtime'].min()
print(f"Shortest overview: {shortest}mn")

longest = df['Runtime'].max()
print(f"Longest overview: {longest} mn")

average = df['Runtime'].mean()
print(f"Average overview length: {average:.2f} mn")

#Now saving data to json file
try:
    rows_to_json(df)
except IOError as e:
    print(f"Error while writing json: {e}")
    exit(1)