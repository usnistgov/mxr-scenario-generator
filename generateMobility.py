
#  NIST-developed software is provided by NIST as a public service. You may use,
#  copy and distribute copies of the software in any medium, provided that you
#  keep intact this entire notice. You may improve,modify and create derivative
#  works of the software or any portion of the software, and you may copy and
#  distribute such modifications or works. Modified works should carry a notice
#  stating that you changed the software and should note the date and nature of
#  any such change. Please explicitly acknowledge the National Institute of
#  Standards and Technology as the source of the software.
 
#  NIST-developed software is expressly provided "AS IS." NIST MAKES NO
#  WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF
#  LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT
#  AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE
#  OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT
#  ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY
#  REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF,
#  INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY,
#  OR USEFULNESS OF THE SOFTWARE.
 
#  You are solely responsible for determining the appropriateness of using and
#  distributing the software and you assume all risks associated with its use,
#  including but not limited to the risks and costs of program errors,
#  compliance with applicable laws, damage to or loss of data, programs or
#  equipment, and the unavailability or interruption of operation. This
#  software is not intended to be used in any situation where a failure could
#  cause risk of injury or damage to property. The software developed by NIST
#  employees is not subject to copyright protection within the United States.
 


import random
import numpy as np
import math
import csv
import os
import json
import shutil




numberOfScenarioToGenerate = 10
nbTimeStep = 595
nbMobileSta = 1
jsonFolder = "JSON"
textFolder = "Input"
scenariosFolder = "surgeryScenarios"
patientLimb = [-3.03,-3.04,0.99]
screenSurgeon = [-3.81,-0.09,1.66]
focus_interval = 100
rotation_steps = 10
focus_duration = 30
staHeight = 1.75

# Initial AP coordinates for each scenario
initial_ap_coordinates = [
    [-5.75, -0.01, 2.7],
    [-5.75, -2.73, 2.7],
    [-5.75, -5.47, 2.7],
    [-2.875, -0.01, 2.7],
    [-2.875, -2.73, 2.7],
    [-2.875, -5.47, 2.7],
    [-0.01, -0.01, 2.7],
    [-0.01, -2.73, 2.7],
    [-0.01, -5.47, 3],
    [-3.13, -3.16, 2.7],
]

# Normalize the angle difference to be within [-π, π]
def normalize_angle_difference(diff):
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

# Calculate the rotation between two points
def calculate_rotation(node_a, node_b):
    vector_ab = [node_a[0] - node_b[0], node_a[1] -
                 node_b[1], node_a[2] - node_b[2]]

    # Calculate the length of the vector from Node B to Node A
    dist_ab = math.sqrt(vector_ab[0]**2 + vector_ab[1]**2 + vector_ab[2]**2)

    # Calculate the yaw (rotation around the z-axis), pitch (rotation around the x-axis), and roll (rotation around the y-axis)
    yaw = math.atan2(vector_ab[1], vector_ab[0])
    pitch = math.atan2(-vector_ab[2], dist_ab)
    roll = math.atan2(math.sin(yaw)*vector_ab[0] - math.cos(
        yaw)*vector_ab[1], -math.sin(yaw)*vector_ab[1] - math.cos(yaw)*vector_ab[0])
    return (yaw, 0, pitch)


# Class for AP
class AccessPoint:
    def __init__(self, x, y, z, yaw, roll, pitch):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.roll = roll
        self.pitch = pitch

# Class for STA
class MovingSTA:
    def __init__(self, x, y, z, yaw, roll, pitch, ap):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.roll = roll
        self.pitch = pitch
        self.ap = ap
        self.vx = 0  
        self.vy = 0 

