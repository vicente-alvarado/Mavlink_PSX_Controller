# ps4_controller.py
import pygame
import time

BUTTON_MAP = {
    0: "cross",
    1: "circle",
    2: "square",
    3: "triangle",
    4: "share",
    6: "options",
    7: "L3",
    8: "R3",
    9: "L1",
    10: "R1",
    11: "dpad_up",
    12: "dpad_down",
    13: "dpad_left",
    14: "dpad_right",
    15: "touchpad",
}

def get_direction(x_axis, y_axis, deadzone=0.3):
    if y_axis < -deadzone:
        return "up"
    elif y_axis > deadzone:
        return "down"
    elif x_axis < -deadzone:
        return "left"
    elif x_axis > deadzone:
        return "right"
    return None

def trigger_pressed(value, threshold=0.5):
    return value > threshold

def init_controller():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        raise RuntimeError("No joystick detected")

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick detected: {joystick.get_name()}")
    return joystick

def get_events(joystick, prev_state):
    pygame.event.pump()

    events = {
        "left_stick": None,
        "right_stick": None,
        "L2": None,
        "R2": None,
        "buttons": {},
        "vibration": [],
        "axes": {}  # nuevo
    }

    # Sticks
    x_left = joystick.get_axis(0)
    y_left = joystick.get_axis(1)
    x_right = joystick.get_axis(2)
    y_right = joystick.get_axis(3)

    direction_left = get_direction(x_left, y_left)
    if direction_left != prev_state["axes"]["left_stick"]:
        if direction_left:
            events["left_stick"] = direction_left

    direction_right = get_direction(x_right, y_right)
    if direction_right != prev_state["axes"]["right_stick"]:
        if direction_right:
            events["right_stick"] = direction_right

    # Guardamos coordenadas
    events["axes"]["left_stick"] = (x_left, y_left)
    events["axes"]["right_stick"] = (x_right, y_right)

    # Gatillos L2 y R2
    lt_val = joystick.get_axis(4)
    rt_val = joystick.get_axis(5)

    lt_pressed = trigger_pressed(lt_val)
    rt_pressed = trigger_pressed(rt_val)

    if lt_pressed != prev_state["L2"]:
        events["L2"] = "pressed" if lt_pressed else "released"
        if lt_pressed and hasattr(joystick, "rumble"):
            joystick.rumble(0.8, 0.8, 500)
            events["vibration"].append("L2")

    if rt_pressed != prev_state["R2"]:
        events["R2"] = "pressed" if rt_pressed else "released"
        if rt_pressed and hasattr(joystick, "rumble"):
            joystick.rumble(0.8, 0.8, 500)
            events["vibration"].append("R2")

    # Botones
    for i in range(joystick.get_numbuttons()):
        btn = joystick.get_button(i)
        if btn != prev_state["buttons"].get(i, 0):
            state = "pressed" if btn else "released"
            btn_name = BUTTON_MAP.get(i, f"button_{i}")
            events["buttons"][btn_name] = state

    return events, {
        "left_stick": direction_left,
        "right_stick": direction_right,
        "L2": lt_pressed,
        "R2": rt_pressed,
        "buttons": {i: joystick.get_button(i) for i in range(joystick.get_numbuttons())},
        "axes": {
            "left_stick": (x_left, y_left),
            "right_stick": (x_right, y_right),
        }
    }
