#!/usr/bin/env python3
#
from glob import glob
import os
import numpy as np
from settings import *

#--------1---------2---------3---------4---------5---------6---------7---------8
#
# Convert a font into bdf format using otf2bdf then generate LCD font fle.
# The otf2bdf is required to be installed to run this script.
#
#   fname: source font file, otf or ttf
#   ftype: either 'horizontal' or 'vertical'
#   psize: font size in pixel unit
#   start_ch: starting ASCII code
#   end_ch: ending ASCII code
#
def generate_font_file(fname,
        ftype = DEFAULT_OUTPUT_TYPE,
        psize = DEFAULT_POINT_SIZE,
        start_ch = DEFAULT_START_CHAR,
        end_ch = DEFAULT_END_CHAR):

    # generate bdf from otf
    os.system('otf2bdf'
                + ' -p ' + str(psize)
                + ' -l ' + '\'' + str(start_ch) + '_' + str(end_ch) + '\''
                + ' -o bdfdata ' + fname)

    # open bdf data file
    try:
        f = open('bdfdata')
    except:
        print('')
        print('> Failed to open bdf file.')
        print('')
        return False

    # file version
    version = 0.0
    for line in f:
        if 'STARTFONT' in line:
            version = float(line.split(' ')[1])
            break

    if version != 2.1:
        print('')
        print('> Unsupported BDF file format')
        print('')
        return False

    # font size in point
    for line in f:
        if 'SIZE' in line:
            point_size = int(line.split(' ')[1])
            break

    # bounding box
    for line in f:
        if 'FONTBOUNDINGBOX' in line:
            fbbx, fbby, xoff, yoff = [int(x) for x in (line.split(' ')[1:])]
            break

    # family name
    for line in f:
        if 'FAMILY_NAME' in line:
            family_name = line.partition(' ')[2].strip('\n').strip('"')
            break

    # weight name
    for line in f:
        if 'WEIGHT_NAME' in line:
            weight_name = line.partition(' ')[2].strip('\n').strip('"')
            break

    # slant
    for line in f:
        if 'SLANT' in line:
            slant = line.partition(' ')[2].strip('\n').strip('"')
            break;

    # setwidth_name
    for line in f:
        if 'SETWIDTH_NAME' in line:
            setwidth_name = line.partition(' ')[2].strip('\n').strip('"')
            break;

    # addstyle_name
    for line in f:
        if 'ADD_STYLE_NAME' in line:
            addstyle_name = line.partition(' ')[2].strip('\n').strip('"')
            break;

    # pixel size
    for line in f:
        if 'PIXEL_SIZE' in line:
            pixel_size = int(line.partition(' ')[2])
            break;

    # spacing
    for line in f:
        if 'SPACING' in line:
            spacing = line.partition(' ')[2].strip('\n').strip('"')
            break;

    # skip the rest of the properties
    for line in f:
        if 'ENDPROPERTIES' in line:
            break;

    # ---------------------------------
    # decode each glyph data
    glyphdata = []
    for line in  f:
        # new character
        if 'STARTCHAR' in line:
            glyph = {}
        # character code
        if 'ENCODING' in line:
            glyph['ENCODING'] = int(line.split(' ')[1])
        # width
        elif 'DWIDTH' in line:
            glyph['DWIDTH'] = int(line.split(' ')[1])
        # bounding box
        elif 'BBX' in line:
            glyph['BBX'] = [int(x) for x in (line.split(' ')[1:])]
        # bitmap data
        elif 'BITMAP' in line:
            # read bbh lines of widthbytes bitmap data
            bitmap = []
            for line in f:
                # end of glyph data
                if 'ENDCHAR' in line:
                    glyph['BITMAP'] = bitmap
                    glyphdata.append(glyph)
                    break
                # collect bitmap data
                else:
                    bitmap.append(int(line.rstrip('\n '), 16))

    f.close()

    # we don't need bdfdata anymore
    os.system('rm -f bdfdata')

    # ---------------------------------
    if DEBUG_OUT:
        print('')
        print('version:', version)
        print('point size:', point_size)
        print('bounding box:', fbbx, fbby, xoff, yoff)
        print('family name:', family_name)
        print('weight name:', weight_name)
        print('slant:', slant)
        print('setwidth name:', setwidth_name)
        print('add style name:', addstyle_name)
        print('pixel size:', pixel_size)
        print('spacing:', spacing)
        for glyph in glyphdata:
            print('glyph: ', glyph)

    # ---------------------------------
    # prepare header string
    header = []
    header.append('/*\n')
    header.append(' * Font Information\n')
    header.append(' *\n')
    header.append(' *\tfont source: {}\n'.format(fname[fname.rfind('/')+1:]))
    header.append(' *\tfamily name: {}\n'.format(family_name))
    header.append(' *\tweight name: {}\n'.format(weight_name))
    header.append(' *\tslant: {}\n'.format(slant))
    header.append(' *\tsetwidth name: {}\n'.format(setwidth_name))
    if addstyle_name in vars():
        header.append(' *\taddstyle name: {}\n'.format(addstyle_name))
    header.append(' *\tpoint size: {}\n'.format(point_size))
    header.append(' *\tbounding box: ({},{})\n'.format(fbbx,fbby))
    header.append(' *\tdata format: {}\n'.format(ftype))
    header.append(' */\n\n')

    # ---------------------------------
    # build glyph data array
    #
    widthbytes = (fbbx + 7) // 8
    for g in glyphdata:

        hdata = []

        # aliasing
        bbw = g['BBX'][0]
        bbh = g['BBX'][1]
        dwidth = g['DWIDTH']
        bitmap = g['BITMAP']

        # x margin in pixel from the leftmost position
        px_v = -xoff + g['BBX'][2]
        # y margin in pixel from the topmost position
        px_h = fbby + yoff - g['BBX'][3] - bbh

        # actual glyph width
        hdata.append(max(dwidth, px_v + bbw))

        # fill the leading horizontal blank lines
        idx = 0
        while idx < px_h:
            for l in range(widthbytes):
                hdata.append(0)
            idx = idx + 1

        # determine the width of glyph data
        if bbw <= 8:
            k = 24
        elif bbw <= 16:
            k = 16
        elif bbw <= 24:
            k = 8
        elif bbw <= 32:
            k = 0
        else:
            print('Error: glyph data is too big. BBw = {}.\n'.format(bbw))

        # fill glyph data
        for j in range(bbh):
            # align data to the leftmost position of 32bit
            bitmap[j] = bitmap[j] << k
            # compensate leading zero columns
            bitmap[j] = bitmap[j] >> px_v

            for l in range(widthbytes):
                hdata.append((bitmap[j]>>(8*(3-l))) & 0xff)

            idx = idx + 1

        # fill trailing zero
        while idx < fbby:
            for l in range(widthbytes):
                hdata.append(0)
            idx = idx + 1

        # attach to the glyph dictionary
        g['HDATA'] = hdata

    # ---------------------------------
    # horizontal format glyph data
    #
    if ftype == 'horizontal':

        # build font filename
        fname = family_name + ' ' + weight_name
        if slant == 'I':
            fname = fname + ' Italic'
        if addstyle_name != '':
            fname = fname + ' ' + addstyle_name
        fname = fname.replace(' ', '_')
        fname = fname + '_' + str(point_size)

        # create output directory if necessary
        if not os.path.exists(DEFAULT_OUTPUT_DIR):
            os.makedirs(DEFAULT_OUTPUT_DIR)

        f = open(DEFAULT_OUTPUT_DIR + '/' + fname + '.h', 'w')

        # augment header
        header.append('#ifndef __{}_H_\n'.format(fname.upper()))
        header.append('#define __{}_H_\n\n'.format(fname.upper()))
        header.append('#include "lcd_font.h"\n\n')
        header.append('const uint8_t {}[] =\n'.format(fname.lower() + '_glyph'))
        header.append('{\n')

        # write header part
        f.writelines(header)

        code = start_ch
        for g in glyphdata:
            data = g['HDATA']
            f.write('\t')
            for x in data:
                f.write('0x{:02x},'.format(x))
            f.write(' // \'{:c}\'\n'.format(code))
            code = code + 1

        f.write('};\n\n')
        f.write('lcd_font {} = \n'.format(fname))
        f.write('{\n')
        f.write('\t{},\n'.format(widthbytes))
        f.write('\t{},\n'.format(fbby))
        f.write('\t\'{:c}\',\n'.format(start_ch))
        f.write('\t\'{:c}\',\n'.format(end_ch))
        f.write('\t{},\n'.format(fname.lower() + '_glyph'))
        f.write('};\n\n')
        f.write('#endif // __{}_H_'.format(fname.upper()))

        f.close()

    # ---------------------------------
    # vertical format glyph data for Epson SED 1520 compatible controller
    # font data array should be rotated
    else:

        heightbytes = (fbby + 7) // 8
        if heightbytes > 4:
            print('The font size is too big... Exiting...\n')
            return;

        for g in glyphdata:
            # skip the glyph width byte
            hdata = g['HDATA'][1:]

            # create numpy array of size: (heightbytes*8, widthbytes*8)
            # note that the sizes of axis must be multiple of 8 in both axes
            npbmp = np.zeros((heightbytes*8, widthbytes*8), dtype = np.bool)
            # top area must be filled with blank data
            offset = npbmp.shape[0] - fbby

            # idx1 is glyph height
            for idx1 in range(fbby):
                for idx2 in range(widthbytes):
                    for idx3 in range(8):
                        npbmp[idx1 + offset, idx2*8 + idx3] = (
                                hdata[idx1*widthbytes + idx2] & 1<<(7-idx3)
                                == 1<<(7-idx3))

            # now collect data vertically
            vdata = []
            # glyph width must be the same
            vdata.append(g['HDATA'][0])

            for idx1 in range(fbbx):
                for idx2 in range(heightbytes):
                    x = 0
                    for idx3 in range(8):
                        if npbmp[idx2 * 8 + idx3,idx1]:
                            x = x +  (1<<(idx3))

                    vdata.append(x)

            g['VDATA'] = vdata

        # now ready to write file

        # build font filename
        fname = family_name + ' ' + weight_name
        if slant == 'I':
            fname = fname + ' Italic'
        if addstyle_name != '':
            fname = fname + ' ' + addstyle_name
        fname = fname.replace(' ', '_')
        fname = fname + '_' + str(point_size) + 'V'

        f = open(DEFAULT_OUTPUT_DIR + '/' + fname + '.h', 'w')

        # augment header
        header.append('#ifndef __{}_H_\n'.format(fname.upper()))
        header.append('#define __{}_H_\n\n'.format(fname.upper()))
        header.append('#include "lcd_font.h"\n\n')
        header.append('const uint8_t {}[] =\n'.format(fname.lower() + '_glyph'))
        header.append('{\n')

        # write header part
        f.writelines(header)

        code = start_ch
        for g in glyphdata:
            data = g['VDATA']
            f.write('\t')
            for x in data:
                f.write('0x{:02x},'.format(x))
            f.write(' // \'{:c}\'\n'.format(code))
            code = code + 1

        f.write('};\n\n')
        f.write('lcd_font_v {} = \n'.format(fname))
        f.write('{\n')
        f.write('\t{},\n'.format(heightbytes))
        f.write('\t{},\n'.format(fbbx))
        f.write('\t\'{:c}\',\n'.format(start_ch))
        f.write('\t\'{:c}\',\n'.format(end_ch))
        f.write('\t{},\n'.format(fname.lower() + '_glyph'))
        f.write('};\n\n')
        f.write('#endif // __{}_H_'.format(fname.upper()))

        f.close()

#--------1---------2---------3---------4---------5---------6---------7---------8
if __name__ == '__main__':

    # enumerate the font files in the FONT_DIR
    flist = glob(DEFAULT_FONT_DIR + '/*.ttf')
    flist.extend(glob(DEFAULT_FONT_DIR + '/*.otf'))

    if len(flist) == 0:
        print('')
        print('> No font file (otf,ttf) found in ', DEFAULT_FONT_DIR)
        print('> Copy font file of your choice into the folder.')
        print('')
    else:
        # convert each font into lcd font with default setting
        for f in flist :
            generate_font_file(f)

#--------1---------2---------3---------4---------5---------6---------7---------8
