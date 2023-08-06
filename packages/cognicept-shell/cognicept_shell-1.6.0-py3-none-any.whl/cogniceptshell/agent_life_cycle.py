# Copyright 2020 Cognicept Systems
# Author: Jakub Tomasek (jakub@cognicept.systems)
# --> AgentLifeCycle handles life cycle of Cognicept Agents

import time
import docker
import boto3
import getpass
import base64
import json
import os
import sys
import subprocess
import dateutil
from datetime import datetime
from ping3 import ping
import re
from docker.errors import DockerException
import glob
from multiprocessing import Process, Queue
import requests
import botocore
import shutil
import pkg_resources
from tabulate import tabulate
from cogniceptshell.common import bcolors
from cogniceptshell.common import generate_progress_bar
from cogniceptshell.common import permission_safe_docker_call
from subprocess import DEVNULL
from docker.types import LogConfig
from compose.cli.main import TopLevelCommand, project_from_options

class AgentLifeCycle:
    """
    A class to manage agent and Cognicept's docker container lifecycle
    ...

    Parameters
    ----------
    None

    Methods
    -------
    configure_containers(cfg):
        Loads agent configuration from `COG_AGENT_CONTAINERS` and `COG_AGENT_IMAGES`
    get_status(args):
        Prints status of docker containers listed in `COG_AGENT_CONTAINERS`.
    get_last_event(args):
        Prints last log in `~/.cognicept/agent/logs/`.
    restart(args):
        Stops and starts the containers listed in `COG_AGENT_CONTAINERS`.
    start(args):
        Starts the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, starts only containers in the list.
    stop(args):
        Stops the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, stops only containers in the list.
    update(args):
        Pulls docker images listed in `COG_AGENT_IMAGES`.
    run_orbitty(args):
        Starts Orbitty.
    """

    # default configuration of containers and images
    _docker_container_names = ["cgs_diagnostics_agent", "remote_intervention_agent",
                               "cgs_diagnostics_ecs_api", "cgs_diagnostics_streamer_api", "cgs_bagger_server"]
    _docker_compose_container_name = []
    _docker_images = {}
    _docker_images["remote_intervention_agent"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/remote_intervention_agent:latest"
    _docker_images["kriya_watchdog"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/remote_intervention_agent:latest"
    _docker_images["cgs_diagnostics_agent"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/cognicept_diagnostics_agent:latest"
    _docker_images["cgs_diagnostics_ecs_api"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/cognicept_diagnostics_api:latest"
    _docker_images["cgs_diagnostics_streamer_api"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/cognicept_diagnostics_api:latest"
    _docker_images["colab_master"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:master"
    _docker_images["colab_description"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:colab-desc"
    _docker_images["cgs_mission_sys"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/mission_system:latest"
    _docker_images["orbitty"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/orbitty:latest"
    _docker_images["cgs_bagger_server"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/cognicept_rosbagger:latest"
    _docker_images["health_aggregator"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/health_aggregator:dev"
    _docker_images["diagnostics_aggregator"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/health_aggregator:dev"
    _docker_images["smartplus_sound"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/smartplus_sound_server:latest"
    _docker_images["map_manager"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/map_manager:latest"
    _docker_images["computer_health_metrics"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:computer_health_metrics"
    _docker_images["slamtec_adapter"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/slamtec_adapter:latest"
    _docker_images["cam_capture"] = "412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/ros:camera_capture"

    def configure_containers(object, cfg):
        """
        Loads agent configuration from `COG_AGENT_CONTAINERS`, `COG_AGENT_IMAGES` and `COG_COMPOSE_FILE`

                Parameters:
                        cfg (Configuration): Cognicept configuration
                Returns:
                        None
        """

        if("COG_AGENT_CONTAINERS" in cfg.config and "COG_AGENT_IMAGES" in cfg.config):
            container_names = cfg.config["COG_AGENT_CONTAINERS"].split(";")
            image_names = cfg.config["COG_AGENT_IMAGES"].split(";")
            if(len(image_names) == len(container_names)):
                object._docker_container_names = container_names
                object._docker_images = {}
                i = 0
                for container_name in container_names:
                    object._docker_images[container_name] = image_names[i]
                    i = i + 1
            else:
                print(
                    "`COG_AGENT_CONTAINERS` and `COG_AGENT_IMAGES` do not coincide. Using default.")

            if("COG_ORBITTY_ENABLED" in cfg.config and "COG_ORBITTY_IMAGE" in cfg.config):
                if(bool(cfg.config["COG_ORBITTY_ENABLED"])):
                    object._docker_images["orbitty"] = cfg.config["COG_ORBITTY_IMAGE"]
        else:
            print(
                "Undefined `COG_AGENT_CONTAINERS` or `COG_AGENT_IMAGES`. Using default.")

        if "COG_COMPOSE_FILE" in cfg.config:
            object._compose_dir = os.path.dirname(os.path.expanduser(cfg.config["COG_COMPOSE_FILE"]))
            docker_compose_dict = cfg.get_docker_compose()

            if docker_compose_dict == {}:
                print(f"{bcolors.WARNING}Warning: failed to load docker compose file - {cfg.config['COG_COMPOSE_FILE']} {bcolors.ENDC}")
            else:
                for container_name in docker_compose_dict:
                    object._docker_container_names.append(container_name)
                    object._docker_compose_container_name.append(container_name)
                object._docker_images.update(docker_compose_dict)

    def _get_latest_log_loc(object, args):
        """
        Retrieve path to the last log in `~/.cognicept/agent/logs/` relative to `~/.cognicept/` or `path` specified by args.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        latest_log_loc (str): path to latest log relative to `~/.cognicept/`
        """
        # get latest log location
        latest_log_loc_file_path = os.path.expanduser(
            args.path+"agent/logs/latest_log_loc.txt")
        latest_log_loc = ""
        try:
            with open(latest_log_loc_file_path) as txt_file:
                latest_log_loc_temp = txt_file.readline()
                latest_log_loc_temp = latest_log_loc_temp[:-1]
                latest_log_loc = latest_log_loc_temp.replace(
                    "/$HOME/.cognicept/", "")
                latest_log_loc = latest_log_loc.replace(".cognicept/", "")
        except:
            cgs_agent_status = bcolors.FAIL + "UNKNOWN" + bcolors.ENDC

        return latest_log_loc

    def get_status(object, args):
        """
        Prints status of docker containers listed in `COG_AGENT_CONTAINERS`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`

        """
        permission_docker_call_result = permission_safe_docker_call(
            docker.from_env)
        if permission_docker_call_result is None:
            return False
        client = permission_docker_call_result
        # check status of cgs_agent
        # get latest log location
        latest_log_loc = object._get_latest_log_loc(args)
        # read latest status and set for display
        file_path = os.path.expanduser(
            args.path+latest_log_loc+"/logDataStatus.json")
        try:
            with open(file_path) as json_file:
                data = json.load(json_file)
                period_since_update = datetime.utcnow(
                ) - dateutil.parser.parse(data["timestamp"])
                if(period_since_update.seconds < 30 and period_since_update.seconds >= 0):
                    cgs_agent_status = bcolors.OKBLUE + \
                        data["message"].upper() + bcolors.ENDC
                else:
                    cgs_agent_status = bcolors.WARNING + "STALE" + bcolors.ENDC

        except:
            cgs_agent_status = bcolors.FAIL + "Error" + bcolors.ENDC

        container_names = object._docker_container_names
        for container_name in container_names:
            print(container_name, end=': ', flush=True)
            try:
                container = client.containers.get(container_name)
                if container.status != "running":
                    print(bcolors.WARNING + "OFFLINE" + bcolors.ENDC)
                else:
                    if(container_name == "cgs_diagnostics_agent"):
                        print(cgs_agent_status)
                    elif(container_name == "remote_intervention_agent"):
                        object._parse_remote_intervention_agent_logs(
                            container.logs(tail=50))
                    else:
                        print(bcolors.OKBLUE + "ONLINE" + bcolors.ENDC)
            except docker.errors.NotFound:
                print(bcolors.FAIL + "CONTAINER NOT FOUND" + bcolors.ENDC)

    def get_last_event(object, args):
        """
        Prints last log in `~/.cognicept/agent/logs/`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`

        """
        # get latest log location
        latest_log_loc = object._get_latest_log_loc(args)

        # read and display latest log if any
        file_path = os.path.expanduser(args.path+latest_log_loc)
        try:
            print(bcolors.OKBLUE +
                  "Looking for the latest event log..." + bcolors.ENDC)
            # should read only latest logData#.json file and not logDataStatus.json
            list_of_log_files = [fn for fn in glob.glob(file_path + "/*.json")
                                 if not os.path.basename(fn).endswith("logDataStatus.json")]
            latest_log_file = max(list_of_log_files, key=os.path.getctime)

            with open(latest_log_file) as json_file:
                data = json.load(json_file)
                print(bcolors.OKGREEN+"Latest Event Log:" + bcolors.ENDC)
                print(json.dumps(data, indent=4, sort_keys=True))
        except:
            print(bcolors.WARNING + "No event logs present." + bcolors.ENDC)

    def check_docker_image_exists(object, args):
        """
        Checks if this docker image exists.
        
                Parameters:
                        args (str): Input container names.
        """
        image_set = set()
        missing_image = set()

        # If list of agents is not specified, get all container_names
        if(not hasattr(args, 'list') or len(args.list) == 0):
            args.list = object._docker_container_names

        # Based on args.list to get image(s)
        for container_name in args.list:
            try:
                image_set.add(object._docker_images[container_name])
            except KeyError as exp:
                print(bcolors.WARNING + "Container: " + container_name + " not found. Skipping." + bcolors.ENDC)

        success_flag = True
        docker_client = permission_safe_docker_call(docker.from_env)
        for image in image_set:
            try:
                image = docker_client.images.get(image)

            except docker.errors.ImageNotFound:
                missing_image.add(image) #Track image(s) that is/are missing
                success_flag = False

        return success_flag, missing_image

    def _parse_remote_intervention_agent_logs(object, logs):
        """
        Parses logs to find status of remote intervention agent. Prints status.

                Parameters:
                        logs: container logs

        """
        logs_lines = logs.splitlines()
        # parse logs to get current status
        ri_agent_status = {}
        ri_agent_status["AGENT"] = ""
        ri_agent_status["WEBRTC"] = ""
        ri_agent_status["WEBSOCKET"] = ""

        # find latest status of the each module (agent, webrtc, websocket)
        for line in reversed(logs_lines):
            for key, value in ri_agent_status.items():
                if(value != ""):
                    continue
                matches = re.search(
                    '^.*{}:: STATUS:: (?P<status>.*).*$'.format(key), str(line))
                if(matches is not None):
                    ri_agent_status[key] = matches.groups(0)[0]
            if(ri_agent_status["AGENT"] != "" and ri_agent_status["WEBRTC"] != "" and ri_agent_status["WEBSOCKET"] != ""):
                continue

        output_text = bcolors.OKBLUE + "ONLINE" + bcolors.ENDC

        for key, value in ri_agent_status.items():
            if(value == ""):
                # if not found, it was not yet initialized
                output_text = bcolors.WARNING + "NOT INITIALIZED" + bcolors.ENDC
                break
            if(value != "OK"):
                output_text = bcolors.WARNING + key + value + bcolors.ENDC
                break
        print(output_text)

    def _detached_restart(object, args):
        """
        Runs _restart_protocol in detached mode with printing muted.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """

        if os.fork() != 0:
            return
        sys.stdout = open(os.devnull, 'w')
        result = object._restart_protocol(args)
        sys.stdout = sys.__stdout__
        return result

    def _restart_protocol(object, args):
        """
        Stops and starts the containers listed in `COG_AGENT_CONTAINERS`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        object.stop(args)
        result = object.start(args)
        return result

    def restart(object, args):
        """
        Stops and starts the containers listed in `COG_AGENT_CONTAINERS`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded in attached mode, always True in detached mode
        """
        success_flag, missing_images = object.check_docker_image_exists(args) #success_flag is a bool to check if all image(s) exist before running restart protocol

        if success_flag:
            if args.detach:
                result = True
                print("Running restart in detached mode")
                p = Process(target=object._detached_restart, args=(args,))
                p.start()
            else:
                result = object._restart_protocol(args)
            if args.prune:
                print("Clearing logs")
                object.clear_logs(args)
                            
        else:
            result = success_flag
            print(bcolors.FAIL + "Error: The following image(s) shown below cannot be found" + bcolors.ENDC)
            print(*missing_images, sep = "\n")
        return result

    def start(object, args):
        """
        Starts the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, starts only containers in the list.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        print("Called start")
        print("Starting agents")
        result = object.run_agents(args)
        return result

    def stop(object, args):
        """
        Stops the containers listed in `COG_AGENT_CONTAINERS`. If `args` has parameter `list`, stops only containers in the list.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        print("Stopping agents")
        result = object.remove_agents(args)
        return result
    
    def check_sudo_password(object, password):
        '''
        Checks if user entered password for clearing logs is correct. Runs a dummy sudo command to test input password.
        '''
        cmd = ["sudo","-kS","echo","test"]
        
        p = subprocess.run(cmd, capture_output=True, input=password, encoding="ascii")

        if "incorrect password" in str(p):
            return False
        else:
            return True
        
    
    def clear_logs(object, args):
        """
        Remove all unused containers, networks, images (both dangling and unreferenced). Removes all .txt logs stored in /kriya_logs
        and .json logs stored in /agents/logs
                
        """
        log_list = ["sudo","-S","-k", "rm"]
        kriya_log_count = 0
        agent_folder_list = ["sudo","-S","-k","rm","-r"]
        cognicept_dir_path = os.path.expanduser(args.path)
        kriya_logs_dir = cognicept_dir_path + "kriya_logs/"
        if os.path.exists(kriya_logs_dir):
            kriya_logs = os.listdir(kriya_logs_dir)
            for item in kriya_logs:
                if item.endswith(".txt"):
                    log_list.append(str(kriya_logs_dir + item))
                    kriya_log_count += 1

        agent_logs_dir = cognicept_dir_path + "agent/logs/"
        if os.path.exists(agent_logs_dir):
            agent_folders = os.listdir(agent_logs_dir)
            
            for folder in agent_folders:
                folder_path = agent_logs_dir + folder
                if os.path.isdir(folder_path) and folder != "bunched_logs" and folder != "unittest_logs":
                    agent_folder_list.append(str(folder_path))
                
                elif folder == "bunched_logs":
                    bunched_logs = os.listdir(folder_path)
                    bunched_log_count = len(bunched_logs)
                    for item in bunched_logs:
                        log_list.append(str(folder_path + "/" + item))
                
                elif folder == "unittest_logs":
                    unittest_logs = os.listdir(folder_path)
                    unittest_log_count = len(unittest_logs)
                    for item in unittest_logs:
                        log_list.append(str(folder_path + "/" + item))

        agent_folder_count = len(agent_folder_list)-4

        print(f'\nClear File Summary: \n-Kriya: {kriya_log_count} Logs Found \n-Agent: {agent_folder_count} Folders Found \n-Bunched: {bunched_log_count} Logs Found \n-Unittest: {unittest_log_count} Logs Found')
        if kriya_log_count + bunched_log_count + unittest_log_count + agent_folder_count == 0:
            print("No detected Logs and Files to be cleared.")
        else:
            print("Do you wish to proceed?")
            user_input = input("(Y/N)")
            if user_input.lower() == "y":
                
                attempt = 0
                success = False
                while attempt < 3 and success == False:
                    password = getpass.getpass("Enter sudo password: ")
                    success = object.check_sudo_password(password)
                    
                    if not success:
                        
                        attempt += 1
                
                if success:
                
                    if kriya_log_count > 0:
                        print("Successfully removed all kriya_folder")
                    
                    if agent_folder_count > 0:
                        clear_agent_folder = subprocess.Popen(agent_folder_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = clear_agent_folder.communicate(input=(password + '\n').encode())
                        print("Successfully removed all agent_folder")

                    if bunched_log_count > 0:
                        print("Successfully removed all bunched_logs")

                    if unittest_log_count > 0:
                        print("Successfully removed all unittest_logs")

                    clear_logs = subprocess.Popen(log_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = clear_logs.communicate(input=(password + '\n').encode())

                else:
                    print("Logs and Files not cleared, Sudo Password Incorrect.")
            else:
                print("Logs and Files not cleared")

    def status(object, args):
        object.get_status(args)
        object.status_datadog(args)
        return True

    def remove_agents(object, args):
        """
        Stops the containers listed in `args.list`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """

        # if list of agents is not specified, restart all
        if(not hasattr(args, 'list') or len(args.list) == 0):
            args.list = object._docker_container_names
        permission_docker_call_result = permission_safe_docker_call(
            docker.from_env)
        if permission_docker_call_result is None:
            return False

        client = permission_docker_call_result
        print("STOP: ")
        flag_success = True
        for container_name in args.list:
            print("   - " + container_name, end=': ', flush=True)
            try:
                container = client.containers.get(container_name)
                container.stop(timeout=10)
                container.remove()
                print(bcolors.OKBLUE + "DONE" + bcolors.ENDC)
            except docker.errors.NotFound:
                print(bcolors.WARNING + "NOT FOUND" + bcolors.ENDC)
                flag_success = False
            except docker.errors.APIError:
                print(bcolors.FAIL + "ERROR" + bcolors.ENDC)
                flag_success = False
        return flag_success

    def run_agents(object, args):
        """
        Starts the containers listed in `args.list`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        # if list of agents is not specified, restart all and run the docker-compose file
        if(not hasattr(args, 'list') or len(args.list) == 0):
            args.list = object._docker_container_names
        
        object._agent_run_options = {}

        # diagnostics agent/API run config
        object._agent_run_options["cgs_diagnostics_agent"] = {"command": "rosrun error_resolution_diagnoser error_resolution_diagnoser", "volumes": {
            args.config.config_path + "agent/logs/": {"bind": "/root/.cognicept/agent/logs", "mode": "rw"}}, "network_mode": "host"}
        object._agent_run_options["cgs_diagnostics_ecs_api"] = {
            "command": "/src/ecs_endpoint.py", "network_mode": "host"}
        object._agent_run_options["cgs_diagnostics_streamer_api"] = {"command": "/src/streamer_endpoint.py", "volumes": {
            args.config.config_path + "agent/logs/bunched_logs": {"bind": "/root/.cognicept/agent/logs/bunched_logs", "mode": "rw"}}, "network_mode": "host"}

        # health aggregator run config
        object._agent_run_options["health_aggregator"] = {"command": "roslaunch health_monitoring_aggregator aggregator.launch --wait", "volumes": {
            args.config.config_path + "health_config.yaml": {"bind": "/home/aggregator_ws/src/health_monitoring_aggregator/config.yml", "mode": "rw"}}, "network_mode": "host"}
        
        # diagnostics aggregator run config
        object._agent_run_options["diagnostics_aggregator"] = {"command": "roslaunch diagnostic_aggregator aggregator.launch --wait", "volumes": {
            args.config.config_path + "diag_analyzers.yaml": {"bind": "/opt/ros/noetic/share/diagnostic_aggregator/demo/pr2_analyzers.yaml", "mode": "rw"}}, "network_mode": "host"}

        # kriya run config
        object._agent_run_options["remote_intervention_agent"] = {
            "command": "", "network_mode": "host"}
        if(args.config.is_ssh_enabled()):
            object._agent_run_options["remote_intervention_agent"]["volumes"] = {
                args.config.config_path + "ssh/id_rsa": {"bind": "/root/.ssh/id_rsa", "mode": "rw"}}
        if(args.config.is_audio_enabled()):
            object._agent_run_options["remote_intervention_agent"]["devices"] = ["/dev/snd"]
        object._agent_run_options["kriya"] = object._agent_run_options["remote_intervention_agent"]
        object._agent_run_options["kriya_watchdog"] = {
            "command": "python3 /home/watchdog.py", "volumes": {
                args.config.config_path + "kriya_logs/": {"bind": "/root/logs/", "mode": "rw"},
                "/var/run/docker.sock/": {"bind": "/var/run/docker.sock/", "mode": "rw"}}}

        # kopilot run config
        object._agent_run_options["kopilot"] = {"command": "", "network_mode": "host", "volumes": {
            args.config.config_path + "kockpit.yaml": {"bind": "/root/config/kockpit.yaml", "mode": "rw"}}}

        # ROSBagger run config
        object._agent_run_options["cgs_bagger_server"] = {"command": "rosrun cognicept_rosbagger bagger_action_server.py", "volumes": {
            args.config.config_path + "bags/": {"bind": "/root/.cognicept/bags", "mode": "rw"}}, "network_mode": "host"}
        
        # Smart+ Sound Server run config
        object._agent_run_options["smartplus_sound"] = {"volumes": {
            args.config.config_path + "sounds/": {"bind": "/root/.cognicept/sounds", "mode": "rw"},
            args.config.config_path + "tts_configuration.yaml": {"bind": "/home/smartplus_sound_server_ws/src/tts/config/sample_configuration.yaml", "mode": "rw"}},
            "network_mode": "host", "devices": ["/dev/snd"]}

        # Map Manager run config
        object._agent_run_options["map_manager"] = {"volumes": {
            args.config.config_path + "slamware_maps/": {"bind": "/root/.cognicept/slamware_maps", "mode": "rw"},
            args.config.config_path + "map_server_maps/": {"bind": "/root/.cognicept/map_server_maps", "mode": "rw"},
            args.config.config_path + "building_info.json": {"bind": "/home/map_manager_ws/src/map_manager/config/sample_building_info.json", "mode": "rw"}},
            "network_mode": "host"}
        
        # Computer Health Metrics run config
        object._agent_run_options["computer_health_metrics"] = {"volumes": {
            args.config.config_path + "health_config.yaml": {"bind": "/home/health_ws/src/computer_health_metrics/config/computer_params.yml", "mode": "rw"},
            "/var/run/docker.sock/": {"bind": "/var/run/docker.sock/", "mode": "rw"}},
             "network_mode": "host"}

        # Slamware adapter run config
        object._agent_run_options["slamtec_adapter"] = {"volumes": {
            args.config.config_path + "slamware_maps/": {"bind": "/root/.cognicept/slamware_maps", "mode": "rw"}},
            "network_mode": "host"}
        
        # Camera capture run config 
        object._agent_run_options["cam_capture"] = {"volumes": {
            args.config.config_path + "inspect_images/" : {"bind": "/root/.cognicept/inspect_images/", "mode": "rw"},
            args.config.config_path + "runtime.env" : {"bind": "/root/.cognicept/runtime.env", "mode": "rw"}},
            "network_mode": "host"}
        

        # Default other config
        object._agent_run_options["other"] = {
            "command": "", "network_mode": "host"}
        permission_docker_call_result = permission_safe_docker_call(
            docker.from_env)
        if permission_docker_call_result is None:
            return False
        client = permission_docker_call_result
        print("RUN: ")
        success_flag = True
        for container_name in args.list:
            print("   - " + container_name, end=': ', flush=True)
            try:
                if(container_name not in object._docker_images):
                    if("COG_AGENT_CONTAINERS" in args.config.config):
                        containers = " (configured list: " + \
                            args.config.config["COG_AGENT_CONTAINERS"] + ")"
                    else:
                        containers = ""
                    print(bcolors.WARNING + "NOT FOUND" +
                          bcolors.ENDC + containers)
                    success_flag = False
                    continue

                if(container_name in object._agent_run_options.keys()):
                    options = object._agent_run_options[container_name]
                else:
                    options = object._agent_run_options["other"]
                options["name"] = container_name
                options["detach"] = True
                options["environment"] = args.config.config
                try:
                    if container_name == "smartplus_sound":
                        options["environment"]["ALSA_CARD"] = options["environment"]["SOUND_DEV_OUT"]
                    elif container_name == "remote_intervention_agent":
                        options["environment"]["ALSA_CARD"] = options["environment"]["SOUND_DEV_IN"]
                except KeyError as exp:
                    print(bcolors.WARNING + 'Missing sound device configuration in runtime.' +
                        ' Might result in sound features not working as expected.' +
                        ' Explicitly define `SOUND_DEV_IN` and `SOUND_DEV_OUT` variables.' + 
                        bcolors.ENDC)
                options["restart_policy"] = {"Name": "unless-stopped"}
                options["tty"] = True
                options["log_config"] = LogConfig(
                    type=LogConfig.types.JSON, config={'max-size': '5m'})
                if "command" in options:
                    command = options.pop("command")
                else:
                    command = ""
                
                #if container name is within docker-compose service, trigger run function
                # check whether the container's image is not found
                if container_name in object._docker_compose_container_name:
                    object._run_docker_compose_service(container_name)
                else:
                    container = client.containers.run(
                        object._docker_images[container_name], command, **options)
                
                print(bcolors.OKBLUE + "DONE" + bcolors.ENDC)
            except docker.errors.ContainerError:
                print(bcolors.WARNING + "ALREADY EXISTS" +
                      bcolors.ENDC + " (run `cognicept update`)")
            except docker.errors.ImageNotFound:
                print(bcolors.WARNING + "IMAGE NOT FOUND" +
                      bcolors.ENDC + " (run `cognicept update`)")
                success_flag = False
            except docker.errors.APIError as exp:
                print(exp)
                print(bcolors.FAIL + "DOCKER ERROR" + bcolors.ENDC)
                success_flag = False
        return success_flag

    def status_datadog(object, args):
        """
        Prints datadog status.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        sts = subprocess.call(
            ['sudo', 'sh', '-c', "systemctl status datadog-agent", "-p"], shell=True, stdout=DEVNULL, stderr=DEVNULL)
        if sts == 0:
            print("Health monitor status:" +
                  bcolors.OKBLUE + " ACTIVE" + bcolors.ENDC)
        elif sts == 4:
            print("Health monitor status:" +
                  bcolors.FAIL + " NOT FOUND" + bcolors.ENDC)
        else:
            print("Health monitor status:" +
                  bcolors.WARNING + " INACTIVE" + bcolors.ENDC)

    def run_orbitty(object, args):
        """
        Starts Orbitty.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        None
        """
        os.system("xhost +local:root")
        permission_docker_call_result = permission_safe_docker_call(
            docker.from_env)
        if permission_docker_call_result is None:
            return False
        client = permission_docker_call_result
        try:
            options = {}
            options["name"] = "orbitty"
            options["detach"] = False
            options["privileged"] = True
            options["volumes"] = {}
            options["volumes"][args.config.config_path] = {
                "bind": "/config", "mode": "rw"}
            options["volumes"]["/tmp/.X11-unix"] = {
                "bind": "/tmp/.X11-unix", "mode": "rw"}
            environment = args.config.config
            environment["QT_X11_NO_MITSHM"] = 1
            environment["DISPLAY"] = ":0"
            options["environment"] = args.config.config
            options["remove"] = True
            options["tty"] = True
            command = "roslaunch orbitty orbitty.launch"
            client.containers.run(
                object._docker_images["orbitty"], command, **options)
        except docker.errors.ContainerError:
            print(bcolors.WARNING + "ALREADY RUNNING" + bcolors.ENDC)
        except docker.errors.ImageNotFound:
            print(bcolors.WARNING + "IMAGE NOT FOUND" +
                  bcolors.ENDC + " (run `cognicept update`)")
        except docker.errors.APIError:
            print(bcolors.FAIL + "DOCKER ERROR" + bcolors.ENDC)
        os.system("xhost -local:root")

    def cognicept_version_update(object):
        current_version = pkg_resources.require("cognicept-shell")[0].version
        package = 'cognicept-shell'
        response = requests.get(f'https://pypi.org/pypi/{package}/json')
        latest_version = response.json()['info']['version']
        if latest_version != current_version:
            print(f"{package} current version {current_version} - Installing Version {latest_version}")
            os.system(f'pip3 install -q {package}=={latest_version}')
            print(f'Installation {package} to version {latest_version}:'+bcolors.OKBLUE + " DONE" + bcolors.ENDC)
        else:
            print(f"{package} already in latest version={latest_version}")

    def pull_image(object,image_name,N,i):
        """
        Pulls a Docker image and displays a progress bar.

            Parameters:
                image_name : The name of the Docker image to pull.
                N : The total number of images to pull.
                i : index
        """
        image_name_short = image_name.replace("412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/", "cognicept/")
        for status in object.docker_client.pull(image_name, stream=True, decode=True):
            if("progress" not in status):
                status["progress"] = ""
            if("status" not in status):
                status["status"] = "Error"
            terminal_size = shutil.get_terminal_size().columns
            progress = ""
            if("progressDetail" in status and "total" in status["progressDetail"]):
                progress = generate_progress_bar(
                    status["progressDetail"]["current"], status["progressDetail"]["total"], 1, 10)
                status = "[" + str(i) + "/" + str(N) + "] " + image_name_short + \
                    " - " + status["status"] + " " + progress
                if(terminal_size > 0):
                    print('{:{terminal_size}.{terminal_size}}'.format(
                        status, terminal_size=terminal_size), end="\r", flush=True)
                else:
                    print('{:{trm_sz}.{trm_sz}}'.format(
                        status, trm_sz=80), end="\r", flush=True)
        print("[" + str(i) + "/" + str(N) + "] " + image_name_short +
            " - " + bcolors.OKBLUE + "OK" + bcolors.ENDC + "\033[K")

    def update_agents(object, args):
        """
        Starts the containers listed in `args.list` for the purpose of update.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        
        # if list of agents is not specified, update all agents
        
        if((not hasattr(args, 'list') or not args.list) and (not hasattr(args, 'image') or not args.image)):
            images = set(object._docker_images.values())
            # load extra images to update
            if("COG_EXTRA_IMAGES" in args.config.config):
                image_names = args.config.config["COG_EXTRA_IMAGES"].split(";")
                if(len(image_names) > 0):
                    images = images.union(set(image_names))
            
            N = len(images)
            object.cognicept_version_update()
            print("Info: This may take a while depending on your connection.")
        # if list of agents is specified, update only that particular set of agents
        else: 
            images = set()
            if args.list:
                for container_name in args.list:
                    if container_name in object._docker_container_names:
                        images.add(object._docker_images[container_name])
                    else:
                        print(f"Error: Container {container_name} not found")
                        success_flag = False

            if args.image:
                for image_name in args.image:
                    images.add(image_name)

            N = len(images)
            print("Info: Update " + str(N) + " agent_image(s).")

        i = 0 # For indexing
        success_flag = True

        for image_name in images:
            i = i + 1
            try:
                if('412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/' in image_name):
                    object.pull_image(image_name, N=N, i=i)
                else:
                    object.pull_image('412284733352.dkr.ecr.ap-southeast-1.amazonaws.com/' + image_name, N=N, i=i)

            except docker.errors.NotFound:
                try:
                    object.pull_image(image_name,N=N, i=i)
                    
                except docker.errors.NotFound:
                    print(bcolors.FAIL + "Error: " + bcolors.ENDC + f"Image {image_name} can’t be accessed in ECR or Docker Hub.")
                    print("[" + str(i) + "/" + str(N) + "] " + image_name +
                        " - " + bcolors.FAIL + "FAILED" + bcolors.ENDC + "\033[K")
                    success_flag = False
                    
                except DockerException as ex:
                    print("[" + str(i) + "/" + str(N) + "] " + image_name +
                        " - " + bcolors.FAIL + "FAILED" + bcolors.ENDC + "\033[K")
                    print(f"Error: {ex}")
                    success_flag = False
                    continue  # skip the current image and continue with the next one
            except:
                print("[" + str(i) + "/" + str(N) + "] " + image_name +
                    " - " + bcolors.FAIL + "FAILED" + bcolors.ENDC + "\033[K")
                success_flag = False

        if not success_flag:
            print("There were errors while updating some images.")
        print("Info: Run `cognicept restart` to redeploy updated agents.")

        return success_flag
    
    def _update_protocol(object, args):
        """
        Pulls docker images listed in `COG_AGENT_IMAGES`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        #Check internet connection, if cannot connect, notify user and return false
        response_time = ping('google.com')
        if response_time == False:
            print("No internet connection. Please check the internet connection and try 'cognicept update` again.")
            return False
        else:
            login_success = object._ecr_login(args)
            if login_success is False:
                print("Your login has failed due to the error mentioned above. Please try again.")
                return False
            if object.update_agents(args) is False:
                config_file_path = os.path.expanduser('~/.docker/config.json')
                if os.path.exists(config_file_path):
                    print(bcolors.WARNING + "There is a conflict in authentication file, run rm ~/.docker/config.json to remove conflicting file" + bcolors.ENDC)   
                    return False
                else:
                    print(bcolors.WARNING + "Your update credentials may have expired. Run `cognicept keyrotate` to refresh credentials and try `cognicept update` again." + bcolors.ENDC)
                    return False   
        
    def _detached_update(object, args):
        """
        Runs the _update_protocol that pulls docker images listed in `COG_AGENT_IMAGES`.

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        if os.fork() != 0:
            return

        sys.stdout = open(os.devnull, 'w')

        result = object._update_protocol(args)

        sys.stdout = sys.__stdout__

        return result

    def update(object, args):
        """
        Pulls docker images listed in `COG_AGENT_IMAGES`. Can be run in detached mode where printing is muted

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): Always True if run in detached mode, otherwise True if successful
        """
        if args.detach:
            result = True
            print("Running update in detached mode")
            p = Process(target=object._detached_update, args=(args,))
            p.start()
        else:
            result = object._update_protocol(args)

        return result

    def _construct_ecr_client(object, config_obj):
        """
        Member utility function to create ECR client `object.ecr_client` based on runtime.env credentials

                Parameters:
                        config_obj (Configuration): object holding Cognicept configuration
                Returns:
                        None      
        """
        # Get config
        local_cfg = config_obj.fetch_aws_keys()
        if local_cfg == False:
            return False
        if 'SessionToken' in local_cfg:
            object.ecr_client = boto3.client(
                'ecr', region_name='ap-southeast-1',
                aws_access_key_id=local_cfg['AccessKeyId'],
                aws_secret_access_key=local_cfg['SecretAccessKey'],
                aws_session_token=local_cfg['SessionToken'])
        else:
            object.ecr_client = boto3.client(
                'ecr', region_name='ap-southeast-1',
                aws_access_key_id=local_cfg['AccessKeyId'],
                aws_secret_access_key=local_cfg['SecretAccessKey'])
        return True

    def _ecr_login(object, args):
        """
        Member utility function that is called to login to ECR

                Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
                Returns:
                        result (bool): True if succeeded
        """
        # Construct client
        result = object._construct_ecr_client(args.config)
        if result == False:
            return False
        num_retries = 3
        for trial in range(num_retries):
            try:
                # Get token
                token = object.ecr_client.get_authorization_token()
                # Parse username, password
                username, password = base64.b64decode(
                    token['authorizationData'][0]['authorizationToken']).decode().split(':')
                # Get registry
                registry = token['authorizationData'][0]['proxyEndpoint']
                # Login
                docker_call_result = permission_safe_docker_call(docker.APIClient,
                                                                 base_url='unix://var/run/docker.sock')
                if docker_call_result is None:
                    return False

                object.docker_client = docker_call_result

                object.docker_client.login(username, password,
                                           registry=registry, reauth=True)
                # Return true for successful login
                return True
            except (docker.errors.APIError, botocore.exceptions.ClientError) as e:
                # On failure, retry
                print('Attempt #' + str(trial+1) + bcolors.FAIL +
                      " FAILED" + bcolors.ENDC + "\033[K")
                error_message = str(e)
                # Wait for 1 second before retrying
                time.sleep(1.0)
        # If the loop is completed, login failed, so return false
        print(bcolors.FAIL + error_message + bcolors.ENDC)
        return False

    def display_version(object, args):
        """
        Display Cognicept-Shell version and docker images version

        Parameters:
                        args: populated argument namespace returned by `argparse.parse_args()`
        """
        version = pkg_resources.require("cognicept-shell")[0].version
        data = {}
        images_version = []
        data['Container Name'] = object._docker_container_names
        # default value for version: "unknown/latest"
        for x in data['Container Name']:
            if x in object._docker_images:
                image_data = object._docker_images[x].split(':')
                if len(image_data) > 1:
                    images_version.append(image_data[1])
                    image_data = []
            else:
                images_version.append("unknown/latest")
        data['Version'] = images_version
        print("Cognicept Shell Version "+version)
        print(tabulate(data, headers='keys', tablefmt='psql'))
        print("Runtime enviroment file directory: " +args.path)


    def _run_docker_compose_service(object, container_name,):
        option = {"--detach":True, 
                "SERVICE" :[f"{container_name}"],
                "--no-deps": "",
                "--no-color":True,
                "--no-recreate": True,
                "--always-recreate-deps": "",
                "--abort-on-container-exit": False,
                "--remove-orphans": False,
                "--force-recreate": False,
                "--build": False,
                "--no-build": True,
                "--scale": [f'{container_name}=1'],
                "--quiet-pull": True,
                }
        project = project_from_options(object._compose_dir,option)
        compose_cmd = TopLevelCommand(project)
        compose_cmd.up(option)

