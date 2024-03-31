import math

speed_of_light = 299792458


def calculate_signal_attenuation_db(frequency, transmitter_pos: tuple[float, float], receiver_pos: tuple[float, float]):
    distance = math.sqrt((transmitter_pos[0] - receiver_pos[0]) ** 2 + (transmitter_pos[1] - receiver_pos[1]) ** 2)
    if distance < speed_of_light / frequency:
        return 0
    return 20 * math.log(4 * math.pi * distance * frequency / speed_of_light, 10)
