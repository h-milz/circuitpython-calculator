# SPDX-FileCopyrightText: 2024 Harald Milz <hm@seneca.muc.de> (https://github.com/h-milz/circuitpython-calculator)
#
# SPDX-License-Identifier: MIT


from os import uname
from gc import mem_free, collect
from re import sub
# import sys
import adafruit_ili9341
import adafruit_imageload
# from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_pcf8523.pcf8523 import PCF8523
import board
import busio
import sdcardio
import storage
import terminalio
import displayio
import fourwire
import analogio
import tsc2004
from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
import neopixel
import time
from supervisor import runtime
from keymap import *
from umath import *        # all these wrapper functions
# from plot import plot

runtime.autoreload = False           # otherwise the thing reboots then and again. 

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)
neopix_pin = board.D11
pixels = neopixel.NeoPixel(neopix_pin, 1, brightness=0.05)
pixels[0] = OFF


# Release any resources currently in use for the displays
displayio.release_displays()

# Use Hardware SPI
spi = board.SPI()

# initialize and mount sd card
# TODO Does not mount: "no SD card"
cs = board.D5
'''
try:
    sdcard = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    print 
except Exception as e:
    raise e
    pass
'''

# initialize display
display_bus = fourwire.FourWire(spi, chip_select=board.D9, command=board.D10)
display_width = 320
display_height = 240
display = adafruit_ili9341.ILI9341(display_bus, width=display_width, height=display_height)

# initialize i2c, keyboard, touch, and RTC
i2c = board.I2C()

kbd = BBQ10Keyboard(i2c)
# seems the kbd needs a short time to settle. 
time.sleep(0.1)
kbd.backlight = 0.2
# kbd.report_mods = True
tsc = tsc2004.TSC2004(i2c)
rtc = PCF8523(i2c)

ps1 = ">>> "     # this should be sys.ps1 but it seems not available. 
ps2 = "... "
prompt = ps1
# command = ""
command = []        # let's use a list here. Easier for insert and delete 
cursor = 0
mod_sym = 0
historyfile = "/history.txt" 
historylist = []
historyptr = 0
oldcommand = ""
ans = ""            # Casio-like ANS string
in_compound_statement = False
compound_statement = ""

usbpin = analogio.AnalogIn(board.A2)
batpin = analogio.AnalogIn(board.VOLTAGE_MONITOR)
FULL = 2
WARN = 1
EMPTY = 0
batstat = FULL


clear_display = '\033[2J'
ceol = '\033[K'    # clear to end of line 
move_cursor_left = '\033[1D'


def stifle(lst, n):
    '''
    shortens a list to the last n entries. The top ones are discarded. 
    '''
    if len(lst) <= n:
        return lst
    else:
        return lst[-n:]


def history(cmd, hlist):
    '''
    appends the last command to the historylist and writes it to the history file. 
    '''
    if cmd == '':                        # if the cmd is empty, do nothing.  
        return hlist
    try:
        # appending works only when the USB cable is not attached. 
        with open(historyfile, "a") as file:
            file.write("{}\r\n".format(cmd))
            file.flush()
    except OSError as e:
        # for example if none is available. Maybe we should inform the user. 
        # tprint ("\r\n{}\r\n".format(e)) 
        pass
    # print ("history: cmd {} is {}".format(cmd,type(cmd)))
    hlist.append(cmd)
    hlist = stifle(hlist, 100)
    return hlist


def is_statement(cmd):
    # https://docs.python.org/3/reference/compound_stmts.html 
    # check if cmd begins with one of these keywords: 
    # this is for simple single-line statements like
    # for i in range(10): print("sqr({}) = {}".format(i, i*i)) 
    # create value tables and such.  
    # statement must end with an empty line. The ... prompt is required here too. 
    keywords = ("for", "while", "if", "try")
    if any(cmd.startswith(keyword) for keyword in keywords):
        return True    
    # or if it is a variable assignment
    if "=" in cmd:
        return True
    # otherwise we probably have an expression like "5*8". 
    return False


