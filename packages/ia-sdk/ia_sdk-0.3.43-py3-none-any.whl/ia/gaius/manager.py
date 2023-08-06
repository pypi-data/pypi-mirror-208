#!/usr/bin/env python3
import os
import docker
import json
import logging as logger
import platformdirs as plat
import shutil
import uuid
import subprocess
from ia.gaius.agent_client import AgentClient
from ia.scripts.spawn_agent import stopit, start_agent
from contextlib import contextmanager


class AgentInfo:
    def __init__(self, user_id: str, agent_id: str, agent_name: str, genome_name: str = None, genome_file: str = None, agent_config=None, location: str = 'local', LOG_LEVEL=logger.INFO, api_key="ABCD-1234", genome_dir=None, agents_dir=None):
        """Wrapper class for Agent information. Used to start/stop agents, and save config information to a central location

        Args:
            user_id (str): User id attached to docker contaienrs spawned using AgentInfo
            agent_id (str): Agent id attached to docker containers spawned using AgentInfo
            agent_name (str): Descriptive, user-friendly name to refer to agent by
            genome_name (str, optional): If genome already in centralized location, refer to it by its name
            genome_file (str, optional): To copy outside genome into genome store, provide filepath here
            agent_config (_type_, optional): Stores AgentConfig details once agent is spawned.
            location (str, optional): In future will support spawning at several locations (local, private cloud, DigitalOcean, etc). Defaults to 'local'.
            LOG_LEVEL (logging.LEVEL, optional): Used to control verbosity of messages in agent spawn script. Defaults to logging.INFO.
            api_key (str, optional): Used to set API KEY of spawned agent. Defaults to "ABCD-1234"
        """
        logger.basicConfig(level=logger.INFO)
        self.data_dir = plat.user_data_dir(
            appname="IA_SDK_AgentManager", appauthor="IntelligentArtifacts")
        self.genome_dir = f'{self.data_dir}/genomes'
        if genome_dir:
            self.genome_dir = genome_dir
        self.agents_dir = f'{self.data_dir}/agents'
        if agents_dir:
            self.agents_dir = agents_dir

        if genome_name:
            self.genome_name = genome_name
        else:
            self.genome_name = os.path.basename(genome_file)
            if os.path.exists(f'{self.genome_dir}/{self.genome_name}'):
                logger.warn(
                    f'copying genome to genome dir would overwrite current genome {os.path.basename(genome_file)}, using genome already present')
            else:
                shutil.copyfile(src=genome_file,
                                dst=f'{self.genome_dir}/{self.genome_name}')

        self.genome_file = f'{self.genome_dir}/{self.genome_name}'
        self.user_id = user_id
        self.agent_id = agent_id
        self.location = location
        self.agent_name = agent_name
        self.agent_config = agent_config
        self.api_key = api_key

    def check_running(self):
        """Check if we can access the agent

        Returns:
            bool: True for success, False for failure
        """
        if self.location == 'local':

            agent = AgentClient(bottle_info=self.agent_config)
            try:
                agent.set_timeout(10)
                agent.connect()
            except Exception:
                return False

            return True

        else:
            raise Exception(f'unknown location {self.location}')

    def delete_config_file(self):
        """Kill agent and delete config information from agents directory
        """
        self.kill_agent()
        if os.path.exists(f'{self.agents_dir}/{self.agent_name}'):
            os.remove(f'{self.agents_dir}/{self.agent_name}')
        return f"deleted {self.agents_dir}/{self.agent_name}"

    def save_config_file(self):
        """Store config information for agent in agents directory, based on agent name
        """
        with open(f'{self.agents_dir}/{self.agent_name}', 'w') as f:
            json.dump(obj=self.toJSON(), fp=f)

        print(f'saved to {self.agents_dir}/{self.agent_name}')
        return f'{self.agents_dir}/{self.agent_name}'

    def kill_agent(self):
        """Attempt to kill a running agent
        """
        stopit(self.genome_file, user_id=self.user_id, agent_id=self.agent_id)

    def spawn(self, connect_jia=True):
        """Start a new agent using information provided in constructor

        Args:
            api_key (str, optional): API Key for agent. Defaults to "ABCD-1234".
        """
        with open(self.genome_file, 'r') as f:
            genome = json.load(f)

        json_obj = {'agent_id': self.agent_id,
                    'user_id': self.user_id,
                    'kill': False,
                    'network': None,
                    'api_key': self.api_key,
                    'genome': genome}

        self.agent_config, ports = start_agent(json_obj=json_obj)
        print(
            f'updating config file with new agent config: {self.agent_config}')
        self.save_config_file()

        if connect_jia:
            self.connect_jia()

        return json.loads(json.dumps(self.agent_config))

    def get_docker_networks(self):
        """Get names of networks this agent is a part of (uses gaius-api-{user_id}-{agent_id})

        Raises:
            Exception: More that one container found with same name

        Returns:
            _type_: list of networks
        """
        docker_client = docker.from_env()
        gapi_container = docker_client.containers.list(
            filters={'name': f'gaius-api-{self.user_id}-{self.agent_id}'})
        gapi_container = [container for container in gapi_container if container.name == f'gaius-api-{self.user_id}-{self.agent_id}']
        if len(gapi_container) == 1:
            gapi_container = gapi_container[0]
            return list(gapi_container.attrs['NetworkSettings']['Networks'].keys())
        elif len(gapi_container) > 1:
            self.delete_config_file()
            raise Exception(
                'too many docker containers with same GAIuS API name')
        else:
            raise Exception('gaius-api container not found, start agent first')

    def connect_jia(self):
        """Connect agent to jia (add jia to the agent's network)
        """
        docker_client = docker.from_env()
        jias = docker_client.containers.list()
        jias = [container for container in jias if any(['registry.digitalocean.com/intelligent-artifacts/jia' in tag for tag in container.image.tags])]
        nets = self.get_docker_networks()
        nets = docker_client.networks.list(names=nets)
        if len(jias) == 0:
            print("No JIA notebooks found! Skipping...")
        elif len(jias) == 1:
            print(f'connecting single jia')
            jia = docker_client.containers.get(
                jias[0].short_id)  # .attrs['Config']['Name']
            for net in nets:
                net.reload()
                if jia.id in [cont.id for cont in net.containers]:
                    print(f'jia already connected to network {net.name}')
                    continue
                net.connect(jia)
                print(f"Connecting JIA id: {jia.name} on {net.name}")
        elif len(jias) > 1:
            def connect_jia_func():
                print("More than one JIA found. Please select which to connect:")
                for c, i in enumerate(jias):
                    x = int(input(f"    {i}: {c} {c.name} connect? Y/N - "))
                    if x.lowercase() == 'y':
                        for net in nets:
                            net.reload()
                            if c.id in [cont.id for cont in net.containers]:
                                print(
                                    f'jia already connected to network {net.name}')
                                continue
                            net.connect(c)
                            print(f"Connecting JIA id: {c.name} on {net.name}")
                    else:
                        print("Invalid entry. Try again...")

    def get_agent_client(self):
        """Retreive AgentClient object from started agent

        Returns:
            ia.gaius.agent_client.AgentClient
        """
        if self.agent_config == None:
            raise Exception(
                'agent_config information empty, must start agent first')
        return AgentClient(bottle_info=self.agent_config)

    def toJSON(self):
        """Dump config information to a JSON object (dict)

        Returns:
            dict: config information
        """
        return {'genome_name': self.genome_name,
                'genome_file': self.genome_file,
                'agent_id': self.agent_id,
                'user_id': self.user_id,
                'agent_name': self.agent_name,
                'location': self.location,
                'agent_config': self.agent_config,
                'api_key': self.api_key,
                'genome_dir': str(self.genome_dir),
                'agents_dir': str(self.agents_dir)
                }

    @classmethod
    def fromFile(cls, filepath: str):
        """Construct AgentInfo object from file

        Args:
            filepath (str): path to file to load

        Returns:
            AgentInfo: AgentInfo object created from the file
        """
        with open(filepath, 'r') as f:
            json_obj = json.load(f)

        return cls.fromJSON(json_obj=json_obj)

    @classmethod
    def fromJSON(cls, json_obj):
        """Construct AgentInfo from JSON object

        Args:
            json_obj (dict): Contains fields necessary for constructing AgentInfo

        Returns:
            AgentInfo: AgentInfo object created from JSON object
        """
        return cls(**json_obj)


