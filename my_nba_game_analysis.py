import csv
import re
import pandas as pd
import numpy as np

def open_csv(file_name):
    content = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file, delimiter = '|')
        for row in reader:
            content.append(row)
    return content

def is_away_team(away_team, relevant_team):
    return away_team == relevant_team

def regxinv():
    regx = []
    regx.append(re.compile(r"([A-Z]\. [A-Za-z]+) makes 2-pt")) #P2: 2-Point Field Goals                            - i0
    regx.append(re.compile(r"([A-Z]\. [A-Za-z]+) misses 2-pt")) #FGA: 2-Point Field Goal Attempts                  - i1
    regx.append(re.compile(r"([A-Z]\. [A-Za-z]+) makes 3-pt")) #3P: 3-Point Field Goals                            - i2
    regx.append(re.compile(r"([A-Z]\. [A-Za-z]+) misses 3-pt")) #3PA: 3-Point Field Goal Attempts                  - i3
    regx.append(re.compile(r"([A-Z]\. [A-Za-z]+) makes free throw")) #FT: Free Throws                              - i4
    regx.append(re.compile(r"([A-Z]\. [A-Za-z]+) misses free throw")) #FTA: Free Throw Attempts                    - i5
    regx.append(re.compile(r"Offensive rebound by ([A-Z]\. [A-Za-z]+)")) #ORB: Offensive Rebounds   - i6
    regx.append(re.compile(r"Defensive rebound by ([A-Z]\. [A-Za-z]+)")) #DRB: Defensive Rebounds   - i7
    regx.append(re.compile(r"assist by ([A-Z]\. [A-Za-z]+)")) #AST: Assists                         - i8
    regx.append(re.compile(r"steal by ([A-Z]\. [A-Za-z]+)")) #STL: Steals                           - i9
    regx.append(re.compile(r"block by ([A-Z]\. [A-Za-z]+)")) #BLK: Blocks                           - i10
    regx.append(re.compile(r"Turnover by ([A-Z]\. [A-Za-z]+)")) #TOV: Turnovers                     - i11
    regx.append(re.compile(r"Personal foul by ([A-Z]\. [A-Za-z]+)")) #PF: Personal Fouls            - i12
    return regx


def player_search(player_stats, regx):
    player_data = ["P2", "P2A", "3P", "3PA", "FT", "FTA", "ORB", "DRB", "AST", "STL", "BLK", "TOV", "PF"]
    player_name = ""
    global total_player_data

    for i in range(len(regx)):
        data = regx[i].search(player_stats)
        if (data and data.group(1)):
            player_name = data.group(1)
            total_player_data = player_data[i]
            break
    
    return total_player_data, player_name
 
def analyse_nba_game(play_by_play_moves):
    team = {"home_team": {"name": play_by_play_moves[0][4], "player_data": {}}, "away_team": {"name": play_by_play_moves[0][3], "player_data": {}}}
    regx = regxinv()

    for play in play_by_play_moves:
        relevant_team = play[2]
        home_team = play[4]
        away_team = play[3]

        data = ( play[7])

        ret, player_name = player_search(play[7], regx)
        if ret and player_name:
            if is_away_team(away_team,relevant_team):
                if player_name not in team["away_team"]["player_data"]:
                    team["away_team"]["player_data"][player_name] = {"P2": 0, "P2A": 0, "3P": 0, "3PA": 0, "FT": 0, "FTA": 0, "ORB": 0, "DRB": 0, "TRB": 0, "AST": 0, "STL": 0, "BLK": 0, "TOV": 0, "PF": 0}
                team["away_team"]["player_data"][player_name][ret] += 1
            else:
                if player_name not in team["home_team"]["player_data"]:
                    team["home_team"]["player_data"][player_name] = {"P2": 0, "P2A": 0, "3P": 0, "3PA": 0, "FT": 0, "FTA": 0, "ORB": 0, "DRB": 0, "TRB": 0, "AST": 0, "STL": 0, "BLK": 0, "TOV": 0, "PF": 0}        
                team["home_team"]["player_data"][player_name][ret] += 1
            player_name = None

    return team  

def print_nba_game_stats(team):
    #header = ["Players","FG","FGA","FG%","3P","3PA","3P%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS"]
    #REMINDER: extend the dictionarry by the calculated columns in analyse_nba_game, so no need for inserts

    df = pd.DataFrame.from_dict(team["player_data"]) 
    df = df.T
    
    FG = df["P2"] + df["3P"]
    df.insert(0, "FG", FG)

    FGA = df["P2A"] + df["3PA"]
    df.insert(1, "FGA", FGA)

    fg_perc = df.FGA.div(df["FG"].sum()) #FG% = FG / FGA, if FGA < 0
    df.insert(2, "FG%", fg_perc) #can be simplified in analyse_nba_game
    
    df["P3A"] = df["3PA"]
    p3_perc = df.P3A.div(df["3PA"].sum()) #3P% = 3P / 3PA, if 3PA < 0 / "3PA" drops syntax error
    df.insert(7, "3P%", p3_perc)

    ft_perc = df.FTA.div(df.FT) #FT% = FT / FTA, if FTA < 0
    df.insert(10, "FT%", ft_perc)
    
    df["TRB"] = df["ORB"] + df["DRB"] #TRB = ORB + DRB

    df["P3"] = df["3P"]
    df["PTS"] = df.P2.multiply(2) + df.P3.multiply(3) #PTS = (FG*2) + (3P*3)
    df = df.drop(["P3A","P3", "P2", "P2A"], axis=1)

    df.loc["Total"] = [df["FG"].sum(), df["FGA"].sum(), df["FG%"].mean(), df["3P"].sum(), df["3PA"].sum(), df["3P%"].mean(), df["FT"].sum(), df["FTA"].sum(), df["FT%"].mean(), df["ORB"].sum(), df["DRB"].sum(), df["TRB"].sum(), df["AST"].sum(), df["STL"].sum(), df["BLK"].sum(), df["TOV"].sum(), df["PF"].sum(), df["PTS"].sum()] #% shall be average

    df = df.fillna(0)
  
    print(df)

def _main_():
    play_by_play_moves = open_csv("nba_game_blazers_lakers_20181018.txt")
    analyse_nba_game(play_by_play_moves)
    team = analyse_nba_game(play_by_play_moves)
    print_nba_game_stats(team["home_team"])
    #print_nba_game_stats(team["away_team"]) # for the other team´s data
   
_main_()