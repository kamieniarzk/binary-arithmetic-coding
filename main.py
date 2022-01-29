import random

import numpy as np
import itertools
from bitstring import BitArray
from bitarray import bitarray
from PIL import Image
from matplotlib import cm
from matplotlib import pyplot as plt
# from bitstring import BitArray
import math

int_size = 32
b = 8 # register length
b_bit_map = '0' * (int_size - b) + '1' * b
halfB = 2 ** (b - 1)
quarterB = 2 ** (b - 2)


def calculate_binary_symbol_frequency(bits: bitarray):
    c0, c1 = 0, 0
    for element in bits.tolist():
        if element:
            c0 += 1
        else:
            c1 += 1
    return c0, c1


def printB(binary_int, variable=''):
    print_num = bin(binary_int)[2:]
    while len(print_num) < b:
        print_num = '0' + print_num
    print(variable + ': ' + print_num + ' (' + str(binary_int) + ')')


def join_int_list(int_list):
    return ''.join(list(map(str, int_list)))


def shift_left_and_fill(number, fill_bit='0'):
    shifted = (number << 1) & int(b_bit_map, 2)
    zeros = '0' * (int_size - 1)
    return shifted | int(f'{zeros}{fill_bit}', 2)


def binary_arithmetic_encoding(input_sequence: bitarray):
    c0, c1 = calculate_binary_symbol_frequency(input_sequence)
    D = 0
    R = 2 ** b
    LN = 0
    out_list = bitarray()
    mult_factor = c0 / (c0 + c1)

    for element in input_sequence:
        R1 = math.floor(R * mult_factor)
        R2 = R - R1

        if element:
            R = R1
            D = D + R2
        else:
            R = R2

        while R <= quarterB:
            if D >= halfB:
                out_list.append(1)
                while LN > 0:
                    out_list.append(0)
                    LN -= 1
                D -= halfB
            elif D + R <= halfB:
                out_list.append(0)
                while LN > 0:
                    out_list.append(1)
                    LN -= 1
            else:
                LN += 1
                D -= quarterB
            D = shift_left_and_fill(D, 0)
            R = shift_left_and_fill(R, 0)

    endingR = []

    for i in range(0, b):
        last_bit = D & 1
        D >>= 1
        if i == b - 1:
            while LN > 0:
                endingR.insert(0, 1 - last_bit)
                LN -= 1
        endingR.insert(0, last_bit)

    out_list += endingR

    return [out_list, c0, c1]


def binary_arithmetic_decoding(encoded_sequence, c0, c1):
    D = 0
    R = 2 ** b
    mult_factor = c0 / (c0 + c1)

    input_len = len(encoded_sequence)
    kn_initial_len = b if input_len > b else input_len
    Kn = int(join_int_list(encoded_sequence[:kn_initial_len]), 2)
    output = bitarray()
    k = 0
    input_string_counter = kn_initial_len
    while k < c0 + c1:
        R1 = math.floor(R * mult_factor)
        R2 = R - R1

        if Kn - D >= R2:
            R = R1
            D += R2
            output.append(1)
        else:
            R = R2
            output.append(0)

        while R <= quarterB:
            if D + R <= halfB:
                pass
            elif D >= halfB:
                D -= halfB
                Kn -= halfB
            else:
                D -= quarterB
                Kn -= quarterB
            D = shift_left_and_fill(D, 0)
            R = shift_left_and_fill(R, 0)
            Kn = shift_left_and_fill(Kn, str(
                encoded_sequence[input_string_counter] if input_string_counter < len(encoded_sequence) else '0'))
            input_string_counter += 1
        k += 1

    return output


def test_binary_arithmetic_encoding_decoding(input_sequence: bitarray):
    encoded, c0, c1 = binary_arithmetic_encoding(input_sequence)
    decoded = binary_arithmetic_decoding(encoded, c0, c1)
    return decoded == input_sequence, len(encoded), len(input_sequence)


def run_test_with_all_possible_binary_numbers_in_range(low: int, hi: int):
    test_cases = []

    for length in range(low, hi + 1):
        new_cases = [''.join(item)
                     for item in itertools.product('01', repeat=length)]
        test_cases.extend(new_cases)

    failed_cases = []
    succeeded_cases = []
    input_length_cumulative_sum = 0
    encoded_length_cumulative_sum = 0

    for case in test_cases:
        success, encoded_len, input_len = test_binary_arithmetic_encoding_decoding(bitarray(case))
        if success:
            succeeded_cases.append(case)
        else:
            failed_cases.append(case)
        input_length_cumulative_sum += input_len
        encoded_length_cumulative_sum += encoded_len

    print(f'Succeeded: {len(test_cases) - len(failed_cases)}')
    print(f'Failed: {len(failed_cases)}')
    print(f'Average compression rate: {encoded_length_cumulative_sum / input_length_cumulative_sum}')


def run_test_with_file(input_file_path: str, compressed_file_path: str, decoded_file_path: str):
    bits = bitarray()
    bits.fromfile(open(input_file_path, 'rb'))
    input_len = len(bits)
    print(f'input length: {input_len}')
    encoded, c0, c1 = binary_arithmetic_encoding(bits)
    encoded_len = len(encoded)
    print(f'encoded length: {encoded_len}')
    encoded.tofile(open(compressed_file_path, 'wb'))
    decoded = binary_arithmetic_decoding(encoded, c0, c1)
    decoded.tofile(open(decoded_file_path, 'wb'))
    print(f'compression rate: {encoded_len / input_len}')


def test_arbitrary_sequence_with_given_length(length: int):
    bits = bitarray()
    for i in range(0, length):
        bits.append(random.randint(0, 1))
    success, encoded_len, input_len = test_binary_arithmetic_encoding_decoding(bits)
    compression_rate = encoded_len / input_len
    print(f'test passed: {success}, compression rate: {compression_rate}')


if __name__ == '__main__':
    run_test_with_all_possible_binary_numbers_in_range(8, 10)

    input_file_path = 'images/pseudokod.jpg'
    compressed_file_path = 'compressed.txt'
    decoded_file_path = 'decoded.jpg'

    # run_test_with_file(input_file_path, compressed_file_path, decoded_file_path)
    # test_arbitrary_sequence_with_given_length(1000000)

