import pandas as pd

def preprocess_data(df):

    # Filter to include only the last 10 years
    current_year = df['Year'].max()
    df = df[df['Year'] >= current_year - 10]

    # Calculate new features

    # Current Features:
    # Player,Tm,FantPos,Age,G,GS,
    # Passing Cmp,Passing Att,Passing Yds,Passing TD,Passing Int,
    # Rushing Att,Rushing Yds,Yards per Rushing Attempt,Rushing TD,
    # Tgt,Rec,Receiving Yds,Yards per Reception,Receiving TD,
    # Fmb,FL,Total TD,2PM,2PP,
    # FantPt,PPR,hPPR,VBD,PosRank,OvRank,Year

    df.loc[:, 'hPPR/G'] = df['hPPR'] / df['G']
    df.loc[:, 'TD/G'] = df['TD'] / df['G']
    df.loc[:, 'PassYds/G'] = df['Passing Yds'] / df['G']
    df.loc[:, 'RecYds/G'] = df['Receiving Yds'] / df['G']
    df.loc[:, 'Receptions/G'] = df['Receptions'] / df['G']
    df.loc[:, 'Tgt/G'] = df['Tgt'] / df['G']
    df.loc[:, 'RecYds/G'] = df['Rec'] / df['G']
    df.loc[:, 'RushYds/G'] = df['Rushing Yds'] / df['G']

    # Handle division by zero and fill NaNs
    df.replace([float('inf'), -float('inf')], 0, inplace=True)
    df.fillna(0, inplace=True)

    return df

