# stabilize_mode.py
import time
from pymavlink import mavutil
import ps4_controller  # Tu script funcional de mapeo

# --- Constantes ---
THROTTLE_MIN = 1000
THROTTLE_MAX = 2000
THROTTLE_STEP = 5      # Cuánto sube/baja por ciclo
THROTTLE_INITIAL = 1000  # Valor inicial seguro > 1200
EMA_ALPHA = 0.3  # Suavizado exponencial
DEADZONE = 0.05  # Zona muerta para ejes

# --- Funciones auxiliares ---
def apply_deadzone(value, deadzone=DEADZONE):
    return 0.0 if abs(value) < deadzone else value

def expo_curve(value, expo=0.4):
    return value * (1 - expo) + (value ** 3) * expo

# Escala para otros ejes (roll, pitch, yaw)
def scale_joystick(value):
    curved = expo_curve(value)
    return int(1500 + (curved * 500))

def arm_disarm(master, arm):
    cmd = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
    param1 = 1 if arm else 0
    print("Armando..." if arm else "Desarmando...")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        cmd,
        0,
        param1, 0, 0, 0, 0, 0, 0
    )

def send_rc_override(master, roll, pitch, throttle, yaw):
    master.mav.rc_channels_override_send(
        master.target_system,
        master.target_component,
        roll, pitch, throttle, yaw,
        0, 0, 0, 0
    )

def main():
    joystick = ps4_controller.init_controller()
    master = mavutil.mavlink_connection('COM12', baud=57600)
    master.wait_heartbeat()
    print("Heartbeat recibido. Control listo.")

    prev_state = {
        "axes": {
            "left_stick": (0.0, 0.0),
            "right_stick": (0.0, 0.0)
        },
        "L2": False,
        "R2": False,
        "buttons": {}
    }

    throttle_pwm = THROTTLE_INITIAL

    # Variables suavizadas
    smoothed_rx, smoothed_ry, smoothed_lx = 0.0, 0.0, 0.0

    while True:
        events, prev_state = ps4_controller.get_events(joystick, prev_state)

        # Armado con L2
        if events["L2"] == "pressed":
            arm_disarm(master, True)

        # Desarmado con R2
        if events["R2"] == "pressed":
            arm_disarm(master, False)

        lx, ly = prev_state["axes"]["left_stick"]   # ly controla throttle
        rx, ry = prev_state["axes"]["right_stick"]  # rx/ry controlan yaw/pitch

        # Aplicar zona muerta
        lx = apply_deadzone(lx)
        ly = apply_deadzone(ly)
        rx = apply_deadzone(rx)
        ry = apply_deadzone(ry)

        # Suavizado EMA
        smoothed_rx = EMA_ALPHA * rx + (1 - EMA_ALPHA) * smoothed_rx
        smoothed_ry = EMA_ALPHA * ry + (1 - EMA_ALPHA) * smoothed_ry
        smoothed_lx = EMA_ALPHA * lx + (1 - EMA_ALPHA) * smoothed_lx

        # --- Acelerador progresivo con ly ---
        if ly < -0.1:  # Mover stick hacia arriba → acelerar
            throttle_pwm = min(THROTTLE_MAX, throttle_pwm + THROTTLE_STEP)
        elif ly > 0.1:  # Mover stick hacia abajo → desacelerar
            throttle_pwm = max(THROTTLE_MIN, throttle_pwm - THROTTLE_STEP)

        roll  = scale_joystick(smoothed_rx)
        pitch = scale_joystick(-smoothed_ry)
        yaw   = scale_joystick(smoothed_lx)

        send_rc_override(master, roll, pitch, throttle_pwm, yaw)

        time.sleep(0.01)  # tiempo1 > 0.05

if __name__ == "__main__":
    main()
