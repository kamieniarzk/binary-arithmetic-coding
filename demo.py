import numpy

def read_pgm(pgmf):
    """Return a raster of integers from a PGM as a list of lists."""
    assert pgmf.readline() == 'P5\n'
    (width, height) = [int(i) for i in pgmf.readline().split()]
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
    pgm = read_pgm(f)

# hist, bin_edges = numpy.histogram(a=im,
#                                   bins=range(0, 257))
# frequency_table = {key: value for key, value in zip(bin_edges[0:256], hist)}