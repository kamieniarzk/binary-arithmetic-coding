import itertools
import math
import random
from bitarray import bitarray
from timeit import default_timer as timer

INT_SIZE = 32
B = 8  # register length - at least 8
B_BIT_MAP = '0' * (INT_SIZE - B) + '1' * B
HALF_B = 2 ** (B - 1)
QUARTER_B = 2 ** (B - 2)


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

        d, bits_outstanding, r = normalize_encode(d, bits_outstanding, r, out_array)

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

        next_input_bit = encoded_sequence[input_string_counter] if input_string_counter < len(encoded_sequence) else 0
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
        success, encoded_len, input_len = test_binary_arithmetic_encoding_decoding(bitarray(case))
        if success:
            succeeded_cases.append(case)
        else:
            failed_cases.append(case)
        input_length_cumulative_sum += input_len
        encoded_length_cumulative_sum += encoded_len

    print(f'Succeeded: {len(test_cases) - len(failed_cases)}')
    print(f'Failed: {len(failed_cases)}')
    print(f'Average compression rate: {input_length_cumulative_sum / encoded_length_cumulative_sum}')


def run_test_with_file(input_file_path: str, compressed_file_path: str, decoded_file_path: str):
    bits = bitarray()
    bits.fromfile(open(input_file_path, 'rb'))
    input_len = len(bits)
    print(f'input length: {input_len}')
    start_encode = timer()
    encoded, c0, c1 = binary_arithmetic_encoding(bits)
    end_decode = timer()
    encoded_len = len(encoded)
    print(f'encoded length: {encoded_len}')
    encoded.tofile(open(compressed_file_path, 'wb'))
    start_decode = timer()
    decoded = binary_arithmetic_decoding(encoded, c0, c1)
    end_decode = timer()
    decoded.tofile(open(decoded_file_path, 'wb'))
    print(f'compression rate: {input_len / encoded_len}')
    print(f'compression time: {end_decode - start_encode}')
    print(f'decompression time: {end_decode - start_decode}')


def test_arbitrary_sequence_with_given_length(length: int):
    bits = bitarray()
    for i in range(0, length):
        bits.append(random.randint(0, 1))
    success, encoded_len, input_len = test_binary_arithmetic_encoding_decoding(bits)
    compression_rate = encoded_len / input_len
    print(f'test passed: {success}, compression rate: {compression_rate}')


if __name__ == '__main__':
    # run_test_with_all_possible_binary_numbers_in_range(8, 13)

    input_file_path = 'data/distributions/uniform.pgm'
    compressed_file_path = 'compressed.txt'
    decoded_file_path = 'decoded.pgm'

    print(f'file: {input_file_path}')
    run_test_with_file(input_file_path, compressed_file_path, decoded_file_path)
    # test_arbitrary_sequence_with_given_length(1000000)

