# mavlink_arm_disarm.py
import time
from pymavlink import mavutil
import ps4_controller

def arm_disarm(master, arm):
    if arm:
        print("Armando drone...")
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0
        )
    else:
        print("Desarmando drone...")
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0
        )

def main():
    joystick = ps4_controller.init_controller()

    # Cambia 'COM12' por tu puerto si es diferente
    master = mavutil.mavlink_connection('COM12', baud=57600)
    master.wait_heartbeat()
    print("Heartbeat recibido.")

    prev_state = {
        "axes": {
            "left_stick": (0.0, 0.0),
            "right_stick": (0.0, 0.0)
        },
        "L2": False,
        "R2": False,
        "buttons": {}
    }

    while True:
        events, prev_state = ps4_controller.get_events(joystick, prev_state)

        # Arm / Disarm según gatillos
        if events["L2"] == "pressed":
            arm_disarm(master, True)
        if events["R2"] == "pressed":
            arm_disarm(master, False)

        time.sleep(0.05)

if __name__ == "__main__":
    main()
