import os
from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import LaunchConfiguration, ThisLaunchFileDir

def generate_launch_description():
    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("husky_description"), "urdf", "husky.urdf.xacro"]
            ),
            " ",
            "name:=husky",
            " ",
            "prefix:=''",
            " ",
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    
    #the cartographer and nav configs 
    namespace = ''
    package_name = 'husky_base'
    use_respawn = False
    use_sim_time = True
    autostart = True
    params_file = os.path.join(get_package_share_directory(package_name),'config','nav2_params.yaml')

    # Nav node
    nav_launch_path = os.path.join(get_package_share_directory(package_name),'launch','navigation_launch.py')
    nav_params_path = os.path.join(get_package_share_directory(package_name),'config','nav2_params.yaml')
    # tree_params_path = os.path.join(get_package_share_directory(package_name),'config','navigate_w_replanning_and_recovery.xml')
    nav_node = IncludeLaunchDescription(PythonLaunchDescriptionSource([nav_launch_path]),
                                        launch_arguments={'namespace': '',
                                                        'use_sim_time': 'true',
                                                        'autostart': 'true',
                                                        'params_file': nav_params_path,
                                                        # 'default_bt_xml_filename': tree_params_path,
                                                        'use_lifecycle_mgr': 'false',
                                                        'map_subscribe_transient_local': 'true'}.items())


    

    # Cartographer node
    # use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    # trailbot_cartographer_prefix = get_package_share_directory(package_name)
    # cartographer_config_dir = LaunchConfiguration('cartographer_config_dir', default=os.path.join(
    #                                               trailbot_cartographer_prefix, 'config'))
    # configuration_basename = LaunchConfiguration('configuration_basename', default='trailbot_lds_2d.lua') 
    # resolution = LaunchConfiguration('resolution', default='0.05')
    # publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')

    # cartographer_node = Node(
    #     package='cartographer_ros',
    #     executable='cartographer_node',
    #     name='cartographer_node',
    #     output='screen',
    #     parameters=[{'use_sim_time': use_sim_time}],
    #     arguments=['-configuration_directory', cartographer_config_dir,
    #                '-configuration_basename', configuration_basename],
    #     remappings=[('/husky_velocity_controller/odom', '/odom')],
    #     # remappings=[('/husky_velocity_controller/odom', '/odom')]
    # )

    # occupancy_grid = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(get_package_share_directory(package_name), 'launch', 'occupancy_grid.launch.py')]),
    #     launch_arguments={'resolution':resolution,
    #                       'publish_period_sec': publish_period_sec}.items(),)

    slam_node = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join('/opt/ros/humble/share/nav2_bringup/launch', 'slam_launch.py')),
            # condition=IfCondition(slam),
    #         launch_arguments={'namespace': namespace,
    #                           'use_sim_time': use_sim_time,
    #                           'autostart': autostart,
    #                           'use_respawn': use_respawn,
    #                           'params_file': params_file}.items()
    # )       
            launch_arguments={'namespace': '',
                              'use_sim_time': 'true',
                              'autostart': 'true',
                              'use_respawn': 'false',
                              'params_file': params_file}.items()
    )

    pc2scan_node = Node(
        package = 'pointcloud_to_laserscan',
        executable = 'pointcloud_to_laserscan_node',
        output = 'screen',
        respawn = use_respawn,
        respawn_delay = 2.0,
        remappings=[('/velodyne_points', '/cloud_in')],

    )

    config_husky_velocity_controller = PathJoinSubstitution(
        [FindPackageShare("husky_control"),
        "config",
        "control.yaml"],
        # remappings=['/husky_velocity_controller/odom', '/odom']

    )

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
        remappings=[('/husky_velocity_controller/odom', '/odom')],
    )

    node_controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, config_husky_velocity_controller],
        output={
            "stdout": "screen",
            "stderr": "screen",
        },
        remappings=[('/husky_velocity_controller/odom', '/odom')],
    )

    spawn_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
        remappings=[('/husky_velocity_controller/odom', '/odom')],
    )

    spawn_husky_velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["husky_velocity_controller"],
        output="screen",
        remappings=[('/husky_velocity_controller/odom', '/odom')],
        
    )

    # Launch husky_control/control.launch.py which is just robot_localization.
    launch_husky_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
        [FindPackageShare("husky_control"), 'launch', 'control.launch.py'])))

    # Launch husky_control/teleop_base.launch.py which is various ways to tele-op
    # the robot but does not include the joystick. Also, has a twist mux.
    launch_husky_teleop_base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
        [FindPackageShare("husky_control"), 'launch', 'teleop_base.launch.py'])))

    # Launch husky_control/teleop_joy.launch.py which is tele-operation using a physical joystick.
    launch_husky_teleop_joy = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
        [FindPackageShare("husky_control"), 'launch', 'teleop_joy.launch.py'])))


    # Launch husky_bringup/accessories.launch.py which is the sensors commonly used on the Husky.
    launch_husky_accessories = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
        [FindPackageShare("husky_bringup"), 'launch', 'accessories.launch.py'])))


    ld = LaunchDescription()
    ld.add_action(node_robot_state_publisher)
    ld.add_action(node_controller_manager)
    ld.add_action(spawn_controller)
    ld.add_action(spawn_husky_velocity_controller)
    ld.add_action(launch_husky_control)
    ld.add_action(launch_husky_teleop_base)
    ld.add_action(launch_husky_teleop_joy)
    ld.add_action(launch_husky_accessories)
    ld.add_action(slam_node)
    # ld.add_action(pc2scan_node)
    # ld.add_action(cartographer_node)
    ld.add_action(nav_node)

    return ld
