import numpy as np
from PIL import Image
from matplotlib import cm
from matplotlib import pyplot as plt
import math


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
    '''@depracated'''
    sum_of_all = np.sum(list(freq_map.values()))
    prob_map = {}
    for key in freq_map:
        prob_map[key] = freq_map[key] / sum_of_all
    return prob_map


def calculate_prob_table(input_list):
    '''@depracated'''
    freq_table = calculate_freq_table(input_list)
    return calculate_prob_table_from_freq(freq_table)


def calculate_prob_mass_from_prob_table(prob_map):
    '''@depracated'''
    prev_el = 0
    prob_mass_map = {}
    for key in prob_map:
        upper_bound = prob_map[key] + prev_el
        prob_mass_map[key] = [prev_el, upper_bound]
        prev_el = upper_bound
    return prob_mass_map


def calculate_prob_mass(input_list):
    '''@depracated'''
    table = calculate_prob_table(input_list)
    return calculate_prob_mass_from_prob_table(table)


def calculate_integer_prob_mass_from_freq_table(freq_table):
    prob_map = {}
    prev_freq = 0
    for symbol in freq_table:
        current_upper_bound = freq_table[symbol] + prev_freq
        prob_map[symbol] = [prev_freq, current_upper_bound]
        prev_freq = current_upper_bound

    return prob_map


def calculate_integer_prob_mass(input_list):
    freq_table = calculate_freq_table(input_list)
    return calculate_integer_prob_mass_from_freq_table(freq_table)


def calculate_sum_of_all(input_list):
    freq_table = calculate_freq_table(input_list)
    return np.sum(list(freq_table.values()))


def arithmetic_coding(input_list):
    # prob_mass = calculate_prob_mass(input_list)
    # prob_table = calculate_prob_table(input_list)
    prob_mass = calculate_prob_mass('AEKMRTYATY')
    prob_table = calculate_prob_table('AEKMRTYATY')

    passed_elements = []

    current_lower_bound = prob_mass[input_list[0]][0]
    current_upper_bound = prob_mass[input_list[0]][1]
    # currant_radius = current_upper_bound - current_lower_bound

    i = 0
    for element in input_list:
        if i == 0:
            i += 1
            continue
        print(f'===> ITERATION {i}')
        print(
            f'in bounds: lower - {current_lower_bound} | upper - {current_upper_bound}')
        element_lower_bound = prob_mass[element][0]
        element_upper_bound = prob_mass[element][1]
        print(
            f'element bounds: lower - {element_lower_bound} | upper - {element_upper_bound}')

        height = current_upper_bound - current_lower_bound
        current_lower_bound = current_lower_bound + \
            (current_upper_bound - current_lower_bound) * element_lower_bound
        current_upper_bound = current_lower_bound + \
            (height * (element_upper_bound - element_lower_bound))
        # currant_radius = current_upper_bound - current_lower_bound

        i += 1
        print(
            f'out bounds: lower - {current_lower_bound} | upper - {current_upper_bound}')

    # print(f'===> iteration {i}')
    # print(f'in bound: {current_bound}')
    # element_bounds = prob_mass[element][0]
    # current_offset = 1
    #  passed_elements.append(element)
    #   print(passed_elements)

    #    for passed_element in passed_elements:
    #         current_offset *= prob_mass[passed_element][0]
    #         print(f'offset-multiply: {prob_table[passed_element]}')
    #     if len(passed_elements) > 1:
    #         current_bound += current_offset
    #     print(f'out bound: {current_bound}')
    #     print(current_offset)
    #     i += 1

    # print('prob mass table')
    # print(prob_mass)
    return [current_lower_bound, prob_table, prob_mass]


def printB(binarty_int, variable=''):
    print_num = bin(binarty_int)[2:]
    while len(print_num) < 8:
        print_num = '0' + print_num
    print(variable + ': ' + print_num + ' (' + str(binarty_int) + ')')


def join_int_list(int_list):
    return ''.join(list(map(str, int_list)))


def arithmetic_decoding(input, prob_mass, prob_table):
    symbols = []
    divider = 1
    lower_bound = 0
    i = 0
    while input > 0:
        current_key = ''
        for key in prob_mass:
            bounds = prob_mass[key]
            print(f'curr check: {input} {bounds[0]} {bounds[1]}')
            if input > bounds[0] and input < bounds[1]:
                current_key = key
                lower_bound = bounds[0]
        symbols.append(current_key)
        print(f'result: {input} {prob_table[current_key]}')
        if input < 0.0001:
            input = 0
        else:
            input = (input - lower_bound) / prob_table[current_key]

        i += 1
        if i > 10:
            input = 0

    return symbols