def is_compound_statement(cmd):
    keywords = ("for", "while", "if", "try")
    if any(cmd.startswith(keyword) for keyword in keywords) and cmd.endswith(":"):
        return True    
    # in this case we can potentially run true multiline statements with the "..." prompt. 
    # like in real Python, and empty line ends the statement. 
    # i.e. write all statements to a temporary file and then open and read it like this: 
    '''
    # Open the text file containing the Python program
    with open("program.py", "r") as file:
        python_code = file.read()

    # Execute the Python program
    exec(python_code)
    '''
    # this way, we can also execute short programs residing on the SD card, like a solution library. 
    

def replace_stmt(match):
    string = match.group(0)
    return 'l{}'.format(string)


def process(cmd):
    ''' 
    takes a command string and feeds it in either exec or eval, depending if it's 
    a statement or an expression. Errors are trapped and returned to the user. 
    '''
    '''
    in compound statements, do we have ints or Decimals? 
    print does not print to the screen.  
    '''
    # TODO exec and eval should only allow a specific set of keywords. 

    try:
        if is_compound_statement(cmd):
            # print ("process: exec cmpnd cmd = {}".format(cmd))
            cmd = sub(r'print', replace_stmt, cmd)
            exec(cmd)
            return None
        if is_statement(cmd):
            # print ("process: exec cmd = {}".format(cmd))
            exec(cmd)   
            return None
        else:
            # print ("process: eval cmd = {}".format(cmd))
            result = eval(cmd)
            return result
    # since we don't know which exceptions are due, we just catch them all. 
    except Exception as e:
        return e


def tprint(line):
    print(line, file=myterm, end="")


def lprint(line):
    tprint("\n\r{}".format(line))    

    
def update_status(status):
    collect()
    mmax = 37321 # 4.2V                     # strange that RP2040 and M4 have different values. 
    mmin = 30212 # 3.4V proportional von 4.2 
    bat = 100 * (batpin.value - mmin) / (mmax - mmin)   # percentage. 3.4V = 0%, 4.2V = 100%. BAT is connected via a ~50% resistor divider.
    bat = bat if bat <= 100.0 else 100.0        # clamp to 100
    free = mem_free() // 1024
    time = date()
    status.text = f"{free}K free    {bat:.1f}%    {time} "
    # set Neopixel according to bat status. 
    # with a small 2% hysteresis
    if bat < 10 and batstat != EMPTY:
        batstat = EMPTY
        pixels[0] = RED
    elif 12 < bat < 20 and batstat != WARN:
        batstat = WARN
        pixels[0] = YELLOW
    else: # if bat > 22 and batstat != FULL:
        batstat = FULL
        pixels[0] = OFF



def date(d=None):
    if d == None:   # get date
        t = rtc.datetime
        return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d} {t.tm_hour:02d}:{t.tm_min:02d}"
    else:           # set date YYYY-MM-DD HH:MM
        _date, _time = d.split()
        year, month, day = _date.split('-')
        hour, minute = _time.split(':')
        t = time.struct_time((int(year), int(month), int(day), int(hour), int(minute), 0, 1, -1, -1))
        rtc.datetime = t
        return None
    

def inv(c):
    # invert a single character by shifting it to the upper half of the character table
    # ASCII 96 = 0x60
    return chr(ord(c) + 96)


# initialize display layout

myfont = terminalio.FONT
# terminalio works only with the builtin font :-( 
# myfont = bitmap_font.load_font("/fonts/myfont.bdf")

root = displayio.Group()

# the main terminal window
term = displayio.Group()
fontx, fonty = myfont.get_bounding_box()
term_palette = displayio.Palette(2)
term_palette[0] = 0x000000
term_palette[1] = 0xffffff
termbox = displayio.TileGrid(myfont.bitmap, 
                             x=0, 
                             y=fonty, 
                             width=display.width // fontx,
                             height=(display.height-fonty) // fonty,
                             tile_width=fontx,
                             tile_height=fonty,
                             pixel_shader=term_palette)
