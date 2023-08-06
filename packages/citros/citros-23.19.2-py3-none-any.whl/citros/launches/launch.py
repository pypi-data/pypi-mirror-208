import os
from datetime import datetime
from typing import cast
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, Event
from launch.actions import EmitEvent, ExecuteProcess, IncludeLaunchDescription, DeclareLaunchArgument, OpaqueFunction, RegisterEventHandler, LogInfo, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, LocalSubstitution, TextSubstitution
from launch.event_handlers import (OnExecutionComplete, OnProcessExit,
                                OnProcessIO, OnProcessStart, OnShutdown)
from launch.events import Shutdown, process
from launch.actions import SetLaunchConfiguration
from citros import Citros

################################
# Entrypoint        
################################
def generate_launch_description(batch_run_id, simulation_run_id, timeout):  
    batch_run_id = str(batch_run_id)    
    simulation_run_id = str(simulation_run_id)    
    timeout = str(timeout)    
    
    citros = Citros(batch_run_id, simulation_run_id)
    citros.log.debug("+ generate_launch_description()")
    citros.log.debug(f"batch_run_id: {batch_run_id}")
    citros.log.debug(f"simulation_run_id: {simulation_run_id}")
    citros.log.debug(f"timeout: {timeout}")
    
    resp = citros.checkStatus()
    if not resp:        
        return 
    citros.log.debug("Health-check: OK")
    citros.events.init(batch_run_id=batch_run_id, sid=simulation_run_id, tag="INIT", message="updated config", metadata=None)
    
    ld = LaunchDescription([
        LogInfo(msg='CITROS launch file!')
    ])
    ld.add_action(SetLaunchConfiguration('batch_run_id', batch_run_id))
    ld.add_action(SetLaunchConfiguration('simulation_run_id', simulation_run_id))
    
    batch = citros.batch.get_batch(batch_run_id) 
    # overide TIMEOUT setting.
    timeout_from_client = batch['batchRun']['simulation']['timeout']            
    if (float(timeout_from_client) > 1):
        timeout = str(timeout_from_client)
    ld.add_action(SetLaunchConfiguration('timeout', timeout))  
        
    citros.log.info(f"initializing simulation batch_run_id: {batch_run_id}, simulation_run_id: {simulation_run_id}, timeout: {timeout}")
    
    ################################
    # Arguments        
    ################################
    ld.add_action(DeclareLaunchArgument(
        "log_level",
        default_value=["debug"],
        description="Logging level",
    ))
    
    ld.add_action(DeclareLaunchArgument(
        'batch_run_id',
        description=(
            "Batch Run id"
        ),      
    ))
    
    ld.add_action(DeclareLaunchArgument(
        'simulation_run_id',
        description=(
            "Simulation run id, as part of [sequence]/[simulation.repeats]"
        ),
    ))
    
    ld.add_action(DeclareLaunchArgument(
        'timeout',
        description=(
            "The timeout for the simulation [sec]"
        ),   
        default_value=str(60*60*24*7),   
    ))
    
    ################################
    # RECORDING BAG Proccess 
    ################################ 
    import shutil
    bag_folder = 'tmp/bag' 
    bag_name = 'bag_0.db3'  # default to sqlite3
    
    # delete folder if exists
    try:
        shutil.rmtree(bag_folder)
    except Exception as e:
        # citros.log.exception(e)
        pass

    bag_cmd = ['ros2', 'bag', 'record', '-a', '-o', bag_folder]
    mcap = False
    if mcap:
        bag_cmd.append('-s')
        bag_cmd.append('mcap')
        bag_name = 'bag_0.mcap'
         
    record_proccess = ExecuteProcess(
        cmd=bag_cmd,
        output='screen', 
        log_cmd=True
    )
    ld.add_action(record_proccess)
    
    def handle_done_recording(context, *args, **kwargs):    
        citros.log.debug("handle_done_recording")        
        
        batch_run_id = LaunchConfiguration("batch_run_id").perform(context)  
        simulation_run_id = LaunchConfiguration("simulation_run_id").perform(context)     
                
        citros.log.info("start uploading bag")
        citros.events.stopping(batch_run_id, simulation_run_id, tag="BAG", message="uploading bag", metadata=None)
                
        # send bag to DB        
        bag_resp, batch_text, resp = citros.bag.emit(f"{bag_folder}/{bag_name}", batch_run_id, simulation_run_id, 'google')        
        if bag_resp:
            citros.events.stopping(batch_run_id, simulation_run_id, tag="BAG", message=batch_text, metadata=resp)
        else:
            citros.events.error(batch_run_id, simulation_run_id, tag="BAG", message=batch_text, metadata=None)
        
        bag_resp, batch_text, resp = citros.bag.emit(f"{bag_folder}/{bag_name}", batch_run_id, simulation_run_id, 'postgres')        
        if bag_resp:
            citros.events.stopping(batch_run_id, simulation_run_id, tag="BAG", message=batch_text, metadata=resp)
        else:
            citros.events.error(batch_run_id, simulation_run_id, tag="BAG", message=batch_text, metadata=None)
            
        citros.events.done(batch_run_id, simulation_run_id, tag="DONE", message='done', metadata=resp)    
            
        citros.log.info("done uploading bag")
        
    ld.add_action(RegisterEventHandler(
        OnExecutionComplete(
            target_action=record_proccess,
            on_completion=[
                LogInfo(msg='OnExecutionComplete: Done Recording event'),                    
                OpaqueFunction(function=handle_done_recording),               
            ]
        )
    ))
    
    ld.add_action(RegisterEventHandler(OnProcessExit(
        target_action=record_proccess,
        on_exit=[
            LogInfo(msg='OnProcessExit: Done Recording event'),                    
            OpaqueFunction(function=handle_done_recording),               
        ]
    )))
    
    
    ################################
    # STD LOG on ros events. 
    ################################   
    # Setup a custom event handler for all stdout/stderr from processes.
    # Later, this will be a configurable, but always present, extension to the LaunchService.
    def on_output(event: Event) -> None:                
        # citros.log.info(f"[ROS][{cast(process.ProcessIO, event).process_name}]{event.text.decode()}")
        
        # cast(process.ProcessIO, event).process_name
        for line in event.text.decode().splitlines():
            # citros.log.debug('[{}] {}'.format(cast(process.ProcessIO, event).process_name, line))
            citros.log.info(f"[ROS][{cast(process.ProcessIO, event).process_name}]{line}")

    ld.add_action(RegisterEventHandler(
        OnProcessIO(                
                on_stdout=on_output,
                on_stderr=on_output,
            )
        )
    )
  
    ################################
    # User launch file
    ################################           
    
    def launch_setup(context, *args, **kwargs):
        citros.log.debug("launch_setup")
        batch_run_id = LaunchConfiguration("batch_run_id").perform(context)
        simulation_run_id = LaunchConfiguration("simulation_run_id").perform(context)
                
        # config
        config = citros.params.init_params(batch_run_id, simulation_run_id)
        # send event with the config to CiTROS
        citros.events.starting(batch_run_id=batch_run_id, sid=simulation_run_id, tag="CONFIG", message="updated config", metadata=config)
            
        # launch
        data = citros.utils.get_launch(batch_run_id)
        batch = data["batchRun"]
        if not batch["simulation"]:
            citros.log.error("There is not simulation attached to batch object. aborting.")
            citros.events.error(batch_run_id=batch_run_id, sid=simulation_run_id, tag="ERROR", message="updated config", metadata={})
            # raise 'ERROR - There is not simulation attached to batch object. aborting.'
            return [
                EmitEvent(event=Shutdown(reason='ERROR - There is not simulation attached to batch object. aborting.'))
            ]
        launch = batch["simulation"]["launch"]
        package = launch["package"]
            
        client_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(get_package_share_directory(package["name"]), 'launch'), 
                f"/{launch['name']}"
            ]),
            launch_arguments={}.items(),
        )
        
        citros.log.info("Starting clients launch")
        citros.events.running(batch_run_id=batch_run_id, sid=simulation_run_id, tag="LAUNCH", message="Starting clients launch", metadata=None)
        
        return [
            client_launch
        ]

        # second option. add actions for nodes. 
        # client_launch
        listeners = []
        sub_entities = client_launch.get_sub_entities()
        # citros.log.debug("sub_entities", sub_entities)
        for launchDescription in sub_entities:
            eps = launchDescription.entities         
            for ep in eps:                        
                if type(ep) in [Node, ExecuteProcess]:
                    # citros.log.debug("adding event OnProcessStart")
                    listeners.append(ep)
                    listeners.append(RegisterEventHandler(
                        OnProcessStart(
                            target_action=ep,
                            on_start=[
                                # citros.log.debug(' +++++++++++ OnProcessStart'),
                                LogInfo(msg=" +++++++++++ OnProcessStart")                    
                            ]
                        )
                    ))
                    
                    listeners.append(RegisterEventHandler(
                        OnProcessExit(
                            target_action=ep,
                            on_exit=[
                                LogInfo(msg=" ----------- OnProcessExit")                    
                            ]
                        )
                    ))

        citros.log.debug(f"running {len(listeners)} entities")
        return listeners
      
    ld.add_action(OpaqueFunction(function=launch_setup))
                
    ################################
    # Timeout Events
    ################################  
    def handle_timeout(context, *args, **kwargs):   
        citros.log.debug("handle_timeout")        
        batch_run_id = LaunchConfiguration("batch_run_id").perform(context)  
        simulation_run_id = LaunchConfiguration("simulation_run_id").perform(context)       
        timeout = LaunchConfiguration("timeout").perform(context)
        citros.events.terminating(batch_run_id, simulation_run_id, tag="TIMOUT", message=f"Reached timeout of: { timeout } sec", metadata=None)            
                 
    ld.add_action(
        TimerAction(
            period=LaunchConfiguration("timeout"),
            actions=[LogInfo(msg="---------TIMEOUT---------"), 
                    OpaqueFunction(function=handle_timeout),
                    EmitEvent(event=Shutdown(reason='TIMEOUT'))],
        )
    )

    ################################
    # Exit
    ################################  
    def handle_shutdown(context, *args, **kwargs):   
        citros.log.debug("handle_shutdown")
        batch_run_id = LaunchConfiguration("batch_run_id").perform(context)  
        simulation_run_id = LaunchConfiguration("simulation_run_id").perform(context)            
        reason = LocalSubstitution('event.reason').perform(context)
        citros.events.terminating(batch_run_id, simulation_run_id, tag="SHUTDOWN", message=reason, metadata=None)    

    ld.add_action(RegisterEventHandler(
        OnShutdown(
            on_shutdown=[
                OpaqueFunction(function=handle_shutdown),
                LogInfo(msg=['Launch was asked to shutdown: ', LocalSubstitution('event.reason')]
            )]
        )
    ))
    
    return ld
