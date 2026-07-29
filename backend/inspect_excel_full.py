import pandas as pd
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel("Striver_A2Z_Playlist_Links.xlsx")
print(f"Total rows in Excel: {len(df)}")
for idx, row in df.iterrows():
    sno = row['S.No']
    vid = row['Video ID']
    title = row['Title']
    print(f"{sno:3d} | {vid} | {title}")