# Main loop for generating scenarios
for idScenario in range(numberOfScenarioToGenerate):

    # AP1 = AccessPoint(-5.75,-2.85,2.70,0, 0, 0)
    xAp,yAp,zAp = initial_ap_coordinates[idScenario]
    AP1 = AccessPoint( xAp,yAp,zAp ,0, 0, 0)
    
    rotation_phase = 0  # 0: Focusing on patientLimb, 1: Transition, 2: Focusing on screenSurgeon

    stationary_stas = []
  

    # Generate coordinates for moving STAs
    moving_stas = []
    staAllCoordinates = []
    staAllRotations = []
    # keep track of STAs for each AP
    ap_stas = {AP1: []}
    listAp = [AP1]
    # keep track of STA counts for each AP
    ap_stas_counts = {AP1: 0}
    for i in range(nbMobileSta):   
        x = -2.75
        y = -2.5
        z = staHeight
        ap = 0
        yaw, pitch, roll = calculate_rotation(patientLimb, [x, y, z])
        sta = MovingSTA(x, y, z, yaw, pitch, roll, ap)

        # Add STA to list of moving STAs
        sta_itself = []
        sta_itself.append(sta)
        moving_stas.append(sta_itself)

        aStaCoordinate = []
        aStaCoordinate.append([x, y, z])
        staAllCoordinates.append(aStaCoordinate)

        aStaRotation = []
        aStaRotation.append([yaw, pitch, roll])
        staAllRotations.append(aStaRotation)

    for i in range(nbTimeStep-1):
        for idSta in range(nbMobileSta):
            new_x = moving_stas[idSta][i].x + random.uniform(-0.01, 0.01)
        new_x = moving_stas[idSta][i].x + random.uniform(-0.01, 0.01)
        new_y = moving_stas[idSta][i].y + random.uniform(-0.01, 0.01)
        
        cycle_pos = i % (focus_interval + 2*rotation_steps + focus_duration)

        if 0 <= cycle_pos < focus_interval:
            # Focusing on patientLimb
            desired_yaw, desired_pitch, desired_roll = calculate_rotation(patientLimb, [new_x, new_y, z])

        elif focus_interval <= cycle_pos < focus_interval + rotation_steps:
            # Transition to screenSurgeon
            start_yaw, _, _ = calculate_rotation(patientLimb, [new_x, new_y, z])
            end_yaw, end_pitch, end_roll = calculate_rotation(screenSurgeon, [new_x, new_y, z])
            alpha = (cycle_pos - focus_interval) / rotation_steps
            yaw_diff = normalize_angle_difference(end_yaw - start_yaw)
            desired_yaw = start_yaw + alpha * yaw_diff
            desired_pitch = (1 - alpha) * moving_stas[idSta][i].pitch + alpha * end_pitch
            desired_roll = (1 - alpha) * moving_stas[idSta][i].roll + alpha * end_roll

        elif focus_interval + rotation_steps <= cycle_pos < focus_interval + rotation_steps + focus_duration:
            # Focusing on screenSurgeon
            desired_yaw, desired_pitch, desired_roll = calculate_rotation(screenSurgeon, [new_x, new_y, z])

        else:
            # Transition back to patientLimb
            start_yaw, _, _ = calculate_rotation(screenSurgeon, [new_x, new_y, z])
            end_yaw, end_pitch, end_roll = calculate_rotation(patientLimb, [new_x, new_y, z])
            alpha = (cycle_pos - focus_interval - rotation_steps - focus_duration) / rotation_steps
            yaw_diff = normalize_angle_difference(end_yaw - start_yaw)
            desired_yaw = start_yaw + alpha * yaw_diff
            desired_pitch = (1 - alpha) * moving_stas[idSta][i].pitch + alpha * end_pitch
            desired_roll = (1 - alpha) * moving_stas[idSta][i].roll + alpha * end_roll

        apId = moving_stas[idSta][i].ap
        newPos = MovingSTA(new_x, new_y, staHeight, desired_yaw, desired_pitch, desired_roll, apId)
        newPos.vx = moving_stas[idSta][i].vx
        newPos.vy = moving_stas[idSta][i].vy
        moving_stas[idSta].append(newPos)
        staAllCoordinates[idSta].append([new_x, new_y, staHeight])
        staAllRotations[idSta].append([desired_yaw, desired_pitch, desired_roll])



    # Define the name of the file to be written
    if not os.path.exists(scenariosFolder):
        os.makedirs(scenariosFolder)

    scenarioFolder = os.path.join(scenariosFolder, str(idScenario))
    if not os.path.exists(scenarioFolder):
        os.makedirs(scenarioFolder)

    if not os.path.exists(os.path.join(
            scenarioFolder, jsonFolder)):
        os.makedirs(os.path.join(
            scenarioFolder, jsonFolder))
    if not os.path.exists(os.path.join(
            scenarioFolder, textFolder)):
        os.makedirs(os.path.join(
            scenarioFolder, textFolder))


    nodePositionFile = os.path.join(
        scenarioFolder, jsonFolder, "NodePositions.json")
 
    with open(nodePositionFile, "w") as f:
        idNode = 0
        for ap in (ap_stas):
           
            coord = np.tile([ap.x, ap.y, ap.z], (nbTimeStep, 1)).tolist()
            rot = np.tile([ap.yaw, ap.roll, ap.pitch],
                          (nbTimeStep, 1)).tolist()
            data = {
                "Node": idNode,
                "Position":  coord,
                "Rotation": rot,
            }

            json.dump(data, f)
            idNode += 1
            f.write("\n")

            fileInput = os.path.join(
                scenarioFolder, textFolder, "NodePosition"+str(idNode-1)+".dat")

            with open(fileInput, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for point in coord:
                    writer.writerow(point)

            fileInput = os.path.join(
                scenarioFolder, textFolder, "NodeRotation"+str(idNode-1)+".dat")
            with open(fileInput, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for point in rot:
                    writer.writerow(point)

        for idSta in range(nbMobileSta):
            # Define the data to be written as a list of dictionaries
            coord = staAllCoordinates[idSta]
            rot = staAllRotations[idSta]
            data = {
                "Node": idNode,
                "Position":  staAllCoordinates[idSta],
                "Rotation": rot,
            }

            json.dump(data, f)
            idNode += 1
            f.write("\n")

            fileInput = os.path.join(
                scenarioFolder, textFolder, "NodePosition"+str(idNode-1)+".dat")
            with open(fileInput, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                # writer.writerow(['x', 'y'])
                for point in coord:
                    writer.writerow(point)

            fileInput = os.path.join(
                scenarioFolder, textFolder, "NodeRotation"+str(idNode-1)+".dat")
            with open(fileInput, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                # writer.writerow(['x', 'y'])
                for point in rot:
                    writer.writerow(point)

    # Handle PAA position file
    paaPositionFile = os.path.join(
        scenarioFolder, jsonFolder, "PAAPosition.json")

    # Write the data to the file
    with open(paaPositionFile, "w") as f:
        idNode = 0
        for ap in (ap_stas):
            # Handle NodePosition.json
            coord = np.tile([ap.x, ap.y, ap.z], (nbTimeStep, 1)).tolist()
            rot = np.tile([ap.yaw, ap.roll, ap.pitch],
                          (nbTimeStep, 1)).tolist()
            data = {
                "Node": idNode,
                "PAA": 0,
                "Centroid": 0,
                "Orientation": [0, 0, 0],
                "Position":  coord,
            }

            json.dump(data, f)
            idNode += 1
            f.write("\n")

        
        for idSta in range(nbMobileSta):
            # Define the data to be written as a list of dictionaries
            coord = staAllCoordinates[idSta]
            data = {
                "Node": idNode,
                "PAA": 0,
                "Centroid": 0,
                "Orientation": [0, 0, 0],
                "Position":  coord,
            }

            json.dump(data, f)
            idNode += 1
            f.write("\n")

    baselineFolder = "baselineScenario" 
    inputFolder = os.path.join(scenarioFolder, textFolder)
    for filename in os.listdir(baselineFolder):
        source_file = os.path.join(baselineFolder, filename)
        destination_file = os.path.join(inputFolder, filename)
        shutil.copy(source_file, destination_file)

