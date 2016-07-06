#######################################
# match.py                            #
# Contains classes related to matches #
#######################################

import datetime

class System(object):

    def __init__(self, constant, tolerance):
        self.__attributes = {'system_constant': constant,
                             'system_tolerance': tolerance}
    
    @property
    def constant(self): return self.__attributes['system_constant']

    @property
    def tolerance(self): return self.__attributes['system_tolerance']

################################################################################

class Participant(object):

    def __init__(self, player_id, team):
        self.__attributes = {'player_id': player_id,
                             'team': team}
    
    # GETTERS
    @property
    def player_id(self): return self.__attributes['player_id']

    @property
    def team(self): return self.__attributes['team']

################################################################################

class Match(object):
    
    def __init__(self, match_id, create_date, create_time,
                 match_date=None, match_time=None, completed=False,
                 participants=None, winner=None, replay=None):

        self.__attributes = {'match_id': match_id,
                             'create_date': create_date,
                             'create_time': create_time,
                             'match_date': match_date,
                             'match_time': match_time,
                             'completed': completed,
                             'participants': participants,
                             'winner': winner,
                             'replay': replay}

    # GETTERS
    @property
    def match_id(self): return self.__attributes['match_id']

    @property
    def create_date(self): return self.__attributes['create_date']

    @property
    def create_time(self): return self.__attributes['create_time']

    @property
    def match_date(self): return self.__attributes['match_date']

    @property
    def match_time(self): return self.__attributes['match_date']

    @property
    def completed(self): return self.__attributes['completed']

    @property
    def participants(self): return self.__attributes['participants']

    @property
    def winner(self): return self.__attributes['winner']

    @property
    def replay(self): return self.__attributes['replay']

    # SETTERS
    @completed.setter
    def completed(self, value):
        if isinstance(value, bool):
            self.__attributes['completed'] = value

    @match_date.setter
    def match_date(self, value):
        if isinstance(value, datetime.date):
            self.__attributes['match_date'] = value

    @match_time.setter
    def match_time(self, value):
        if isinstance(value, datetime.time):
            self.__attributes['match_time'] = value

    @participants.setter
    def participants(self, value):
        if isinstance(value, list):
            if all(isinstance(i, Participant) for i in value):
                self.__attributes['participants'] = value
    
    @winner.setter
    def winner(self, value):
        if 0 <= value <=1:
            self.__attributes['winner'] = value

    @replay.setter
    def replay(self, value):
        if isinstance(value, str):
            self.__attributes['replay'] = value
