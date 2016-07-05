import math

#################################
# Equations Related to Glicko-2 #
#################################

##### STEP 0: SET THE SYSTEM CONSTANT AND TOLERANCE
system = { 'constant': 0.5,
           'tolerance': 0.000001 }

# STEP 1: Determine a rating and RD for each player at the onset of the rating period. The
# system constant, tau, which constrains the change in volatility over time, needs to be
# set prior to the application of the system. Reasonable choices are between 0.3 and 1.2,
# though the system should be tested to decide which value results in greatest predictive
# accuracy. Smaller values of tau prevent the volatility measures from changing by large
# amounts, which in turn prevent enormous changes in ratings based on very improbable
# results. If the application of Glicko-2 is expected to involve extremely improbable
# collections of game outcomes, then tau should be set to a small value, even as small as,
# say, tau = 0.2.
#
# (a) If the player is unrated, set the rating to 1500 and the RD to 350. Set the player's
# volatility to 0.06 (this value depends on the particular application)
# (b) Otherwise, use the player's most recent rating, RD, and volatility sigma.

# STEP 2: Converting Glicko r and RD into Glicko-2 rating (mu) and deviation (theta).
def mu(r):
    return float((r - 1500)) / 173.7178

def theta(RD):
    return float(RD) / 173.7178

# defining g() and E()
def g(deviation):
     return 1/(math.sqrt(1+(3*deviation)/(math.pi ** 2)))

def E(pRating, oRating, oDeviation):
    return 1/(1+math.exp((-1 * g(oDeviation)) * (pRating - oRating)))

# STEP 3: Compute quantity v. This is the estimated variance of the team's/player's
# rating based only on game outcomes
def v(pRating, periodMatchHistory):   #periodMatchHistory = [{'score': int 1 or 0, 'oRating': float opponent's mu, 'oDeviation': float opponent's theta}, {..., ..., ...}, ...]
    variance = 0
    for i in range(len(periodMatchHistory)):
        fg = g(theta(periodMatchHistory[i]['oDeviation']))
        fE = E(mu(pRating), mu(periodMatchHistory[i]['oRating']), theta(periodMatchHistory[i]['oDeviation']))
        variance += ((fg ** 2) * fE * (1 - fE))
               
    variance = variance ** -1
    return variance

# STEP 4: Compute quantity delta, the estimated improvement in rating by comparing the
# pre-period rating to the performance rating based only on game outcomes.
def delta(pRating, periodMatchHistory):
    fv = v(pRating, periodMatchHistory)
    estimatedImprovement = 0.0
    for i in range(len(periodMatchHistory)):
        fg = g(theta(periodMatchHistory[i]['oDeviation']))
        fE = E(mu(pRating), mu(periodMatchHistory[i]['oRating']), theta(periodMatchHistory[i]['oDeviation']))
        estimatedImprovement += (fg * (periodMatchHistory[i]['score'] - fE))
    estimatedImprovement = fv * estimatedImprovement
    return estimatedImprovement

# STEP 5: Determine the new value, sigma1, of the volatility. This computation requires iteration.

def sigma(player, periodMatchHistory):
    # 1. Let a = ln(sigma ** 2) and define f(x)
    a = math.log(player['volatility'] ** 2)
    fdelta = delta(player['rating'], periodMatchHistory)
    ftheta = theta(player['deviation'])
    fv = v(player['rating'], periodMatchHistory)
    tau = system['constant']
    def fx(x):
        result1 = ((math.e ** x) * ((fdelta ** 2) - (ftheta ** 2) - fv - (math.e ** x)))
        result1 = (result1 / (2 * ((ftheta ** 2) + fv + (math.e ** x)) ** 2))
        result2 = (x - a) / (tau ** 2)
        result = result1 - result2
        return result
    # also define a convergence tolerance
    epsilon = system['tolerance']
    # 2. Set the initial values of the iterative algorithm
    A = a
    if (fdelta ** 2) > ((ftheta ** 2) + fv):
        B = math.log((fdelta ** 2) - (ftheta ** 2) - fv)
    else:
        k = 1
        while fx(a - (k * tau)) < 0:
            k += 1
        B = a - (k * tau)
    # 3. let fA = f(A) and fB = f(B)
    fA = fx(A)
    fB = fx(B)
    # 4. while |B - A| > epsilon, carry out the following steps.
    while abs(B - A) > epsilon:
        # (a) let C = A+(A-B)fA/(fB-FA), and let fC = f(C)
        C = A + (A - B) * fA / (fB - fA)
        fC = fx(C)
        # (b)if fCfB < 0, then set A <- B and fA <- fB; otherwise, just set fA <- fA/2
        if (fC * fB) < 0:
            A = B
            fA = fB 
        else:
            fA = fA / 2
        # (c) set B <- C and fB <- fC
        B = C
        fB = fC
        # (d) Stop if |B-A|<= epsilon. Repeat the above steps otherwise.
    # Once |B - A| <= epsilon, set new sigma and return
    sigma1 = (math.e ** (A / 2))
    return sigma1

# STEP 6: Update the rating deviation to the new pre-rating period value, theta`
def theta_s(player, periodMatchHistory):
    ftheta = theta(player['deviation'])
    fsigma = sigma(player, periodMatchHistory)
    ftheta_s = math.sqrt((ftheta ** 2) + (fsigma ** 2))
    return ftheta_s

# STEP 7: Update the rating and RD to the new values, mu` and theta`
def new_theta(player, periodMatchHistory):
    ftheta = theta(player['deviation'])
    ftheta_s = theta_s(player, periodMatchHistory)
    fv = v(player['rating'], periodMatchHistory)
    fRD = 1 / math.sqrt((1 / (ftheta_s ** 2)) + (1 / (fv)))
    return fRD
    
def new_mu(player, periodMatchHistory):
    fnew_theta = new_theta(player, periodMatchHistory)
    fmu = mu(player['rating'])
    improvement = 0.0
    for i in range(len(periodMatchHistory)):
        fg = g(theta(periodMatchHistory[i]['oDeviation']))
        fE = E(mu(player['rating']), mu(periodMatchHistory[i]['oRating']), theta(periodMatchHistory[i]['oDeviation']))
        improvement += fg * (periodMatchHistory[i]['score'] - fE)
    improvement = fmu + (fnew_theta ** 2) * improvement
    return improvement

# STEP 8: Finally, convert back to the Glicko scale:
#   **** These are the probably the functions you are going to want to call. The previous ones are usable
#        so you can get data from any of the steps if you need it for something, but the next two, if you pass
#        them new_mu() and new_theta() from Step 7 directly, will give you the new updated r and RD in the
#        original Glicko scale (which makes more sense to people).
def get_new_r(nmu):
    return (173.7178 * nmu)+1500.0

def get_new_RD(ntheta):
    return 173.7178 * ntheta
    
# EXAMPLE:
"""
testplayer = {'rating': 1500.0, 'deviation': 200.0, 'volatility': 0.06}
testhistory = [{'score': 1.0, 'oRating': 1400.0, 'oDeviation': 30.0},
               {'score': 0.0, 'oRating': 1550.0, 'oDeviation': 100.0},
               {'score': 0.0, 'oRating': 1700.0, 'oDeviation': 300.0}]

print get_new_r(new_mu(testplayer, testhistory))
print get_new_RD(new_theta(testplayer, testhistory))
"""
