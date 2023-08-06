import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from dry_scraper.data_sources.nhl.pydantic_models.nhl_game_live_feed_api_source import (
    LiveFeedLink,
    Status,
)
from dry_scraper.data_sources.nhl.pydantic_models.nhl_teams_api_source import (
    ShortTeam,
    ShortVenue,
)


class LeagueRecord(BaseModel):
    wins: int
    losses: int
    ot: Optional[int]
    type: str


class Team(BaseModel):
    league_record: LeagueRecord = Field(alias="leagueRecord")
    score: int
    team: ShortTeam


class Teams(BaseModel):
    away: Team
    home: Team


class Game(BaseModel):
    gamePk: int
    link: LiveFeedLink
    game_type: str = Field(alias="gameType")
    season: str = Field(alias="season")
    game_date: datetime.datetime = Field(alias="gameDate")
    status: Status
    teams: Teams
    venue: ShortVenue


class Date(BaseModel):
    date: datetime.date
    total_items: int = Field(alias="totalItems")
    total_games: int = Field(alias="totalGames")
    games: List[Game]


class Schedule(BaseModel):
    total_items: int = Field(alias="totalItems")
    total_games: int = Field(alias="totalGames")
    dates: List[Date]


schedule_df_model = {
    "date": "str",
    "season": "int",
    "gamePk": "int",
    "game_type": "str",
    "game_date": "datetime64[m]",
    "abstract_game_state": "str",
    "coded_game_state": "int",
    "detailed_state": "str",
    "status_code": "int",
    "start_time_tbd": "bool",
    "away_team_id": "int",
    "away_team_name": "str",
    "away_record_wins": "int",
    "away_record_losses": "int",
    "away_record_ot": "int",
    "away_record_type": "str",
    "away_score": "int",
    "home_team_id": "int",
    "home_team_name": "str",
    "home_record_wins": "int",
    "home_record_losses": "int",
    "home_record_ot": "int",
    "home_record_type": "str",
    "home_score": "int",
    "venue_id": "int",
    "venue_name": "str",
}