term.append(termbox)
myterm = terminalio.Terminal(termbox, myfont)
root.append(term)

# the logo window top left
logo = displayio.Group()
# Load the blinka12 bitmap
sprite = displayio.OnDiskBitmap("/bitmaps/blinka12.bmp")
# Create a sprite (tilegrid)
logobox = displayio.TileGrid(sprite, pixel_shader=sprite.pixel_shader)
# Add the sprite to the Group
logo.append(logobox)
# Set sprite location
logo.x = 0
logo.y = 0
root.append(logo)

# status line
text = "Hello World!" + " "*38
color = 0xFFFFFF
status = label.Label(myfont, text=text, color=color)
status.anchor_point = (0,0)
status.anchored_position = (2 * sprite.width, 0)
root.append(status)

display.root_group = root

# print greeting and init prompt. 
(sysname, nodename, release, version, machine) = uname()

# open on-disk history file and feed it into the historylist
try:
    with open(historyfile, "r") as file:
        historylist = [line.rstrip() for line in file] # remove line breaks
        historylist = stifle(historylist, 100) 
    # write back shortened list
    with open(historyfile, "w") as file:
        file.write('\n'.join(historylist))
        file.flush()
except OSError as e:
    # we should never end up here, but ... 
    tprint ("\r\n/history.txt: {}\r\n".format(e))
    # pass


# print greeting
print("Hello Serial!")  # serial console
tprint ("\r\nAdafruit CircuitPython {}".format(version))
tprint ("\r\n{}".format(machine))
# uncomment to debug boot process
#tprint ("\r\n")
#with open ("/boot_out.txt", "r") as fp:
#    for line in fp: 
#        tprint ("\r" + line)
tprint ("\r\n")
tprint ("\r\n" + prompt + inv(' '))


