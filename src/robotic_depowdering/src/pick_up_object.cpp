#include "rclcpp/rclcpp.hpp"
#include "robotic_depowdering_interfaces/srv/gpd_grasp.hpp"
#include "builtin_interfaces/msg/duration.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"
#include "trajectory_msgs/msg/joint_trajectory_point.hpp"
#include "gpd_interface.hpp"
#include "robotic_depowdering_interfaces/srv/move_to_pose.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "Eigen/Geometry"
#include <flexiv/Robot.hpp>
#include <flexiv/Exception.hpp>
#include <flexiv/Log.hpp>
#include <flexiv/Gripper.hpp>
#include <flexiv/Utility.hpp>

#include <chrono>
#include <cstdlib>
#include <memory>
#include <ctime>
#include <thread>
#include <string>

using namespace std::chrono_literals;

std::shared_ptr<rclcpp::Node> node;

void control_gripper(float grasp_width, float grasp_force = 5.0) {
    std::string robotIP = "192.168.2.100";
    std::string localIP = "192.168.2.105"; // TOOD: update
    flexiv::Robot robot(robotIP, localIP);


    // Clear fault on robot server if any
    if (robot.isFault()) {
        RCLCPP_ERROR(node->get_logger(), "Fault occurred on robot server, trying to clear ...");
        // Try to clear the fault
        robot.clearFault();
        std::this_thread::sleep_for(std::chrono::seconds(2));
        // Check again
        if (robot.isFault()) {
            RCLCPP_ERROR(node->get_logger(), "Fault cannot be cleared, exiting ...");
            return; // TODO: Proper error handling
        }
        RCLCPP_INFO(node->get_logger(), "Fault on robot server is cleared");
    }

    // Enable the robot, make sure the E-stop is released before enabling
    RCLCPP_INFO(node->get_logger(), "Enabling robot ...");
    robot.enable();

    // Wait for the robot to become operational
    while (!robot.isOperational()) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    RCLCPP_INFO(node->get_logger(), "Robot is now operational");

    // Gripper Control
    // =========================================================================================
    // Gripper control is not available if the robot is in IDLE mode, so switch to some mode
    // other than IDLE
    // Instantiate gripper control interface
    flexiv::Gripper gripper(robot);
    RCLCPP_INFO(node->get_logger(), "Closing grip for object");
    gripper.move(grasp_width, 0.02, grasp_force);

    std::this_thread::sleep_for(std::chrono::seconds(5));
    
    RCLCPP_INFO(node->get_logger(), "Opening grip for object");
    gripper.move(0.1, 0.02);
    std::this_thread::sleep_for(std::chrono::seconds(5));
    RCLCPP_INFO(node->get_logger(), "Stopping gripper");
    gripper.stop();
}

