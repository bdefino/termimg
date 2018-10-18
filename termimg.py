# Copyright (C) 2018 Bailey Defino
# <https://bdefino.github.io>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__doc__ = """print an image's ANSI and/or ASCII equivalent to STDOUT"""

from PIL import Image
import os
import random
import signal
import sys

global INTENSITY_TO_ASCII # a rough order of ASCII by intensity
INTENSITY_TO_ASCII = ['#', '&', '@', '$', '%', 'Z', 'Y', 'X', 'W', 'V', 'U',
    'T', 'S', 'R', 'Q', 'P', 'O', 'N', 'M', 'L', 'K', 'J', 'I', 'H', 'G',
    'F', 'E', 'D', 'C', 'B', 'A', '@', '9', '8', '7', '6', '5', '4', '3',
    '2', '1', '0', 'z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p',
    'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b',
    'a', '}', '{', ']', '[', ')', '(', '?', '=', '>', '<', '|', '\\', '/',
    '+', '*', '!', ';', ':', '^', '~', '"', '_', "'", ',', '-', '.', '`', ' ']

global NEWLINE
NEWLINE = '\n'

if os.name == "nt":
    NEWLINE = "\r\n"

def ansi_colorize(s, codes = None, bg = False):
    """wrap s with RGB ANSI color codes"""
    if not codes:
        codes = []
    
    if isinstance(codes, int):
        codes = eight_bit_to_rgb(codes)
    codes = [str(c) for c in codes[:3]]
    reset = 39
    set = 38

    if bg:
        reset = 49
        set = 48
    return "\x1b[%s;2;%sm%s\x1b[%sm" % (
        str(set), ';'.join(codes), s, str(reset))

def _default_signal_handler(sig, _sf):
    """force ANSI reset then exit"""
    print "\x1b[39;49m"
    sys.stdout.flush()
    sys.exit(1)

def eight_bit_to_rgb(col):
    """convert an 8-bit color to RGB"""
    return col >> 5, col & int("0c", 16) >> 2, col & int("03", 16)

def _help():
    """print help information"""
    print "print an image's ANSI and/or ASCII equivalent to STDOUT\n" \
          "Usage: python termimg.py PATH [OPTIONS] [WIDTH [PERCENT_ROWS]]\n" \
          "PATH\n" \
          "\ta path to an image or directory\n" \
          "OPTIONS\n" \
          "\t-b, --background\texclusively use background colors\n" \
          "\t-c, --colorless\tcolorless\n" \
          "\t-f, --horizontal\thorizontal (mnemonic is f(lat))\n" \
          "\t-h, --help\tdisplay this text and exit\n" \
          "\t-i, --intensify-light\treverse intensity\n" \
          "\t\tdefault behavior intensifies darker colors\n" \
          "\t-l, --rotate-left-90\trotate left 90 degrees\n" \
          "\t-r, --rough\trough processing\n" \
          "\t\tdon't average values for resized output\n" \
          "\t-v, --vertical\tvertical\n" \
          "WIDTH\n" \
          "\tthe maximum desired width in characters\n" \
          "\ta value of zero uses the image width\n" \
          "\tthe default value is 79\n" \
          "PERCENT_ROWS\n" \
          "\tthe percentage of rows to actually include\n" \
          "\tthis is useful because character formatting isn't perfectly" \
          " square or grid-like\n" \
          "\tthe default (and recommended) value is 50"

def mean_pixel(pixels, row, col, nrows, ncols, size):
    """
    return the mean pixel in box from
    from (col, row) to (col + ncols - 1, row + nrows - 1), inclusive
    """
    mean = pixels[col, row]

    if isinstance(mean, int):
        mean = 0
    else:
        mean = [0 for e in mean]
    ncols = min((col + ncols, size[0])) - col
    nrows = min((row + nrows, size[1])) - row

    for r in range(row, row + nrows):
        for c in range(col, col + ncols):
            p = pixels[c, r]
            
            if isinstance(p, int):
                mean += p
            else:
                for i in range(len(p)):
                    mean[i] += p[i]

    if isinstance(mean, int):
        mean /= ncols * nrows
    else:
        mean = [e / (ncols * nrows) for e in mean]
    return mean

