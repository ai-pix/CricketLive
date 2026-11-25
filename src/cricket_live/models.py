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


class BowlerState(BaseModel):
    name: str
    wickets: int = 0
    runs_conceded: int = 0
    overs: str = "0.0"
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
    ticker_items: list[str] = Field(
        default_factory=lambda: [
            "HARSHIT RANA 1-28 (5.4)",
            "LIKE • SHARE • SUBSCRIBE",
            "UAE 182/5 IN 39.5 OVERS",
            "H. BHATIA 102* (121)",
        ]
    )
