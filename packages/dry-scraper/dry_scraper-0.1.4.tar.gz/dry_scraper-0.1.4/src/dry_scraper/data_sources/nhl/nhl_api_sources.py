import re
from abc import ABC
from datetime import datetime
from typing import ClassVar, TypeVar

import pandas as pd
import pydantic
import requests

from dry_scraper.data_sources.nhl.pydantic_models import (
    nhl_schedule_api_source,
    nhl_teams_api_source,
    nhl_divisions_api_source,
    nhl_conferences_api_source,
)
from dry_scraper.data_sources.data_source import DataSource


DataModel = TypeVar("DataModel", bound=pydantic.BaseModel)


class NhlApiSource(DataSource, ABC):
    """
    Abstract subclass of DataSource that represents a request and result from NHL API.
    API fully documented here: https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md

    ...

    Attributes
    ----------
    _url_stub : ClassVar[str]
        partial URL location of data source
    _extension : ClassVar[str]
        file extension to be used when writing the raw data source to disk e.g. json, HTM
    _pyd_model : DataModel
        pydantic model class describing the response
    _url : str
        fully qualified URL location of data source, completed on instantiation
    _query : dict
        dict representation of API query
    _content : str
        string representation of raw data retrieved by fetch_content()
    _content_pyd : DataModel
        pydantic model representation of the requested data created on call to parse_to_pyd()

    Methods
    -------
    fetch_content(): -> Self:
        fetch content from self.url and store response in self.content
    parse_to_pyd(): -> Self:
        Parse content into pydantic model and store result in self.content_pyd
    """

    _url_stub: ClassVar[str] = "https://statsapi.web.nhl.com/api/v1"
    _extension: ClassVar[str] = "json"
    _pyd_model: DataModel  # ClassVar
    _url: str
    _query: dict
    _content: str
    _content_pyd: DataModel

    @property
    def query(self) -> dict | None:
        return getattr(self, "_query", None)

    @query.setter
    def query(self, value: dict) -> None:
        self._query = value

    @property
    def pyd_model(self) -> DataModel:
        return self._pyd_model

    @property
    def content_pyd(self) -> DataModel:
        return self._content_pyd

    def parse_to_pyd(self):  # -> Self:
        """
        Parse content into a Pydantic model and store result in self.content_pyd

        Returns:
        self
        """
        self._content_pyd = self.pyd_model.parse_raw(self.content)
        return self

    def fetch_content(self):
        """
        Query NHL API endpoint at self.url and store response in self.content

        Returns:
            self
        """
        try:
            response = requests.get(self.url, self.query, timeout=10)
            response.raise_for_status()
            self.content = response.text
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)
        return self


