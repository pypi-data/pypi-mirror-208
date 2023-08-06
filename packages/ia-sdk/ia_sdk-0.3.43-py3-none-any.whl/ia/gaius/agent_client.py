import functools
import json
import uuid
import traceback
from typing import Dict, List, Any, Tuple, Union
from os.path import join, splitext
from datetime import datetime
from copy import deepcopy
import requests
from zipfile import ZipFile, ZIP_DEFLATED, is_zipfile
import warnings
from ia.gaius.genome_info import Genome

class AgentQueryError(BaseException):
    """Raised if any query to any node returns an error."""
    pass


class AgentConnectionError(BaseException):
    """Raised if connecting to any node returns an error."""
    pass

class AgentQueryWarning(Warning):
    """Used to warn user that a query partially did not complete"""

def _ensure_connected(f):
    @functools.wraps(f)
    def inner(self, *args, **kwargs):
        if not self._connected:
            raise AgentConnectionError(
                'Not connected to a agent. You must call `connect()` \
                    on a AgentClient instance before making queries'
            )
        return f(self, *args, **kwargs)

    return inner


def _remove_unique_id(response: dict) -> dict:
    """Return *response* with the key 'unique_id'
        removed regardless of nesting."""
    if isinstance(response, dict):
        if 'unique_id' in response:
            del response['unique_id']
        for value in response.values():
            if isinstance(value, dict):
                _remove_unique_id(value)
    return response


