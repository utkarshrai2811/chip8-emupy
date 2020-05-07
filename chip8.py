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




CLS_BG = (0, 0, 0)
COL_FG = (255, 255, 255)

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
    ("ROMs/spaceInvaders.ch8", 500),
    ("ROMs/bowling.ch8", 200)])


ROM_index = 0
ROM_filename = list(ROMs.keys())[ROM_index]
ROM_FPS = list(ROMs.values())[ROM_index]

FPS = ROM_FPS






class chip8CPU(object):
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
        logger.warning('chip8 CPU initialize')

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

        logger.warning('chip8 CPU Fonts Loaded...')


        self.time = 0

        self.tone = 0

        self.draw_flag = False

        self.ROMloaded = ''
        self.cycle_num = 0

    def ROMload(self, filename=''):    
        logger.warning('chip8 CPU ROM REGISTERS set...')

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

        asm = self.OPCdecode()

        if self.tone > 0:
            self.tone -= 1

        if self.time > 0:
            self.time -= 1
        


        self.opcode_asm.insert(0, asm)
        self.opcode_asm.pop()


        if TEST_VRAM or CONSOLE_DEBUG_SCREEN or CONSOLE_DEBUG_MSG:
            print(self)

        self.PC += 2
    

    def OPCdecode(self):
        self.opcode = (self.memory[self.PC] << 8) | self.memory[self.PC + 1]

        
        self.X = ((self.opcode & 0x0F00) >> 8) & 0xF
        self.Y = ((self.opcode & 0x00F0) >> 4) & 0xF
        self.n = self.opcode & 0x000F
        self.nn = self.opcode & 0x00FF
        self.nnn = self.opcode & 0x0FFF

        if CONSOLE_DEBUG_MSG:
            print(' PC:' + str(hex(self.PC))),

        self.opcode_lookup = {

            
            0x0000: self.op_CLS_RET_RCA_1802,
            0x00E0: self.op_cls,                   
            0x00EE: self.op_RTS,                   

            0x1000: self.op_JMP,                   
            
            0x2000: self.op_SUB,

            0x3000: self.op_SE_vx_nn,              
            0x4000: self.op_SNE_vx_nn,             

            0x5000: self.op_SE_vx_vy,              

            0x6000: self.op_LD_vx_nn,              
            0x7000: self.op_ADD_vx_nn,             

            0x8000: self.op_LD_vx_vy,              

            
            0x8001: self.op_LD_vx_vx_or_vy,
            
            0x8002: self.op_LD_vx_vx_and_vy,
            
            0x8003: self.op_LD_vx_vx_xor_vy,
            
            0x8004: self.op_LD_vx_vx_add_vy,
            
            0x8005: self.op_LD_vx_vx_sub_vy,
            
            0x8006: self.op_SHR_vx,
            

            
            0x8007: self.op_SUBn_vx_vy,
            

            
            0x800E: self.op_SHL_vx,
            

            0x9000: self.op_SNE_vx_vy,             


            
            0xA000: self.op_LOAD_I_nnn,

            0xB000: self.op_JP_v0_nnn,              

            
            0xC000: self.op_RND_vx_nn,


            0xD000: self.op_D_XYN,                  

            
            0xE09E: self.op_SKP_vx,
            
            0xE0A1: self.op_SKNP_vx,


            0xF007: self.op_LD_VX_dt,               

            
            0xF00A: self.op_LD_VX_n,
            


            0xF015: self.op_LD_dt_VX,
            
            0xF018: self.op_LD_st_VX,
            0xF01E: self.op_ADD_i_VX,               


            
            0xF029: self.op_LD_f_VX,
           

            0xF033: self.op_LD_b_VX,
            



            0xF055: self.op_LD_i_VX,

            


            0xF065: self.op_LD_VX_i
            
            }

        op_test = self.opcode & 0xF000

        if op_test == 0xb000:
            winsound.Beep(Freq, 50)

        switch = {

            0x0000: lambda: 0x0000 | self.opcode & 0xF0FF,

            
            0x8000: lambda: 0x8000 | self.opcode & 0xF00F,
            
            0xE000: lambda: 0xE000 | self.opcode & 0xF0FF,

            
            0xF000: lambda: 0xF000 | self.opcode & 0xF0FF
            

        }

        if op_test in switch:
            lookup = switch[op_test]()

        else:
            lookup = self.opcode & 0xF000

        try:
            self.opcode_lookup[lookup]()

            return str(hex(self.opcode)) + '\t' + self.opc_mnemo
        except KeyError:
            return str(hex(self.opcode)) + ' Look up error'
            pass

    def op_CLS_RET_RCA_1802(self):

        
        self.opc_mnemo = 'unused RCA 1802 ' + str(hex(self.opcode))

    

    def op_cls(self):

        for i in range(len(self.VRAM)):
            self.VRAM[i] = 0

        



        if PYGAME_DISPLAY:
            pxarray[:display_width * screen_scale,
                    :display_height * screen_scale] = CLS_BG

        self.opc_mnemo = "CLS"

    
    def op_RTS(self):

        self.SP -= 1
        self.PC = self.stack[self.SP % 12]

        self.opc_mnemo = "RTS"

    

    def op_JMP(self):

        self.PC = self.nnn

        self.opc_mnemo = "JP " + str(hex(self.nnn))
        self.PC -= 2                        




    def op_SUB(self):                           

        
        self.stack[self.SP % 12] = self.PC
        self.SP += 1

        self.PC = self.nnn                      
        self.PC -= 2

        self.opc_mnemo = "SUB ~ call " + str(hex(self.nnn))

    

    def op_SE_vx_nn(self):
        X = self.X

        if self.nn == self.V[X]:
            self.PC += 2

        self.opc_mnemo = "SE V" + str(X) + ', ' + str(self.nn)

    

    def op_SNE_vx_nn(self):
        X = self.X

        if self.V[X] != self.nn:
            self.PC += 2

        self.opc_mnemo = "SNE VX " + \
            str(X) + ", " + str(hex(self.nn)) + " = nn"

    

    def op_SE_vx_vy(self):
        X = self.X
        Y = self.Y

        if self.V[X] == self.V[Y]:
            self.PC += 2

        self.opc_mnemo = "SE V" + \
            str(X) + " = " + str(hex(self.V[X])) + \
            ", V" + str(Y) + " = " + str(hex(self.V[Y]))

    

    def op_LD_vx_nn(self):
        X = self.X

        self.V[X] = self.nn

        self.opc_mnemo = "LD V" + str(X) + ", " + str(hex(self.nn))

    

    def op_ADD_vx_nn(self):
        X = self.X

        self.opc_mnemo = "ADD V" + \
            str(X) + ", " + str(self.V[X]) + ", " + str(self.nn)

        self.V[X] = (self.V[X] + self.nn) & 0xFF  
        

    

    def op_LD_vx_vy(self):
        X = self.X
        Y = self.Y

        self.V[X] = self.V[Y]

        self.opc_mnemo = "LD V" + str(X) + ", " + "V" + str(Y)

    
    def op_LD_vx_vx_or_vy(self):
        X = self.X
        Y = self.Y

        self.V[X] = (self.V[X] | self.V[Y]) & 0xFF  

        self.opc_mnemo = "or V" + str(X) + ", " + "V" + str(Y)

    

    def op_LD_vx_vx_and_vy(self):
        X = self.X
        Y = self.Y

        self.V[X] = (self.V[X] & self.V[Y]) & 0xFF      

        self.opc_mnemo = "and V" + str(X) + ", " + "V" + str(Y)

    

    def op_LD_vx_vx_xor_vy(self):
        X = self.X
        Y = self.Y

        
        self.V[X] = (self.V[X] ^ self.V[Y]) & 0xFF

        self.opc_mnemo = "xor V" + str(X) + ", " + "V" + str(Y)

    

    def op_LD_vx_vx_add_vy(self):
        X = self.X
        Y = self.Y

        val = self.V[X] + self.V[Y]
        if val > 255:
            self.V[0xF] = 0x1  
        else:
            self.V[0xF] = 0x0

        self.V[X] = val & 0xFF
        

        self.opc_mnemo = "add V" + \
            str(X) + ", " + "V" + str(Y) + ' carry: ' + str(self.V[0xF])

    

    def op_LD_vx_vx_sub_vy(self):
        X = self.X
        Y = self.Y

        val = self.V[X] - self.V[Y]

        if self.V[X] > self.V[Y]:
            self.V[0xF] = 0x1
        else:
            self.V[0xF] = 0x0

        
        self.V[X] = val & 0xFF              
        
        

        self.opc_mnemo = "sub V" + \
            str(X) + ", " + "V" + str(Y) + ' carry: ' + str(self.V[0xF])

    
    

    def op_SUBn_vx_vy(self):
        X = self.X
        Y = self.Y

        val = self.V[Y] - self.V[X]

        if self.V[Y] > self.V[X]:
            self.V[0xF] = 0x1
        else:
            self.V[0xF] = 0x0

        self.V[X] = val & 0xFF              

        self.opc_mnemo = "subn V" + \
            str(X) + ", " + "V" + str(Y) + ' VF borrow: ' + str(self.V[0xF])

    
    

    def op_SHR_vx(self):
        X = self.X
        Y = self.Y

        self.V[0xF] = self.V[X] & 0x01
        self.V[X] = (self.V[X] >> 1) & 0xFF

        self.opc_mnemo = "shr V" + str(X) + " >>1"

    
    
    def op_SHL_vx(self):
        X = self.X
        Y = self.Y

        self.V[0xF] = (self.V[X] >> 7) & 0x01
        self.V[X] = (self.V[X] << 1) & 0xFF

        self.opc_mnemo = "shl V" + str(X) + " <<1"

    

    def op_SNE_vx_vy(self):
        X = self.X
        Y = self.Y

        if self.V[X] != self.V[Y]:
            self.PC += 2

        self.opc_mnemo = "SNE V" + \
            str(X) + '('+str(hex(X)) + ')' + ", V" + \
            str(Y) + '('+str(hex(Y)) + ')'

    

    def op_LOAD_I_nnn(self):

        self.I = self.nnn

        self.opc_mnemo = "LD I, " + str(hex(self.I))

    

    def op_JP_v0_nnn(self):

        self.PC = self.nnn + self.V[0]
        self.PC -= 2

        self.opc_mnemo = "JP V0 " + ", " + \
            str(hex(self.PC)) + ' PC=(' + \
            str(hex(self.V[0])) + ' + ' + str(hex(self.nnn)) + ')'

    

    def op_RND_vx_nn(self):
        X = self.X
        nn = self.nn

        self.V[X] = (randint(0, 255) & nn) & 0xFF  
        self.opc_mnemo = "rnd VX " + str(hex(X)) + ", " + str(hex(nn))




    def op_D_XYN(self):                       

        X = self.V[self.X]
        Y = self.V[self.Y]
        n = self.n

        self.V[0xF] = 0

        for next_pix in range(n):
            pixel = self.memory[self.I + next_pix]

            for x_line in range(8):           
                
                x_pos = (X + x_line) % display_width
                y_pos = (Y + next_pix) % display_height

                sprite_bit = (pixel >> (7 - x_line)) & 1

                bit_pos = y_pos * display_width + x_pos
                VRAM_old = self.VRAM[bit_pos]

                self.VRAM[bit_pos] = VRAM_old ^ sprite_bit

                if VRAM_old != 0 and self.VRAM[bit_pos] == 0:
                    self.V[0xF] = 1

                new_x = x_pos * screen_scale
                new_y = y_pos * screen_scale

                if VRAM_old ^ sprite_bit:
                    if PYGAME_DISPLAY:
                        pxarray[new_x: new_x + screen_scale,
                                new_y: new_y + screen_scale] = COL_FG
                else:
                    if self.V[0xF]:
                        if PYGAME_DISPLAY:
                            pxarray[new_x: new_x + screen_scale,
                                    new_y: new_y + screen_scale] = CLS_BG




        self.draw_flag = True

        
        self.opc_mnemo = "DRW " + str(X) + ' ' + str(Y) + ' ' + str(n)

    
    def op_SKP_vx(self):
        X = self.X

        if self.KBOARD[self.V[X] & 0xF] == 1:
            self.PC += 2

        self.opc_mnemo = "SKP_vx"

    

    def op_SKNP_vx(self):
        X = self.X

        if self.KBOARD[self.V[X] & 0xF] != 1:
            self.PC += 2

        self.opc_mnemo = "SKNP_vx"

    

    def op_LD_VX_dt(self):
        X = self.X
        self.V[X] = self.time

        self.opc_mnemo = "LD V" + str(X) + ', ' + str(self.time)

    

    def op_LD_VX_n(self):
        X = self.X

        if key_down:
            self.KBOARD[KEY_MAP[key_down]] = 1      
            
            self.V[X] = KEY_MAP[key_down]
        else:
            self.PC -= 2

    

    def op_LD_st_VX(self):
        X = self.X

        self.tone = self.V[X]
        self.opc_mnemo = "LD st, V" + str(X) + " (" + str(hex(self.V[X])) + ")"

    
    def op_LD_dt_VX(self):
        X = self.X

        self.time = self.V[X]
        self.opc_mnemo = "LD dt, V" + str(X) + " (" + str(hex(self.V[X])) + ")"

    

    def op_ADD_i_VX(self):
        X = self.X

        self.I = (self.I & 0xFFF) + self.V[X]
        self.V[0xF] = self.I >> 12

        self.opc_mnemo = "ADD I, V" + str(X) + ', ' + str(hex(self.V[X]))

    
    def op_LD_f_VX(self):
        X = self.X
        
        self.I = (self.V[X] & 0xFF) * 5
        
        self.opc_mnemo = "LD f, V" + str(X) + ' (' + (str(self.I)) + ')'

    

    def op_LD_b_VX(self):
        X = self.X
        VX = self.V[X]

        self.memory[self.I & 0xFFF] = int(((VX / 100) % 10)) & 0xFF
        self.memory[(self.I + 1) & 0xFFF] = int(((VX / 10) % 10)) & 0xFF
        self.memory[(self.I + 2) & 0xFFF] = int(((VX / 1) % 10)) & 0xFF

        self.opc_mnemo = "LD B, V" + str(X) + ' (' + (str(hex(VX))) + ')'

    

    def op_LD_i_VX(self):
        X = self.X

        self.opc_mnemo = 'LD memI[' + \
            str(hex(self.I)) + ']+' + ", V 0-" + str(hex(X))

        for i in range(X + 1):
            self.memory[(self.I + i) & 0xFFF] = self.V[i]

    

    def op_LD_VX_i(self):
        X = self.X

        self.opc_mnemo = "LD V 0-" + \
            str(hex(X)) + ', memI[' + str(hex(self.I)) + ']+'

        for i in range(X + 1):
            self.V[i] = self.memory[(self.I + i) & 0xFFF]


