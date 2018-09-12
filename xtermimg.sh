setterm --foreground white --background black
clear
python termimg.py $@
printf \\x1b[0m
