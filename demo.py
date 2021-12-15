import numpy as np
from PIL import Image
from matplotlib import cm
from matplotlib import pyplot as plt


def read_pgm(pgmf):
    """Return a raster of integers from a PGM as a list of lists."""
    first_line = pgmf.readline()
    assert first_line == b'P5\n'
    pgmf.readline()
    second_line = pgmf.readline()
    (width, height) = [int(i) for i in second_line.split()]
    depth = int(pgmf.readline())
    assert depth <= 255

    raster = []
    for y in range(height):
        row = []
        for y in range(width):
            row.append(ord(pgmf.read(1)))
        raster.append(row)
    return raster


def flat_arr(t):
    return [item for sublist in t for item in sublist]


def calculate_freq_table(input_list):
    freq_dict = {}
    for element in input_list:
        freq_dict[element] = freq_dict[element] + \
            1 if element in freq_dict else 1

    return freq_dict


def calculate_prob_table_from_freq(freq_map):
    sum_of_all = np.sum(list(freq_map.values()))
    prob_map = {}
    for key in freq_map:
        prob_map[key] = freq_map[key] / sum_of_all
    return prob_map


def calculate_prob_table(input_list):
    freq_table = calculate_freq_table(input_list)
    return calculate_prob_table_from_freq(freq_table)


def calculate_prob_mass_from_prob_table(prob_map):
    prev_el = 0
    prob_mass_map = {}
    for key in prob_map:
        upper_bound = prob_map[key] + prev_el
        prob_mass_map[key] = [prev_el, upper_bound]
        prev_el = upper_bound
    return prob_mass_map


def calculate_prob_mass(input_list):
    table = calculate_prob_table(input_list)
    return calculate_prob_mass_from_prob_table(table)


def arithmetic_coding(input_list):
    prob_mass = calculate_prob_mass(input_list)
    prob_table = calculate_prob_table(input_list)

    passed_elements = []

    current_bound = prob_mass[input_list[0]][0]
    print('first bound')
    print(current_bound)

    i = 0
    for element in input_list:
        # element_bounds = prob_mass[element][0]
        current_offset = 1
        passed_elements.append(element)
        for passed_element in passed_elements:
            current_offset *= prob_table[passed_element]
        if len(passed_elements) > 1:
            current_bound += current_offset
        print(f'iteration {i}')
        print(current_bound)
        print(current_offset)
        i += 1

    print('prob mass table')
    print(prob_mass)
    return current_bound


if __name__ == '__main__':
    f = open('boat.pgm', 'rb')
    pgm = np.array(read_pgm(f))
    pgm = pgm/255
    print(np.amax(pgm))
    im = Image.fromarray(np.uint8(cm.gist_gray(pgm)*255))
    # im.show()
    hist, bin_edges = np.histogram(im, bins=range(0, 257))
    print(hist)
    # plot = plt.plot(np.arange(0, 256), hist)
    frequency_table = {key: value for key,
                       value in zip(bin_edges[0:256], hist)}
    print(frequency_table)
    # plt.plot(np.arange(0, 256), frequency_table)
    sum_of_all = np.sum(list(frequency_table.values()))
    frequency_list = list(frequency_table.values())
    print('SUM')
    probability_list = frequency_list/sum_of_all
    probability_mass = []
    mass_sum = 0
    for probability in probability_list:
        probability_mass.append(probability + mass_sum)
        mass_sum += probability
    flat_pgm = flat_arr(pgm)

    test_input = ['C', 'D', 'B', 'C', 'D']

    print(arithmetic_coding(test_input))
