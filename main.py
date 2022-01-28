import numpy as np
import itertools
from PIL import Image
from matplotlib import cm
from matplotlib import pyplot as plt
# from bitstring import BitArray
import math

int_size = 32
b = 8
b_bit_map = '0' * (int_size - b) + '1' * b
halfB = 2**(b - 1)
quarterB = 2**(b - 2)


def calculate_binary_symbol_frequency(input_list):
    c1, c2 = 0, 0
    for element in input_list:
        if element == '0':
            c1 += 1
        else:
            c2 += 1
    return c1, c2


def printB(binarty_int, variable=''):
    print_num = bin(binarty_int)[2:]
    while len(print_num) < b:
        print_num = '0' + print_num
    print(variable + ': ' + print_num + ' (' + str(binarty_int) + ')')


def join_int_list(int_list):
    return ''.join(list(map(str, int_list)))


def shift_left_and_fill(number, fill_bit='0'):
    shifted = (number << 1) & int(b_bit_map, 2)
    zeros = '0' * (int_size - 1)
    return shifted | int(f'{zeros}{fill_bit}', 2)


def shift_left_and_add(number, add_bit):
    shifted = (number << 1)
    shifted += add_bit
    return shifted & int(b_bit_map, 2)


def rshift(val, n): return val >> n if val >= 0 else (val+0x100000000) >> n


def getLpsClps(c0, c1):
    if c0 < c1:
        return ['0', c0]

    return ['1', c1]


def binary_arithmetic_encoding(input_list):
    c0, c1 = calculate_binary_symbol_frequency(input_list)

    lps, clps = getLpsClps(c0, c1)

    L = 0
    R = 2**(b)

    LN = 0
    k = 0

    out_list = []

    k = 0
    for bit in input_list:
        rLPS = math.floor(R * clps / (c0 + c1))
        rMPS = R - rLPS

        if bit == lps:
            L = L + rMPS
            R = rLPS
        else:
            R = rMPS

        L, R, LN, out_list = encoder_renormalization(L, R, LN, out_list)

    k = 0
    ending = []

    # # # jeśli zakodowany ciąg ma długość mniej niz 8 - doklejamy znaczące bity z L albo zera
    # while last_bit == 0 and k < 8:
    #     L = rshift(L, 1)
    #     last_bit = L & int('00000001', 2)
    #     k += 1

    # if k < 8:
    #     for i in range(k, 8):
    #         last_bit = L & int('00000001', 2)
    #         L = rshift(L, 1)
    #         ending.insert(0, last_bit)

    # out_list += ending

    endingR = []

    for i in range(0, b):
        zeros = '0' * (int_size - 1)
        last_bit = R & int(f'{zeros}1', 2)
        R = rshift(R, 1)
        endingR.insert(0, last_bit)

    out_list += endingR

    if (len(out_list) % b) != 0:
        zeros_to_add = b - (len(out_list) % b)
        zeros_array = []
        i = 0
        while i < zeros_to_add:
            zeros_array.append(0)
            i += 1
        out_list += zeros_array

    return [out_list, c0, c1]


def bit_plus_follow(bit, follow_count):
    out_list = [bit]
    while follow_count > 0:
        out_list.append(str(1 - int(bit)))
        follow_count -= 1
    return out_list


def encoder_renormalization(L, R, LN, out_list):
    while R <= quarterB:
        if L + R <= halfB:
            out_list += bit_plus_follow('0', LN)
            LN = 0

        elif L >= halfB:
            out_list += bit_plus_follow('1', LN)
            L = L - halfB
            LN = 0

        else:
            LN += 1
            L -= quarterB

        L = shift_left_and_fill(L)
        R = shift_left_and_fill(R)

    return L, R, LN, out_list


def binary_arithmetic_decoding(input_string, c0, c1):
    L = 0
    R = 2**(b)

    lps, clps = getLpsClps(c0, c1)
    N = c0 + c1

    input_len = len(input_string)
    V_initial_len = b if input_len > b else input_len
    V = int(join_int_list(input_string[:V_initial_len]), 2)

    output = []
    k = 0
    input_counter = V_initial_len

    D = V

    while k < N:

        rLPS = math.floor(R * clps / (c0 + c1))
        rMPS = R - rLPS

        if D >= rMPS:
            output.append(lps)
            D -= rMPS
            R = rLPS
        else:
            output.append(str(1 - int(lps)))
            R = rMPS

        # assert R != 0
        # input_string, D, R, V, input_counter = decoder_renormalization(
        #     input_string, D, R, V, input_counter)

        while R <= quarterB:
            R = shift_left_and_fill(R)
            D = shift_left_and_add(D, pobierz_bit(input_string, input_counter))
            input_counter += 1

        k += 1

    return output


def pobierz_bit(input_string, input_counter):
    if input_counter >= len(input_string):
        return 0
    return int(input_string[input_counter])


def decoder_renormalization(input_string, L, R, V, input_counter):
    while R <= quarterB:
        if L + R <= halfB:
            pass
        elif L >= halfB:
            L -= halfB
            V -= halfB
        else:
            L -= quarterB
            V -= quarterB
        L = shift_left_and_fill(L)
        R = shift_left_and_fill(R)
        V = shift_left_and_add(V, pobierz_bit(input_string, input_counter))
        input_counter += 1

    return input_string, L, R, V, input_counter


def test_binary_arithmetic_encoding_decoding(input_string):
    messages = []
    messages.append('#######################################\n')
    messages.append(f'#### TESTING INPUT: {input_string}\n')
    messages.append('#######################################\n')
    output, c1, c2 = binary_arithmetic_encoding(input_string)
    decoded = binary_arithmetic_decoding(output, c1, c2)
    decoded_string = ''.join(list(map(str, decoded)))
    is_success = decoded_string == input_string
    if is_success:
        messages.append('#######################################\n')
        messages.append('#### TEST PASSED ######################\n')
        messages.append('#######################################\n')
    else:
        messages.append('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
        messages.append('#### TEST FAILED ######################\n')
        messages.append(f'output: {decoded_string}\n')
        messages.append('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
    return decoded_string, messages


def run_test():
    MIN_LENGTH = 1
    MAX_LENGTH = 8
    test_cases = []

    for length in range(MIN_LENGTH, MAX_LENGTH + 1):
        new_cases = [''.join(item)
                     for item in itertools.product('01', repeat=length)]
        test_cases.extend(new_cases)

    failed_cases = []
    succeeded_cases = []

    for case in test_cases:
        result, messages = test_binary_arithmetic_encoding_decoding(case)
        if case != result:
            failed_cases.append(case + ' ' + result)
        else:
            succeeded_cases.append(case)

    print('Succeed cases:')
    print(succeeded_cases)

    print('Failed cases:')
    print(failed_cases)

    print(f'Succeed: {len(test_cases) - len(failed_cases)}')
    print(f'Failed: {len(failed_cases)}')


if __name__ == '__main__':
    run_test()
    # test_binary_arithmetic_encoding_decoding('1001')
