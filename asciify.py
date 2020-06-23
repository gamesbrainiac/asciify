
import argparse
from PIL import Image
from math import floor, ceil
import os

parser = argparse.ArgumentParser(description='convert an image to ascii art')
parser.add_argument('source', 
    help='path to the source image')
parser.add_argument('width', 
    type=int, 
    help='output width in characters')
parser.add_argument('-i', '--invert', 
    action='store_true', 
    help=(
        'invert colors to look right for black text on a white background. '
        'by default looks correct for white text on a black background'))

parser.add_argument('-s', '--save', 
    dest='output_path', 
    metavar='PATH', 
    nargs='?',
    action='store',
    const='',
    default=None,
    help=(
        'write the result to a file, rather than stdout. '
        'if no path is specified, `source` is used, but with the `.txt` extension'))

args = parser.parse_args()
source_path = args.source

im = Image.open(source_path)
original_width, original_height = im.size

if im.mode == 'RGBA': 
    # don't know what RGB values transparent pixels will have,
    # to control this, blend with an opaque single color background image
    background_color = (255, 255, 255) if args.invert else (0, 0, 0)
    background_image = Image.new('RGBA', im.size, color=background_color + (255,))
    im = Image.alpha_composite(background_image, im)
    im.convert('RGB')


# aspect ratio of a character when its displayed 
# (they aren't perfect squares like pixels)
# height / width
# char_aspect = 2

# samples per pixel
horiz_samples = 2
vert_samples = 4

# scale down to desired size
pixels_across = args.width
subpixel_width = original_width / (pixels_across * horiz_samples)
pixels_down = original_height / (subpixel_width * vert_samples) # may not be an integer

downscaled = im.resize(
    (int(pixels_across * horiz_samples), 
     int(pixels_down * vert_samples)))

pixels_down = ceil(pixels_down)

# convert RGB -> Luminosity
greyscale = downscaled.convert('L')

# tonemap so darkest char for min_lum
#       and lightest char for max_lum
min_lum, max_lum = greyscale.getextrema()

pixels = list(greyscale.getdata())

# levels = ' +#'
# levels = ' .,-:+*?$#'
# levels = ' ░▒▓█'

base_code = 0x2800

# if args.invert:  # TODO: make it work
#     levels = levels[::-1]

rows = []
for y in range(pixels_down):
    char_row = [] 
    for x in range(pixels_across):
        
        samples = 0
        for dx in range(horiz_samples):
            for dy in range(vert_samples):
                i = (x * horiz_samples + dx + 
                    (y * vert_samples + dy) * pixels_across * horiz_samples)
                
                if i < len(pixels):
                    luminance = pixels[i]
                    bit = round((luminance - min_lum) / (max_lum - min_lum))
                else:
                    # off the edge - just output black
                    bit = 0

                if args.invert:
                    bit = 1 - bit

                # 0 3
                # 1 4
                # 2 5
                # 6 7
                samples |= bit << (dx * 3 + dy if dy < 3 else dx + 6)
        
        char = chr(base_code + samples)
        char_row.append(char)
    rows.append(''.join(char_row))

if args.output_path is None:
    for row in rows:
        print(row)

else:
    output_path = args.output_path
    if output_path == '':
        base_path, _ = os.path.splitext(source_path)
        output_path = base_path + '.txt'
    
    with open(output_path, 'wb') as f:
        f.writelines((row + os.linesep).encode('utf-8') for row in rows)
    
    print(f'saved to {output_path}')
