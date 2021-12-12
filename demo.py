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
    frequency_table = {key: value for key, value in zip(bin_edges[0:256], hist)}
    print(frequency_table)
    # plt.plot(np.arange(0, 256), frequency_table)
    

