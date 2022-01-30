import itertools
import math
import random
from bitarray import bitarray
from timeit import default_timer as timer
from os import walk
import numpy as np
import matplotlib.pyplot as plt

INT_SIZE = 32
B = 32  # register length - at least 8
B_BIT_MAP = '0' * (INT_SIZE - B) + '1' * B
HALF_B = 2 ** (B - 1)
QUARTER_B = 2 ** (B - 2)

# old


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

#####


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
    while len(print_num) < B:
        print_num = '0' + print_num
    print(variable + ': ' + print_num + ' (' + str(binary_int) + ')')


def join_int_list(int_list):
    return ''.join(list(map(str, int_list)))


def binary_arithmetic_encoding(input_sequence: bitarray):
    c0, c1 = calculate_binary_symbol_frequency(input_sequence)
    d = 0
    r = 2 ** B
    bits_outstanding = 0
    out_array = bitarray()
    constant_coefficient = c0 / (c0 + c1)

    for symbol in input_sequence:
        r1 = math.floor(r * constant_coefficient)
        r2 = r - r1

        if symbol:  # 1
            r = r1
            d = d + r2
        else:  # 0
            r = r2

        d, bits_outstanding, r = normalize_encode(
            d, bits_outstanding, r, out_array)

    out_array += flush_bits_from_D(d, bits_outstanding)

    return [out_array, c0, c1]


def flush_bits_from_D(d, bits_outstanding):
    endingR = []
    for i in range(0, B):
        last_bit = d & 1
        d >>= 1
        if i == B - 1:
            while bits_outstanding > 0:
                endingR.insert(0, 1 - last_bit)
                bits_outstanding -= 1
        endingR.insert(0, last_bit)
    return endingR


def normalize_encode(d, bits_outstanding, r, out_list):
    while r <= QUARTER_B:
        if d >= HALF_B:
            out_list.append(1)
            while bits_outstanding > 0:
                out_list.append(0)
                bits_outstanding -= 1
            d -= HALF_B
        elif d + r <= HALF_B:
            out_list.append(0)
            while bits_outstanding > 0:
                out_list.append(1)
                bits_outstanding -= 1
        else:
            bits_outstanding += 1
            d -= QUARTER_B
        d <<= 1
        r <<= 1
    return d, bits_outstanding, r


def binary_arithmetic_decoding(encoded_sequence: bitarray, c0, c1):
    d = 0
    r = 2 ** B
    mult_factor = c0 / (c0 + c1)

    input_len = len(encoded_sequence)
    input_buffer = int(encoded_sequence[:B].to01(), 2)
    # input_buffer = int(join_int_list(encoded_sequence[:initial_buffer_len]), 2)
    output = bitarray()
    k = 0
    bits_already_seen = B
    while k < c0 + c1:
        r1 = math.floor(r * mult_factor)
        r2 = r - r1

        if input_buffer - d >= r2:
            r = r1
            d += r2
            output.append(1)
        else:
            r = r2
            output.append(0)

        d, input_buffer, r, bits_already_seen = normalize_decode(d, input_buffer, r, encoded_sequence,
                                                                 bits_already_seen)
        k += 1

    return output


def normalize_decode(d, input_buffer, r, encoded_sequence, input_string_counter):
    while r <= QUARTER_B:
        if d + r <= HALF_B:
            pass
        elif d >= HALF_B:
            d -= HALF_B
            input_buffer -= HALF_B
        else:
            d -= QUARTER_B
            input_buffer -= QUARTER_B
        d <<= 1
        r <<= 1

        next_input_bit = encoded_sequence[input_string_counter] if input_string_counter < len(
            encoded_sequence) else 0
        input_buffer <<= 1
        input_buffer |= next_input_bit
        input_string_counter += 1
    return d, input_buffer, r, input_string_counter


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
        success, encoded_len, input_len = test_binary_arithmetic_encoding_decoding(
            bitarray(case))
        if success:
            succeeded_cases.append(case)
        else:
            failed_cases.append(case)
        input_length_cumulative_sum += input_len
        encoded_length_cumulative_sum += encoded_len

    print(f'Succeeded: {len(test_cases) - len(failed_cases)}')
    print(f'Failed: {len(failed_cases)}')
    print(
        f'Average compression rate: {input_length_cumulative_sum / encoded_length_cumulative_sum}')


def run_test_with_file(input_file_path: str, compressed_file_path: str, decoded_file_path: str):
    bits = bitarray()
    bits.fromfile(open(input_file_path, 'rb'))
    input_len = len(bits)
    start_encode = timer()
    encoded, c0, c1 = binary_arithmetic_encoding(bits)
    end_encode = timer()
    encoded_len = len(encoded)
    encoded.tofile(open(compressed_file_path, 'wb'))
    start_decode = timer()
    decoded = binary_arithmetic_decoding(encoded, c0, c1)
    end_decode = timer()
    decoded.tofile(open(decoded_file_path, 'wb'))

    encoding_length = end_encode - start_encode
    decoding_length = end_decode - start_decode

    return [input_len, encoded_len, encoding_length, decoding_length]


