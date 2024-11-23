# Robotic Depowdering Github Repo

## Packages
- ```flexiv_ros2```: contains the Flexiv ROS2 package and RDK, used for interfacing with, controlling and simulating the Flexiv Rizon 4s.
- ```vcpd```: VCPD grasp generation library, extended with FEA-based grasp analysis.
- ```rizon_pick_and_place```: interface to MoveIt! for motion planning and IK.
- ```robotic_depowdering```: nodes and services used in the depowdering process.
- ```robotic_depowdering_interfaces```: message and service definitions used by ```robotic_depowdering```.
## System requirements
This project requires the following software versions:
<table>
  <tr>
    <td>Ubuntu</td>
    <td>ROS2</td>
    <td>Gazebo</td>
  </tr>
  <tr>
    <td>22.04</td>
    <td>Humble</td>
    <td>Fortress</td>
  </tr>
</table>

The following options for which platform you run the software on are supported. Depending on the platform you decide to use to develop for this robot, you'll be able to do the following:
<table>
  <tr>
    <td>Platform</td>
    <td>Simulation of robot in RViz + Gazebo</td>
    <td>Control of physical robot from your host machine</td>
  </tr>
  <tr>
    <td>Native Ubuntu 22.04 install (or dual boot)</td>
    <td>✔️</td>
    <td>✔️</td>
  </tr>
  <tr>
    <td>Ubuntu 22.04 virtual machine (Linux, Windows, Mac)</td>
    <td>✔️</td>
    <td>❌</td>
  </tr>
  <tr>
    <td>Docker container (on Linux, Windows, or Mac)</td>
    <td>✔️</td>
    <td>❌</td>
  </tr>
  <tr>
    <td>WSL2 Ubuntu 22.04</td>
    <td>✔️</td>
    <td>❌</td>
  </tr>
</table>


