# testgen.py
# (C) John Warburton 2020
# GPL 3

# Generates test patterns, using YUV origination wherever possible

import numpy


class Yuv4Mpeg:
    def __init__(self, width=1920, height=1080, rate='30:1', interlace='p', aspect='1:1', colorspace='444p10'):
        self.headertext = 'YUV4MPEG2 ' + \
            'W' + str(width) + ' ' + \
            'H' + str(height) + ' ' + \
            'F' + rate + ' ' + \
            'I' + interlace + ' ' + \
            'A' + aspect + ' ' + \
            'C' + colorspace + '\n'
        # This needs to be bytes, not a string, because the output is pure binary data, though
        # it is human-readable.
        self.header = self.headertext.encode()

    def appendframe(self, inputframe):
        # input is the aYCrCb array, [3 x channels, w, h]
        # File format is little-endian 16-bit hex encoding
        # Data flows without newlines
        # ONLY AFTER "FRAME" is 0x0a
        # File must end with 0x0a

        # This changes the data to little-endian, then produces a bytearray from it.
        # The bytearray can be handled like a string, though Python treats it differently
        # from a string to prevent issues with non-transparency further down the process.

        pixelslist = b'FRAME' + b'\n' + bytearray(inputframe.flatten())

        # NO! It's pure binary data, not hexadecimal. Confusion.

        # stringsofpixels = [("{:04x}".format(int)[2:]+"{:04x}".format(int)[:2]) for int in pixelslist]
        stringsofhex = self.header + pixelslist + b'\n'

        return stringsofhex


class Colors100:

    grey =     {'Y': 502, 'Cb': 512, 'Cr': 512}
    white =    {'Y': 940, 'Cb': 512, 'Cr': 512}
    yellow =   {'Y': 877, 'Cb': 64,  'Cr': 553}
    cyan =     {'Y': 754, 'Cb': 615, 'Cr': 64 }
    green =    {'Y': 691, 'Cb': 167, 'Cr': 105}
    magenta =  {'Y': 313, 'Cb': 857, 'Cr': 919}
    red =      {'Y': 250, 'Cb': 409, 'Cr': 960}
    blue =     {'Y': 127, 'Cb': 960, 'Cr': 471}
    black =    {'Y': 64,  'Cb': 512, 'Cr': 512}


class YUVpic:

    def __init__(self, x=1920, y=1080):
        black = 64
        neutral = 540
        # The number 4 is for the three planes plus an alpha value
        # The planes will always by Y, U, V, in that order

        self.pic = numpy.zeros((3, y, x), dtype=numpy.int16)
        # Setup the picture as filled with video black
        self.pic[0].fill(black)
        self.pic[1].fill(neutral)
        self.pic[2].fill(neutral)
        self.x = x
        self.y = x


