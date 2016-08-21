import math

class Glicko2(object):
    # Step 0: Set the system constant and tolerance
    def __init__(self, constant=0.5, tolerance=0.000001):
        self.system = {'constant': constant,
                       'tolerance': tolerance}
    
    def getNewRating(self, player, period):
        """
        player: {'rating': Glicko Rating (r),
                 'deviation': Glicko Rating Deviation (RD),
                 'volatility': player's volatility (sigma)}
        period: [{'score': 1 (win) or 0 (loss),
                  'opponent': {'rating': opponent's Glicko Rating (r),
                               'deviation': opponent's Glicko Rating Deviation}}]

        returns: {'rating': the new Glicko Rating (r)
                  'deviation': the new Glicko Rating Deviation (RD)}
        """
        # step 2: convert glicko rating and deviation (r, RD) into glicko-2 equivalents (mu, theta)
        def mu(rating):
            return float((rating - 1500)) / 173.7178
        def theta(deviation):
            return float(deviation) / 173.7178

        player_mu = mu(player['rating'])
        player_theta = theta(player['deviation'])

        # step 3: compute quanity v, the estimated variance of the team or player's rating based only
        # on the game outcomes
        # step  4: compute quantity delta, the estimated improvement in rating by comparing
        # the pre-period rating to the performance rating based only on the game outcomes.
        v = 0.0
        delta = 0.0
        improvement = 0.0
        for i, match in enumerate(period):
            opponent_mu = mu(match['opponent']['rating'])
            opponent_theta = theta(match['opponent']['deviation'])
            g = 1/(math.sqrt(1+(3*opponent_theta)/(math.pi ** 2)))
            E = 1/(1+math.exp((-1 * g) * (player_mu - opponent_mu)))
            v += ((g ** 2) * E * (1 - E))
            delta += (g * (match['score'] - E))
            improvement += g * (match['score'] - E)
        v = v ** -1
        delta = v * delta

        # step 5: determine the new value, sigma1, of the player's volatility.
        # 1. let a = in(sigma ** 2) and define f(x)
        a = math.log(player['volatility'] ** 2)
        def fx(x):
            return (((math.e ** x) * ((delta ** 2) - (player_theta ** 2) - v - (math.e ** x))) /
                (2 * ((player_theta ** 2) + v + (math.e ** x)) ** 2)) - ((x - a) / (self.system['constant'] ** 2))
        # 2. set the initial values of the iterative algorithm
        A = a
        if (delta ** 2) > ((player_theta ** 2) + v):
            B = math.log((delta ** 2) - (player_theta ** 2) - v)
        else:
            k = 1
            while fx(a - (k * self.system['constant'])) < 0:
                k += 1
            B = a - (k * self.system['constant'])
        # 3. let fA = fx(A) and fB = fx(B)
        fA = fx(A)
        fB = fx(B)
        # 4. while |B - A| > epsilon (system tolerance) carry out these steps
        while abs(B - A) > self.system['tolerance']:
            C = A + (A - B) * fA / (fB - fA)
            fC = fx(C)
            if (fC * fB) < 0:
                A = B
                fA = fB
            else:
                fA = fA / 2
            B = C
            fB = fC
        sigma1 = (math.e ** (A / 2))

        # step 6: update the rating deviation to the new pre-rating period value, theta
        theta_s = math.sqrt((player_theta ** 2) + (sigma1 ** 2))

        # step 7: update the mu and theta to their new values
        player_theta = 1 / math.sqrt((1 / (player_theta ** 2)) + (1 / v))
        player_mu = player_mu + ((player_theta ** 2) * improvement)

        # step 8: finally, convert back to the Glicko scale:
        converted = {'rating': (173.7178 * player_mu) + 1500.0,
                     'deviation': 173.7178 * player_theta,
                     'volatility': sigma1}

        return converted


g2eng = Glicko2()
player = {'rating': 1500.0, 'deviation': 350.0, 'volatility': 0.06}
period = [
	{'score': 0, 'opponent': {'rating': 1500.0, 'deviation': 350.0}},
	{'score': 0, 'opponent': {'rating': 1500.0, 'deviation': 350.0}}
	]
updated = g2eng.getNewRating(player, period)
print "NEW RATING:", updated['rating']
print "NEW DEVIATION:", updated['deviation']
print "NEW VOLATILITY:", updated['volatility']
