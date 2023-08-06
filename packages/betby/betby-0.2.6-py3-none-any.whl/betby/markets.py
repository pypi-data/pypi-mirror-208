import numpy as np
from math import exp, factorial


class Get_markets:
    def __init__(self, avg_1, avg_2, score_1=0, score_2=0, time=0,
                 time_full=93, time_block=90, matrix=None, poisson=False,
                 result=None):
        self.avg_1 = avg_1
        self.avg_2 = avg_2
        self.score_1 = score_1
        self.score_2 = score_2
        self.time = time
        self.time_full = time_full
        self.time_block = time_block
        self.matrix = matrix
        self.poisson = poisson
        self.result = {} if result is None else result
        self.poi_1 = len(matrix[0]) if not poisson else None

    # округление кэфов
    def kf_round(self, a, max):
        if a < 3.5:
            a = np.floor(a * 100) / 100
        elif a < 10:
            a = np.floor(a * 10) / 10
        elif a < max:
            a = np.floor(a)
        else:
            a = max
        if a > max:
            a = max
        return a

    # расчет маржи, кэфы на победу низкие
    def margin(self, kf, m=0.05, max=25):

        k_0 = 22 * 0.045 / m  # убывающая прямая
        v_0 = (-m + 0.23 - 0.5 / k_0) / (0.23 - 1 / k_0)  # предельная вер
        m_0 = 0.23 * (1 - v_0)
        n_0 = (1.5 - 1 / k_0) / (1.5 - 0.23)  # показатель (производная)
        ver = 0.5 + abs(1 / kf - 0.5)
        mar_1 = m - (ver - 0.5) / k_0
        mar_2 = 1.5 * (1 - ver) - (1.5 - 0.23) * (
                1 - v_0) * ((1 - ver) / (1 - v_0)) ** n_0
        if ver >= v_0:
            kf_v = (1 - mar_2) / ver
        else:
            kf_v = (1 - mar_1) / ver
        if 1 / kf >= 0.5:
            kf = self.kf_round(kf_v, max)
        else:
            kf = self.kf_round((1 - m) * kf_v / (kf_v - 1 + m), max)
        return kf

    def get_matrix(self):
        avg_1 = self.avg_1 * (self.time_full - self.time) / self.time_full
        avg_2 = self.avg_2 * (self.time_full - self.time) / self.time_full
        if self.poisson:
            self.matrix = np.zeros((self.poisson, self.poisson))
            for i in range(self.poisson):
                for j in range(self.poisson):
                    prob = (exp(-avg_1) * avg_1 ** i / factorial(i)) * (
                            exp(-avg_2) * avg_2 ** j / factorial(j))
                    self.matrix[i, j] = prob
        return self.matrix

    def total(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        self.result.update({'TOTAL': {'outcomes': []}})
        for val in range(2 * self.poisson or 2 * self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if i + j < val + 0.5:
                        prob += self.matrix[i, j]
            if prob >= min_prob and prob <= 1 - min_prob:
                self.result['TOTAL']['outcomes'].append({
                    'spec_' + str(
                        val + 0.5 + self.score_1 + self.score_2): str(
                        val + 0.5 + self.score_1 + self.score_2),
                    'over': {'prob': 1 - prob, 'margin': mar,
                             'ODDS': self.margin(
                                 1 / (1 - prob), mar, max_odds),
                             'block': 0},
                    'under': {'prob': prob, 'margin': mar,
                              'ODDS': self.margin(1 / prob, mar, max_odds),
                              'block': 0}
                })
            prob = 0

    def handicap(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        self.result.update({'HANDICAP': {'outcomes': []}})
        for val in range(1 - (self.poisson or self.poi_1),
                         self.poisson or self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if j - i > val + 0.5:
                        prob += self.matrix[i, j]
            if prob >= min_prob and prob <= 1 - min_prob:
                self.result['HANDICAP']['outcomes'].append({
                    'spec_' + str(
                        val + 0.5 - self.score_1 + self.score_2): str(
                        val + 0.5 - self.score_1 + self.score_2),
                    'H1': {'prob': 1 - prob, 'margin': mar,
                           'ODDS': self.margin(1 / (1 - prob), mar, max_odds),
                           'block': 0},
                    'H2': {'prob': prob, 'margin': mar,
                           'ODDS': self.margin(1 / prob, mar, max_odds),
                           'block': 0}
                })
            prob = 0

    def home_total(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        self.result.update({'HOME_TOTAL': {'outcomes': []}})
        for val in range(self.poisson or self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if i < val + 0.5:
                        prob += self.matrix[i, j]
            if prob >= min_prob and prob <= 1 - min_prob:
                self.result['HOME_TOTAL']['outcomes'].append({
                    'spec_' + str(val + 0.5 + self.score_1): str(
                        val + 0.5 + self.score_1),
                    'over': {'prob': 1 - prob, 'margin': mar, 'ODDS':
                        self.margin(
                            1 / (1 - prob), mar, max_odds), 'block': 0},
                    'under': {'prob': prob, 'margin': mar, 'ODDS': self.margin(
                        1 / prob, mar, max_odds), 'block': 0}
                })
            prob = 0

    def away_total(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        self.result.update({'AWAY_TOTAL': {'outcomes': []}})
        for val in range(self.poisson or self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if j < val + 0.5:
                        prob += self.matrix[i, j]
            if prob >= min_prob and prob <= 1 - min_prob:
                self.result['AWAY_TOTAL']['outcomes'].append({
                    'spec_' + str(val + 0.5 + self.score_2): str(
                        val + 0.5 + self.score_2),
                    'over': {'prob': 1 - prob, 'margin': mar,
                             'ODDS': self.margin(1 / (1 - prob), mar,
                                                 max_odds), 'block': 0},
                    'under': {'prob': prob, 'margin': mar,
                              'ODDS': self.margin(1 / prob, mar, max_odds),
                              'block': 0}
                })
            prob = 0