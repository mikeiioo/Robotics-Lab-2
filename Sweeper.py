from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
import math as m

robot = Create3(Bluetooth())  # Put robot name here.

# --------------------------------------------------------
# Global Variables - feel free to add your own as necessary
# --------------------------------------------------------
ROBOT_TOUCHED = False

# Behavioral
HAS_COLLIDED = False     # The robot has collided with a wall.
HAS_EXPLORED = False     # The robot has finished exploring the box.
HAS_SWEPT = False        # The robot has finished sweeping and
                         # has arrived at its final destination.

# Spatial Awareness
SENSOR2CHECK = 0         # Index of the sensor for the closest side wall,
                         # either 0 for left-most or -1 for right-most.
ROTATION_DIR = ""        # Direction the robot needs to explore.
CORNERS = []             # List to store all corners as the robot explores.
DESTINATION = ()         # Point farthest from the robot, set as final destination.
FINAL_D = False          # Indicates if the robot reached the end.
TURN_NUM = 0

# Constants - Do not change.
ARRIVAL_THRESHOLD = 5    # Robot has arrived if distance to final destination
                         # is less than or equal to this value.
SPEED = 10               # Speed at which the robot should normally move.
ROBOT_MOVE_DISTANCE = 15 # Distance for moving sideways to sweep a new column.

# --------------------------------------------------------
# Implement these three helper functions so that they
# can be used later on.
# --------------------------------------------------------

# Helper Function 1
def farthestDistance(currPosition, positions):
    """Finds the point farthest from currPosition."""
    theTup = ()
    bigD = 0
    x1, y1 = currPosition
    for x2, y2 in positions:
        distance = m.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if distance > bigD:
            bigD = distance
            theTup = (x2, y2)
    return theTup

# Helper Function 2
def movementDirection(readings):
    """Determines movement direction based on IR readings."""
    if readings[0] < readings[-1]:
        return "counterclockwise"
    else:
        return "clockwise"

# Helper Function 3
def checkPositionArrived(current_position, destination, threshold):
    """Checks if robot has arrived within a threshold distance."""
    x1, y1 = current_position
    x2, y2 = destination 
    distance = m.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance <= threshold

# Helper Function 4
def turn(ROTATION_DIR):
    global TURN_NUM
    TURN_NUM += 1
    if ROTATION_DIR == "right":
        return "right" if TURN_NUM % 2 == 1 else "left"
    else:
        return "left" if TURN_NUM % 2 == 1 else "right"

# --------------------------------------------------------
# Implement robot stop and red light on button or bumper press.
# --------------------------------------------------------

# EITHER BUTTON
@event(robot.when_touched, [True, True])  # User buttons: [(.), (..)]
async def when_either_button_touched(robot):
    global ROBOT_TOUCHED 
    ROBOT_TOUCHED = True

# EITHER BUMPER
@event(robot.when_bumped, [True, True])  # [left, right]
async def when_either_bumped(robot):
    global ROBOT_TOUCHED 
    ROBOT_TOUCHED = True

# --------------------------------------------------------
# Main function to set up navigation, exploration, and sweeping.
# --------------------------------------------------------

@event(robot.when_play)
async def play(robot):
    global HAS_COLLIDED, HAS_EXPLORED, HAS_SWEPT, SENSOR2CHECK
    global ROTATION_DIR, CORNERS, DESTINATION, ARRIVAL_THRESHOLD
    global SPEED, ROBOT_MOVE_DISTANCE, FINAL_D
  
    await robot.reset_navigation() 
    readings = (await robot.get_ir_proximity()).sensors
    movement = movementDirection(readings)
    ROTATION_DIR = "right" if movement == "clockwise" else "left"
    SENSOR2CHECK = 0 if ROTATION_DIR == "right" else -1
    await robot.set_wheel_speeds(SPEED, SPEED)
      
    while not ROBOT_TOUCHED: 
        if not HAS_EXPLORED:
            await robot.set_lights_rgb(101, 197, 181) 
            await explore(robot)
        elif HAS_EXPLORED and not HAS_SWEPT:
            await robot.set_lights_rgb(255, 64, 0)
            await sweep(robot)
        if ROBOT_TOUCHED:
            await robot.set_wheel_speeds(0, 0)
            await robot.set_lights_rgb(255, 0, 0)
        if FINAL_D:
            break

# --------------------------------------------------------
# Exploration function to navigate the area.
# --------------------------------------------------------

async def explore(robot):
    global HAS_COLLIDED, HAS_EXPLORED, HAS_SWEPT, SENSOR2CHECK
    global ROTATION_DIR, CORNERS, DESTINATION, ARRIVAL_THRESHOLD
    global SPEED, ROBOT_MOVE_DISTANCE, FINAL_D
  
    readings = (await robot.get_ir_proximity()).sensors
    front_proximity = 4095 / (readings[3] + 1)
    side_proximity = 4095 / (readings[SENSOR2CHECK] + 1)
  
    if front_proximity < 10:
        await robot.set_wheel_speeds(0, 0)
        pos = await robot.get_position()
        currPosition = (pos.x, pos.y)
        CORNERS.append(currPosition)
        
        if len(CORNERS) != 4:
            await (robot.turn_right if ROTATION_DIR == "right" else robot.turn_left)(90)
            await robot.set_wheel_speeds(SPEED, SPEED)
        else:
            DESTINATION = farthestDistance(currPosition, CORNERS)
            print(f"{DESTINATION} is the farthest corner from the robot.")
            HAS_EXPLORED = True

    if side_proximity < 5:
        await (robot.turn_right if ROTATION_DIR == "right" else robot.turn_left)(3)
    elif side_proximity >= 10:
        await (robot.turn_left if ROTATION_DIR == "right" else robot.turn_right)(3)

# --------------------------------------------------------
# Sweeping function to navigate to final destination.
# --------------------------------------------------------

async def sweep(robot):
    global HAS_COLLIDED, HAS_EXPLORED, HAS_SWEPT, SENSOR2CHECK
    global ROTATION_DIR, CORNERS, DESTINATION, ARRIVAL_THRESHOLD
    global SPEED, ROBOT_MOVE_DISTANCE, FINAL_D
  
    readings = (await robot.get_ir_proximity()).sensors
    front_proximity = 4095 / (readings[3] + 1)
  
    pos = await robot.get_position()
    current_position = (pos.x, pos.y)
    if checkPositionArrived(current_position, DESTINATION, ARRIVAL_THRESHOLD):
        await robot.set_wheel_speeds(0, 0)
        await robot.set_lights_spin_rgb(0, 255, 0)
        await robot.set_lights_rgb(0, 255, 0)
        await robot.play_note(Note.C5, 0.5)
        await robot.play_note(Note.E5, 0.5)
        await robot.play_note(Note.G5, 0.5)
        await robot.play_note(Note.C6, 1.0)
        HAS_SWEPT = True
    else:
        if front_proximity <= 10:
            turning = turn(ROTATION_DIR)
            await (robot.turn_right if turning == "right" else robot.turn_left)(90)
            await robot.move(min(ROBOT_MOVE_DISTANCE, front_proximity / 3))
            await (robot.turn_right if turning == "right" else robot.turn_left)(90)
            await robot.set_wheel_speeds(SPEED, SPEED)

# Start the robot
robot.play()