def shift_left_16(number, fill_bit):
    shifted = (number << 1) & int(f'0000000011111111', 2)
    printB(shifted, 'shifted')
    return shifted | int(f'0000000{fill_bit}', 2)


def shift_right_16(number, shift_number):
    return (number >> shift_number) & int('0000000011111111', 2)


def get_oldest_bit(number):
    number = number & int('0000000011111111', 2)
    return (number & int('10000000', 2)) >> 7


def integer_arithmetic_encoding(input_list):
    freq_map = calculate_freq_table(input_list)
    # prob_map = calculate_prob_mass('AEKMRTYATY')
    prob_map = calculate_integer_prob_mass(input_list)
    N = calculate_sum_of_all(input_list)
    D = int('00000000', 2)
    G = int('11111111', 2)
    LN = 0
    k = 0
    prev_element = input_list[0]
    out_list = []

    print('Starting integer encoding...')
    printB(D, 'D')
    printB(G, 'G')

    for element in input_list:
        print(f'\n>>>> iteration: {k}, Element: {element}')
        current_interval = prob_map[element]
        R = G - D + 1
        ORG_D = D
        D = (D + math.floor(R * current_interval[0] / N))
        G = ORG_D + math.floor(R * current_interval[1] / N) - 1
        print(current_interval)
        print(R)
        printB(D, 'D')
        printB(G, 'G')
        D_oldest_bit = get_oldest_bit(D)
        G_oldest_bit = get_oldest_bit(G)

        if D_oldest_bit == G_oldest_bit:
            while D_oldest_bit == G_oldest_bit:
                out_list.append(G_oldest_bit)
                D = shift_left_16(D, 0)
                G = shift_left_16(G, 1)
                print(f'>>> OUT: {G_oldest_bit}')

                for i in range(LN):
                    out_list.append(1 - G_oldest_bit)
                    print(f'>>> OUT from LN: {1 - G_oldest_bit}')

                LN = 0

                D_oldest_bit = get_oldest_bit(D)
                G_oldest_bit = get_oldest_bit(G)

        #else:
        elif (D & int('11000000', 2) == int('01000000')) and (G & int('11000000', 2) == int('10000000')):
            D = (shift_left_16(D, 0) & int('01111111', 2)) | int(
                f'{D_oldest_bit}0000000', 2)
            G = (shift_left_16(G, 1) & int('01111111', 2)) | int(
                f'{G_oldest_bit}0000000', 2)
            LN += 1
            print('shifted D,G incremented LN')
            printB(D, 'D')
            printB(G, 'G')

        k += 1
        print('>> After iteration: (D, G, LN):')
        printB(D, 'D')
        printB(G, 'G')
        printB(LN)

    seen_1 = False
    ending = []
    current_bit = 0
    k = 0

    print('Out D:')
    printB(D, 'D')
    last_bit = D & int('00000001', 2)

    print('Out Output:')
    print(out_list)

    while last_bit == 0 and k < 8:
        D = shift_right_16(D, 1)
        last_bit = D & int('00000001', 2)
        k += 1

    if k < 8:
        for i in range(k, 8):
            last_bit = D & int('00000001', 2)
            D = shift_right_16(D, 1)
            ending.insert(0, last_bit)

        out_list += ending
    else:
        out_list += [0, 0, 0, 0, 0, 0, 0, 0]

    print('Out Ending:')
    print(ending)

    # while len(out_list) < 8:
    #     # out_list.append(0)
    #     out_list.insert(0, last_bit)

    print('>> Encoding finished, output:')
    print(''.join(list(map(str, out_list))))

    return [out_list, prob_map, N]


def find_symbol_in_prob_map(value, prob_map):
    print(f'FIND SYMBOL: {value}')
    print(f'PROB_MAP: {prob_map}')
    for symbol in prob_map:
        current_interval = prob_map[symbol]
        if value >= current_interval[0] and value < current_interval[1]:
            return symbol

    return 'ERROR'


