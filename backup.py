def integer_arithmetic_encoding(input_list):
    freq_map = calculate_freq_table(input_list)
    prob_map = calculate_integer_prob_mass(input_list)
    N = calculate_sum_of_all(input_list)
    D = int('00000000', 2)
    G = int('11111111', 2)
    LN = 0
    k = 0
    prev_element = input_list[0]
    out_list = []

    mult_factor = freq_map['0'] / N

    print('Starting integer encoding...')
    printB(D, 'D')
    printB(G, 'G')

    k = 0

    for element in input_list:
        print(f'\n>>>> iteration: {k}, Element: {element}')
        current_interval = prob_map[element]
        R = G - D + 1
        R1 = math.floor(R * mult_factor)
        print(f'R1: {R1}')
        if element == 0 or element == '0':
            G = D + R1
        else:
            D = D + R1 

        # ORG_D = D
        # D = (D + math.floor(R * current_interval[0] / N))
        # G = ORG_D + math.floor(R * current_interval[1] / N) - 1
        # print(current_interval)
        # print(R)
        # printB(D, 'D')
        # printB(G, 'G')
        D_oldest_bit = get_oldest_bit(D)
        G_oldest_bit = get_oldest_bit(G)

        while True:
            if D_oldest_bit == G_oldest_bit:
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

        # else:
            elif (D & int('11000000', 2) == int('01000000')) and (G & int('11000000', 2) == int('10000000')):
                D = (shift_left_16(D, 0) & int('01111111', 2)) | int(
                    f'{D_oldest_bit}0000000', 2)
                G = (shift_left_16(G, 1) & int('01111111', 2)) | int(
                    f'{G_oldest_bit}0000000', 2)
                LN += 1
                print('shifted D,G incremented LN')
                printB(D, 'D')
                printB(G, 'G')

            else:
                break

        # if not D_oldest_bit == G_oldest_bit:
        #     while (D & int('11000000', 2) == int('01000000', 2)) and (G & int('11000000', 2) == int('10000000', 2)):
        #         D = (shift_left_16(D, 0) & int('01111111', 2)) | int(
        #             f'{D_oldest_bit}0000000', 2)
        #         G = (shift_left_16(G, 1) & int('01111111', 2)) | int(
        #             f'{G_oldest_bit}0000000', 2)
        #         LN += 1
        #         print('shifted D,G incremented LN')
        #         printB(D, 'D')
        #         printB(G, 'G')

        k += 1
        print('>> After iteration: (D, G, LN):')
        printB(D, 'D')
        printB(G, 'G')
        # printB(LN)

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


def integer_arithmetic_decoding(input_string, prob_map, N):
    D = int('00000000', 2)
    G = int('11111111', 2)
    R = int('100000000', 2)

    mult_factor = prob_map['0'][1] / N
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
        R1 = math.floor(R * mult_factor)
        current_value = ((Kn - D + 1) * N - 1) / R

        if Kn - D < R1:
             output.append('0')
             G = D + R1
        else:
            output.append('1')
            D = D + R1

        # current_symbol = find_symbol_in_prob_map(current_value, prob_map)
        # output.append(current_symbol)
        # print(
        #     f'\n>>>> iteration: {k}, current_value={current_value}  input_counter={input_string_counter}, symbol={current_symbol}, Kn = {Kn}')
        # print('IN Kn=')
        # printB(Kn, 'Kn')

        # print(f'current symbol: {current_symbol}')
        # print(f'prob map: {prob_map}')
        # current_interval = prob_map[current_symbol]
        # ORG_D = D
        # D = (D + math.floor(R * current_interval[0] / N))
        # G = ORG_D + math.floor(R * current_interval[1] / N) - 1
        # print(current_interval)
        print(R)
        printB(D, 'D')
        printB(G, 'G')
        D_oldest_bit = get_oldest_bit(D)
        G_oldest_bit = get_oldest_bit(G)

        while D_oldest_bit == G_oldest_bit:
            Kn = shift_left_16(Kn, int(
                input_string[input_string_counter] if input_string_counter < len(input_string) else 0))
            input_string_counter += 1
            D = shift_left_16(D, 0)
            G = shift_left_16(G, 1)
            print(f'>>> OUT: {G_oldest_bit}')

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
