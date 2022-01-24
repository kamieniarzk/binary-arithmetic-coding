import numpy as np
import itertools
from PIL import Image
from matplotlib import cm
from matplotlib import pyplot as plt
# from bitstring import BitArray
import math

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
    while len(print_num) < 8:
        print_num = '0' + print_num
    print(variable + ': ' + print_num + ' (' + str(binarty_int) + ')')

def join_int_list(int_list):
    return ''.join(list(map(str, int_list)))

def shift_left_and_fill(number, fill_bit):
    shifted = (number << 1) & int(f'0000000011111111', 2)
    printB(shifted, 'shifted')
    return shifted | int(f'0000000{fill_bit}', 2)

def binary_arithmetic_encoding(input_list):
    
    c1, c2 = calculate_binary_symbol_frequency(input_list)
    D = int('00000000', 2)
    R = int('100000000', 2)
    LN = 0
    k = 0
    out_list = []
    mult_factor = c1 / (c1 + c2)

    k = 0
    for element in input_list:
      
        R1 = math.floor(R * mult_factor)
        R2 = R - R1

        if element == '0':
            R = R1
            D = D + R2
        else:
            R = R2

        normalizuj_kod(D, R, LN, out_list)
    
    k = 0
    ending = []
    last_bit = D & int('00000001', 2)

    ## jeśli zakodowany ciąg ma długość mniej niz 8 - doklejamy znaczące bity z D albo zera 
    while last_bit == 0 and k < 8:
        D >>= 1
        last_bit = D & int('00000001', 2)
        k += 1

    if k < 8:
        for i in range(k, 8):
            last_bit = D & int('00000001', 2)
            D >>= 1
            ending.insert(0, last_bit)

        out_list += ending
    elif len(out_list) < 8:
        zeros_to_add = 8 - len(out_list) if len(out_list) < 8 else 0 
        zeros_array = []
        i = 0
        while i < zeros_to_add:
            zeros_array.append(0)
            i += 1
        out_list += zeros_array

    return [out_list, c1, c2]

def binary_arithmetic_decoding(input_string, c1, c2):
    POL = 1 << 7
    CWIERC = 1 << 6
    D = int('00000000', 2)
    R = int('100000000', 2)

    mult_factor = c1 / (c1 + c2)
    print(f'mult factor is {mult_factor}')

    input_len = len(input_string)
    kn_initial_len = 8 if input_len > 8 else input_len
    N = c1 + c2
    print(f'Input is: {input_string}')
    Kn = int(join_int_list(input_string[:kn_initial_len]), 2)
    output = []
    k = 0
    input_string_counter = kn_initial_len
    while k < N:
        R1 = math.floor(R * mult_factor)
        R2 = R - R1

        if Kn - D >= R2:
            R = R1 #128
            D += R2 #128
            output.append('0') # 0
        else:
            R = R2
            output.append('1')

        normalizuj_dek(input_string, D, R, Kn, input_string_counter)
        k += 1
        
    return output

def normalizuj_dek(input_string, D, R, Kn, input_string_counter):
    POL = 1 << 7                  
    CWIERC = 1 << 6

    while R <= CWIERC:
        if D + R <= POL: 
            pass
        elif D >= POL:
            D -= POL 
            Kn -= POL 
        else: 
            D -= CWIERC 
            Kn -= CWIERC 
        D <<= 1
        R <<= 1
        Kn <<= 1
        Kn = shift_left_and_fill(Kn, int(input_string[input_string_counter] if input_string_counter < len(input_string) else 0))
        input_string_counter += 1

def normalizuj_kod(D, R, LN, out_list):
    POL = 1 << 7                  
    CWIERC = 1 << 6

    while R <= CWIERC:
        if D >= POL:
            out_list.append(1)
            while LN > 0:
                out_list.append(0)
                LN -= 1
            D -= POL
        elif D + R <= POL:
            out_list.append(0)
            while LN > 0:
                out_list.append(1)
                LN -= 1
        else:
            LN += 1
            D -= CWIERC 
        D <<= 1
        R <<= 1

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
    MIN_LENGTH = 2
    MAX_LENGTH = 6
    test_cases = []

    for length in range(MIN_LENGTH, MAX_LENGTH + 1):
        new_cases = [''.join(item) for item in itertools.product('01', repeat=length)]
        test_cases.extend(new_cases)

    failed_cases = []

    print(test_cases)
    for case in test_cases:
        print(type(case))
        print(f'########## case: {case} ##########')
        result, messages = test_binary_arithmetic_encoding_decoding(case)
        if case != result:
            failed_cases.append(case)
            print(f'case: {case} result: {result}')

    print(f'Succeed: {len(test_cases) - len(failed_cases)}')
    print(f'Failed: {len(failed_cases)}')

    print('Failed cases:')
    print(failed_cases)

if __name__ == '__main__':
    run_test()
    # test_binary_arithmetic_encoding_decoding('1001')
