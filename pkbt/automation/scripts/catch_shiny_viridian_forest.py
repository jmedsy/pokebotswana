# Remove filter in wild_pokemon_is_shiny() to allow other shinies through

from pkbt.config import POKEMON_RED_ROM
from pkbt.input.key_event import KeyEventType
from pkbt.input.key_type import KeyType
from pkbt.input.key_event import KeyEvent
from pkbt.state_manager import initialize_state_manager
from pkbt.config import TEMP_DIR
from pkbt.image_processing import pixel_hex_when_ready, dialogue_arrow_is_visible
from pkbt.text import FULL_DIALOGUE_BOX, read_text
from pkbt.audio import play_success
from pkbt.instances import InstanceGroup, InstanceSlot
import time
import threading
import random

"""Constants"""
STARTING_PORT = 8888 # Leave me alone

"""Tweak as desired"""
NUM_INSTANCES =12
CROSSHAIR = (105, 38)
SHINY_STAR_HEX = "#ffd652"
BATTLE_SCREEN_DIALOGUE_BG_CROSSHAIR = (220, 146)
BATTLE_SCREEN_DIALOGUE_BG_HEX = "#29526b"
BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR = (174, 56)
BATTLE_SCREEN_CAUGHT_BG_CROSSHAIR = (220, 130)
BATTLE_SCREEN_CAUGHT_BG_HEX = "#29526b"
NON_SHINY_KAKUNA_HEX = "#8c7b00"
NON_SHINY_WEEDLE_HEX = "#efad42"
NON_SHINY_CATERPIE_HEX = "#7b9c63"
NON_SHINY_PIKACHU_HEX = "#ffef00"
NON_SHINY_METAPOD_HEX = "#9cd64a"

"""Shared thread-safe variables"""
runs = 0
runs_lock = threading.Lock()
stop_all = False