chip8CPU = chip8CPU()

chip8CPU.initialise()



chip8CPU.ROMload(ROM_filename)

logger.warn('chip8 CPU start...')

winsound.Beep(Freq, Dur)
print("\033[2J\033[1;1f")
pxarray[:, :] = CLS_BG


done = False
status_printing = True


def status_print():
    global status_printing

    font = pygame.font.SysFont('Small Fonts', 28, False, False)

    if FPS == 0:
        text = font.render("Clock: " + "unlimited", True, COL_FG)
    else:
        text = font.render("Clock: " + str(FPS), True, COL_FG)

    if PYGAME_DISPLAY:
        app_screen.blit(text, [8, app_display_height - 60])

        text = font.render("ROM up / dn: " + chip8CPU.ROMloaded, True, COL_FG)
        app_screen.blit(text, [180, app_display_height - 60])
        status_printing = False

while not done:
    if CONSOLE_CLS:
        print("\033[2J\033[1;1f")

    if PYGAME_DISPLAY:
        pxarray = pygame.PixelArray(app_screen)

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            done = True  


        if event.type == pygame.KEYDOWN:
            key_down = event.key
            if key_down in KEY_MAP:
                chip8CPU.KBOARD[KEY_MAP[key_down]] = 1
            if key_down == pygame.K_ESCAPE:
                quit()

            if key_down == pygame.K_UP:
                ROM_index += 1
                if ROM_index > len(ROMs) - 1:
                    ROM_index = 0
            
            if key_down == pygame.K_DOWN:
                ROM_index -= 1
                if ROM_index < 0:
                    ROM_index = len(ROMs) - 1

            if key_down == pygame.K_DOWN or key_down == pygame.K_UP:

                print("\033[2J\033[1;1f")   

                if PYGAME_DISPLAY:
                    pxarray[:, :] = CLS_BG     

                ROM_filename = list(ROMs.keys())[ROM_index]
                ROM_FPS = list(ROMs.values())[ROM_index]
                FPS = ROM_FPS

                chip8CPU.initialise()
                chip8CPU.ROMload(ROM_filename)
                status_printing = True

        
        else:
            chip8CPU.KBOARD = [0]*16
            key_down = False



    chip8CPU.RUNcycle()

    if FPS:
        clock.tick(FPS)

    if PYGAME_DISPLAY:
        del pxarray

    if status_printing:
        status_print()

    if PYGAME_DISPLAY:
        pygame.display.update()


pygame.quit()\

exit()
