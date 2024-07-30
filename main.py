from machine import Pin, PWM
from time import sleep, time
from random import randint
import math

r = PWM(Pin(15), freq=300_000, duty_u16=2**16)
g = PWM(Pin(14), freq=300_000, duty_u16=2**16)
b = PWM(Pin(13), freq=300_000, duty_u16=2**16)
button = machine.Pin(16, Pin.IN, Pin.PULL_UP)

BLUE = (0, 0, 255)
BLUE2 = (0, 0, 95)
RED = (255, 0, 0)
RED2 = (95, 0, 0)
GREEN = (0, 255, 0)
GREEN2 = (0, 95, 0)
WHITE = (255, 255, 255)
WHITE2 = (95, 95, 95)
PURPLE = (255, 0, 255)
PURPLE2 = (95, 0, 95)
YELLOW = (255, 255, 0)
YELLOW2 = (95, 95, 0)

COLORS = ((BLUE, BLUE2),
          (RED, RED2),
          (GREEN, GREEN2),
          (WHITE, WHITE2),
          (PURPLE, PURPLE2),
          (YELLOW, YELLOW2))

rainbow_colors = [
    (255, 0, 0),      # Rosso
    (255, 165, 0),    # Arancione
    (255, 255, 0),    # Giallo
    (0, 255, 0),      # Verde
    (0, 127, 255),    # Azzurro
    (75, 0, 130),     # Indaco
    (148, 0, 211)     # Violetto
]

mode = 0
debounce_time = 0.05  # Tempo di debounce in secondi
power_off_time = 2    # Tempo di pressione per lo spegnimento
holding = False
blink = False
click_time = 0

def power_off():
    global mode, random_color
    set_color((0, 0, 0), chk=False)
    while not button.value(): pass  # Aspetta che venga rilasciato il click
    while button.value():
        sleep(.05)
    mode -= 2

def chk_button():
    global holding, mode, click_time, blink
    if not button.value() and not holding:
        sleep(debounce_time)  # Attendi per il debounce
        if not button.value():  # Verifica di nuovo lo stato del button dopo il debounce
            holding = True
            
            if blink:
                mode += 1
                mode %= len(COLORS) + 1 # colori standard + arcobaleno... lol :)
                blink = False
            else:
                blink = True
                
            click_time = time() # Salva il timestamp per calcolare il tempo passato ed eventualmente spegnere i led
            return False
    elif button.value() and holding:
        holding = False
    elif not button.value() and holding:
        elapsed = time() - click_time
        if elapsed > power_off_time:
            power_off()
            holding = False
    return True

def set_color(color, chk=True):
    r.duty_u16(round((255-color[0]) / 255 * 2**16))
    g.duty_u16(round((255-color[1]) / 255 * 2**16))
    b.duty_u16(round((255-color[2]) / 255 * 2**16))
    
    if chk:
        return chk_button()
    else:
        return True
    
def ease_in_out_sine(t):return 0.5 * (1 - math.cos(math.pi * t))
def quad_ease(t):		return t**2
def linear_ease(t):		return t

# Interpolazione lineare tra due colori
def interpolate_color(color1, color2, t):
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t)
    )

# Transizione tra :color1: e :color2: nel tempo :duration: usando la funzione :easing_function:
def transition_colors(color1, color2, duration, easing_function=linear_ease, steps=100):
    for step in range(steps + 1):
        t = step / steps
        eased_t = easing_function(t)
        interpolated_color = interpolate_color(color1, color2, eased_t)
        if set_color(interpolated_color): # success
            sleep(duration / steps)
        else: # button pressed
            return False
    return True

if __name__ == "__main__":
    while True:
        if mode < len(COLORS):
            if blink:
                if transition_colors(COLORS[mode][0], COLORS[mode][1], 1, ease_in_out_sine):
                    transition_colors(COLORS[mode][1], COLORS[mode][0], 1, ease_in_out_sine)
            else:
                set_color(COLORS[mode][0])
        elif mode == len(COLORS): # RAINBOW!!!!
            for i in range(len(rainbow_colors)-1):
                success = transition_colors(rainbow_colors[i], rainbow_colors[i+1], .6, ease_in_out_sine)
                if not success: break
            if success:
                transition_colors(rainbow_colors[-1], rainbow_colors[0], .6, ease_in_out_sine)