class AgentManager:
    def __init__(self, genome_dir: str = None, agents_dir: str = None):
        """Initialize AgentManager object (setup dirs, etc.)

        This object can be used to spawn Agents using the start_agent() method.
        """
        self.data_dir = plat.user_data_dir(
            appname="IA_SDK_AgentManager", appauthor="IntelligentArtifacts")
        self.genome_dir = f'{self.data_dir}/genomes'
        if genome_dir:
            self.genome_dir = genome_dir
        self.agents_dir = f'{self.data_dir}/agents'
        if agents_dir:
            agents_dir = agents_dir
        self.config_file = f'{self.data_dir}/config.json'

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
        print(f'agents dir: {self.agents_dir}')
        print(f'genome dir: {self.genome_dir}')

        if not os.path.exists(self.genome_dir):
            os.makedirs(self.genome_dir, exist_ok=True)

        if not os.path.exists(self.agents_dir):
            os.makedirs(self.agents_dir, exist_ok=True)

        self.update_current_agents()

    def start_hoster(self):
        START_COMMAND = """
        if [ ! "$(docker ps -a -q -f name=docker-hoster)" ]; then
            if [ "$(docker ps -aq -f status=exited -f name=docker-hoster)" ]; then
                # cleanup
                docker rm docker-hoster
            fi
            # run your container
            
            docker run -d --rm\
                    -v /var/run/docker.sock:/tmp/docker.sock \
                    -v /etc/hosts:/tmp/hosts \
                    --name docker-hoster \
                    dvdarias/docker-hoster
        fi
        """
        output = subprocess.run(START_COMMAND, capture_output=True, shell=True)
        if output.returncode != 0:
            raise Exception(
                f'Starting hoster failed with exitcode {output.returncode}')
        return

    def stop_hoster(self):
        STOP_COMMAND = """
        if [ "$(docker ps -a -q -f name=docker-hoster)" ]; then
            docker rm --force docker-hoster;
        fi
        
        """
        output = subprocess.run(STOP_COMMAND,
                                capture_output=True,
                                shell=True)
        if output.returncode != 0:
            raise Exception(
                f'Stopping hoster failed with exitcode {output.returncode}')
        return

    def start_agent(self, genome_file=None, genome_name=None, user_id: str = 'jia', agent_id: str = '1', agent_name=None, connect_jia=True, api_key='ABCD-1234'):
        """Spawn an agent and save its information in the localized agents dir

        .. note:: 

            If you wish to use a genome that has not been used by the AgentManager before,
            pass it in the genome_file field. This will retrieve the genome from the specified path,
            and save it in the localized genome dir for future use.


        Args:
            genome_file (str, optional): Path to outside genome file. Defaults to None.
            genome_name (str, optional): Name of genome in the localized genome dir. Defaults to None.
            user_id (str, optional): user id for naming docker containers. Defaults to 'jia'.
            agent_id (str, optional): agent id for naming docker containers. Defaults to '1'.
            agent_name (_type_, optional): descriptive name "alias" for agent. Defaults to None.
            connect_jia (bool, optional): Whether to attempt to connect agent to Jia docker container. Defaults to True.
            api_key (str, optional): Control the api key used to access agent. Defaults to 'ABCD-1234'.

        Raises:
            Exception: If there is a conflicting agent with user_id and agent_id already present/alive

        Returns:
            AgentInfo: AgentInfo object corresponding to started agent. can be used to retrieve
            AgentClient object using AgentInfo.get_agent_client()
        """
        if agent_name is None:
            agent_name = f'agent-{uuid.uuid4().hex[:8]}'
        self.update_current_agents()
        for name, agent in self.current_agents.items():
            if agent.agent_id == agent_id and agent.user_id == user_id:
                raise Exception(
                    f'Agent({name}) with user_id {user_id} and agent_id {agent_id} already exists, please choose other ids')

        if agent_name is None:
            f'agent-{uuid.uuid4().hex[:8]}'
        agent = AgentInfo(agent_id=agent_id,
                          user_id=user_id,
                          genome_file=genome_file,
                          genome_name=genome_name,
                          agent_name=agent_name,
                          api_key=api_key,
                          genome_dir=str(self.genome_dir),
                          agents_dir=str(self.agents_dir))
        agent.spawn(connect_jia=True)
        self.update_current_agents()
        print(f'started agent {agent.agent_name}')
        return agent

    def get_all_agent_status(self):
        """Get the status of all agents in current_agents dict

        Returns:
            dict: { agent_name : alive? }
        """
        agent_status = {}
        for agent_name, agent in self.current_agents.items():
            agent_status[agent_name] = agent.check_running()

        return agent_status

    def delete_agent(self, agent_name):
        """Stop/Delete agent & remove config file from agents_dir

        Args:
            agent_name (str): name of agent to stop

        Returns:
            str: string depicting deletion status
        """
        result = self.current_agents[agent_name].delete_config_file()
        del self.current_agents[agent_name]
        self.update_current_agents()
        return result

    def list_genomes(self):
        """List the genomes present in the localized genome store

        Returns:
            list: list of genome files 
        """
        return os.listdir(self.genome_dir)

    def delete_genome(self, genome_name):
        """Delete genome from centralized genome_dir

        Args:
            genome_name (str): genome name to delete
        """
        for name, agent in self.current_agents.items():
            if agent.genome_name == genome_name:
                raise Exception(
                    f'Genome {genome_name} in use by Agent {name}. Please kill agent before removing genome')
        genome_path = os.path.join(self.genome_dir, genome_name)
        print(f'will remove genome {genome_path}')
        os.remove(genome_path)
        return

    def get_genome(self, genome_name):
        """Get genome by name, return as dict

        Args:
            genome_name (str): filename for genome in genome_dir

        Raises:
            Exception: When genome not found

        Returns:
            dict: contents of genome file
        """
        genome_path = os.path.join(self.genome_dir, genome_name)

        if genome_name not in self.list_genomes():
            raise Exception(
                f'{genome_name} not in genome dir: {self.list_genomes()}')
        with open(genome_path, 'r') as f:
            return json.load(f)

    def update_current_agents(self):
        """Update the current_agents_dict
        """

        # retrieve all agent files
        self.current_agents = os.listdir(self.agents_dir)

        # get full paths of agent files
        self.current_agents = [os.path.join(
            self.agents_dir, agent) for agent in self.current_agents]

        # instantiate AgentInfo classes
        self.current_agents = [AgentInfo.fromFile(
            agent) for agent in self.current_agents]

        # make current agents into a dict by agent_name
        self.current_agents = {
            agent.agent_name: agent for agent in self.current_agents}

    def remediate_dead_agents(self):
        """Remove all agents that cannot be pinged.
        """

        agent_status = self.get_all_agent_status()

        killed_agents = []
        for agent_name, alive in agent_status.items():
            if not alive:
                print(f'{agent_name} is not alive, cleaning up')
                self.delete_agent(agent_name)
                killed_agents.append(agent_name)

        print(f'{killed_agents=}')

    def kill_all_agents(self):
        """Kill all agents known to AgentManager
        """
        for agent_name in list(self.current_agents.keys()):
            self.delete_agent(agent_name=agent_name)
    
    @contextmanager
    def agent_context(self, genome_file=None, genome_name=None, user_id: str = 'jia', agent_id: str = '1', agent_name=None, connect_jia=True, api_key='ABCD-1234'):
        agent = self.start_agent(genome_file=genome_file,
                                 genome_name=genome_name,
                                 user_id=user_id,
                                 agent_id=agent_id,
                                 agent_name=agent_name,
                                 connect_jia=connect_jia,
                                 api_key=api_key)
        yield agent.get_agent_client()
        self.delete_agent(agent.agent_name)