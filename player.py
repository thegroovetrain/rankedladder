import glicko2

class Player(object):

    def __init__(self, pid, prating=1500.0, pdeviation=350.0, pvolatility=0.06, phistory=0):
        self.info = {
            'id': int(pid),
            'rating': float(prating),
            'deviation': float(pdeviation),
            'volatility': float(pvolatility)
            }
        self.match_history = phistory

    @property
    def player_id(self): return self.info['id']

    @property
    def rating(self): return self.info['rating']

    @property
    def deviation(self): return self.info['deviation']

    @property
    def volatility(self): return self.info['volatility']

    @property
    def games_played(self):
        if match_history == 0:
            return 0
        else:
            count = 0
            for i in range(len(match_history)):
                for j in range(len(match_history[i])):
                    count += 1
            return count