def addBWramp(yuvpic, xstart, xlen, ystart, ylen):

    for line in range(ystart, ystart+ylen):
        for horiz in range(xstart, xstart + xlen):
            yuvpic.itemset((0, line, horiz), (((horiz - xstart) / xlen) *
                                              (Colors100.white['Y'] - Colors100.black['Y']) +
                                              Colors100.black['Y']))
            yuvpic.itemset((1, line, horiz), Colors100.white['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.white['Cr'])
    return yuvpic

def safeareas(yuvpic):
    ebuCapHoriz = 0.05
    ebuCapVert = 0.05
    ebuActHoriz = 0.035
    ebuActVert = 0.035
    
    # Get the dimensions of the pic: safe areas are in %
    shape = yuvpic.shape
    y = shape[1]
    x = shape[2]
    
    # Calculate exactly where the safe boundaries are
    topCapLine = int(y * ebuCapVert)
    bottomCapLine = y - int(y * ebuCapVert)
    leftCapLine = int(x * ebuCapHoriz)
    rightCapLine = x - int(x * ebuCapHoriz)
    topActLine = int(y * ebuActVert)
    bottomActLine = y - int(y * ebuActVert)
    leftActLine = int(x * ebuActVert)
    rightActLine = x - int(x * ebuActVert)

    for pixel in range(leftCapLine, rightCapLine):
        yuvpic.itemset((0, topCapLine, pixel), Colors100.red['Y'])
        yuvpic.itemset((1, topCapLine, pixel), Colors100.red['Cb'])
        yuvpic.itemset((2, topCapLine, pixel), Colors100.red['Cr'])

    for pixel in range(leftCapLine, rightCapLine):
        yuvpic.itemset((0, bottomCapLine, pixel), Colors100.red['Y'])
        yuvpic.itemset((1, bottomCapLine, pixel), Colors100.red['Cb'])
        yuvpic.itemset((2, bottomCapLine, pixel), Colors100.red['Cr'])

    for pixel in range(topCapLine, bottomCapLine):
        yuvpic.itemset((0, pixel, leftCapLine), Colors100.red['Y'])
        yuvpic.itemset((1, pixel, leftCapLine), Colors100.red['Cb'])
        yuvpic.itemset((2, pixel, leftCapLine), Colors100.red['Cr'])

    for pixel in range(topCapLine, bottomCapLine):
        yuvpic.itemset((0, pixel, rightCapLine), Colors100.red['Y'])
        yuvpic.itemset((1, pixel, rightCapLine), Colors100.red['Cb'])
        yuvpic.itemset((2, pixel, rightCapLine), Colors100.red['Cr'])

    for pixel in range(leftActLine, rightActLine):
        yuvpic.itemset((0, topActLine, pixel), Colors100.green['Y'])
        yuvpic.itemset((1, topActLine, pixel), Colors100.green['Cb'])
        yuvpic.itemset((2, topActLine, pixel), Colors100.green['Cr'])

    for pixel in range(leftActLine, rightActLine):
        yuvpic.itemset((0, bottomActLine, pixel), Colors100.green['Y'])
        yuvpic.itemset((1, bottomActLine, pixel), Colors100.green['Cb'])
        yuvpic.itemset((2, bottomActLine, pixel), Colors100.green['Cr'])

    for pixel in range(topActLine, bottomActLine):
        yuvpic.itemset((0, pixel, leftActLine), Colors100.green['Y'])
        yuvpic.itemset((1, pixel, leftActLine), Colors100.green['Cb'])
        yuvpic.itemset((2, pixel, leftActLine), Colors100.green['Cr'])

    for pixel in range(topActLine, bottomActLine):
        yuvpic.itemset((0, pixel, rightActLine), Colors100.green['Y'])
        yuvpic.itemset((1, pixel, rightActLine), Colors100.green['Cb'])
        yuvpic.itemset((2, pixel, rightActLine), Colors100.green['Cr'])

    return yuvpic

def addHorizontalBars(yuvpic, xstart, xlen, ystart, ylen):
    # There are ten bars
    barWidth = int(xlen/10)
    for line in range(ystart, ystart+ylen):
        for horiz in range(xstart, xstart + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.grey['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.grey['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.grey['Cr'])

        for horiz in range(xstart + barWidth*1, xstart + barWidth*1 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.white['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.white['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.white['Cr'])

        for horiz in range(xstart + barWidth*2, xstart + barWidth*2 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.yellow['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.yellow['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.yellow['Cr'])

        for horiz in range(xstart + barWidth*3, xstart + barWidth*3 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.cyan['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.cyan['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.cyan['Cr'])

        for horiz in range(xstart + barWidth*4, xstart + barWidth*4 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.green['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.green['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.green['Cr'])

        for horiz in range(xstart + barWidth*5, xstart + barWidth*5 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.magenta['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.magenta['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.magenta['Cr'])

        for horiz in range(xstart + barWidth*6, xstart + barWidth*6 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.red['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.red['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.red['Cr'])

        for horiz in range(xstart + barWidth*7, xstart + barWidth*7 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.blue['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.blue['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.blue['Cr'])

        for horiz in range(xstart + barWidth*8, xstart + barWidth*8 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.black['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.black['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.black['Cr'])

        for horiz in range(xstart + barWidth*9, xstart + barWidth*9 + barWidth):
            yuvpic.itemset((0, line, horiz), Colors100.grey['Y'])
            yuvpic.itemset((1, line, horiz), Colors100.grey['Cb'])
            yuvpic.itemset((2, line, horiz), Colors100.grey['Cr'])

    return(yuvpic)


picture = YUVpic(x=1920, y=1080)
print(picture.pic.size)

bars = addHorizontalBars(picture.pic, 0, 1920, 0, 1080)
ramp = addBWramp(bars, 0, 1920, 400, 200)
capt = safeareas(ramp)

start = Yuv4Mpeg(rate="25:1")

ll = start.appendframe(capt)

print()
with open('output.y4m', 'wb') as writer:
    writer.write(ll)