def integer_arithmetic_decoding(input_string, prob_map, N):
    D = int('00000000', 2)
    G = int('11111111', 2)
    R = int('100000000', 2)
    LS = 1
    # int_prob_map = {}
    # for key in prob_map:
    #     interval = prob_map[key]
    #     int_prob_map[key] = ([interval[0] * N, interval[1] * N])

    Kn = int(join_int_list(input_string[:8]), 2)
    output = []
    k = 0
    input_string_counter = 8

    while k < N:
        R = G - D + 1
        current_value = ((Kn - D + 1) * N - 1) / R
        current_symbol = find_symbol_in_prob_map(current_value, prob_map)
        output.append(current_symbol)
        print(
            f'\n>>>> iteration: {k}, current_value={current_value}  input_counter={input_string_counter}, symbol={current_symbol}, Kn = {Kn}')
        print('IN Kn=')
        printB(Kn, 'Kn')

        print(f'current symbol: {current_symbol}')
        print(f'prob map: {prob_map}')
        current_interval = prob_map[current_symbol]
        ORG_D = D
        D = (D + math.floor(R * current_interval[0] / N))
        G = ORG_D + math.floor(R * current_interval[1] / N) - 1
        print(current_interval)
        print(R)
        printB(D, 'D')
        printB(G, 'G')
        D_oldest_bit = get_oldest_bit(D)
        G_oldest_bit = get_oldest_bit(G)

        if D_oldest_bit == G_oldest_bit:
            while D_oldest_bit == G_oldest_bit:
                Kn = shift_left_16(Kn, int(
                    input_string[input_string_counter] if input_string_counter < len(input_string) else 0))
                input_string_counter += 1
                D = shift_left_16(D, 0)
                G = shift_left_16(G, 1)
                print(f'>>> OUT: {G_oldest_bit}')

                # for i in range(LN):
                #     output.append(1 - G_oldest_bit)
                #     print(f'>>> OUT from LN: {1 - G_oldest_bit}')

                D_oldest_bit = get_oldest_bit(D)
                G_oldest_bit = get_oldest_bit(G)

        k += 1
        print('>> After iteration: (D, G, R, Kn):')
        printB(D, 'D')
        printB(G, 'G')
        printB(R)
        printB(Kn, 'Kn')

    print('>> Decoding finished, output:')
    print(''.join(list(map(str, output))))

    return output


def test_arithmetic_encoding_decoding(input_string):
    messages = []
    messages.append('#######################################')
    messages.append(f'#### TESTING INPUT: {input_string}')
    messages.append('#######################################')
    output, prob_map, N = integer_arithmetic_encoding(input_string)
    print(prob_map)
    decoded = integer_arithmetic_decoding(output, prob_map, N)
    decoded_string = ''.join(list(map(str, decoded)))
    is_success = decoded_string == input_string
    if is_success:
        messages.append('#######################################')
        messages.append('#### TEST PASSED ######################')
        messages.append('#######################################')
    else:
        messages.append('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        messages.append('#### TEST FAILED ######################')
        messages.append(f'output: {decoded_string}')
        messages.append('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    return messages


def test_code():
    test_strings = ['AB', 'ABC', 'AAC', 'AAAC', 'AAAAC', 'AACC', 'ACAC', 'AABC', 'ACA', '1234567890', '1234567890', 'ARYTMETYKA', '1111100000',
                    '1234554321', '0000055555', ';lasdjvkop3r92orufe90fuoasdjfvkvnawopsidf0933']
    messages = []
    for test_string in test_strings:
        messages += test_arithmetic_encoding_decoding(test_string)
        messages += '\n'

    for message in messages:
        print(message)

    #test_arithmetic_encoding_decoding('AAC')


if __name__ == '__main__':
    # f = open('boat.pgm', 'rb')
    # pgm = np.array(read_pgm(f))
    # pgm = pgm/255
    # print(np.amax(pgm))
    # im = Image.fromarray(np.uint8(cm.gist_gray(pgm)*255))
    # # im.show()
    # hist, bin_edges = np.histogram(im, bins=range(0, 257))
    # print(hist)
    # # plot = plt.plot(np.arange(0, 256), hist)
    # frequency_table = {key: value for key,
    #                    value in zip(bin_edges[0:256], hist)}
    # print(frequency_table)
    # # plt.plot(np.arange(0, 256), frequency_table)
    # sum_of_all = np.sum(list(frequency_table.values()))
    # frequency_list = list(frequency_table.values())
    # print('SUM')
    # probability_list = frequency_list/sum_of_all
    # probability_mass = []
    # mass_sum = 0
    # for probability in probability_list:
    #     probability_mass.append(probability + mass_sum)
    #     mass_sum += probability
    # flat_pgm = flat_arr(pgm)

    # test_input = list('1234567890')
    # result, prob_table, prob_mass = arithmetic_coding(test_input)
    # print(result)
    # print(arithmetic_decoding(result, prob_mass, prob_table))
    # output, prob_map, N = integer_arithmetic_encoding(test_input)
    # print(prob_map)
    # decoded = integer_arithmetic_decoding(output, prob_map, N)
    # print(decoded)

    test_code()

    # test_arithmetic_encoding_decoding('AAAC')
