# -*- coding: utf-8 -*-

CLEAR = '\x1b[0m'

EMP = '\x1b[1m'
UNDERLINE = '\x1b[4m'
FLASH = '\x1b[5m'

BLACK = '\x1b[30m'
RED = '\x1b[31m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'
BLUE = '\x1b[34m'
MAGENTA = '\x1b[35m'
CYAN = '\x1b[36m'
WHITE = '\x1b[37m'

BLACK_BACK = '\x1b[40m'
RED_BACK = '\x1b[41m'
GREEN_BACK = '\x1b[42m'
YELLOW_BACK = '\x1b[43m'
BLUE_BACK = '\x1b[44m'
MAGENTA_BACK = '\x1b[45m'
CYAN_BACK = '\x1b[46m'
WHITE_BACK = '\x1b[47m'

COLORS = [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]

def strColored(s, *options):
  return reduce(lambda x,y: x + y, options, "") + s + CLEAR
