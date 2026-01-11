#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Color, Button
from pybricks.tools import wait, StopWatch
import config
from hardware import ev3, robot, line_sensor, obstacle_sensor, left_motor, right_motor
from actions import initialize, shutdown, pick_and_drop, check_station_logic

mission_timer = StopWatch()
current_target_idx = 0
corners_passed = 0
white_start_dist = -1
last_corner_finish_dist = -200
confirm_count = 0

try:
    initialize()
    print("{:<10} | {:<10} | {:<10} | {:<10} | {:<15}".format("Dist", "Color", "Ref", "Obj", "Status"))
    print("-" * 75)
    
    while True:
        target_station = config.STATION_SEQUENCE[current_target_idx % len(config.STATION_SEQUENCE)]
        ref = line_sensor.reflection()
        col = line_sensor.color()
        obj_dist = obstacle_sensor.distance()
        curr_dist = robot.distance()
        
        if obj_dist < 50:
            pick_and_drop()
            robot.reset()
            last_corner_finish_dist = -200
            continue 

        if col == Color.RED:
            robot.drive(config.DRIVE_SPEED, 0)
            status_text = "RED-STRAIGHT"
        elif ref > config.THRESHOLD + 20:
            robot.stop()
            left_motor.run(-20)
            right_motor.run(80)
            status_text = "REV-LEFT"
        else:
            turn_rate = (ref - config.THRESHOLD) * config.TURN_GAIN
            robot.drive(config.DRIVE_SPEED, turn_rate)
            status_text = "FOLLOWING"

        if mission_timer.time() > 5000:
            if (curr_dist - last_corner_finish_dist > config.CORNER_COOLDOWN):
                if ref > config.WHITE_THRESHOLD:
                    if white_start_dist == -1: white_start_dist = curr_dist
                    if (curr_dist - white_start_dist) >= config.VALID_WHITE_DIST:
                        corners_passed += 1
                        ev3.speaker.beep()
                        last_corner_finish_dist = curr_dist
                        white_start_dist = -1 
                        print("\n[#] CORNER {} DETECTED\n".format(corners_passed))
                else:
                    white_start_dist = -1 

        if check_station_logic(target_station, col, ref):
            confirm_count += 1
            if confirm_count >= config.CONFIRM_THRESHOLD:
                robot.stop()
                ev3.speaker.say(target_station)
                robot.settings(straight_speed=config.SLOW_PACE)
                robot.straight(80)
                wait(2000)
                current_target_idx += 1
                confirm_count = 0
        else:
            confirm_count = 0

        print("{:<10.1f} | {:<10} | {:<10} | {:<10} | {:<15}".format(
            curr_dist, str(col), ref, obj_dist, status_text
        ))

        if Button.CENTER in ev3.buttons.pressed(): break
        wait(10)

finally:
    shutdown()