class NhlScheduleApiSource(NhlApiSource):
    """
    Subclass of NhlGameApiSource that represents a request from the NHL schedule API
    If no attributes are specified, the API will return today's games

    ...

    Attributes
    ----------
    _pyd_model : DataModel
        pydantic model class describing the response
    _date : str
        single date for the season_query (e.g. 2021-03-17)
    _start_date : str
        start date for a date range season_query
    _end_date : str
        end date for  date range season_query
    _season : str
        8 character representation of an NHL season (e.g. 20202021)
    _team_id : str
        one or more 2 character ID numbers representing NHL teams separated by commas
        or one or more tricodes representing NHL teams separated by commas
        e.g. '1,2,3' or 'NJD,NYI,NYR'
    _game_type : str
        one or more character codes for different game types separated by commas
        (e.g. PR for preseason, R for regular, A for all-star, P for playoffs)
        all options listed here: https://statsapi.web.nhl.com/api/v1/gameTypes
    _expand : str
        descriptor that provides additional information with the response
        'broadcasts' shows broadcast information, 'linescore' shows the line score,
        'tickets' shows ticketing information
        all options listed here: https://statsapi.web.nhl.com/api/v1/expands

    Methods
    -------
    """

    _pyd_model: DataModel = nhl_schedule_api_source.Schedule
    _date: str
    _start_date: str
    _end_date: str
    _season: str
    _team_id: str
    _game_type: str
    _expand: str

    def __init__(
        self,
        date=None,
        start_date=None,
        end_date=None,
        season=None,
        team_id=None,
        game_type=None,
        expand=None,
    ):
        self.date = date
        self.start_date = start_date
        self.end_date = end_date
        self.season = season
        self.team_id = team_id
        self.game_type = game_type
        self.expand = expand
        self.url = f"{self.url_stub}/schedule"
        query = {}
        if date:
            query["date"] = self.date
        if start_date:
            query["startDate"] = self.start_date
        if end_date:
            query["endDate"] = self.end_date
        if season:
            query["season"] = self.season
        if team_id:
            query["teamId"] = self.team_id
        if game_type:
            query["gameType"] = self.game_type
        if expand:
            query["expand"] = self.expand
        self.query = query

    @property
    def date(self) -> str:
        return self._date

    @date.setter
    def date(self, value: str | datetime) -> None:
        if isinstance(value, datetime):
            self._date = value.strftime("%Y-%m-%d")
        else:
            self._date = value

    @property
    def start_date(self) -> str:
        return self._start_date

    @start_date.setter
    def start_date(self, value: str | datetime) -> None:
        if isinstance(value, datetime):
            self._start_date = value.strftime("%Y-%m-%d")
        else:
            self._start_date = value

    @property
    def end_date(self) -> str:
        return self._end_date

    @end_date.setter
    def end_date(self, value: str | datetime) -> None:
        if isinstance(value, datetime):
            self._end_date = value.strftime("%Y-%m-%d")
        else:
            self._end_date = value

    @property
    def season(self) -> str:
        return self._season

    @season.setter
    def season(self, value: int | str) -> None:
        if len(str(value)) == 4:
            value = str(value) + str(int(value)+1)
        self._season = str(value)

    @property
    def team_id(self) -> str:
        return self._team_id

    @team_id.setter
    def team_id(self, value: int | str) -> None:
        """
        Set value of team_id by coercing the user input into the acceptable form of one or more team ID numbers
        Parameters
        ----------
        value : int | str
            an int representing one team ID, or a str representing multiple.
            str can be a comma delimited list of team ID numbers or tricodes.
        """
        num_pattern = re.compile(r"^(\d|\d\d)$|^(\d,|\d\d,)+(\d|\d\d)$")
        tri_pattern = re.compile(r"^[a-zA-Z]{3}$|^([a-zA-Z]{3},)+[a-zA-Z]{3}$")

        if isinstance(value, int) or num_pattern.match(str(value)):
            self._team_id = str(value)
        elif isinstance(value, str) and tri_pattern.match(value):
            tricode_list: list[str] = value.split(",")
            team_dict: dict[str, int] = NhlTeamsApiSource().create_team_dict()
            id_list: list[str] = []
            for team in tricode_list:
                team_id: int = team_dict.get(team)
                if team_id is not None:
                    id_list.append(str(team_id))
            self._team_id = ",".join(id_list)
        else:
            self._team_id = ""

    @property
    def game_type(self) -> str:
        return self._game_type

    @game_type.setter
    def game_type(self, value: str) -> None:
        self._game_type = value

    @property
    def expand(self) -> str:
        return self._expand

    @expand.setter
    def expand(self, value: str) -> None:
        self._expand = value

    def yield_schedule_df(self) -> pd.DataFrame:
        """
            Return a pandas DataFrame representation of the schedule response

        Returns
        -------
            schedule_df (DataFrame): schedule dataframe
        """
        if self.content_pyd is None:
            self.fetch_content()
        schedule_pyd = self.content_pyd.dates
        schedule_df = pd.DataFrame(
            {
                col: pd.Series(dtype=typ)
                for col, typ in nhl_schedule_api_source.schedule_df_model.items()
            }
        )
        for date in schedule_pyd:
            date_str = date.date
            for game in date.games:
                game_dict = {
                    "date": str(date_str),
                    "season": int(game.season),
                    "gamePk": int(game.gamePk),
                    "game_type": str(game.game_type),
                    "game_date": str(game.game_date),
                    "abstract_game_state": str(game.status.abstract_game_state),
                    "coded_game_state": str(game.status.coded_game_state),
                    "detailed_state": str(game.status.detailed_state),
                    "status_code": str(game.status.status_code),
                    "start_time_tbd": game.status.start_time_tbd,
                    "away_team_id": int(game.teams.away.team.id),
                    "away_team_name": str(game.teams.away.team.name),
                    "away_record_wins": int(game.teams.away.league_record.wins),
                    "away_record_losses": int(game.teams.away.league_record.losses),
                    "away_record_ot": (
                        int(game.teams.away.league_record.ot)
                        if game.teams.away.league_record.ot is not None
                        else None
                    ),
                    "away_record_type": str(game.teams.away.league_record.type),
                    "away_score": int(game.teams.away.score),
                    "home_team_id": int(game.teams.home.team.id),
                    "home_team_name": str(game.teams.home.team.name),
                    "home_record_wins": int(game.teams.home.league_record.wins),
                    "home_record_losses": int(game.teams.home.league_record.losses),
                    "home_record_ot": (
                        int(game.teams.home.league_record.ot)
                        if game.teams.home.league_record.ot is not None
                        else None
                    ),
                    "home_record_type": str(game.teams.home.league_record.type),
                    "home_score": int(game.teams.home.score),
                    "venue_id": (
                        int(game.venue.id) if game.venue.id is not None else None
                    ),
                    "venue_name": str(game.venue.name),
                }
                schedule_df.loc[game_dict["gamePk"]] = game_dict
        return schedule_df


