

def angleOfClosestWall(readings):
    """Remember that this function can be autograded!"""
    IR_ANGLES = [-65.3, -38.0, -20.0, -3.0, 14.25, 34.0, 65.3]
    angle = 0
    distance = 0
    final_distance = 0
    
    for i in range(len(readings)):
        if readings[i] > distance:
            distance = readings[i]
            angle = IR_ANGLES[i]

    final_distance = 4095/(distance + 1)
    final_distance = round(final_distance, 3)

    return (final_distance, angle)


def calculateReflectionAngle(angle):
    """Remember that this function can be autograded!"""
    reflection = 0
    direction = ""
    if angle > 0:
       reflection = 180 - (2 * angle)
       direction = "left"
       
    else:
        reflection = 180 + (2 * angle)
        direction = "right"

    reflection = round(reflection, 3)

    return (direction, reflection)
