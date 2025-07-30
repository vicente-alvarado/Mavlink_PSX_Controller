# stabilize_mode.py
import time
from pymavlink import mavutil
import ps4_controller  # Tu script funcional de mapeo

# --- Constantes ---
THROTTLE_MIN = 1000
THROTTLE_MAX = 2000
THROTTLE_STEP = 5      # Cuánto sube/baja por ciclo
THROTTLE_INITIAL = 1000  # Valor inicial seguro > 1200

# Escala para otros ejes (roll, pitch, yaw)
def scale_joystick(value):
    return int(1500 + (value * 500))

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

        # --- Acelerador progresivo con ly ---
        if ly < -0.2:  # Mover stick hacia arriba → acelerar. Zona muerta> -0.2
            throttle_pwm = min(THROTTLE_MAX, throttle_pwm + THROTTLE_STEP)
        elif ly > 0.2:  # Mover stick hacia abajo → desacelerar. Zona muerta> 0.2
            throttle_pwm = max(THROTTLE_MIN, throttle_pwm - THROTTLE_STEP)
        # Si está entre -0.2 y 0.2, se mantiene constante

        roll  = scale_joystick(rx)
        pitch = scale_joystick(-ry)
        yaw   = scale_joystick(lx)

        send_rc_override(master, roll, pitch, throttle_pwm, yaw)

        time.sleep(0.02) #tiempo1> 0.05

if __name__ == "__main__":
    main()
