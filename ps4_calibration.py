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

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick detected: {joystick.get_name()}")

    prev_buttons = [0] * joystick.get_numbuttons()
    prev_direction_left = None
    prev_direction_right = None
    prev_lt = False
    prev_rt = False

    while True:
        pygame.event.pump()

        # Stick izquierdo
        x_left = joystick.get_axis(0)
        y_left = joystick.get_axis(1)
        direction_left = get_direction(x_left, y_left)
        if direction_left != prev_direction_left:
            if direction_left:
                print(f"left_{direction_left}")
            prev_direction_left = direction_left

        # Stick derecho
        x_right = joystick.get_axis(2)
        y_right = joystick.get_axis(3)
        direction_right = get_direction(x_right, y_right)
        if direction_right != prev_direction_right:
            if direction_right:
                print(f"right_{direction_right}")
            prev_direction_right = direction_right

        # Gatillos L2 y R2 (axis 4 y 5)
        lt_val = joystick.get_axis(4)
        rt_val = joystick.get_axis(5)

        lt_pressed = trigger_pressed(lt_val)
        rt_pressed = trigger_pressed(rt_val)

        if lt_pressed != prev_lt:
            state = "pressed" if lt_pressed else "released"
            print(f"L2_{state}")
            if lt_pressed and hasattr(joystick, "rumble"):
                joystick.rumble(0.8, 0.8, 500)
                print("[VIBRATION] Rumble triggered on L2")
            prev_lt = lt_pressed

        if rt_pressed != prev_rt:
            state = "pressed" if rt_pressed else "released"
            print(f"R2_{state}")
            if rt_pressed and hasattr(joystick, "rumble"):
                joystick.rumble(0.8, 0.8, 500)
                print("[VIBRATION] Rumble triggered on R2")
            prev_rt = rt_pressed

        # Botones
        for i in range(joystick.get_numbuttons()):
            btn = joystick.get_button(i)
            if btn != prev_buttons[i]:
                state = "pressed" if btn else "released"
                btn_name = BUTTON_MAP.get(i, f"button_{i}")
                print(f"{btn_name}_{state}")
                prev_buttons[i] = btn

        time.sleep(0.05)

if __name__ == "__main__":
    main()
