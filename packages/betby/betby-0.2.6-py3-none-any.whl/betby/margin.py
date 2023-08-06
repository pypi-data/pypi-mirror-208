import math

# округление кэфов
def kf_round(a, max):
    if a < 3.5:
        a = math.floor(a * 100) / 100
    elif a < 10:
        a = math.floor(a * 10) / 10
    elif a < max:
        a = math.floor(a)
    else:
        a = max
    if a > max:
        a = max
    return a

    # print(kf_round(1.85, 17))

# расчет маржи, кэфы на победу низкие
def margin(kf, m=0.075, max=25):
    k_0 = 22 * 0.045 / m  # убывающая прямая
    v_0 = (-m + 0.23 - 0.5 / k_0) / (
            0.23 - 1 / k_0)  # предельная вер
    m_0 = 0.23 * (1 - v_0)
    n_0 = (1.5 - 1 / k_0) / (
            1.5 - 0.23)  # показатель (производная)
    ver = 0.5 + abs(1 / kf - 0.5)
    mar_1 = m - (ver - 0.5) / k_0
    mar_2 = 1.5 * (1 - ver) - (1.5 - 0.23) * (
            1 - v_0) * ((1 - ver) / (1 - v_0)) ** n_0
    if ver >= v_0:
        kf_v = (1 - mar_2) / ver
    else:
        kf_v = (1 - mar_1) / ver
    if 1 / kf >= 0.5:
        kf = kf_round(kf_v, max)
    else:
        kf = kf_round((1 - m) * kf_v / (kf_v - 1 + m), max)
    return kf