def attempt(slot: InstanceSlot):
    o = slot.orch
    idx = slot.idx
    global runs
    global stop_all

    def start_game():
        slot.abort_if_frozen()
        # The seed is the time from reset until the A press leaves PRESS START.
        # That press can hit 1024 seeds, one per frame for about 17s of game
        # time. The spread below is that long at roughly 10x fast-forward.
        # PRESS START restarts the intro after about 45s of game time.
        o.client.reset_game()
        time.sleep(random.uniform(0.7, 2.5))
        for _ in range(8):
            o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
            time.sleep(0.7)
        time.sleep(2)

    def equip_bike():
        slot.abort_if_frozen()
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.SELECT))
        time.sleep(0.7)

    def brief_zigzag():
        slot.abort_if_frozen()
        for i in range(1):
            o.client.execute_event(KeyEvent(KeyEventType.HOLD, KeyType.RIGHT))
            time.sleep(0.3)
            o.client.execute_event(KeyEvent(KeyEventType.RELEASE, KeyType.RIGHT))
            time.sleep(0.1)
            o.client.execute_event(KeyEvent(KeyEventType.HOLD, KeyType.LEFT))
            time.sleep(0.3)
            o.client.execute_event(KeyEvent(KeyEventType.RELEASE, KeyType.LEFT))
            time.sleep(0.1)

    def capture_pixel(x: int, y: int) -> str:
        slot.abort_if_frozen()
        return pixel_hex_when_ready(
            TEMP_DIR / f"{idx}.png",
            x,
            y,
            lambda: o.client.save_screenshot_to_file(f"{idx}.png"),
        )

    def dialogue_arrow_is_visible_on_screen():
        slot.abort_if_frozen()
        return dialogue_arrow_is_visible(
            TEMP_DIR / f"{idx}.png",
            lambda: o.client.save_screenshot_to_file(f"{idx}.png"),
        )

    def entered_battle():
        slot.abort_if_frozen()
        bg_hex = capture_pixel(BATTLE_SCREEN_DIALOGUE_BG_CROSSHAIR[0], BATTLE_SCREEN_DIALOGUE_BG_CROSSHAIR[1])
        return bg_hex == BATTLE_SCREEN_DIALOGUE_BG_HEX

    def get_wild_pokemon_name():
        slot.abort_if_frozen()
        path = TEMP_DIR / f"{idx}.png"
        capture_pixel(FULL_DIALOGUE_BOX[0], FULL_DIALOGUE_BOX[1])
        text = "".join(read_text(path, FULL_DIALOGUE_BOX).split()).upper()
        prefix = "WILD"
        for suffix in ("APPEARED!", "OPPEORED!"):
            if text.startswith(prefix) and text.endswith(suffix):
                return text[len(prefix):-len(suffix)]
        return ""

    def is_shiny_of_species(pokemon_name: str):
        slot.abort_if_frozen()
        if pokemon_name == "KAKUNA":
            pokemon_hex = capture_pixel(BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[0], BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[1])
            is_shiny = pokemon_hex != NON_SHINY_KAKUNA_HEX
        elif pokemon_name == "WEEDLE":
            pokemon_hex = capture_pixel(BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[0], BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[1])
            is_shiny = pokemon_hex != NON_SHINY_WEEDLE_HEX
        elif pokemon_name == "CATERPIE":
            pokemon_hex = capture_pixel(BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[0], BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[1])
            is_shiny = pokemon_hex != NON_SHINY_CATERPIE_HEX
        elif pokemon_name == "PIKACHU":
            pokemon_hex = capture_pixel(BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[0], BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[1])
            is_shiny = pokemon_hex != NON_SHINY_PIKACHU_HEX
        elif pokemon_name == "METAPOD":
            pokemon_hex = capture_pixel(BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[0], BATTLE_SCREEN_WILD_POKEMON_CROSSHAIR[1])
            is_shiny = pokemon_hex != NON_SHINY_METAPOD_HEX
        else:
            raise ValueError(f"Invalid pokemon name: {pokemon_name}")
        return is_shiny

    def proceed_through_battle_intro_messages():
        slot.abort_if_frozen()
        time.sleep(0.4)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.5)

    def run_away_from_battle():
        slot.abort_if_frozen()
        time.sleep(0.1)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.1)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.RIGHT))
        time.sleep(0.1)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.1)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.1)

    def use_mean_look():
        slot.abort_if_frozen()
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(3)

    def throw_first_ultra_ball():
        slot.abort_if_frozen()
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.RIGHT))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.RIGHT))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.RIGHT))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(3)

    def throw_additional_ultra_ball():
        slot.abort_if_frozen()
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(3)

    def is_caught():
        slot.abort_if_frozen()
        bg_hex = capture_pixel(BATTLE_SCREEN_CAUGHT_BG_CROSSHAIR[0], BATTLE_SCREEN_CAUGHT_BG_CROSSHAIR[1])
        return bg_hex == BATTLE_SCREEN_CAUGHT_BG_HEX

    def finish_battle_messages():
        slot.abort_if_frozen()
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(2.7)

    def pick_up_egg():
        slot.abort_if_frozen()
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)

    def hatch_egg():
        slot.abort_if_frozen()
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.3)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.SELECT))
        time.sleep(0.7)
        for _ in range(250):
            slot.abort_if_frozen()
            o.client.execute_event(KeyEvent(KeyEventType.HOLD, KeyType.LEFT))
            time.sleep(0.5)
            o.client.execute_event(KeyEvent(KeyEventType.RELEASE, KeyType.LEFT))
            o.client.execute_event(KeyEvent(KeyEventType.HOLD, KeyType.RIGHT))
            time.sleep(0.5)
            o.client.execute_event(KeyEvent(KeyEventType.RELEASE, KeyType.RIGHT))

    def go_through_hatching_sequences():
        slot.abort_if_frozen()
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(2)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(2)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(2)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(2)

    def enter_summary():
        slot.abort_if_frozen()
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.START))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.RIGHT))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)

    def save_screenshot():
        slot.abort_if_frozen()
        o.client.save_screenshot_to_file(f"{idx}.png")
        time.sleep(1)

    def save_game():
        slot.abort_if_frozen()
        print(f"Saving game on {idx}")
        time.sleep(2)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.START))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.DOWN))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(0.7)
        o.client.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        time.sleep(3)

    start_game()
    equip_bike()
    while not stop_all:
        brief_zigzag()
        if entered_battle():
            while not dialogue_arrow_is_visible_on_screen():
                time.sleep(0.4)
            pokemon_name = get_wild_pokemon_name()
            runs += 1
            if runs % 50 == 0:
                print(f"Runs: {runs}")
            proceed_through_battle_intro_messages()
            if is_shiny_of_species(pokemon_name):
                print(f"Shiny {pokemon_name} found on {idx} after {runs} runs")
                stop_all = True
                use_mean_look()
                throw_first_ultra_ball()
                while not is_caught():
                    throw_additional_ultra_ball()
                finish_battle_messages()
                save_game()
                play_success(blocking=True)
                group.stop.set()
                break
            else:
                run_away_from_battle()
        else:
            continue

"""Putting it all together and running it"""
initialize_state_manager()
group = InstanceGroup(NUM_INSTANCES, POKEMON_RED_ROM, starting_port=STARTING_PORT)
group.start(fast_forward=True)
group.run(attempt)
