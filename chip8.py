import pygame
import os
from random import randint, seed, randrange
from time import time, sleep
from pprint import pprint
import collections

from pygame.constants import K_SPACE, K_RETURN
import colorama

colorama.init()

import winsound
Freq = 3500
Dur = 20

import sys
print("Native byteorder: ", sys.byteorder)

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

logger = logging.getLogger()


logger.setLevel(logging.CRITICAL)
logger.setLevel(logging.WARN)


os.environ['SDL_VIDEO_CENTERED'] = '1'


pygame.init()


PYGAME_DISPLAY = True
TEST_VRAM = False
CONSOLE_CLS = False
CONSOLE_DEBUG_SCREEN = False
CONSOLE_DEBUG_MSG = False


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

PI = 3.1411592653

display_width, display_height = 64, 32
device_screen_in_pixels = display_width, display_height



if PYGAME_DISPLAY:
    screen_scale = 9
else:
    screen_scale = 1



screen_status_h = 96

app_display_width = display_width * screen_scale
app_display_height = display_height * screen_scale + screen_status_h
app_display_pixels_count = app_display_width * app_display_height

app_display_size = (app_display_width, app_display_height)
app_screen = pygame.display.set_mode(app_display_size)

device_screen_pixels_count = display_width * screen_scale * display_height * screen_scale



pygame.display.set_caption("CHIP8 Emulator")

pxarray = pygame.PixelArray(app_screen)
clock = pygame.time.Clock()
pygame.key.set_repeat(2000, 2000)






REGISTERS_NUM = 0x10



CLS_BG = (128, 128, 128)
COL_FG = (160, 255, 160)

CLS_BG = (100, 200, 100)
COL_FG = (64, 64, 64)

KEY_MAP = {
    pygame.K_KP0: 0x0,
    pygame.K_KP1: 0x1,
    pygame.K_KP2: 0x2,
    pygame.K_KP3: 0x3,
    pygame.K_KP4: 0x4,
    pygame.K_KP5: 0x5,
    pygame.K_KP6: 0x6,
    pygame.K_KP7: 0x7,
    pygame.K_KP8: 0x8,
    pygame.K_KP9: 0x9,
    pygame.K_a: 0xA,
    pygame.K_b: 0xB,
    pygame.K_c: 0xC,
    pygame.K_d: 0xD,
    pygame.K_e: 0xE,
    pygame.K_f: 0xF
}

KEY_MAP = {
    pygame.K_KP0: 0x0,
    pygame.K_KP7: 0x1,
    pygame.K_KP8: 0x2,
    pygame.K_KP9: 0x3,
    pygame.K_KP4: 0x4,
    pygame.K_KP5: 0x5,
    pygame.K_KP6: 0x6,
    pygame.K_KP1: 0x7,
    pygame.K_KP2: 0x8,
    pygame.K_KP3: 0x9,
    pygame.K_a: 0xA,
    pygame.K_b: 0xB,
    pygame.K_c: 0xC,
    pygame.K_d: 0xD,
    pygame.K_e: 0xE,
    pygame.K_f: 0xF
}

key_down = 0


ROMs = collections.OrderedDict([
    ("ROMs/pong2.ch8", 500),
    ("ROMs/spaceInvaders.ch8", 500) ])


ROM_index = 0
ROM_filename = list(ROMs.keys())[ROM_index]
ROM_FPS = list(ROMs.values())[ROM_index]

FPS = ROM_FPS