def test_arbitrary_sequence_with_given_length(length: int):
    bits = bitarray()
    for i in range(0, length):
        bits.append(random.randint(0, 1))
    success, encoded_len, input_len = test_binary_arithmetic_encoding_decoding(
        bits)
    compression_rate = encoded_len / input_len
    print(f'test passed: {success}, compression rate: {compression_rate}')


def print_histograms_for_pgms_from_directory(directory_path, output_path):
    filenames = next(walk(directory_path), (None, None, []))[2]
    for filename in filenames:
        full_path = directory_path + '/' + filename
        pgmf = read_pgm(open(full_path, 'rb'))
        array = np.array(pgmf).flatten()
        plt.hist(array, bins=range(0, 257))
        plt.title(f'"{filename}" - Histogram')
        plt.savefig(f'{output_path}/{filename}_histogram.png')
        plt.close()


def calculate_entropy(c0, c1):
    sym_sum = c0 + c1
    c0_prob = c0/sym_sum
    c1_prob = c1/sym_sum
    print(c0_prob)
    print(c1_prob)
    return -(c0_prob * math.log(c0_prob, 2)) - (c1_prob * math.log(c1_prob, 2))


def calculate_entropy_for_pgms_from_directory(directory_path, results_path='results/entropy.txt'):
    filenames = next(walk(directory_path), (None, None, []))[2]
    entropy_output = results_path
    with open(entropy_output, 'w') as file:
        for filename in filenames:
            full_path = directory_path + '/' + filename
            pgmf = read_pgm(open(full_path, 'rb'))
            array = np.array(pgmf).flatten()
            probs = calculate_prob_table(array)
            entropy = 0
            for i in range(1, 256):
                if i in probs:
                    entropy -= probs[i] * math.log(probs[i], 2)
            file.write(f'Entropy of {filename}: {entropy}\n')


def test_all_files_from_directory(directory_path, compressed_path, decoded_path, logs_path):
    filenames = next(walk(directory_path), (None, None, []))[2]
    with open(logs_path, 'w') as output:
        for filename in filenames:
            full_file_path = directory_path + '/' + filename
            compressed_path_with_name = compressed_path + '/' + filename
            decoded_path_with_name = decoded_path + '/' + filename
            input_len, encoded_len, encoding_length, decoding_length = run_test_with_file(
                full_file_path, compressed_path_with_name, decoded_path_with_name)
            output.write(f'file: {filename}:\t')
            output.write(f'input size (bits): {input_len}\t')
            output.write(f'encoded size (bits): {encoded_len}\t')
            output.write(f'compression rate: {input_len / encoded_len}\t')
            output.write(f'encoding time (s): {encoding_length}\t')
            output.write(f'decoding time size (s): {decoding_length}\n\n')


def read_line_ignore_comment(file):
    line = file.readline()
    while line[0] == ord('#'):
        line = file.readline()
    return line


def read_pgm(pgmf):
    """Return a raster of integers from a PGM as a list of lists."""
    first_line = read_line_ignore_comment(pgmf)
    assert first_line == b'P5\n'
    second_line = read_line_ignore_comment(pgmf)

    (width, height) = [int(i) for i in second_line.split()]
    depth = int(read_line_ignore_comment(pgmf))
    assert depth <= 255

    raster = []
    for y in range(height):
        row = []
        for y in range(width):
            row.append(ord(pgmf.read(1)))
        raster.append(row)
    return raster


if __name__ == '__main__':
    # run_test_with_all_possible_binary_numbers_in_range(8, 13)

    distributions_path = 'data/distributions'
    images_path = 'data/images'
    entropies_path = 'results/entropies'
    histograms_path = 'results/histograms'
    distributions_entropies_filename = 'distributions_entropies.txt'
    images_entropies_filename = 'images_entropies.txt'
    encoded_images_path = 'results/images/encoded'
    decoded_images_path = 'results/images/decoded'
    encoded_distributions_path = 'results/distributions/encoded'
    decoded_distributions_path = 'results/distributions/decoded'
    images_data_path = 'results/images/logs.txt'
    distributions_data_path = 'results/distributions/logs.txt'

    # print_histograms_for_pgms_from_directory(
    #     distributions_path, histograms_path)
    # print_histograms_for_pgms_from_directory(
    #     distributions_path, histograms_path)
    #
    # calculate_entropy_for_pgms_from_directory(
    #     distributions_path, f'{entropies_path}/{distributions_entropies_filename}')
    # calculate_entropy_for_pgms_from_directory(
    #     images_path, f'{entropies_path}/{images_entropies_filename}')

    test_all_files_from_directory(
        images_path, encoded_images_path, decoded_images_path, images_data_path)
    test_all_files_from_directory(
        distributions_path, encoded_distributions_path, decoded_distributions_path, distributions_data_path)
