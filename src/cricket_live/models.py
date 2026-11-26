"""Data models for the live cricket scoreboard overlay."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BatsmanState(BaseModel):
    name: str
    runs: int = 0
    balls: int = 0
    fours: int = 0
    sixes: int = 0
    strike_rate: float = 0.0
    on_strike: bool = False
    dismissal: str = ""


class BowlerState(BaseModel):
    name: str
    wickets: int = 0
    runs_conceded: int = 0
    overs: str = "0.0"
    maidens: int = 0
    economy: float = 0.0


class OverSummary(BaseModel):
    over_number: int
    balls: list[str] = Field(default_factory=list)
    total: int = 0


class ScoreboardState(BaseModel):
    batting_team: str = "UNITED ARAB EMIRATES"
    bowling_team: str = "INDIA A"
    runs: int = 182
    wickets: int = 5
    overs: str = "39.5"
    partnership: str = "28(25)"
    crr: float = 4.57
    last_5_ov: str = "24/2"
    callout: str = "STRIKE ROTATED"
    callout_tone: str = "neutral"  # neutral | four | six | wicket
    prev_over: OverSummary = Field(
        default_factory=lambda: OverSummary(
            over_number=39, balls=["1", "2", "1", "1", "1", "1"], total=7
        )
    )
    curr_over: OverSummary = Field(
        default_factory=lambda: OverSummary(
            over_number=40, balls=["0", "0", "0", "6", "1"], total=7
        )
    )
    non_striker: BatsmanState = Field(
        default_factory=lambda: BatsmanState(
            name="H. BHATIA", runs=102, balls=121, fours=11, sixes=2, strike_rate=84.30
        )
    )
    striker: BatsmanState = Field(
        default_factory=lambda: BatsmanState(
            name="BASIL HAMEED",
            runs=9,
            balls=10,
            fours=0,
            sixes=0,
            strike_rate=90.00,
            on_strike=True,
        )
    )
    bowler: BowlerState = Field(
        default_factory=lambda: BowlerState(
            name="H RANA", wickets=1, runs_conceded=29, overs="5.5", economy=4.97
        )
    )
    last_wicket: str = "AFTAB ALAM SHAH • 2(7)"
    live_commentary: str = ""
    match_title: str = "BAN Vs SA, 2nd Test, BAN Vs SA 2026 Live"
    venue: str = "SuperSport Park, Centurion"
    series_name: str = "BAN vs SA 2026"
    match_date: str = ""
    head_to_head: str = "SA 8 - 0 BAN"
    win_prob_batting: int = 42
    recent_overs: list[OverSummary] = Field(default_factory=list)
    batters_list: list[BatsmanState] = Field(default_factory=list)
    bowlers_list: list[BowlerState] = Field(default_factory=list)
    fall_of_wickets: list[str] = Field(default_factory=list)
    batting_xi: list[str] = Field(default_factory=list)
    bowling_xi: list[str] = Field(default_factory=list)
    match_status: str = "live"  # live | innings_break | completed
    match_result: str = ""
    player_of_match: dict[str, str] = Field(
        default_factory=lambda: {"name": "", "team": "", "figures": ""}
    )
    first_innings: dict[str, object] = Field(
        default_factory=lambda: {"team": "", "score": "", "overs": "", "batters": [], "bowlers": []}
    )
    quiz_prompt: dict[str, str] = Field(
        default_factory=lambda: {"question": "", "players": ""}
    )
    latest_news: list[dict[str, str]] = Field(default_factory=list)
    # CREX extended categories
    rrr: float = 0.0
    target: int = 0
    toss: str = "INDIA WON THE TOSS AND CHOSE TO BAT"
    umpires: dict[str, str] = Field(
        default_factory=lambda: {
            "on_field": "Richard Illingworth, Nitin Menon",
            "third": "Joel Wilson",
            "referee": "Javagal Srinath",
        }
    )
    weather: dict[str, str] = Field(
        default_factory=lambda: {
            "temp": "25.5°C",
            "condition": "Clear",
            "humidity": "68%",
            "rain_chance": "0%",
        }
    )
    venue_stats: dict[str, str | int] = Field(
        default_factory=lambda: {
            "matches": 45,
            "win_bat_first": 48,
            "win_bowl_first": 52,
            "avg_1st": 268,
            "avg_2nd": 234,
            "highest_total": "356/5",
            "lowest_total": "112/10",
            "highest_chased": "319/7",
            "pace_wkts": 84,
            "pace_pct": 59,
            "spin_wkts": 58,
            "spin_pct": 41,
        }
    )
    fan_poll: dict[str, int] = Field(
        default_factory=lambda: {
            "total_votes": 207850,
            "batting_pct": 64,
            "bowling_pct": 36,
        }
    )
    team_form: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "batting": ["W", "W", "L", "W", "W"],
            "bowling": ["W", "L", "W", "W", "L"],
        }
    )
    team_comparison: dict[str, dict[str, str | int]] = Field(
        default_factory=lambda: {
            "batting": {"matches": 10, "win_pct": 70, "avg_score": 284, "high_score": 356, "low_score": 168},
            "bowling": {"matches": 10, "win_pct": 60, "avg_score": 262, "high_score": 334, "low_score": 142},
        }
    )
    recent_h2h: list[dict[str, str]] = Field(
        default_factory=lambda: [
            {"match": "3rd ODI, 2026", "score_a": "IND 312/6 (50.0)", "score_b": "AUS 288/9 (50.0)", "result": "IND Won by 24 runs"},
            {"match": "2nd ODI, 2026", "score_a": "AUS 274/8 (50.0)", "score_b": "IND 278/4 (47.2)", "result": "IND Won by 6 wkts"},
            {"match": "1st ODI, 2026", "score_a": "AUS 295/7 (50.0)", "score_b": "IND 281/10 (48.4)", "result": "AUS Won by 14 runs"},
        ]
    )
    points_table: list[dict[str, str | int]] = Field(
        default_factory=lambda: [
            {"team": "INDIA", "p": 5, "w": 4, "l": 1, "nr": 0, "nrr": "+1.414", "pts": 8},
            {"team": "AUSTRALIA", "p": 5, "w": 4, "l": 1, "nr": 0, "nrr": "+1.120", "pts": 8},
            {"team": "SOUTH AFRICA", "p": 5, "w": 3, "l": 2, "nr": 0, "nrr": "+0.485", "pts": 6},
            {"team": "NEW ZEALAND", "p": 5, "w": 3, "l": 2, "nr": 0, "nrr": "+0.270", "pts": 6},
            {"team": "ENGLAND", "p": 5, "w": 1, "l": 4, "nr": 0, "nrr": "-0.793", "pts": 2},
            {"team": "PAKISTAN", "p": 5, "w": 0, "l": 5, "nr": 0, "nrr": "-1.850", "pts": 0},
        ]
    )
    series_leaders: list[dict[str, str | int]] = Field(
        default_factory=lambda: [
            {"category": "MOST RUNS", "player": "VIRAT KOHLI", "team": "IND", "value": "342 Runs"},
            {"category": "MOST WICKETS", "player": "JASPRIT BUMRAH", "team": "IND", "value": "13 Wkts"},
            {"category": "MOST SIXES", "player": "ROHIT SHARMA", "team": "IND", "value": "14 Sixes"},
            {"category": "BEST STRIKE RATE", "player": "GLENN MAXWELL", "team": "AUS", "value": "148.60 SR"},
        ]
    )
    icc_rankings: dict[str, list[dict[str, str | int]]] = Field(
        default_factory=lambda: {
            "odi_teams": [
                {"rank": 1, "team": "IND", "rating": 116},
                {"rank": 2, "team": "NZ", "rating": 107},
                {"rank": 3, "team": "SA", "rating": 104},
                {"rank": 4, "team": "PAK", "rating": 104},
                {"rank": 5, "team": "AUS", "rating": 100},
                {"rank": 6, "team": "ENG", "rating": 95},
            ],
            "t20_teams": [
                {"rank": 1, "team": "ENG", "rating": 268},
                {"rank": 2, "team": "IND", "rating": 267},
                {"rank": 3, "team": "AUS", "rating": 260},
                {"rank": 4, "team": "NZ", "rating": 248},
                {"rank": 5, "team": "SA", "rating": 241},
                {"rank": 6, "team": "WI", "rating": 236},
            ],
            "top_players": [
                {"role": "ODI BATTER #1", "name": "SHUBMAN GILL", "team": "IND", "rating": 796},
                {"role": "ODI BATTER #2", "name": "VIRAT KOHLI", "team": "IND", "rating": 774},
                {"role": "ODI BOWLER #1", "name": "RASHID KHAN", "team": "AFG", "rating": 710},
                {"role": "T20I ALL-ROUNDER #1", "name": "HARDIK PANDYA", "team": "IND", "rating": 258},
            ],
        }
    )
    ticker_items: list[str] = Field(
        default_factory=lambda: [
            "HARSHIT RANA 1-28 (5.4)",
            "LIKE • SHARE • SUBSCRIBE",
            "UAE 182/5 IN 39.5 OVERS",
            "H. BHATIA 102* (121)",
        ]
    )
    team_comparison: dict[str, object] = Field(default_factory=dict)