## Setup
Clone the repo, then follow instructions for your system:
### System-specific instructions
#### Native Ubuntu 22.04 install
Skip this section, and follow the general instructions. Nothing extra needs to be done.
#### Docker Ubuntu 22.04 container
##### 1. Install docker compose
Visit [https://docs.docker.com/engine/install/](https://docs.docker.com/compose/install/) and follow instructions for your specific system.
##### 2. Build the images
```
docker compose build
```
##### 3. Run the images
Launch bash in the development container:
```
docker compose up -d dev
docker compose exec -it dev bash
```
To develop inside the docker container, install the <a href="https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker">VS Code docker extension</a>. Then, you can open VS code and attach to the running Ubuntu 22.04 container and edit the code inside.

#### Ubuntu 22.04 virtual machine
Make sure you have 3D acceleration enabled and enough CPU cores. Aim for at least 4 cores and 6 GB of memory.
#### WSL2 Ubuntu 22.04 instance
Add this environment variable to fix an OpenGL issue with Gazebo:
```
echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc
source ~/.bashrc
```
### General instructions
Follow the installation instructions to install ROS2 Humble and Gazebo Fortress:
- ROS2: <a>https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html</a>
- Gazebo: <a>https://gazebosim.org/docs/fortress/install_ubuntu</a>
Once everything is installed, move onto installing and building this repo.
1. Source ROS underlay: <br>
```
source /opt/ros/humble/setup.sh
```
2. Install dependencies (from packages + petsc4py + dolfinx):<br>
```
rosdep install --from-paths src --ignore-src -r -y
sudo apt install python3-petsc4py python3-dolfinx
```
3. Install dependencies for the Flexiv ROS2 packages:
```
   sudo apt install -y \
   python3-colcon-common-extensions \
   python3-rosdep2 \
   libeigen3-dev \
   ros-humble-xacro \
   ros-humble-tinyxml2-vendor \
   ros-humble-ros2-control \
   ros-humble-realtime-tools \
   ros-humble-control-toolbox \
   ros-humble-moveit \
   ros-humble-ros2-controllers \
   ros-humble-test-msgs \
   ros-humble-joint-state-publisher \
   ros-humble-joint-state-publisher-gui \
   ros-humble-robot-state-publisher \
   ros-humble-rviz2
   ```

4. Setup workspace:

   ```
   cd ~/Robotic_Depowdering/src
   git clone https://github.com/flexivrobotics/flexiv_ros2.git
   cd flexiv_ros2/
   git submodule update --init --recursive --progress
   ```

5. Install dependencies for ```flexiv_ros2``` package:

   ```
   cd ~/Robotic_Depowdering
   rosdep update
   rosdep install --from-paths src --ignore-src --rosdistro humble -r -y
   ```
6. Choose a directory for installing `flexiv_rdk` library and all its dependencies. For example, a new folder named `rdk_install` under the home directory: `~/rdk_install`. Compile and install to the installation directory:

   ```bash
   mkdir ~/rdk_install
   cd ~/Robotic_Depowdering/src/flexiv_ros2/flexiv_hardware/rdk/thirdparty
   bash build_and_install_dependencies.sh ~/rdk_install
   ```

7. Configure and install `flexiv_rdk`:

   ```bash
   cd ~/Robotic_Depowdering/src/flexiv_ros2/flexiv_hardware/rdk
   mkdir build && cd build
   cmake .. -DCMAKE_INSTALL_PREFIX=~/rdk_install
   cmake --build . --target install --config Release
   ```
   
8. Then build everything else: <br>
```
cd ~/Robotic_Depowdering
colcon build --symlink-install
```

## Running
In any terminal where you run code, do: <br>
```
source /opt/ros/humble/setup.sh
source install/setup.sh
```

### VCPD grasping
#### Pre-process objects
> [!IMPORTANT]
> Ensure the parts are at their location in the loop in their CAD file, i.e. if a part is at (1,1,1) then center the part at (1,1,1) in the OBJ.

Run:
```
ros2 run vcpd mesh_processing --ros-args -p mesh_path:=/home/artyom/Robotic_Depowdering/src/robotic_depowdering/test_parts_vcpd/ -p width:=0.1 -p output_path:=/home/artyom/Robotic_Depowdering/src/robotic_depowdering/test_parts_vcpd_urdf
ros2 run vcpd grasp_analysis --ros-args -p mesh_path:=/home/artyom/Robotic_Depowdering/src/robotic_depowdering/test_parts_vcpd_urdf -p config:=/home/artyom/Robotic_Depowdering/src/vcpd/config/config.json -p output_path:=/home/artyom/Robotic_Depowdering/src/vcpd/test_parts_grasps_out -p gui:=false -p verbose:=false
```
Which parts can you not grasp:
- twisted vase (too big)
- TestDonutMedium (too big)
- Side gear (unsure)
To visualize the grasp generation set gui to true.

### Pick up object + visualization
#### With real robot
> [!IMPORTANT]
> Follow the procedure to connect and set up the robot described in <a href="https://docs.google.com/document/d/1rZFnRo6KGYT_emA9AcjmK8JNeBhtwec6_ygwI96AM5s/edit?usp=sharing">the SOP document</a>. Then, move onto these instructions.

> [!CAUTION]
> Don't damage the Rizon. Test your code thoroughly in simulation to ensure it works.
> When running code on the Rizon, always keep your finger on the emergency stop button and don't get distracted. The Rizon is an expensive piece of equipment - don't break it.

Connect robot and power it on. Test connection:
```
ping 192.168.2.100
```
Find your IP address: (look for ```inet``` under ```eth0```):
```
ifconfig
```
In one terminal run:<br>
```
ros2 launch rizon_pick_and_place rizon_pick_and_place.launch.py robot_ip:=192.167.2.100 local_ip:=[your IP]
```
In another terminal run:<br>
```
ros2 launch robotic_depowdering robotic_depowdering.launch.py test_object:=Buckle.obj test_object_x_pos:=0.5 test_object_y_pos:=0.5 test_object_z_pos:=-0.015
```
Replace Buckle.obj with the name of the part you want to use, and the positions with the position of where the part is located. This will make the robot move and pick up the part.<br>

> [!NOTE]
> The robot's base plate is 15 mm thick, so if you place the object flat on the table it will be at z = -0.015.

#### Without robot (just simulation)
In one terminal run:<br>
```
ros2 launch rizon_pick_and_place rizon_pick_and_place.launch.py robot_ip:=dont-care local_ip:=dont-care use_fake_hardware:=true
```
In another terminal run:<br>
```
ros2 launch robotic_depowdering robotic_depowdering.launch.py test_object:=Buckle.obj test_object_x_pos:=0.5 test_object_y_pos:=0.5 test_object_z_pos:=1.0
```
Replace Buckle.obj with the name of the part you want to use, and the positions with the position of where the part is located.
## Test parts
- All test parts are in `src/robotic_depowdering/test_parts`. The obj, stl and binary stl are provided.
- The parts are centered at (0,0,0) in the CAD files - if you place the part at a different location while testing, you pass this location into ```robotic_depowdering.launch.py``` by adjusting the ``` test_object_x_pos```, ```test_object_y_pos```, and ```test_object_z_pos``` parameters, instead of modifying the CAD file.
  - Keep in mind, the Rizon's base plate is 15mm thick. So if you place parts on the ground, and the rizon is on the base plate mounted on the ground, your part's z-coordinate is -0.015.
- The dimensions of the part are in metres. If you want to 3D print a part, then CURA will automatically scale the part up to mm.
