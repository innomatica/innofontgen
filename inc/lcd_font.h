/*
 * Fonts defined to realize BDF (bitmap distribution font) in embedded
 * environment, where antiliasing is not considered.
 *
 * Two types of fonts, horizontal and vertical are identical in the data
 * structure but different in meaning. There is no risk of confusion since
 * two structures will not be used in the same system.
 *
 * The horizontal format is designed to be used with TFT LCD device where
 * the LCD controller takes image data in horozintal scanning fashion.
 * Program should decode each byte of bitmap into 8 pixels from left to right.
 *
 * LCDs equipped with SED1520 controller or its equivalents, usually known as
 * dot matrix LCD are different in that each byte of data constitutes a
 * 8 pixel vertical area where each bit of the byte corresponds to one of the
 * vertically aligned pixels. Note that these dot matrix LCDs are monochromatic.
 * Thus program can send stream of byte of glyph directly without decoding.
 *
 */

#ifndef __LCD_FONT_H
#define __LCD_FONT_H

/*
 * horizontal format raster bitmap font
 *
 *	widthbytes: number of bytes allocated to each horizontal pixel line
 *	height: number of horizontal lines of the glyph
 *	startcode: start ASCII code of the glyph array
 *	endcode: end ASCII code of the glyph array
 *	glyph: glyph data has the format of
 *		(glyph width) (first line) (second line) ... (height th line)
 *		where the glyph with is one byte and each line data is widthbytes.
 */

typedef struct _horizontal_raster_font
{
	int widthbytes;
	int height;
	char startcode;
	char endcode;
	const uint8_t *glyph;
} lcd_font;

/*
 * SED1520 compatible vertical format raster bitmap font
 *
 *	heightbytes: number of bytes allocated to each vertical pixel line
 *	width: number of vertical lines of the glyph
 *	startcode: start ASCII code of the glyph array
 *	endcode: end ASCII code of the glyph array
 *	glyph: glyph data has the format of
 *		(glyph width) (first line) (second line) ... (width th line)
 *		where the glyph with is one byte and each line data is heightbytes.
 *
 */

typedef struct _vertical_raster_font
{
	int heightbytes;
	int width;
	char startcode;
	char endcode;
	const uint8_t *glyph;
} lcd_font_v;

#endif // __LCD_FONT_H