class chup8CPU(object):
    def __init__(self):
        self.fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0,
                        0x20, 0x60, 0x20, 0x20, 0x70,
                        0xF0, 0x10, 0xF0, 0x80, 0xF0,
                        0xF0, 0x10, 0xF0, 0x10, 0xF0,
                        0x90, 0x90, 0xF0, 0x10, 0x10,
                        0xF0, 0x80, 0xF0, 0x10, 0xF0,
                        0xF0, 0x80, 0xF0, 0x90, 0xF0,
                        0xF0, 0x10, 0x20, 0x40, 0x40,
                        0xF0, 0x90, 0xF0, 0x90, 0xF0,
                        0xF0, 0x90, 0xF0, 0x10, 0xF0,
                        0xF0, 0x90, 0xF0, 0x90, 0x90,
                        0xE0, 0x90, 0xE0, 0x90, 0xE0,
                        0xF0, 0x80, 0x80, 0x80, 0xF0,
                        0xE0, 0x90, 0x90, 0x90, 0xE0,
                        0xF0, 0x80, 0xF0, 0x80, 0xF0,
                        0xF0, 0x80, 0xF0, 0x80, 0x80]

    def initialise(self):
        logger.warn('chip8 CPU initialize')

        seed()

        self.SP = 0

        self.stack = [0]*16

        self.opcode = 0

        self.opc_mnemo = ''

        self.opcode_asm = ['']*6

        self.memory = bytearray([0] * 4096)

        self.PC = 0x200

        self.I = 0

        self.V = bytearray([0] * 16)

        self.VRAM = bytearray([0] * 4096)

        self.KBOARD = [0]*16


        self.t_last = time()

        self.memory[:80] = bytearray(self.fontset)

        logger.warn('chip8 CPU Fonts Loaded...')


        self.time = 0

        self.tone = 0

        self.draw_flag = False

        self.ROMloaded = ''
        self.cycle_num = 0

    def ROMload(self, filename=''):    
        logger.warn('chip8 CPU ROM REGISTERS set...')

        fhand = open(filename, 'rb')
        ROMfile = fhand.read()
        
        self.PC = 0x200

        self.memory[self.PC: len(ROMfile)] = bytearray(ROMfile)

        fhand.close()
        logger.warn('Done')

        self.ROMloaded = filename.split('/')[1]


    def __str__(self):
        if CONSOLE_DEBUG_SCREEN:
            response = "\n*** chip8CPU object state: REGISTERS *** PLRANG *** \n\n\t"
            response += "STACK: \t\t" + str(repr(self.stack)) + "\n\n\t"
            response += "OPCOD: \t\t" + \
                str(hex(self.opcode)) + "\t" + str(self.opcode) + \
                '\t' + self.opcode_asm[0] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[1] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[2] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[3] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[4] + "\n\n\t"

            mp = ''
            for i in range(len(self.memory[0x200: 0x200+30])):
                tmp += format(self.memory[0x200+i], '02x') + ' '

            response += "MEM: \t\t" + str(tmp) + "\n\t"

            response += "PC: \t\t" + str(self.PC) + "\n\t"
            response += "I: \t\t" + str(self.I) + "\n\t"
            response += "SP: \t\t" + str(self.SP) + "\n\t"

            tmp = ''
            for i in range(len(self.V)):
                tmp += format(self.V[i], '02x') + ' '

            response += "V: \t\t" + \
                str(tmp) + ' len:' + str(len(self.V)) + "\n\t"

            response += "KEY: \t\t" + str(key_down) + "\n\t"

            if key_down in KEY_MAP:
                response += "KEY E: \t\t" + str(KEY_MAP[key_down]) + "\n\t"



            tmp = ''
            for i in range(len(self.VRAM[0:30])):
                tmp += format(self.VRAM[0+i], '02x') + ' '

            response += "VRAM: \t\t" + str(tmp) + "\n\t"

            response += "KB_BUF: \t" + str(repr(self.KBOARD)) + "\n\t"
            response += "FONTS: \t\t" + "pass" + "\n\t"
            response += "TIME: \t\t" + str(self.time) + "\n\t"
            response += "TONE: \t\t" + str(self.tone) + "\n\t"

            response += "\n*** chip8CPU object state: OTHER ***\n\n\t"
            response += "Python time: " + str(self.t_last) + "\n\t"
            response += "Draw flag: " + str(self.draw_flag) + "\t\t"
            response += "ROM loaded: " + self.ROMloaded + "\t\t"
            response += "Cycle num: \t" + \
                str(self.cycle_num) + "\t" + "FPS: " + str(FPS)
        else:
            response = ''


        if TEST_VRAM:
            response = ''
            count_w = 1
            vram_len = 0
            line_store = ''

            print("\033[1;1f]")



            for pixel in self.VRAM:
                if not pixel:
                    pixOff = ' ' * screen_scale
                    response += pixOff
                    line_store += pixOff
                else:
                    pixOn = chr(219) * screen_scale
                    response += pixOn
                    line_store += pixOn


                if count_w * screen_scale % app_display_width == 0:
                    response += '\n'
                    line_store += '\n'
                    line_store = line_store * (screen_scale-1)

                    response += line_store
                    count_w = 0

                    line_store = ''

                

                count_w += 1
                vram_len += 1

                if vram_len > display_width * display_height:
                    vram_len = 0
                    break

        if CONSOLE_DEBUG_MSG:
            response = ' OP:' + str(hex(self.opcode)) + ' : ' + self.opc_mnemo

        return response

    
    def RUNcycle(self):
        self.cycle_num +=1

