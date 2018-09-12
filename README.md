# termimg (a quick-and-dirty script)
print images to STDOUT via pointillism

# motivation
just a fun little script to play with

# requires
- Python 2.7

- [the Python Imaging Library (PIL)](http://pythonware.com/products/pil/) for Python 2.7

# supports
- ANSI foreground/background in RGB

- reversible intensity in ASCII

# examples
`python termimg.py examples/original.png`

![](examples/ascii.png?raw=true)

`python termimg.py examples/original.png -c`

![](examples/ascii-colorless.png?raw=true)

`python termimg.py examples/original.png -i`

![](examples/ascii-reverse-intensity.png?raw=true)

`python termimg.py examples/original.png -l`

![](examples/ascii-rotated-left-90-degrees.png?raw=true)

`python termimg.py examples/original.png -b`

![](examples/background-only.png?raw=true)

`python termimg.py examples/original.png -br`

![](examples/background-only-rough.png?raw=true)

# help

    print an image's ANSI and/or ASCII equivalent to STDOUT
    Usage: python termimg.py PATH [OPTIONS] [WIDTH [PERCENT_ROWS]]
    PATH
    	a path to an image or directory
    OPTIONS
  	  -b, --background	exclusively use background colors
  	  -c, --colorless	colorless
  	  -f, --horizontal	horizontal (mnemonic is f(lat))
	    -h, --help	display this text and exit
	    -i, --intensify-light	reverse intensity
	    	default behavior intensifies darker colors
	    -l, --rotate-left-90	rotate left 90 degrees
	    -r, --rough	rough processing
  	  	don't average values for resized output
  	  -v, --vertical	vertical
    WIDTH
	    the maximum desired width in characters
	    a value of zero uses the image width
	    the default value is 79
    PERCENT_ROWS
	    the percentage of rows to actually include
	    this is useful because character formatting isn't perfectly square or grid-like
	    the default (and recommended) value is 50