status_timeout = -1
while True:
    screen_timeout = 0
    while kbd.key_count == 0:
        status_timeout = (status_timeout + 1) % 90       # we update the status line every ~ 10s. 
        if status_timeout == 0:
            update_status(status)
        screen_timeout = (screen_timeout + 1) % 500      # screen goes dark after ~ 60 s
        if screen_timeout == 0:
            kbd.backlight = 0.0
            kbd.backlight2 = 0.1
        ''' 
        if tsc.touched:
            print ("touche")
            screen_timeout = 0
            kbd.backlight = 0.2
            kbd.backlight2 = 1.0
        ''' 
        time.sleep(0.1)
    kbd.backlight = 0.2
    kbd.backlight2 = 1.0                # keypress -> turn it on again. 
    
    for keys in kbd.keys:               # this could be more than one. 
        (state, key) = keys
        # print (" key {}, {}, state {}".format(key, ord(key), state))
        if mod_sym != 0:   # we need to handle only SYM / CTRL
            key = ord(key)
            if 0 <= key < len(keymap):
                key = keymap[key]
        if (state == STATE_PRESS):
            # print (" key {}, state {}".format(key, state))
            if key == KEY_UP:
                # we'll go backward in the historylist until we reach the top.
                lh = len(historylist)
                if lh != 0:                 # make sure the list is not empty
                    if historyptr > -lh:
                        historyptr -= 1
                    # if up is pressed for the first name, copy the former command for later
                    if historyptr == -1:
                        oldcommand = command[0:]     # we need a real copy. 
                    command = list(historylist[historyptr])
                    cursor = len(command)
                # print ("key_up: ptr = {}, cursor = {}".format(historyptr, cursor))
                # print ("        command: {}".format(command))
            elif key == KEY_DOWN:
                # we'll go forward in the historylist until we reach the youngest entry.
                if historyptr < 0:
                    historyptr += 1 
                # copy back former command if we're at the bottom
                # else take the next entry down the list. 
                if historyptr == 0:
                    command = oldcommand[0:]
                else:                            
                    command = list(historylist[historyptr])
                cursor = len(command)
                # print ("key_down: ptr = {}, cursor = {}".format(historyptr, cursor))
                # print ("          command: {}".format(command))
            elif key == KEY_LEFT:
                if cursor > 0:
                    cursor -= 1
                # print ("key_left: cursor: {}, len: {}".format(cursor, len(command)))
            elif key == KEY_RIGHT:
                if cursor < len(command):
                    cursor += 1
                # print ("key_right: cursor: {}, len: {}".format(cursor, len(command)))
            elif key == KEY_ESC:
                # end of plotting
                display.root_group = root
            elif key == KEY_SYM:
                mod_sym = 1
                # print ("setting mod_sym to ", mod_sym)
            elif key == '\t':                       # tab
                if in_compound_statement: 
                    command.insert(cursor, "    ")  # 4 spaces.
                    cursor += 4
                else:
                    pass                            # tab completion? 
            elif key in (KEY_ENTER, chr(5)):
                result = None
                line = ''.join(command)
                tprint('\r' + prompt + line + ceol)
                # print ("enter: line = {}".format(line))
                historylist = history(line, historylist)        # erst in die History, falls was schief geht. 
                historyptr = 0                      # reset pointer so we're at the bottom again. 
                # print ("historylist: {}".format(historylist))

                # check for compound statement first
                if is_compound_statement(line):
                    in_compound_statement = True    # set state
                    prompt = ps2                    # change prompt to continuation prompt
                if in_compound_statement:
                    if line == '':                  # when line is empty, it's the line finishing the compound statement
                        result = process(compound_statement)      # process the statement
                        if not isinstance(result, str): # ??? otherwise it was an error message.
                            ans = result      
                        prompt = ps1                # switch back prompt
                    else:                           # continue
                        compound_statement += line + "\n"
                elif line != '':                    # wenn nicht leer, ... 
                    result = process(line)          # ... ausführen. Fehler werden als result zurück gegeben. 
                    if not isinstance(result, str): # otherwise it was an error message.
                        ans = result                    # Casio-like ANS string
                # print ("enter: result = >{}<".format(result))
                tprint ("\r\n")                     # nächste Zeile anfangen. 
                if result is None:                  # wenn result leer, 
                    pass                            # nichts
                elif isinstance (result, complex):
                    # we need to round the value to one digit less in order to avoid float64 rounding errors to be displayed.
                    # g also makes sure that trailing zeros are suppressed. 
                    tprint ("{:.15g}{:+.15g}j\r\n".format(result.real, result.imag))
                elif isinstance (result, (int, float)):
                    tprint("{:.15g}\r\n".format(result))
                else: # str, errors, ... 
                    tprint("{}\r\n".format(result))
                command = []
                cursor = 0
            elif key == KEY_BACKSPACE: 
                if cursor > 0:
                    cursor -= 1
                    # print ("backsp: cursor: {}, len: {}".format(cursor, len(command)))
                    del command[cursor]             # technisch ist das das Zeichen _vor_ dem angezeigten Cursor. 
                # print ("backsp: cursor: {}, len: {}".format(cursor, len(command)))
                # print ("backsp: command: {}".format(command))
            else:
                # default action- insert key at cursor pos. 
                # nobody needs this for now. - alt-enter. 
                if key == '|':
                    key = '=' 
                command.insert(cursor, key) 
                cursor += 1
                # print ("else: cursor: {}, len: {}".format(cursor, len(command)))
                # print ("else: command: {}".format(command))
            # now redraw entry line
            # insert cursor only for display - we work on a copy of command
            line = ''.join(command)
            if cursor == len(line):
                line = line + inv(' ')
            elif cursor == 0:
                line = inv(line[0]) + line[1:]
            else:
                line = line[:cursor] + inv(line[cursor]) + line[cursor+1:]    # slicing is fun - last index not included. 
            tprint('\r' + prompt + line + ceol)     # print prompt, command, and delete until eol. 
        elif state == STATE_RELEASE:
            if key == KEY_SYM:
                mod_sym = 0
                # print ("setting mod_sym to ", mod_sym)


# TODO: Sym-d macht supervisor.reload() 
# Sym-c : Aktion abbrechen, default prompt




