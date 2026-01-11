#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Button, Color
from pybricks.tools import wait, StopWatch
import config
import hardware
import actions

# --- MAIN EXECUTION ---
try:
    # 1. INITIALIZE
    actions.initialize_robot()
    
    # 2. START IMMEDIATELY
    mission_timer = StopWatch()
    mission_timer.reset()
    
    # Map & State Variables
    next_station = 1
    corners_passed = 0
    stn1_required_corners = 3 
    
    # Detection Variables
    white_start_dist = -1
    last_corner_finish_dist = -200
    station_consecutive_count = 0
    
    # 🆕 DYNAMIC COOLDOWN SETUP
    station_departure_time = -5000 
    current_cooldown = 1000  # Default 1s
    
    # Trash State
    held_item = "None" 
    
    print("--- MISSION STARTED ---")
    print("Format: Color | Reflection | Object Distance")

    while True:
        if Button.CENTER in hardware.ev3.buttons.pressed(): break
        
        # 1. READ SENSORS
        col = hardware.line_sensor.color()
        ref = hardware.line_sensor.reflection()
        curr_dist = hardware.robot.distance()
        obj_dist = hardware.obstacle_sensor.distance() 
        
        # 🔍 DEBUG LOGS
        print(str(col) + " | Ref: " + str(ref) + " | Dist: " + str(obj_dist))
        
        # 2. ULTRASONIC OBJECT DETECTION
        if obj_dist < 50 and held_item == "None":
            print(">>> OBJECT DETECTED: " + str(obj_dist) + "mm")
            held_item, trash_col, trash_ref = actions.pick_and_drop()
            hardware.robot.reset()
            last_corner_finish_dist = -200
            print(">>> HOLDING: " + held_item)

        # 3. STRICT LINE FOLLOWING
        turn_rate = (ref - config.THRESHOLD) * config.TURN_GAIN
        current_speed = config.DRIVE_SPEED
        
        # 4. CORNER COUNTING
        if (curr_dist - last_corner_finish_dist > config.CORNER_COOLDOWN):
            if ref > config.WHITE_THRESHOLD:
                if white_start_dist == -1: white_start_dist = curr_dist 
                if (curr_dist - white_start_dist) >= config.VALID_WHITE_DIST:
                    corners_passed += 1
                    hardware.ev3.speaker.beep()
                    last_corner_finish_dist = curr_dist
                    white_start_dist = -1 
                    print("\n[#] CORNER {} DETECTED\n".format(corners_passed))
            else:
                white_start_dist = -1 

        # 5. STATION IDENTIFICATION (Dynamic Cooldown)
        is_matching = False
        time_since_departure = mission_timer.time() - station_departure_time
        
        # 🆕 USE VARIABLE COOLDOWN (1s or 3s)
        if time_since_departure > current_cooldown:
            is_matching = actions.check_station(next_station, col, ref)
        
        if is_matching:
            station_consecutive_count += 1
            turn_rate = 0 
        else:
            station_consecutive_count = 0
            
        # 6. STATION ARRIVAL
        if station_consecutive_count >= 3:
            hardware.robot.stop()
            print(">>> ARRIVED AT STATION: " + str(next_station))
            
            # A. ANNOUNCE
            if next_station == 1:
                hardware.ev3.speaker.say("Plastic Station")
            elif next_station == 2:
                hardware.ev3.speaker.say("Other Station")
            elif next_station == 3:
                hardware.ev3.speaker.say("Paper Station")
            
            # B. DROP LOGIC
            should_drop = False
            if next_station == 1 and held_item == "Plastic": should_drop = True
            if next_station == 2 and held_item == "Others": should_drop = True
            if next_station == 3 and held_item == "Paper": should_drop = True
            
            if should_drop:
                print(">>> DROPPING ITEM: " + held_item)
                hardware.ev3.speaker.say("Dropping")
                actions.unload_sequence() 
                held_item = "None"
            else:
                print(">>> KEEPING ITEM (Wrong Station)")
                hardware.ev3.speaker.beep()
            
            # C. UPDATE MAP & SET COOLDOWN
            if next_station == 1: 
                next_station = 2
                corners_passed = 0 
                # 🆕 Leaving Plastic Station -> Wait 3 Seconds
                current_cooldown = 5000 
                print(">>> COOLDOWN SET: 5 Seconds")
                
            elif next_station == 2: 
                next_station = 3
                corners_passed = 0
                current_cooldown = 1000 # Normal 1s
                
            elif next_station == 3: 
                next_station = 1
                corners_passed = 0
                current_cooldown = 1000 # Normal 1s
            
            # D. RESET & DEPART
            station_departure_time = mission_timer.time()
            station_consecutive_count = 0
            white_start_dist = -1
            hardware.robot.reset()
            last_corner_finish_dist = -200
            
        else:
            hardware.robot.drive(current_speed, turn_rate)
        
        wait(10)

finally:
    actions.park_and_shutdown()