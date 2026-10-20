#!/usr/bin/env python3
"""Reproducible NFL game-level evidence, not a market pricing engine.
Data: nflverse play-by-play (CC BY 4.0). Regular season 2023–2025.
Output: odds-evidence.json, published by GitHub Actions.
"""
import json, math, pathlib, tempfile, urllib.request
import pandas as pd

SEASONS = (2023, 2024, 2025)
BASE = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{}.parquet"
SOURCE = "https://github.com/nflverse/nflverse-data/releases/tag/pbp"
OUT = pathlib.Path(__file__).resolve().parents[1] / "odds-evidence.json"
RULES = {
    "Will a game have a safety?": ("safety", "A game contains at least one play flagged as a safety."),
    "Will a punt be blocked and returned for a touchdown?": ("blocked_punt_td", "A play is marked as a blocked punt and a return touchdown."),
    "Will there be 15+ accepted penalties in one game?": ("penalties_15", "At least 15 play-by-play rows have an accepted penalty flag; multiple penalties on a single play may be undercounted."),
    "Will there be 125+ total penalty yards in one game?": ("penalty_yards_125", "Sum of absolute penalty_yards across recorded plays reaches 125; play-by-play may omit offsetting or declined penalties."),
    "Will a player be flagged for taunting after a first down?": ("taunting_first_down", "A taunting penalty appears on a play marked first down; sequence after the first down cannot be confirmed."),
    "Will a coach get an unsportsmanlike conduct flag?": ("coach_unsportsmanlike", "Not identifiable from play-by-play alone; excluded from statistical output."),
}
def truth(v):
    return pd.to_numeric(v, errors="coerce").fillna(0).gt(0)
def wilson(k,n):
    z=1.96;p=k/n;d=1+z*z/n
    center=(p+z*z/(2*n))/d
    half=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/d
    return [round(100*(center-half),2),round(100*(center+half),2)]
def main():
    games={}
    for year in SEASONS:
        url=BASE.format(year)
        print("Downloading",url,flush=True)
        with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
            urllib.request.urlretrieve(url,tmp.name)
            df=pd.read_parquet(tmp.name)
        df=df[df["season_type"].eq("REG")].copy()
        for game_id,g in df.groupby("game_id",sort=False):
            safety=truth(g["safety"]).any() if "safety" in g else False
            blocked=truth(g["punt_blocked"]) if "punt_blocked" in g else pd.Series(False,index=g.index)
            td=truth(g["return_touchdown"]) if "return_touchdown" in g else pd.Series(False,index=g.index)
            penalties=truth(g["penalty"]) if "penalty" in g else pd.Series(False,index=g.index)
            yards=pd.to_numeric(g["penalty_yards"],errors="coerce").fillna(0).abs().sum() if "penalty_yards" in g else 0
            first=truth(g["first_down"]) if "first_down" in g else pd.Series(False,index=g.index)
            taunting=g["penalty_type"].fillna("").astype(str).str.contains("Taunting",case=False,regex=False) if "penalty_type" in g else pd.Series(False,index=g.index)
            games[str(game_id)]={
                "safety":bool(safety),
                "blocked_punt_td":bool((blocked & td).any()),
                "penalties_15":bool(penalties.sum()>=15),
                "penalty_yards_125":bool(yards>=125),
                "taunting_first_down":bool((taunting & first).any())
            }
    n=len(games)
    if n<750: raise RuntimeError(f"Too few regular-season games: {n}")
    results={}
    for title,(key,definition) in RULES.items():
        if key=="coach_unsportsmanlike":continue
        k=sum(int(g[key]) for g in games.values())
        results[title]={"observed_games":k,"sample_games":n,"rate_percent":round(100*k/n,2),
          "wilson_95_percent":wilson(k,n),"window":"2023–2025 NFL regular seasons",
          "definition":definition,"source":SOURCE,
          "status":"proxy" if key in ("penalties_15","penalty_yards_125","taunting_first_down") else "verified_game_level"}
    OUT.write_text(json.dumps({"methodology":"Empirical fraction of NFL regular-season games with recorded event; not a prediction for any particular matchup. Wilson 95% interval. Source: nflverse play-by-play CC BY 4.0.","seasons":list(SEASONS),"total_games":n,"markets":results},indent=2)+"\n")
    print("Saved",OUT,n,"games",len(results),"market measurements")
if __name__=="__main__":main()
