# import modules from game_lib.py
import arena, field

# -- START STATIC CONFIG --
blue_raspi = "blue"
red_raspi = "red"

blue_amp_pin = 10
blue_spkr_pin = 11

blue_amp = {"pin": blue_amp_pin, "location": blue_raspi}
blue_spkr = {"pin": blue_spkr_pin, "location": blue_raspi}

red_amp_pin = 10
red_spkr_pin = 11

red_amp = {"pin": red_amp_pin, "location": red_raspi}
red_spkr = {"pin": red_spkr_pin, "location": red_raspi}
# -- END STATIC CONFIG --

while True:
    try:
        # -- START GAME LOGIC --

        arena.modifyPoints(redA=1)
        
        # -- END GAME LOGIC --
    except Exception as e:
        print(e)
        print("Error in game logic")