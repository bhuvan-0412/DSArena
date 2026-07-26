import sys, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_excel('../Striver_A2Z_Playlist_Links.xlsx', sheet_name='Playlist')
with open('all_titles.txt', 'w', encoding='utf-8') as f:
    for i, row in df.iterrows():
        f.write(f"[{int(row['S.No']):3d}] {row['Video ID']} | {row['Title']}\n")
print('Done - written to all_titles.txt')
