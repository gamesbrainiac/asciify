
from PIL import Image
from math import floor
from os.path import splitext 
import sys

if len(sys.argv) < 3:
    print('expected filename and width')
    exit()

filename = sys.argv[1]

im = Image.open(filename)
original_width, original_height = im.size

if im.mode == 'RGBA': 
    # don't know what RGB values transparent pixels will have,
    # to control this, blend with an opaque single color background image
    background_color = (255, 255, 255)
    background_image = Image.new('RGBA', im.size, color=background_color + (255,))
    im = Image.alpha_composite(background_image, im)
    im.convert('RGB')


# aspect ratio of a character when its displayed 
# (they arent perfect squares like pixels)
# height / width
char_aspect = 2

# scale down to desired size (1 pixel per char)
width = int(sys.argv[2])
height = int(width * original_height / original_width / char_aspect)
downscaled = im.resize((width, height))

# convert RGB -> Luminosity
greyscale = downscaled.convert('L')

# tonemap so darkest char for min_lum
#       and lightest char for max_lum
min_lum, max_lum = greyscale.getextrema()
# min_lum, max_lum = (0, 255)

pixels = list(greyscale.getdata())

levels = ' +#'
# levels = ' .,-:+*?$#'
# levels = ' ░▒▓█'

rows = []
for y in range(height):
    char_row = []
    for x in range(width):
        luminance = pixels[x + y * width]
        
        i = floor((luminance - min_lum) / (max_lum + 1 - min_lum) * len(levels))
        
        char = levels[i]
        char_row.append(char)
    rows.append(''.join(char_row) + '\n')

basefilename, _ = splitext(filename)
outfilename = basefilename + '.txt'

with open(outfilename, 'wb') as f:
    f.writelines((row.encode('utf-8') for row in rows))
