import os

import launch.conditions
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import OpaqueFunction

# def evaluate_waypoint_parameters(context, *args, **kwargs):
#     waypoints_file_path = LaunchConfiguration('waypoints_file').perform(context)
#     waypoints_x = "[ ]"
#     waypoints_y = "[ ]"
#     with open(waypoints_file_path, 'r') as f:
#         for line in f.readlines():
#             if "waypoints_x" in line:
#                 waypoints_x = line.split(":")[1]
#             if "waypoints_y" in line:
#                 waypoints_y = line.split(":")[1]

#     return [
#         DeclareLaunchArgument('waypoints_x', description="List of waypoint x coordinates. Will override waypoints_file is specified.", default_value=waypoints_x),
#         DeclareLaunchArgument('waypoints_y', description="List of waypoint y coordinates. Will override waypoints_file is specified.", default_value=waypoints_y),
#     ]

def generate_launch_description():

    # use_sim_time = LaunchConfiguration('use_sim_time')
    # display_type = LaunchConfiguration('display_type')

    # robot_description = LaunchConfiguration('robot_description')

    launch_description = LaunchDescription([

        # Elevation Grid
        DeclareLaunchArgument('use_elevation', default_value='False', description="Elevation grid - To use elevation or slope value when making occupancy grid based on heightmap."),
        DeclareLaunchArgument('slope_threshold', default_value='0.5', description="Elevation grid - Threshold within which next waypoint selected."),
        DeclareLaunchArgument('grid_height', default_value='200.0', description="Elevation grid - Grid height."),
        DeclareLaunchArgument('grid_width', default_value='200.0', description="Elevation grid - Grid width."),
        DeclareLaunchArgument('grid_llx', default_value='-100.0', description="Elevation grid - X coordinate grid bottom left anchor point."),
        DeclareLaunchArgument('grid_lly', default_value='-100.0', description="Elevation grid - Y coordinate grid bottom left anchor point."),
        DeclareLaunchArgument('grid_res', default_value='0.5', description="Elevation grid - Grid resolution in meters."),
        DeclareLaunchArgument('grid_dilate', default_value='False', description="Elevation grid - Whether or not to apply dilation."),
        DeclareLaunchArgument('grid_dilate_x', default_value='2.0', description="Elevation grid - Amount of dilation in x."),
        DeclareLaunchArgument('grid_dilate_y', default_value='2.0', description="Elevation grid - Amount of dilation in y."),
        DeclareLaunchArgument('grid_dilate_proportion', default_value='0.8', description="Elevation grid - Proportion of original grid cell to dilate with."),
        DeclareLaunchArgument('cull_lidar', default_value='False', description="Elevation grid - Cull lidar points flag based on distance from odometry."),
        DeclareLaunchArgument('cull_lidar_dist', default_value='90.0', description="Elevation grid - Distance used to cull lidar points"),
        DeclareLaunchArgument('use_registered', default_value='False', description="Elevation grid - If true, assumes lidar points are in world coordinates. Else assumes in robot odom coordinates."),
        DeclareLaunchArgument('stitch_lidar_points', default_value='False', description="Elevation grid - If true, lidar scans will be stitched together. Else, each point cloud 2 message will be independent and the grid will be cleared between messages."),
        DeclareLaunchArgument('filter_highest_lidar', default_value='False', description="Elevation grid - If true, the highest point in each cell will be ignored and the second highest will be used for the slope calculations. If false, the highest point will be used."),


        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher',
            arguments=["0", "0", "0", "0", "0", "0", "map", "odom"]),

        Node(
            package='avt_341',
            executable='avt_341_perception_node',
            name='perception_node',
            output='screen',
            parameters=[{
                'use_elevation': launch.substitutions.LaunchConfiguration('use_elevation'),
                'slope_threshold': launch.substitutions.LaunchConfiguration('slope_threshold'),
                'grid_height': launch.substitutions.LaunchConfiguration('grid_height'),
                'grid_width': launch.substitutions.LaunchConfiguration('grid_width'),
                'grid_llx': launch.substitutions.LaunchConfiguration('grid_llx'),
                'grid_lly': launch.substitutions.LaunchConfiguration('grid_lly'),
                'grid_res': launch.substitutions.LaunchConfiguration('grid_res'),
                'overhead_clearance': 7.0,
                'grid_dilate': launch.substitutions.LaunchConfiguration('grid_dilate'),
                'grid_dilate_x': launch.substitutions.LaunchConfiguration('grid_dilate_x'),
                'grid_dilate_y': launch.substitutions.LaunchConfiguration('grid_dilate_y'),
                'grid_dilate_proportion': launch.substitutions.LaunchConfiguration('grid_dilate_proportion'),
                'cull_lidar': launch.substitutions.LaunchConfiguration('cull_lidar'),
                'cull_lidar_dist': launch.substitutions.LaunchConfiguration('cull_lidar_dist'),
                'warmup_time': 5.0,
                'use_registered': launch.substitutions.LaunchConfiguration('use_registered'),
                #'display': display_type,
                'stitch_lidar_points': launch.substitutions.LaunchConfiguration('stitch_lidar_points'),
                'filter_highest_lidar': launch.substitutions.LaunchConfiguration('filter_highest_lidar')
            }],
            remappings=[
                # ("/scan","avt_341/points"),
                # ("diff_cont/odom","avt_341/odometry" ),
                # ("avt_341/points", "/scan"),
                # ("avt_341/odometry","diff_cont/odom"),
                # (,"avt_341/occupancy_grid"),
                # (,"avt_341/segmentation_grid")

            ]
        )
  
   
    ])

    return launch_description