// Should this run only once, or multiple times?
// Turn this into an action.
int main(int argc, char** argv) {

    rclcpp::init(argc, argv);

    node = rclcpp::Node::make_shared("pick_up_object_client");
    const auto logger = node->get_logger();

    // Assume all arguments are correctly formed.
    // Will have to change this.
    if (argc < 2) {
        RCLCPP_ERROR(logger, "Usage: ros2 run robotic_depowdering pick_up_object [filename.obj] [x-coord=0.0] [y-coord=0.0] [z-coord=0.0]");
        return -1;
    }

    float obj_x_pos = 0.0f, obj_y_pos = 0.0f, obj_z_pos = 0.0f;
    if (argc >= 3) {
        // x pos set
        obj_x_pos = atof(argv[2]);
    }
    if (argc >= 4) {
        // y pos set
        obj_y_pos = atof(argv[3]);
    }
    if (argc >= 5) {
        // y pos set
        obj_z_pos = atof(argv[4]);
    }

    Eigen::Vector3d test_object_position = {obj_x_pos, obj_y_pos, obj_z_pos};

    std::string test_object_filename = argv[1];

    RCLCPP_INFO(logger, "Test object %s is placed at (%f, %f, %f)", test_object_filename.c_str(), obj_x_pos, obj_y_pos, obj_z_pos);

    auto grasp_config = generateGraspPose(test_object_filename);

    if (!grasp_config) {
        RCLCPP_ERROR(logger, "GPD failed to generate a grasp pose. Check output for details.");
        return -1;
    }

    
    // Offset grasp position to account for objects not placed at origin.
    grasp_config->setPosition(grasp_config->getPosition() + test_object_position);

    const auto GRIPPER_HEIGHT = 0.1165 + 0.0868 - 0.005;
    grasp_config->setPosition(grasp_config->getPosition() - (GRIPPER_HEIGHT * grasp_config->getApproach().normalized()));

    RCLCPP_INFO(logger, "\tposition: <%f, %f, %f>", 
        grasp_config->getPosition().x(), grasp_config->getPosition().y(), grasp_config->getPosition().z());
    RCLCPP_INFO(logger, "\tapproach: <%f, %f, %f>", 
        grasp_config->getApproach().x(), grasp_config->getApproach().y(), grasp_config->getApproach().z());
    RCLCPP_INFO(logger, "\tbinormal: <%f, %f, %f>", 
        grasp_config->getBinormal().x(), grasp_config->getBinormal().y(), grasp_config->getBinormal().z());
    RCLCPP_INFO(logger, "\taxis: <%f, %f, %f>", 
        grasp_config->getAxis().x(), grasp_config->getAxis().y(), grasp_config->getAxis().z());
    RCLCPP_INFO(logger, "\taperture: %f", 
        grasp_config->getGraspWidth());
    RCLCPP_INFO(logger, "\tscore: %f", 
        grasp_config->getScore());

    // Set the target pose for the robot to move to
    auto target_pose = geometry_msgs::msg::Pose();

    // Test grasp:
    //  -0.253032 -0.262199 0.448278 0.001090 0.999790 0.002011 0.020383
    target_pose.position.x = -0.253032; // grasp_config->getPosition().x();
    target_pose.position.y = -0.262199; // grasp_config->getPosition().y();
    target_pose.position.z = 0.448278; // grasp_config->getPosition().z();
    Eigen::Matrix3d rot_mat;
    rot_mat << grasp_config->getAxis().x(), grasp_config->getBinormal().x(), grasp_config->getApproach().x(),
           grasp_config->getAxis().y(), grasp_config->getBinormal().y(), grasp_config->getApproach().y(),
           grasp_config->getAxis().z(), grasp_config->getBinormal().z(), grasp_config->getApproach().z();
    Eigen::Quaternion<double> rot_q(rot_mat);
    rot_q.normalize();
    target_pose.orientation.w = 0.020383; // rot_q.w();
    target_pose.orientation.x = 0.001090; // rot_q.x();
    target_pose.orientation.y = 0.999790; // rot_q.y();
    target_pose.orientation.z = 0.002011; // rot_q.z();

    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Got quaternion w:%f x:%f y:%f z:%f", rot_q.x(), rot_q.y(), rot_q.z(), rot_q.w());
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "%f %f %f %f %f %f %f",
        grasp_config->getPosition().x(), grasp_config->getPosition().y(), grasp_config->getPosition().z(),
        rot_q.x(), rot_q.y(), rot_q.z(), rot_q.w());

    // Create a service client to call the move_to_pose service
    auto client = node->create_client<robotic_depowdering_interfaces::srv::MoveToPose>("move_to_pose");
    while (!client->wait_for_service(std::chrono::seconds(1))) {
        if (!rclcpp::ok()) {
            RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Interrupted while waiting for the service. Exiting.");
            return 0;
        }
        RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Waiting for the service to be available...");
    }

    auto request = std::make_shared<robotic_depowdering_interfaces::srv::MoveToPose::Request>();
    request->target_pose = target_pose;

    auto result = client->async_send_request(request);
    if (rclcpp::spin_until_future_complete(node, result) == rclcpp::FutureReturnCode::SUCCESS) {
        if (result.get()->success) {
            RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Successfully moved to target pose.");
        } else {
            RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Failed to move to target pose.");
        }
    } else {
        RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Failed to call service move_to_pose");
    }



    bool physical_robot = true;
    if (physical_robot){
    control_gripper(grasp_config->getGraspWidth());
    }
    rclcpp::shutdown();
    return 0;
}