def termimg(img, bg = False, colorize = True, intensify_light = False,
        width = 0, percent_rows = 100, rough = False, rotateleft90 = False):
    """
    return an ASCII and/or ANSI version of the image
    note that specifying bg also specifies colorize
    """
    if bg:
        colorize = True
    _width = width
    
    if width <= 0:
        width = img.size[0]
    colstep = img.size[0] / width
    matrix = []
    pixels = img.load()
    rowstep = int(100.0 / percent_rows * colstep)

    if rotateleft90:
        if _width <= 0:
            width = img.size[1]
        rowstep = img.size[1] / width
        colstep = int(100.0 / percent_rows * rowstep)
    
    for r in range(0, img.size[1], rowstep):
        matrix.append([])

        for c in range(0, img.size[0], colstep):
            ascii = ' '
            pixel = pixels[c, r]

            if not rough:
                pixel = mean_pixel(pixels, r, c, rowstep, colstep, img.size)

            if not bg:
                mean_color = pixel

                if not isinstance(pixel, int):
                    mean_color = sum(pixel) / len(pixel)
                intensity = mean_color * len(INTENSITY_TO_ASCII) / 256

                if intensify_light:
                    intensity = len(INTENSITY_TO_ASCII) - intensity - 1
                ascii = INTENSITY_TO_ASCII[intensity]
            
            if colorize:
                ascii = ansi_colorize(ascii, pixel, bg)
            matrix[-1].append(ascii)
    del pixels

    if rotateleft90:
        _matrix = matrix
        matrix = []

        for c in range(len(_matrix[0])):
            matrix.append([])
            
            for r in range(len(_matrix)):
                matrix[-1].append(_matrix[r][c])
        matrix.reverse()
        del _matrix
    return NEWLINE.join(("".join(l) for l in matrix))

if __name__ == "__main__" and len(sys.argv) > 1:
    for sig in (signal.SIGABRT, signal.SIGHUP, signal.SIGINT, signal.SIGQUIT,
            signal.SIGTERM):
        signal.signal(sig, _default_signal_handler)
    bg = False
    colorize = True
    horizontal = False
    intensify_light = False
    percent_rows = 50
    rotateleft90 = False
    rough = False
    vertical = False
    width = 79

    for i in range(len(sys.argv) - 1, -1, -1):
        arg = sys.argv[i]
        
        if arg.startswith("--"):
            arg = arg[2:]

            if arg == "background":
                bg = True
            elif arg == "help":
                _help()
                sys.exit()
            elif arg == "horizontal":
                horizontal = True
            elif arg == "intensify-light":
                intensify_light = True
            elif arg == "nocolor":
                colorize = False
            elif arg == "rotate-left-90":
                rotateleft90 = True
            elif arg == "rough":
                rough = True
            elif arg == "vertical":
                vertical = True
            sys.argv.pop(i)
        elif arg.startswith('-'):
            for c in arg[1:]:
                if c == 'b':
                    bg = True
                elif c == 'c':
                    colorize = False
                elif c == 'f':
                    horizontal = False
                elif c == 'h':
                    _help()
                    sys.exit()
                elif c == 'i':
                    intensify_light = True
                elif c == 'l':
                    rotateleft90 = True
                elif c == 'r':
                    rough = True
                elif c == 'v':
                    vertical = True
            sys.argv.pop(i)
    
    if len(sys.argv) > 2:
        try:
            width = int(sys.argv[2])
        except:
            print "WIDTH argument must be an integer."
            _help()
            sys.exit()

        if len(sys.argv) > 3:
            try:
                percent_rows = int(sys.argv[3])
            except:
                print "PERCENT_ROWS argument must be an integer."
                _help()
                sys.exit()
    elif not len(sys.argv) or not os.path.exists(sys.argv[1]):
        print "PATH argument is required."
        _help()
        sys.exit()
        

    if os.path.isdir(sys.argv[1]):
        for r, ds, fs in os.walk(sys.argv[1]):
            for f in fs:
                p = os.path.join(r, f)

                try:
                    img = Image.open(p)
                    _w = width

                    if horizontal or vertical:
                        rotateleft90 = False
                        
                        if ((horizontal and img.size[0] < img.size[1])
                                or (vertical and img.size[0] > img.size[1])):
                            rotateleft90 = True

                    if width <= 0:
                        _w = img.size[0]
                    print termimg(img, bg, colorize, intensify_light, _w,
                        percent_rows, rough, rotateleft90)
                    img.close()
                except KeyboardInterrupt:
                    raise KeyboardInterrupt()
                except SystemExit:
                    raise SystemExit()
                except:
                    pass
    else:
        img = Image.open(sys.argv[1])
        _w = width

        if horizontal or vertical:
            rotateleft90 = False
            
            if ((horizontal and img.size[0] < img.size[1])
                    or (vertical and img.size[0] > img.size[1])):
                rotateleft90 = True

        if width <= 0:
            _w = img.size[0]
        print termimg(img, bg, colorize, intensify_light, width, percent_rows,
            rough, rotateleft90)
        img.close()
else:
    _help()
