# **ArUco Triggered PX4 Landing**

A ROS 2 \+ OpenCV prototype that detects a specific ArUco marker from a Gazebo camera and commands the PX4 flight controller to perform a normal landing.

## **Overview**

The system follows a simple event-triggered architecture:

| GAZEBO DOWNWARD CAMERA ↓ |
| :---: |
| ROS 2 IMAGE ↓ |
| OPENCV ↓ |
| ARUCO DETECTION ↓ |
| TARGET ID DETECTED ↓ |
| PX4 LAND COMMAND ↓ |
| NORMAL PX4 LANDING  |

The objective of this prototype is to land the drone using PX4 when the ArUco marker is detected.

Once the target marker is detected, the ROS 2 node publishes VEHICLE\_CMD\_NAV\_LAND through the PX4 ROS 2 interface.

## **Features**

* ROS 2 image subscription  
* Gazebo camera integration  
* OpenCV-based ArUco marker detection  
* Detection of a specific target marker ID  
* Automatic PX4 LAND command  
* One-time LAND command protection  
* Real-time camera visualization  
* Compatible with the older OpenCV ArUco API

**System Requirements**

### **Operating System**

* Ubuntu 24.04 LTS

### **Software**

* ROS 2 Jazzy  
* PX4 Autopilot  
* Gazebo  
* Python 3  
* OpenCV  
* cv2.aruco  
* cv\_bridge  
* px4\_msgs


## **Project Structure**

drone\_landing\_project  
│  
├── aruco\_detector.py  
├── generate\_marker.py  
├── marker0.png  
└── README.md

| aruco\_detector.py |
| :---: |

### 

Main ROS 2 node.

It:

1. Receives camera images from Gazebo.  
2. Converts the ROS image into an OpenCV image.  
3. Detects ArUco markers.  
4. Checks whether the detected marker has the target ID.  
5. Sends a PX4 LAND command when the target is detected.

### 

| generate\_marker.py |
| :---: |

Generates the ArUco marker used as the visual target.

### 

| marker0.png |
| :---: |

### 

Generated ArUco marker image.

### **README.md**

Documentation for the project.

# **How the System Works**

## **1\. Gazebo Camera**

The downward-facing camera mounted on the simulated drone provides images of the environment.

The camera topic used by this project is:

**/world/aruco/model/x500\_mono\_cam\_down\_0/link/camera\_link/sensor/camera/image**

The camera image is published through ROS 2\.

## **2\. ROS 2 Image Subscription**

The Python node subscribes to the camera topic:

self.subscription \= self.create\_subscription(  
    Image,  
    self.camera\_topic,  
    self.image\_callback,  
    10  
)

Whenever a new image arrives, ROS 2 calls:

image\_callback()

## **3\. ROS Image → OpenCV Image**

The ROS image is converted using CvBridge:

frame \= self.bridge.imgmsg\_to\_cv2(  
    msg,  
    desired\_encoding='bgr8'  
)

This allows OpenCV to process the camera frame.

## **4\. Grayscale Conversion**

The image is converted to grayscale:

gray \= cv2.cvtColor(  
    frame,  
    cv2.COLOR\_BGR2GRAY  
)

ArUco detection can work on the grayscale image, reducing unnecessary image information.

## **5\. ArUco Detection**

The detector uses an ArUco dictionary:

self.dictionary \= aruco.getPredefinedDictionary(  
    aruco.DICT\_4X4\_50  
)

The image is then processed:

corners, ids, rejected \= aruco.detectMarkers(  
    gray,  
    self.dictionary  
)

The detector returns:

* corners — locations of detected marker corners  
* ids — IDs of detected markers  
* rejected — candidate regions rejected as markers

# **Target Marker**

The system uses marker:

ID \= 0

This is configured using:

self.target\_id \= 0

If the camera detects another marker, such as:

ID \= 5

the landing command is not triggered.

Only:

ID \= 0

triggers landing.

# **PX4 LAND Command**

The most important part of the program is the PX4 command:

msg.command \= VehicleCommand.VEHICLE\_CMD\_NAV\_LAND

The message is published to:

/fmu/in/vehicle\_command

The communication path is:

Python ROS 2 Node  
       ↓  
VehicleCommand  
       ↓  
/fmu/in/vehicle\_command  
       ↓  
PX4  
       ↓  
NAV\_LAND  
       ↓  
PX4 Landing Controller  
       ↓  
Drone Lands

The Python program does **not** directly control the motors.

It simply requests that PX4 perform a normal landing.

# **One-Time Landing Trigger**

The camera may detect the marker in many consecutive frames.

For example:

Frame 1 → ID 0 detected  
Frame 2 → ID 0 detected  
Frame 3 → ID 0 detected  
Frame 4 → ID 0 detected  
...

Sending a LAND command repeatedly is unnecessary.

Therefore the program uses:

self.land\_command\_sent \= False

After detecting the target:

self.send\_land\_command()  
self.land\_command\_sent \= True

This changes the state from:

LAND command not sent  
        ↓  
