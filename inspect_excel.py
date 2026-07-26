import pandas as pd
df = pd.read_excel('Striver_A2Z_Playlist_Links.xlsx', sheet_name='Playlist')
print('Total rows:', len(df))
print()
for i, row in df.iterrows():
    print(f"  [{int(row['S.No']):3d}] {row['Title']}")
