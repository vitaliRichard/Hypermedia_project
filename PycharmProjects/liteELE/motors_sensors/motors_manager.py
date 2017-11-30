from threading import Thread
from time import sleep

import motors_sensors.Pins as pins

probo_queue = []
ears_eyes_queue = []


class Proboscis:
    position = 5


def add_to_probo_queue(n_slider):
    probo_queue.append(n_slider)


def add_to_ee_queue(part_to_move, time):
    if part_to_move == "eyes":
        cmd = "on-f"
    elif part_to_move == "ears":
        cmd = "on-b"
    ears_eyes_queue.append({"cmd": cmd, "time": time})


def execute_cmd(motor_number, cmd, time):
    pins.dcMotor(motor_number, cmd)
    sleep(time)
    pins.dcMotor(motor_number, "off")


def scan_probo():
    while 1:
        if len(probo_queue) > 0:
            curr_move = probo_queue.pop(0)
            if curr_move == 5:
                execute_cmd('1', "on-f", 1.5)
            elif curr_move == 1:
                execute_cmd('1', "on-b", 1.5)
            else:
                difference = curr_move - Proboscis.position
                if difference > 0:
                    execute_cmd('1', "on-f", difference * 0.3)
                elif difference < 0:
                    execute_cmd('1', "on-b", -difference * 0.2)
            Proboscis.position = curr_move
        else:
            sleep(0.2)


def scan_ee():
    while 1:
        if len(ears_eyes_queue) > 0:
            curr_elem = ears_eyes_queue.pop(0)
            execute_cmd('2', curr_elem["cmd"], curr_elem["time"])
        else:
            sleep(0.2)


def start_movements_queue():
    execute_cmd(1, 'on-f', 2)
    execute_cmd(2, 'on-b', 2)
    probo = Thread(target=scan_probo)
    ee = Thread(target=scan_ee)
    probo.start()
    ee.start()


add_to_probo_queue(5)