LAND command sent

Future camera frames will not repeatedly send the command.

# **Installation**

Make sure ROS 2 Jazzy is installed.

Source ROS 2:

source /opt/ros/jazzy/setup.bash

Source the PX4 ROS 2 workspace:

source \~/px4\_ros2\_ws/install/setup.bash

Verify that px4\_msgs is available:

ros2 pkg list | grep px4\_msgs

Expected output:

px4\_msgs

# **Running the Simulation**

## **Terminal 1 — Start PX4 SITL**

cd \~/PX4-Autopilot  
make px4\_sitl gz\_x500\_mono\_cam\_down\_aruco

This starts the PX4 SITL drone and Gazebo simulation.

## **Terminal 2 — Start Micro XRCE-DDS Agent**

MicroXRCEAgent udp4 \-p 8888

This provides the communication bridge between PX4's uORB messaging system and ROS 2 through DDS.

## **Terminal 3 — Source ROS 2**

source /opt/ros/jazzy/setup.bash  
source \~/px4\_ros2\_ws/install/setup.bash

## **Terminal 3 — Run the Detector**

cd \~/drone\_project/stage2  
python3 aruco\_detector.py

The node should start with a message similar to:

ArUco detector started  
Waiting for Gazebo camera...

# **Verifying the Camera Topic**

Check available ROS 2 topics:

ros2 topic list

Look for:

/world/aruco/model/x500\_mono\_cam\_down\_0/link/camera\_link/sensor/camera/image

You can also check the camera publishing rate:

ros2 topic hz /world/aruco/model/x500\_mono\_cam\_down\_0/link/camera\_link/sensor/camera/image

# 

# 

# **Expected Behaviour**

When the target marker is not visible:

SEARCHING FOR MARKER

When the marker is detected:

MARKER DETECTED | ID=0

The node then sends:

VEHICLE\_CMD\_NAV\_LAND

to PX4.

PX4 subsequently performs its normal landing procedure.

# **Important Configuration**

## **Target Marker ID**

Change:

self.target\_id \= 0

if another marker ID should trigger landing.

For example:

self.target\_id \= 5

would make marker ID 5 the landing trigger.

## **ArUco Dictionary**

The detector currently uses:

aruco.DICT\_4X4\_50

The marker being detected must be generated using the **same dictionary**.

For example:

dictionary \= aruco.getPredefinedDictionary(  
    aruco.DICT\_4X4\_50  
)

Using a different dictionary for generation and detection can cause the marker not to be recognized.

# **Troubleshooting**

## **ModuleNotFoundError: No module named 'px4\_msgs'**

Source the ROS 2 environments:

source /opt/ros/jazzy/setup.bash  
source \~/px4\_ros2\_ws/install/setup.bash

Then check:

ros2 pkg list | grep px4\_msgs

If it does not appear, build the workspace:

cd \~/px4\_ros2\_ws  
colcon build \--symlink-install

Then source it again:

source /opt/ros/jazzy/setup.bash  
source \~/px4\_ros2\_ws/install/setup.bash

## **Marker is not detected**

Check that:

1. The camera topic is correct.  
2. The marker is visible in the camera.  
3. The marker dictionary matches the detector.  
4. The marker ID is correct.  
5. Lighting/contrast is sufficient.  
6. The camera is actually publishing images.

Check the topic:

ros2 topic list

Check the frame rate:

ros2 topic hz /world/aruco/model/x500\_mono\_cam\_down\_0/link/camera\_link/sensor/camera/image

## **LAND command does not execute**

The LAND command being published does not guarantee that PX4 will accept it under every vehicle/simulation state.

Check:

* PX4 is running.  
* The vehicle is armed when required.  
* PX4 is receiving commands.  
* The vehicle is in a state in which landing is permitted.  
* The PX4 ROS 2/DDS connection is active.

# **Future Development**

The next stage can extend this trigger-based system into a true precision-landing pipeline:

SEARCH  
  ↓  
ACQUIRE MARKER  
  ↓  
LOCK TARGET  
  ↓  
ESTIMATE RELATIVE POSITION  
  ↓  
HORIZONTAL ALIGNMENT  
  ↓  
DESCENT  
  ↓  
CONTINUOUS CORRECTION  
  ↓  
LAND

Potential future improvements include:

* Marker position estimation  
* Camera calibration  
* Pixel-to-metric conversion  
* Body-frame coordinate transformation  
* Velocity-based control  
* PX4 Offboard control  
* Marker-loss recovery  
* Search behaviour  
* Multiple marker handling  
* Landing verification  
* PX4-native precision landing interfaces

# 

# 

# 

# **Summary**

This project implements a minimal autonomous landing trigger:

ArUco ID 0 detected  
        ↓  
ROS 2 publishes VehicleCommand  
        ↓  
PX4 receives VEHICLE\_CMD\_NAV\_LAND  
        ↓  
PX4 performs normal landing

The key principle is:

**ArUco detection decides WHEN to land; PX4 decides HOW to land.**

---