class NhlTeamsApiSource(NhlApiSource):
    """
    Subclass of NhlApiSource that represents a request to the NHL teams API

    ...

    Attributes
    ----------
    _team_id : int
        team id number for the NHL API query

    Methods
    -------
    create_team_dict -> dict[str, int]:
        Request the full list of NHL teams and return a dictionary associating tricodes
        to team ID numbers
    """

    _pyd_model: DataModel = nhl_teams_api_source.Teams
    _team_id: str

    def __init__(self, team_id="") -> None:
        self.team_id = team_id
        self.url = f"{self.url_stub}" "/teams/" f"{self.team_id}"

    @property
    def team_id(self) -> str:
        return self._team_id

    @team_id.setter
    def team_id(self, value: str | int) -> None:
        self._team_id = str(value)

    @staticmethod
    def create_team_dict() -> dict[str, int]:
        """
        Request the full list of NHL teams and return a dictionary associating tricodes
        to team ID numbers.

        For now, use hardcoded version

        Returns:
        team_dict : dict[str:int]
            dictionary associating tricodes to team ID numbers
        """
        from dry_scraper.teams import TEAMS

        team_dict = {}

        for team in TEAMS:
            tricode = TEAMS[team]["abbreviation"]
            id_number = TEAMS[team]["id"]
            team_dict[tricode] = id_number

        return team_dict


class NhlDivisionApiSource(NhlApiSource):
    """
    Subclass of NhlApiSource that represents a request to the NHL divisions API

    ...

    Attributes
    ----------
    _division_id : int
        division id number for the NHL API query

    Methods
    -------
    """

    _pyd_model: DataModel = nhl_divisions_api_source.Divisions
    _division_id: str

    def __init__(self, division_id="") -> None:
        self.division_id = division_id
        self.url = f"{self.url_stub}" "/divisions/" f"{self.division_id}"

    @property
    def division_id(self) -> str:
        return self._division_id

    @division_id.setter
    def division_id(self, value: str | int) -> None:
        self._division_id = str(value)


class NhlConferenceApiSource(NhlApiSource):
    """
    Subclass of NhlApiSource that represents a request to the NHL conferences API

    ...

    Attributes
    ----------
    _conference_id : int
        conference id number for the NHL API query

    Methods
    -------
    """

    _pyd_model: DataModel = nhl_conferences_api_source.Conferences
    _conference_id: str

    def __init__(self, conference_id=""):  # -> Self:
        self.conference_id = conference_id
        self.url = f"{self.url_stub}" "/conferences/" f"{self.conference_id}"

    @property
    def conference_id(self) -> str:
        return self._conference_id

    @conference_id.setter
    def conference_id(self, value: str | int) -> None:
        self._conference_id = str(value)