class AgentClient:
    """Interface for interacting with agents."""

    def __init__(self,
                 bottle_info: dict,
                 verify: bool = True,
                 timeout: float = None):
        """
        Provide agent information in a dictionary.

        Args:
            bottle_info (dict, required): the info used to connect and
                authenticate with a GAIuS agent
            verify (bool, optional): whether to enable SSL Verification
                on api commands to an agent

        Example:
            .. code-block:: python

                from ia.gaius.agent_client import AgentClient

                agent_info = {'api_key': 'ABCD-1234',
                            'name': 'gaius-agent',
                            'domain': 'intelligent-artifacts.com',
                            'secure': False}

                agent = AgentClient(agent_info)
                agent.connect()

                agent.set_ingress_nodes(['P1'])
                agent.set_query_nodes(['P1'])

        """
        self.session = requests.Session()
        self.session.request = functools.partial(self.session.request, timeout=timeout)
        self._timeout = timeout
        self.genome = None
        self._bottle_info = bottle_info
        self.name = bottle_info['name']
        self._domain = bottle_info['domain']
        self._api_key = bottle_info['api_key']
        self.ingress_nodes = []
        self.query_nodes = []
        self._headers = {'X-API-KEY': self._api_key}
        self.all_nodes = []
        self._connected = False
        self.genome = None
        self.gaius_agent = None
        self.send_unique_ids = True
        self.summarize_for_single_node = True
        self._verify = verify
        if 'secure' not in self._bottle_info or self._bottle_info['secure']:
            self._secure = True
            if not self.name:
                self._url = 'https://{domain}/'.format(**self._bottle_info)
            else:
                self._url = 'https://{name}.{domain}/'.format(**self._bottle_info)
        else:
            self._secure = False
            if not self.name:
                self._url = 'http://{domain}/'.format(**self._bottle_info)
            else:
                self._url = 'http://{name}.{domain}/'.format(**self._bottle_info)

    def __repr__(self) -> str:
        return (
            '<{name}.{domain}| secure: %r, connected: %s, gaius_agent: %s, \
                  ingress_nodes: %i, query_nodes: %i>'.format(
                **self._bottle_info
            )
            % (
                self._secure,
                self._connected,
                self.gaius_agent,
                len(self.ingress_nodes),
                len(self.query_nodes),
            )
        )

    def set_timeout(self, timeout: float):
        """Redefine timeout for AgentClient API Calls. Requires re-instantiating requests.Session object

        Args:
            timeout (float): The requested timeout (in seconds)
        """
        self.session = requests.Session()
        self.session.request = functools.partial(self.session.request, timeout=timeout)
        return
    
    def receive_unique_ids(self, should_set: bool = True) -> bool:
        self.send_unique_ids = should_set
        return self.send_unique_ids

    def connect(self) -> Dict:
        """Establishes initial connection to GAIuS agent and grabs the
            agent's genome for node definitions.

            Example:
                    .. code-block:: python

                        agent_info = {...}
                        agent = AgentClient(agent_info)
                        agent.connect()
        """
        response_data = self.session.get(f'{self._url}connect',
                                         verify=self._verify,
                                         headers=self._headers).json()
        if 'status' not in response_data or response_data['status'] != 'okay':
            self._connected = False
            raise AgentConnectionError("Connection failed!", response_data)

        self.genome = Genome(response_data['genome'])
        self.gaius_agent = response_data['genome']['agent']
        self.all_nodes = [{"name": i['name'], "id": i['id']} for i in self.genome.primitives.values()]
        if response_data['connection'] == 'okay':
            self._connected = True
        else:
            self._connected = False

        return {'connection': response_data['connection'],
                'agent': response_data['genie']}

    def set_ingress_nodes(self, nodes: List = None) -> List:
        """List of primitive names to define where data will be sent.

            Example:
                .. code-block:: python

                    # when observing data, it will be sent to only P1 by default
                    agent.set_ingress_nodes(nodes=["P1"])
        """
        if nodes is None:
            nodes = []
        self.ingress_nodes = [{'id': self.genome.primitive_map[node],
                               'name': node}
                              for node in nodes]
        return self.ingress_nodes

    def set_query_nodes(self, nodes: List = None) -> List:
        """List of primitive names to define which nodes should return answers.

            Example:
                .. code-block:: python

                    # when getting predictions, it will be received only from P1 by default
                    agent.set_query_nodes(nodes=["P1"])
        """
        if nodes is None:
            nodes = []
        self.query_nodes = [{'id': self.genome.primitive_map[node], 'name': node} for node in nodes]
        return self.query_nodes

    def _query(self,
               query_method: Any,
               path: str,
               data: Union[dict, str] = None,
               nodes: List = None,
               unique_id: str = None) -> Union[dict, Tuple[dict, str]]:
        """Internal helper function to make a REST API call with the given *query* and *data*."""
        if not self._connected:
            raise AgentConnectionError(
                'Not connected to a agent. You must call `connect()` on a AgentClient instance before making queries'
            )
        result = {}
        if unique_id is not None:
            if data:
                data['unique_id'] = unique_id
            else:
                data = {'unique_id': unique_id}

        data = json.loads(json.dumps(data))

        if isinstance(nodes[0], str):
            nodes = [{'name': name, 'id': self.genome.primitive_map[name]} for name in nodes]
        for node in nodes:
            full_path = f'{self._url}{node["id"]}/{path}'
            try:
                if data is not None:
                    response = query_method(full_path,
                                            verify=self._verify,
                                            headers=self._headers,
                                            json={'data': data})
                else:
                    response = query_method(full_path,
                                            verify=self._verify,
                                            headers=self._headers)
                response.raise_for_status()
                response = response.json()
                if response['status'] != 'okay':
                    raise AgentQueryError(response['message'])
                if not self.send_unique_ids:
                    response = _remove_unique_id(response['message'])
                else:
                    response = response['message']
                if len(nodes) == 1 and self.summarize_for_single_node:
                    result = response
                else:
                    result[node['name']] = response
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        if unique_id is not None:
            return result, unique_id
        return result

    def set_summarize_for_single_node(self, value: bool):
        """When True, queries against a single node return responses directly
        instead of in a dict key.

        Example:
            .. code-block:: python

                # set summarize_for_single_node to True
                >>> agent.set_summarize_for_single_node(value=True)
                >>> gdf={'strings':['hello'], 'vectors': [], 'emotives':{}}
                >>> agent.observe(gdf)
                'observed'

                # set summarize_for_single_node to False
                >>> agent.set_summarize_for_single_node(value=False)
                >>> agent.observe(gdf)
                {'P1': 'observed'}

        """
        self.summarize_for_single_node = value

    def observe(self, data: Dict, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Exclusively uses the 'observe' call.
            Will observe on nodes specified by set_ingress_nodes()
            unless nodes explicitly provided

            Args:
                data (dict): the GDF data to be observed
                nodes (list, optional): Nodes to observe data on,
                    defaults to ingress nodes

            Example:
                .. code-block:: python

                    from ia.gaius.utils import create_gdf
                    >>> gdf = create_gdf(strings=['hello'])
                    >>> agent.observe(data=gdf, nodes=["P1"])
                    'observed'

        """
        if nodes is None:
            nodes = self.ingress_nodes
        return self._query(self.session.post, 'observe', data=data, nodes=nodes)

    def _observe_event(self, data: Dict, unique_id: str = None) -> Tuple[dict, str]:
        """Exclusively uses the 'observe' call."""
        results = {}
        uid = None
        if unique_id is None:
            unique_id = str(uuid.uuid4())
        for node, node_data in data.items():
            response, uid = self._query(self.session.post,
                                        'observe',
                                        data=node_data,
                                        nodes=[node],
                                        unique_id=unique_id)
            results[node] = response
        return results, uid

    @_ensure_connected
    def observe_classification(self, data=None, nodes: List = None):
        """Send a classification to all nodes as a singular symbol in the
        last event.

        Sending the classification as a single symbol in the last event is
        the canonical way to classify a sequence.
        """
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post, 'observe', data=data, nodes=nodes)

    def show_status(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return the current status of the agent.

        Example:
            .. code-block:: python

                >>> agent.show_status(nodes=['P1'])
                {'PREDICT': True,
                'SLEEPING': False,
                'emotives': {},
                'last_learned_model_name': '',
                'models_kb': '{KB| objects: 0}',
                'name': 'P1',
                'size_WM': 0,
                'target': '',
                'time': 0,
                'vectors_kb': '{KB| objects: 0}'}
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'status', nodes=nodes)

    def learn(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return the learn results.

        Example:
            .. code-block:: python

                >>> agent.learn(nodes=["P1"])
                'MODEL|004da01b0ef40d7c3e0965a6b4fd0f413672fbff'
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'learn', nodes=nodes)

    def get_wm(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return information about Working Memory.

        Example:
            .. code-block:: python

                >>> gdf = {'strings':['hello'], 'vectors': [], 'emotives':{}}
                >>> agent.observe(gdf, nodes=['P1'])
                >>> agent.get_wm(nodes=['P1'])
                [['hello']]

        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'working-memory', nodes=nodes)

    def get_predictions(self, unique_id: str = None, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return prediction result data.

        Example:
            .. code-block:: python

                predictions = agent.get_predictions(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post, 'predictions', nodes=nodes, unique_id=unique_id)

    def clear_wm(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Clear the Working Memory of the Agent.
        Will not delete any persisted memory from the KnowledgeBase

        Example:
            .. code-block:: python

                >>> agent.clear_wm(nodes=['P1'])
                'wm-cleared'
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'working-memory/clear', nodes=nodes)

    def clear_all_memory(self, clear_blacklist=True, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Clear both the Working Memory and persisted memory.
        Equivalent to re-initializing the nodes specified

        Args:
            clear_blacklist (bool, optional): Controls if symbol blacklist is
                also cleared or not. Defaults to False.
            nodes (List, optional): List of nodes to call command on.
                Defaults to None.

        .. code-block:: python

                >>> agent.clear_all_memory(nodes=["P1"])
                'all-cleared'

        Returns:
            Union[dict, Tuple[dict, str]]: _description_
        """
        if nodes is None:
            nodes = self.all_nodes

        data = {"clear_blacklist": clear_blacklist}

        return self._query(self.session.post, 'clear-all-memory', nodes=nodes, data=data)

    def get_percept_data(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return percept data.

        Example:
            .. code-block:: python

                percept_data = agent.get_percept_data(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'percept-data', nodes=nodes)

    def get_cognition_data(self, unique_id: str = None, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return cognition data.

        Example:
            .. code-block:: python

                cog_data = agent.get_cognition_data(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.get, 'cognition-data', nodes=nodes, unique_id=unique_id)

    def get_all_genes(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return all genes for nodes.

        Example:
            .. code-block:: python

                genes = agent.get_all_genes(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'all-genes', nodes=nodes)

    @_ensure_connected
    def change_genes(self, gene_data: Dict, nodes: List = None) -> Union[dict, Any]:
        """Change the genes in *gene_data* to their associated values.

        This will do live updates to an existing agent, rather than stopping
        an agent and starting a new one, as per 'injectGenome'.
        gene_data of form:

            {gene: value}

        Example:
            .. code-block:: python

                agent.change_genes(gene_data={"recall_threshold" : 0.15})

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]

        result = {}
        for node in nodes:
            response = self.session.post(
                f"{self._url}{node['id']}/genes/change",
                verify=self._verify,
                headers=self._headers,
                json={'data': gene_data},
            ).json()
            if 'error' in response or response['status'] == 'failed':
                if len(nodes) == 1 and self.summarize_for_single_node:
                    raise AgentQueryError(response)
            self.genome.change_genes(node['id'], gene_data)
            if len(nodes) == 1 and self.summarize_for_single_node:
                return response['message']
            result[node['name']] = response['message']
        return result

    @_ensure_connected
    def get_gene(self, gene: str, nodes: List = None) -> Union[dict, Dict[Any, Dict[str, Any]]]:
        """Return the value for the gene *gene* on *nodes*.

        Example:
                .. code-block:: python

                    agent.get_gene(gene="recall_threshold")

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(f"{self._url}{node['id']}/gene/{gene}",
                                            verify=self._verify,
                                            headers=self._headers
                                            ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return {gene: response['message']}
                result[node['name']] = {gene: response['message']}
            except BaseException as exception:
                raise AgentQueryError(exception) from None

        return result

    @_ensure_connected
    def get_model(self, model_name: str, nodes: List = None) -> Union[dict, Any]:
        """Returns model with name *model_name*.

        Model name is unique, so it should not matter that we query all nodes, only
        one model will be found.

        Args:
            model_name (str): Name of model to retrieve
            nodes (List, optional): list of nodes to retrieve model from.
                Defaults to None (all nodes).

        Returns:
            Union[dict, Any]: dictionary of {node_name : model} pairs
        Example:
                .. code-block:: python

                    agent.get_model("MODEL|d85f28ebda228064299035bf2dbf58f5c6484108")

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(f"{self._url}{node['id']}/model/{model_name}",
                                            headers=self._headers,
                                            verify=self._verify
                                            ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    @_ensure_connected
    def delete_model(self, model_name: str, nodes: List = None) -> Union[dict, Any]:
        """Deletes model with name *model_name*.

        Model name is unique, so it should not matter that we query all nodes,
        all its duplicates everywhere will be deleted.
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.delete(f"{self._url}{node['id']}/model/{model_name}",
                                               headers=self._headers,
                                               verify=self._verify
                                               ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    @_ensure_connected
    def update_model(self, model_name: str, model: Dict, nodes: List = None) -> Union[dict, Any]:
        """Update the model  **model_name** with the data in **model**
        on update_model **nodes**

        .. note::

            This function is only capable of updating the emotives
            corresponding to a model. In order to update the sequence
            corresponding to a model, delete this model and reobserve
            the updated sequence

        Example:
            .. code-block:: python

                # retrieve a model already learned on an agent
                model_name = 'MODEL|d85f28ebda228064299035bf2dbf58f5c6484108'
                model = agent.get_model(model_name=model_name, nodes=['P1'])

                # update the emotives in the model
                model["emotives"] = {'utility': [150, 200, 500]}
                agent.update_model(model_name=model_name, model=model, nodes=['P1'])

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.put(f"{self._url}{node['id']}/model/{model_name}",
                                            headers=self._headers,
                                            verify=self._verify,
                                            json={'model': model}
                                            ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    @_ensure_connected
    def resolve_model(self, model_name: str, nodes: List = None) -> Union[dict, Any]:
        """Returns model with name *model_name*.

        Model name is unique, so it should not matter that we query all nodes,
        only one model will be found.
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(f"{self._url}{node['id']}/model/{model_name}",
                                            headers=self._headers,
                                            verify=self._verify
                                            ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    def get_name(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return name of *nodes*.

            Example:
                .. code-block:: python

                    agent.get_name(nodes=["P1", "P2"])

        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'name', nodes=nodes)

    def get_time(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Return time on *nodes*.

            Example:
                .. code-block:: python

                    >>> agent.get_time(nodes=['P1'])
                    '1'
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.get, 'time', nodes=nodes)

    @_ensure_connected
    def get_models_with_symbols(self, symbols_list: List = None, nodes: List = None) -> Union[dict, Any]:
        '''
            Function which search the kbs on the nodes for models with certain
            symbols. All symbols must be present in model.sequence, or the
            model will not be returned
        '''
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.post(f"{self._url}{node['id']}/get-models-with-symbols",
                                             verify=self._verify,
                                             headers=self._headers,
                                             json={'data': symbols_list}
                                             ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    @_ensure_connected
    def get_models_with_patterns(self,
                                 symbols_list: List = None,
                                 nodes: List = None) -> Union[dict, Any]:
        '''
            Function which search the kbs on the nodes for models with
            certain regex patterns.

            All regex patterns must be present in model.sequence, or
            the model will not be returned
        '''
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.post(f"{self._url}{node['id']}/get-models-with-patterns",
                                             verify=self._verify,
                                             headers=self._headers,
                                             json={'data': symbols_list},
                                             ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    @_ensure_connected
    def add_model(self, sequence: List,
                  vector: List = None,
                  frequency: int = 1,
                  emotives: Dict = {},
                  metadata: List = [],
                  nodes: List = None) -> Union[dict, Any]:
        '''
            Function to explicitely add a model with the given sequence
            of symbols, frequency, and emotives. Returns the hash of
            the generated function
        '''
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.put(f"{self._url}{node['id']}/add-model",
                                            verify=self._verify,
                                            headers=self._headers,
                                            json={'sequence': sequence,
                                                  'vector': vector,
                                                  'frequency': frequency,
                                                  'emotives': emotives,
                                                  "metadata": metadata},
                                            ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    @_ensure_connected
    def remove_symbols_from_system(self,
                                   symbols_list: List,
                                   nodes: List = None) -> Union[dict, Any]:
        """Function which search the kbs on the nodes for models with
        certain symbols.

        Symbols are removed, and the symbols are blacklisted, thus making
        it impossible fo them to be in the working memory in the future.

        Args:
            symbols_list (List): list of symbols to remove. Defaults to None.
            nodes (List, optional): list of nodes to remove symbols from.
            Defaults to None (all nodes).

        Raises:
            AgentQueryError: Error in Cognitive Processor handling

        Returns:
            Union[dict, Any]: dict showing old model hash -> new model hash
            (or 'deleted') pairs
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.delete(f"{self._url}{node['id']}/symbols/remove",
                                               verify=self._verify,
                                               headers=self._headers,
                                               json={'data': symbols_list},
                                               ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    @_ensure_connected
    def remove_patterns_from_system(self,
                                    symbols_list: List,
                                    nodes: List = None) -> Union[dict, Any]:
        """
        Function which search the kbs on the nodes for models with
        certain regex patterns. Removed symbols that matches patterns,
        but does not blacklist them. So patterns may show up in the future.

        Args:
            symbols_list (List): list of regex symbol patterns to remove.
            nodes (List, optional): list of nodes to remove symbols on.
                Defaults to None (all nodes).

        Raises:
            AgentQueryError: Error in Cognitive Processor handling

        Returns:
            Union[dict, Any]: dict showing old model hash -> new model hash
                (or 'deleted') pairs

        Example:
            .. code-block:: python

                from ia.gaius.kb_ops import list_symbols

                symbols_before = list_symbols(agent)
                agent.remove_patterns_from_system(['VECTOR|.+'])
                symbols_after = list_symbols(agent)

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.delete(f"{self._url}{node['id']}/patterns/remove",
                                               verify=self._verify,
                                               headers=self._headers,
                                               json={'data': symbols_list}
                                               ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    def add_blacklisted_symbols(self,
                                symbols_list: List,
                                nodes: List = None):
        """Add a symbol to the blacklist manually.
        List all symbols currently in the blacklist using :func:`list_blacklisted_symbols`.
        Symbols may be removed from this list by using :func:`remove_blacklisted_symbols`.

        Args:
            symbols_list (List): list of symbols to add to the blacklist
            nodes (List, optional): list of nodes to add blacklisted symbols on.
                Defaults to None (all nodes).

        Raises:
            AgentQueryError: Error in Cognitive Processor handling

        Returns:
            dict or str: Depicting result of adding blacklisted symbols to each CP in nodes
        """

        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.post(f"{self._url}{node['id']}/blacklisted-symbols/add",
                                             verify=self._verify,
                                             headers=self._headers,
                                             json={'data': symbols_list}
                                             ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    def list_blacklisted_symbols(self, nodes: List = None):
        """Display a list of all symbols currently 'blacklisted' on each
        node in *nodes*.

        Symbols enter this list by being removed from a Cognitive Processor
        via :func:`remove_symbols_from_system` or
        :func:`remove_patterns_from_system`.

        Symbols may be removed from this list by using
        :func:`remove_blacklisted_symbols`.

        Args:
            nodes (List, optional): list of nodes to show blacklisted symbols
                on. Defaults to None (all nodes).

        Example:
            .. code-block:: python

                from ia.gaius.kb_ops import list_symbols,
                    get_models_containing_symbol

                symbols_before = list_symbols(agent)
                blacklisted_symbols = agent.list_blacklisted_symbols()
                # ensure all blacklisted symbols do not appear in the system
                assert all([sym not in symbols_before for sym in blacklisted_symbols])

                # ensure no models contain the blacklisted symbols
                models_containing_symbol = get_models_containing_symbol(agent, symbol_set=set(blacklisted_symbols))
                assert all([len(val) == 0 for val in models_containing_symbol.values()])
        """

        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(f"{self._url}{node['id']}/list-blacklisted-symbols",
                                            verify=self._verify,
                                            headers=self._headers
                                            ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    def remove_blacklisted_symbols(self,
                                   symbols_to_remove: List,
                                   nodes: List = None):
        """Remove symbols from blacklist on each Cognitive
        Processor in *nodes*

        Args:
            symbols_to_remove (List): list of symbols to remove from
                blacklisted symbols
            nodes (List, optional): list of nodes to remove blacklisted
                symbols on. Defaults to None (all nodes).

        Raises:
            AgentQueryError: Error in Cognitive Processor handling

        Returns:
            str: 'removed-blacklisted-symbols' or
            'failed-to-remove-some-symbols-from-blacklist'
        """

        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.delete(f"{self._url}{node['id']}/blacklisted-symbols/remove",
                                               verify=self._verify,
                                               headers=self._headers,
                                               json={'data': symbols_to_remove}
                                               ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None
        return result

    @_ensure_connected
    def get_vector(self, vector_name: str, nodes: List = None) -> Union[dict, Dict[Any, Dict[str, Any]]]:
        """Return the vector with *vector_name* on *nodes* (it will be present on at most one).

            Example:
                .. code-block:: python

                    agent.get_vector(vector_name="VECTOR|0b7f2aac43ae8a0d94c58be08a5b8b0ab28079de")

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(
                    f"{self._url}{node['id']}/vector", headers=self._headers, verify=self._verify, json={'data': vector_name}
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    @_ensure_connected
    def increment_recall_threshold(self, increment: float, nodes: List = None) -> Dict[Any, Dict[str, Any]]:
        """Increment recall threshold by *increment* on *nodes*.

            Args:
                increment (float): value by which to increment the recall threshold by

            Example:
                .. code-block:: python

                    agent.increment_recall_threshold(increment=0.05, nodes=["P1"])

            .. note::

                This command with only update the recall threshold by a specified value.
                In order to set the recall threshold to a specific value,
                use :func:`change_genes` instead.
        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.post(
                    f"{self._url}{node['id']}/gene/increment-recall-threshold",
                    verify=self._verify,
                    headers=self._headers,
                    json={'increment': increment},
                ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                else:
                    self.genome.primitives[node['id']]['recall_threshold'] += increment
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return {"recall_threshold": response['message']}
                result[node['name']] = {"recall_threshold": response['message']}
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result

    def start_sleeping(self,
                       nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to start sleeping.

            Example:
                    .. code-block:: python

                        # will disable observing new data on node P1
                        agent.start_sleeping(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'sleeping/start', nodes=nodes)

    def stop_sleeping(self,
                      nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Wakes up sleeping *nodes*.

            Example:
                .. code-block:: python

                    # will enable observing new data on node P1
                    agent.stop_sleeping(nodes=["P1"])

        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'sleeping/stop', nodes=nodes)

    def start_predicting(self,
                         nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to start predicting.

            Example:
                .. code-block:: python

                    # will enable prediction generation on node P1
                    agent.start_predicting(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'predicting/start', nodes=nodes)

    def stop_predicting(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to stop predicting.

        Useful for faster training, but abstracted nodes will not learn.

        Example:
            .. code-block:: python

                # will disable prediction generation on node P1
                agent.stop_predicting(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'predicting/stop', nodes=nodes)

    def start_autolearning(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to start predicting.

            Example:
                .. code-block:: python

                    # will enable prediction generation on node P1
                    agent.start_predicting(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'autolearning/start', nodes=nodes)

    def stop_autolearning(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Tells *nodes* to stop predicting.

        Useful for faster training, but abstracted nodes will not learn.

        Example:
            .. code-block:: python

                # will disable prediction generation on node P1
                agent.stop_predicting(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.all_nodes
        return self._query(self.session.post, 'autolearning/stop', nodes=nodes)

    @_ensure_connected
    def ping(self, nodes: List = None) -> Union[dict, Any]:
        """Ping a node to ensure it's up.

            Example:

                .. code-block:: python

                    agent.ping(nodes=["P1"])
        """
        if nodes is None:
            return self.session.get(f'{self._url}gaius-api/ping',
                                    headers=self._headers).json()

        nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        results = {}
        for node in nodes:
            response = self.session.get(f"{self._url}{node['id']}/ping",
                                        verify=self._verify,
                                        headers=self._headers).json()
            if 'error' in response or response["status"] == 'failed':
                if len(nodes) == 1 and self.summarize_for_single_node:
                    raise AgentQueryError(response)
                warnings.warn(response["message"], AgentQueryWarning)
            if len(nodes) == 1 and self.summarize_for_single_node:
                return response['message']
            results[node['name']] = response["message"]
        return results

    @_ensure_connected
    def get_kbs(self, directory='./'): # pragma: no cover
        """Returns the KBs for the agent.
        This is a mongo-db and can be used to store or analyze locally.
        Choose the directory to save in with the directory keyword.
        Default is in './'.

        .. warning::

            .. deprecated:: 11.0 (Kehl)

            Use :func:`get_kbs_as_json` instead.

        """
        _headers = self._headers
        _headers['Content-Encoding'] = 'gzip'
        archive = self.session.get(f"{self._url}database",
                                   headers=_headers,
                                   json={},
                                   verify=self._verify
                                   )
        archive_file = join(directory,
                            f'{self.gaius_agent}-{self.name}-{datetime.now()}-kb.archive.gz')
        with open(archive_file, 'wb') as f:
            f.write(archive.content)
        return f"Saved as {archive_file}"


    @_ensure_connected
    def _get_kbs_as_json_compressed(self,
                                   nodes: List = None,
                                   directory='./',
                                   filename=None,
                                   ids=True) -> str:
        """Returns KBs of specified nodes in a zip file (separated by node)

        """
        field = 'name'
        if ids:
            field = 'id'
        if filename is None:
            filename = join(directory, f'{self.gaius_agent}-{self.name}-{datetime.now()}-kb.zip')
        with ZipFile(filename, 'w', compression=ZIP_DEFLATED) as kb_zip:
            if nodes is None:
                nodes = self.all_nodes
            prev_summarize_state = self.summarize_for_single_node

            try:
                self.set_summarize_for_single_node(False)
                for node in nodes:
                    output = self.session.get(f'{self._url}{node["id"]}/get_kb/raw', headers=self._headers)
                    if output.status_code != 200:
                        raise Exception(f'failed to get kb from node {node["id"]}')
                    print(f'writing kb for node {node["name"]}')
                    with kb_zip.open(f'{node[field]}.json', 'w', force_zip64=True) as f:
                        f.write(output.content)
            except Exception as e:
                print(f'failed to get kb: {e}')
                raise e
            finally:
                self.set_summarize_for_single_node(prev_summarize_state)

        return filename

    @_ensure_connected
    def get_kbs_as_json(self,
                        nodes: List = None,
                        directory='./',
                        filename=None,
                        separated=False,
                        ids=True,
                        obj=False,
                        compressed=False) -> Union[List[str], dict]:
        """Returns KBs of specified nodes as JSON Objects

        Args:
            nodes (list, optional): Defaults to None.
            directory (str, optional): Defaults to './'.
            separated (bool, optional): store each KB separately.
                Defaults to False
            ids (bool, optional): use primitive_ids as keys for knowledgebase
                instead of node numbers. Defaults to True
            obj (bool, optional): whether to save the kbs to a filepath
                or a python object returned from the function
            compressed (bool, optional): whether to save the kbs to a zip file. Not compatible with
                "separated" or "obj" arguments
        Returns:
            Union[List(str), Dict]: List of files where KB is stored
            if obj = False, or dictionary where KB is to be
            stored if obj = True


        Example:
            .. code-block:: python

                # save the KBs in a specified directory, without using node IDs
                # will use node names instead (e.g. P1, P2, P3)
                kb_path = "../path/to/save/dir/"
                agent.get_kbs_from_json(directory=kb_path, separated=False, ids=False)

                #save the KBs to the active directory, using node IDs (e.g. p46514fa2, etc.)
                agent.get_kbs_from_json(ids=True)

                #save the KBs to a dictionary object, using node names
                kb = agent.get_kbs_from_json(ids=False, obj=True)

        """

        if obj is True and separated is True:
            print("obj == True and separated == True is not yet supported")
            return None

        if compressed == True:
            return self._get_kbs_as_json_compressed(nodes=nodes, directory=directory, filename=filename, ids=ids)

        if nodes is None:
            nodes = self.all_nodes
        prev_summarize_state = self.summarize_for_single_node
        try:
            self.set_summarize_for_single_node(False)
            output = self._query(requests.get, 'get_kb', nodes=nodes)
        except Exception as e:
            print(f'failed to get kb: {e}')
            raise e
        finally:
            self.set_summarize_for_single_node(prev_summarize_state)

        filenames = []
        if isinstance(output, dict):
            altered_output = {}
            if ids is True and "metadata" not in output:
                for key in output.keys():
                    node_id = [node["id"] for node in self.all_nodes if node['name'] == key][0]
                    altered_output[node_id] = output[key]
            else:
                altered_output = output
            if separated:
                for key in altered_output.keys():
                    archive_file = join(directory, f'{self.gaius_agent}-{self.name}-{key}-{datetime.now()}-kb.json')
                    filenames.append(archive_file)
                    with open(archive_file, 'w') as f:
                        f.write(json.dumps({key: altered_output[key]}))
            else:
                archive_file = join(directory, f'{self.gaius_agent}-{self.name}-{datetime.now()}-kb.json')
                if filename:
                    archive_file = filename

                filenames.append(archive_file)

                # return kb as json object
                if obj is True:
                    return altered_output
                # otherwise write json file
                with open(archive_file, 'w') as f:
                    f.write(json.dumps(altered_output))

        return filenames

    def _load_compressed_kb(self, path):
        node_dict = {}
        for item in self.all_nodes:
            node_dict[item['name']] = item['id']
            node_dict[item['id']] = item['id']

        with ZipFile(path, 'r') as kb_zip:
            kb_names = kb_zip.namelist()
            for filename in kb_names:
                node_name = splitext(filename)[0]
                if node_name not in node_dict:
                    print(f'node {node_name} not found in topology, skipping')
                    continue
                with kb_zip.open(filename, 'r') as f:
                    prim_id = node_dict[node_name]
                    response = self.session.post(f'{self._url}{prim_id}/load_kb',
                                            headers={'X-API-KEY': self._api_key,
                                                    'content-type':'application/json'},
                                            data=f)
                    if response.status_code != 200:
                        print(f'error loading kb for node {prim_id}: {response.text}')
                        return 'failed', response.status_code
                    response = self.session.post(f'{self._url}{prim_id}/working-memory/clear',
                                                headers={'X-API-KEY': self._api_key})
                    if response.status_code != 200:
                        print(f'error loading kb for node {prim_id}: {response.text}')
                        return 'failed', response.status_code

                    print(f'loading node {prim_id} succeeded')
        return 'success'

    @_ensure_connected
    def load_kbs_from_json(self, path=None, obj=None):
        """Load KBs from a JSON file

        Args:
            path (str, optional): path to JSON file where KBs are stored.
            obj  (dict, optional): object to load KnowledgeBase from

        Returns:
            str: 'success' or 'failed'

        Example:
            .. code-block:: python

                kb_path = "../path/to/kb.json"
                agent.load_kbs_from_json(path=kb_path)

        """

        node_dict = {}
        for item in self.all_nodes:
            node_dict[item['name']] = item['id']
            node_dict[item['id']] = item['id']

        kb = None
        if path is not None:
            if is_zipfile(path):
                # load_compressed_kb here
                return self._load_compressed_kb(path)

            with open(path, 'r') as f:
                kb = json.load(f)
        elif obj is not None:
            kb = obj
        else:
            raise Exception("Must specify path or obj argument")

        # check if the kb is only for a single node (simple-topology edge case)
        if 'metadata' in kb.keys():
            kb = {'P1': kb}

        for key, value in kb.items():
            prim_id = key
            if prim_id in node_dict:
                prim_id = node_dict[prim_id]
            else:
                print(f'node {prim_id} not found in topology, skipping')
                continue
            print(f'loading node {prim_id} from kb for {key}')
            response = self.session.post(f'{self._url}{prim_id}/load_kb',
                                         headers={'X-API-KEY': self._api_key},
                                         json={'data': value})
            if response.status_code != 200:
                print(f'error loading kb for node {prim_id}: {response.text}')
                return 'failed', response.status_code
            print(f'loading node {prim_id} succeeded')

        return 'success'

    @_ensure_connected
    def load_kbs_from_json_iter(self, path):
        """Uses ijson library to load KBs more efficiently

        Args:
            path (str): path to JSON file where KBs are stored.


        Returns:
            str: 'success' or 'failed'

        Example:
            .. code-block:: python

                kb_path = "../path/to/kb.json"
                agent.load_kbs_from_json(path=kb_path)

        """
        import ijson

        node_dict = {}
        for item in self.all_nodes:
            node_dict[item['name']] = item['id']
            node_dict[item['id']] = item['id']

        with open(path, 'rb') as kb_file:
            for key, value in ijson.kvitems(kb_file, '', use_float=True):
                prim_id = key
                if key in ['symbols_kb', 'vectors_kb', 'models_kb', 'metadata']:
                    raise Exception(f'use load_kbs_from_json() for a simple node')
                if prim_id in node_dict:
                    prim_id = node_dict[prim_id]
                else:
                    print(f'node {prim_id} not found in topology, skipping')
                    continue
                print(f'loading node {prim_id} from kb for {key}')
                response = self.session.post(f'{self._url}{prim_id}/load_kb',
                                                headers={'X-API-KEY': self._api_key},
                                                json={'data': value})
                if response.status_code != 200:
                    print(f'error loading kb for node {prim_id}: {response.text}')
                    return 'failed'
                print(f'loading node {prim_id} succeeded')

        return 'success'

    @_ensure_connected
    def put_kbs(self, archive_file): # pragma: no cover
        """Uploads KBs from local archive_file file.

        .. warning::

            .. deprecated:: 12.0 (Kehl)

            Use :func:`load_kbs_from_json` instead.

        """
        _headers = self._headers
        _headers['Content-Encoding'] = 'gzip'
        _headers['Content-type'] = 'application/octet-stream'
        with open(archive_file, 'rb') as f:
            data = f.read()
            response = self.session.put(f'{self._url}database',
                                        headers=_headers,
                                        verify=self._verify,
                                        data=data
                                        ).json()
        return response

    def set_target_class(self, target_class: str, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Provide a target_class symbol for the searcher to look for.

        The searcher will ignore all other classes. This is a symbol that
        is in the last event of a classification sequence.

        Example:
                .. code-block:: python

                    agent.set_target_class(target_class="apple", nodes=["P1"])

        .. note::

            This will result in the nodes specified only predicting on models
            that include the target class
        """
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post,
                           'set-target-class',
                           nodes=nodes,
                           data=target_class)

    def clear_target_class(self, nodes: List = None) -> Union[dict, Tuple[dict, str]]:
        """Clears target selection.

            Example:
                .. code-block:: python

                    agent.clear_target_class(nodes=["P1"])
        """
        if nodes is None:
            nodes = self.query_nodes
        return self._query(self.session.post,
                           'clear-target-class',
                           nodes=nodes)

    @_ensure_connected
    def get_symbol(self, symbol_name: str, nodes: List = None) -> Union[dict, Any]:
        """Returns symbol with name *symbol_name*.

        Args:
            symbol_name (str): Name of symbol to retrieve
            nodes (List, optional): list of nodes to retrieve symbol information from.
                Defaults to None (all nodes).

        Returns:
            Union[dict, Any]: dictionary of {node_name : symbol} pairs
        Example:
                .. code-block:: python

                    agent.get_symbol("WEATHER|CLOUDY")

        """
        if nodes is None:
            nodes = self.all_nodes
        else:
            nodes = [node for node in self.all_nodes if (node['name'] in nodes)]
        result = {}
        for node in nodes:
            try:
                response = self.session.get(f"{self._url}{node['id']}/symbol/{symbol_name}",
                                            headers=self._headers,
                                            verify=self._verify
                                            ).json()
                if 'error' in response or response['status'] == 'failed':
                    if len(nodes) == 1 and self.summarize_for_single_node:
                        raise AgentQueryError(response)
                    warnings.warn(response["message"], AgentQueryWarning)
                if len(nodes) == 1 and self.summarize_for_single_node:
                    return response['message']
                else:
                    result[node['name']] = response['message']
            except Exception as exception:
                raise AgentQueryError(str(exception)) from None

        return result



    @_ensure_connected
    def investigate_record(self, node, record: str) -> dict:
        """Function for drilling down on a model recursively in a multi-node
        agent. Will retrieve all data "under" the abstracted model,
        giving a complete representation of the abstracted model

        Args:
            node (list or str): the node to start at/containing
                the model provided in `record`: e.g. ['P4'] or 'P4'
            record (str): the model to search for

        Returns:
            dict: recursive structure containing a complete representation
            of the abstracted model
        """
        data = {}
        try:
            prev_summarize_state = self.summarize_for_single_node
            self.set_summarize_for_single_node(True)
            if isinstance(node, list):
                node = node[0]

            # if the node passed is a primitive_id, get the name
            # (P1, P2, etc.) of the node
            if node in self.genome.primitives:
                node = self.genome.primitives[node]['name']

            return self.__get_model_details(model=record,
                                            node=[node],
                                            topLevel=True)

        except Exception as e:
            print(str(e))
            traceback.print_exc()
        finally:
            self.set_summarize_for_single_node(prev_summarize_state)
        return data

    @_ensure_connected
    def investigate(self, record: str) -> dict:
        """Higher level implementation of :func:`investigate_record` that
        does not require a node to be entered. Operates on abstracted
        symbols, models, etc. Useful when applying in a programatic
        manner, where the node a symbol comes from is unknown.
        May throw exception if unable to identify a starting point.

        Args:
            record (str): the symbol to look for

        Returns:
            dict: recursive structure containing a complete representation
            of the abstracted model

        Example:
            .. code-block:: python

                record = 'PRIMITIVE|p124b23f9|004da01b0ef40d7c3e0965a6b4fd0f413672fbff|matches|KEY|VALUE'
                traceback = agent.investigate(record=record)
        """
        try:

            split_record = str(record).split('|')
            if split_record[0] == 'PRIMITIVE':
                if len(split_record) < 3:
                    raise Exception(f'Investigate does not know what to do with symbol: {record}')

                # print(f'investigating model {split_record[2]} on node {split_record[1]}')
                output = self.investigate_record(record=split_record[2],
                                                 node=split_record[1])
                if not output:
                    return {}
                query = {
                    'record': record,
                    'node_id': split_record[1],
                    'name': split_record[2]
                }
                return {'query': query,
                        'results': output
                        }
            else:
                prev_summarize_state = self.summarize_for_single_node
                try:
                    self.set_summarize_for_single_node(False)
                    tmp_model = self.get_model(record)
                    self.set_summarize_for_single_node(True)
                    actual_model_dict = {}
                    # print(f'{tmp_model = }')
                    for k, v in tmp_model.items():
                        if v:
                            actual_model_dict[k] = v
                    # print(f'{actual_model_dict = }')
                    if len(actual_model_dict) == 1:
                        for k, v in actual_model_dict.items():
                            # print(f'{k = }, {v = }')
                            output = self.investigate_record(record=v['name'],
                                                             node=[k])
                            query = {
                                'record': v['name'],
                                'node_id': k,
                                'name': v['name']
                            }

                            return {'query': query,
                                    'results': output}
                except Exception as e:
                    print(f'Exception in investigate call: {e}')
                finally:
                    self.set_summarize_for_single_node(prev_summarize_state)
        except Exception as e:
            print(f'Exception in investigate call: {e}')
        return {}

    @_ensure_connected
    def __get_model_details(self, model, node, topLevel=False):
        """Recursive function to get details about a specific
        model on a specific node

        Args:
            model (str): the model hash to look for
            node (list(str)): The node to look for the model on (provided as
                a list with a single element)
            topLevel (bool, optional): flag used to show that the function
                is at the top level (no recursing). Defaults to False.

        Returns:
            dict: recursive structure representing the data from the
            topLevel model
        """
        if model is None:
            return None
        p_id = self.genome.get_primitive_map().get(node[0], None)
        if p_id is None:
            return None

        p_name = p_id
        if p_id in self.genome.primitives:
            p_name = self.genome.primitives[p_id]['name']
        # print(f'{p_id=}, {p_name=}')
        if topLevel is True:
            # top level request
            record_data = {'record': f"{model}",
                           'subitems': [],
                           'model': self.get_model(model, nodes=node),
                           'node': p_name,
                           'node_id': p_id,
                           'topLevel': topLevel,
                           'bottomLevel': False}
        else:
            record_data = {'record': f"PRIMITIVE|{p_id}|{model['name']}",
                           'subitems': [],
                           'model': model,
                           'node': p_name,
                           'node_id': p_id,
                           'topLevel': topLevel,
                           'bottomLevel': False}

        for event_list in record_data['model']['sequence']:
            event = []
            for item in event_list:
                symbol = {}
                split_model = item.split('|')
                if split_model[0] == 'PRIMITIVE':
                    node_id = split_model[1]

                    node_name = node_id
                    if node_id in self.genome.primitives:
                        node_name = self.genome.primitives[node_id]['name']

                    sub_model = self.get_model(split_model[2],
                                               nodes=[node_name])
                    symbol = self.__get_model_details(model=sub_model,
                                                      node=[node_name])
                elif split_model[0] == 'VECTOR':
                    symbol = {'record': item,
                              'data': self.get_vector(item, nodes=node),
                              'subitems': None,
                              'bottomLevel': True,
                              'topLevel': False,
                              'node': node[0],
                              'node_id': p_id}
                else:
                    # print(f'reached symbol: {item}')
                    # if 'VECTOR' in item:
                    #     symbol = {'record': item,
                    #               'data': self.get_vector(item, nodes=node),
                    #               'subitems': None,
                    #               'bottomLevel': True,
                    #               'topLevel': False,
                    #               'node': node[0],
                    #               'node_id': p_id}
                    # else:
                    symbol = item
                event.append(deepcopy(symbol))
            record_data["subitems"].append(event)
        if tuple(record_data["subitems"]) == tuple(record_data["model"]["sequence"]):
            del record_data["subitems"]

        if 'subitems' in record_data:
            unique_subitems = []
            for subitem in record_data['subitems']:
                if subitem not in unique_subitems:
                    unique_subitems.append(subitem)

            record_data["subitems"] = tuple(unique_subitems)
        else:
            record_data['bottomLevel'] = True

        return record_data
