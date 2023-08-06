import math
import functools
import json
import operator
from copy import deepcopy
from collections import Counter, defaultdict
from itertools import chain
from traceback import print_exc
import traceback
import os
from pathlib import Path
from tqdm.auto import tqdm

# Visualization
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Data
import numpy as np

# Gaius Agent
from ia.gaius.agent_client import AgentClient
from ia.gaius.pvt.mongo_interface import MongoData, MongoResults
from ia.gaius.data_ops import Data
from ia.gaius.pvt.pvt_utils import init_emotive_on_node, plot_confusion_matrix, \
    compute_residual, compute_abs_residual, compute_squared_residual, smape, rmse,\
    f1_score, false_discovery_rate, false_positive_rate, update_accuracy, update_precision
from ia.gaius.prediction_models import hive_model_classification, average_emotives, prediction_ensemble_model_classification,\
    most_common_ensemble_model_classification, prediction_ensemble_modeled_emotives

class PVTAbortError(Exception):
    """Raised when PVT is aborted by Celery. Used to exit cleanly from nested test/train functions"""
    pass

class PVTMessage():
    """Wrapper for PVT socket messages to be sent during training and testing"""
    def __init__(self, status: str,
                 current_record: int,
                 total_record_count: int,
                 metrics: dict,
                 cur_test_num: int,
                 total_test_num: int,
                 test_id: str = None,
                 user_id: str = '',
                 test_type: str = 'default'):
        self.status = status
        self.current_record = current_record
        self.total_record_count = total_record_count
        self.metrics = metrics
        self.test_id = test_id
        self.user_id = user_id
        self.cur_test_num = cur_test_num
        self.total_test_num = total_test_num
        self.test_type = test_type

    def toJSON(self):
        return json.loads(json.dumps({'status': self.status,
                'current_record': self.current_record,
                'total_record_count': self.total_record_count,
                'metrics': self.metrics,
                'test_id': self.test_id,
                'user_id': self.user_id,
                'cur_test_num': self.cur_test_num,
                'total_test_num': self.total_test_num,
                'test_type': self.test_type
                }))


class PerformanceValidationTest():
    """
    Performance Validation Test (PVT) - Splits a GDF folder into training and testing sets.
    Based on the test type certain visualizations will be produced.

    Test types:

    - Classification
    - Emotive Value
    - Emotives Polarity
    """
    def __init__(self,
                 agent: AgentClient,
                 ingress_nodes: list,
                 query_nodes: list,
                 num_of_tests: int,
                 pct_of_ds: float,
                 pct_res_4_train: float,
                 test_type: str,
                 dataset_location: str = 'filepath',
                 results_filepath=None,
                 ds_filepath: str = None,
                 test_prediction_strategy="continuous",
                 clear_all_memory_before_training: bool = True,
                 turn_prediction_off_during_training: bool = False,
                 shuffle: bool = False,
                 sio=None,
                 task=None,
                 user_id: str = None,
                 mongo_db=None,
                 dataset_info: dict = None,
                 test_id=None,
                 test_configuration: dict = {},
                 socket_channel: str = 'pvt_status',
                 QUIET: bool = False):
        """Initialize the PVT object with all required parameters for execution

        Args:
            agent (AgentClient): GAIuS Agent to use for trainings
            ingress_nodes (list): Ingress nodes for the GAIuS Agent (see :func:`ia.gaius.agent_client.AgentClient.set_query_nodes`)
            query_nodes (list): Query nodes for the GAIuS Agent (see :func:`ia.gaius.agent_client.AgentClient.set_query_nodes`)
            num_of_tests (int): Number of test iterations to complete
            pct_of_ds (float): Percent of the dataset to use for PVT (overall)
            pct_res_4_train (float): Percent of the dataset to be reserved for training
            test_type (str): classification, emotives_value, or emotives_polarity
            dataset_location (str): Location of dataset to utilise, "mongodb", or "filepath"
            results_filepath (_type_): Where to store PVT results
            ds_filepath (str): Path to the directory containing training GDFs
            test_prediction_strategy (str, optional): _description_. Defaults to "continuous".
            clear_all_memory_before_training (bool, optional): Whether the GAIuS agent's memory should be cleared before each training. Defaults to True.
            turn_prediction_off_during_training (bool, optional): Whether predictions should be disabled during training to reduce computational load. Defaults to False.
            shuffle (bool, optional): Whether dataset should be shuffled before each test iteration. Defaults to False.
            sio (_type_, optional): SocketIO object to emit information on. Defaults to None.
            task (_type_, optional): Celery details to emit information about. Defaults to None.
            user_id (str, optional): user_id to emit information to on SocketIO. Defaults to ''.
            mongo_db (pymongo.MongoClient, optional): MongoDB where dataset should be retrieved from
            dataset_info (dict, optional): information about how to retrieve dataset, used for MongoDB query. If dataset_location is mongodb, this must have the user_id, dataset_id, results_collection, logs_collection, and data_files_collection_name keys
            test_id (str, optional): unique identifier to be sent with messages about this test. Also used for storing to mongodb
            test_configuration (dict, optional): dictionary storing additional metadata about test configuration, to be saved in mongodb with test results
            socket_channel (str, optional): SocketIO channel to broadcast results on. Defaults to 'pvt_status'
            QUIET (bool, optional): flag used to disable log output during PVT. Defaults to False
        """

        self.agent                               = agent
        self.ingress_nodes                       = ingress_nodes
        self.query_nodes                         = query_nodes
        self.num_of_tests                        = num_of_tests
        self.dataset_location                    = dataset_location
        self.ds_filepath                         = ds_filepath
        self.results_filepath                    = results_filepath
        self.pct_of_ds                           = pct_of_ds
        self.pct_res_4_train                     = pct_res_4_train
        self.shuffle                             = shuffle
        self.test_type                           = test_type
        self.clear_all_memory_before_training    = clear_all_memory_before_training
        self.turn_prediction_off_during_training = turn_prediction_off_during_training
        self.test_prediction_strategy            = test_prediction_strategy

        self.emotives_set                        = defaultdict(set)
        self.labels_set                          = defaultdict(set)
        self.predictions                         = None
        self.actuals                             = None
        self.emotive_value_results               = None
        self.class_metrics_data_structures       = None
        self.metrics_dataframe                   = None
        self.pvt_results                         = None
        self.sio                                 = sio
        self.task                                = task
        self.user_id                             = user_id
        self.mongo_db                            = mongo_db
        self.dataset_info                        = dataset_info
        self.test_id                             = test_id
        self.testing_log                         = []
        self.mongo_results                       = None
        self.test_configuration                  = test_configuration
        self.labels_counter                      = Counter()
        self.testing_counter                     = Counter()
        self.training_counter                    = Counter()
        self.socket_channel                      = socket_channel
        self.QUIET                               = QUIET

        self.__validate_settings()
        
        self.agent_genes = {}
        
        all_nodes = [node['name'] for node in self.agent.all_nodes]
        self.agent_genes = self.agent.get_all_genes(nodes=all_nodes)
        self.test_configuration['initial_agent_genes'] = self.agent_genes
        self.test_configuration['genome'] = self.agent.genome.topology

        if dataset_location == 'mongodb':
            self.dataset = MongoData(mongo_dataset_details=self.dataset_info,
                                     data_files_collection_name=self.dataset_info['data_files_collection_name'],
                                     mongo_db=mongo_db)
            self.mongo_results = MongoResults(mongo_db=self.mongo_db,
                                              result_collection_name=self.dataset_info['results_collection'],
                                              log_collection_name=self.dataset_info['logs_collection'],
                                              test_id=self.test_id,
                                              user_id=self.user_id,
                                              dataset_id=self.dataset_info['dataset_id'],
                                              test_configuration=self.test_configuration)
        elif dataset_location == 'filepath':
            self.dataset = Data(data_directories=[self.ds_filepath])
        elif dataset_location == 'prepared':
            self.dataset = self.ds_filepath
        elif dataset_location == 'prepared_obj':
            self.dataset = self.ds_filepath

        if self.results_filepath is not None:
            if not os.path.exists(self.results_filepath):
                os.makedirs(self.results_filepath)
        # Show Agent status by Default
        self.agent.show_status()

        # Assign Ingress and Query Nodes
        self.agent.set_ingress_nodes(nodes=self.ingress_nodes)
        self.agent.set_query_nodes(nodes=self.query_nodes)

        # Setting summarize single to False by default in order to handle multiply nodes topologies
        self.agent.set_summarize_for_single_node(False)
        
        if not self.QUIET: # pragma: no cover
            print(f"num_of_tests      = {self.num_of_tests}")
            print(f"ds_filepath       = {self.ds_filepath}")
            print(f"pct_of_ds         = {self.pct_of_ds}")
            print(f"pct_res_4_train   = {self.pct_res_4_train}")
            print(f"summarize_for_single_node status   = {self.agent.summarize_for_single_node}")

    def __validate_settings(self):
        if self.test_prediction_strategy not in ['continuous', 'noncontinuous']:
            raise Exception(
                """
                Not a valid test prediction strategy. Please choose either 
                'continuous': learn the test sequence/answer after the agent has tried to make a prediction
                'noncontinuous': do not learn the test sequence.
                """
            )
        if self.dataset_location not in ['mongodb', 'filepath', 'prepared', 'prepared_obj']:
            raise Exception(f'unknown value for dataset location: {self.dataset_location}')
        if self.test_type not in ['classification', 'emotives_value', 'emotives_polarity']:
            raise Exception(f'unknown value for test_type: {self.test_type}')
        return
    
    def prepare_datasets(self):
        if self.dataset_location not in ['prepared_obj', 'prepared']:
            self.dataset.prep(
                percent_of_dataset_chosen=self.pct_of_ds,
                percent_reserved_for_training=self.pct_res_4_train,
                shuffle=self.shuffle
            )
        if not self.QUIET: # pragma: no cover
            print(f"Length of Training Set = {len(self.dataset.train_sequences)}")
            print(f"Length of Testing Set  = {len(self.dataset.test_sequences)}")
        return

    def run_classification_pvt(self):
        for test_num in range(0, self.num_of_tests):
            self.test_num = test_num
            if not self.QUIET: # pragma: no cover
                print(f'Conducting Test # {test_num}')
                print('\n---------------------')

            self.prepare_datasets()

            if self.sio: # pragma: no cover
                self.sio.emit(self.socket_channel,
                              PVTMessage(status='training',
                                         current_record=0,
                                         total_record_count=len(self.dataset.train_sequences),
                                         metrics={},
                                         cur_test_num=self.test_num,
                                         total_test_num=self.num_of_tests,
                                         test_id=self.test_id,
                                         user_id=self.user_id,
                                         test_type=self.test_type).toJSON(),
                              to=self.user_id)
            try:

                self.train_agent()

                if self.pct_res_4_train == 100:
                    print(f'Complete!')
                    continue

                self.test_agent()

                for k, labels in self.labels_set.items():
                    self.labels_set[k] = set([label.rsplit('|', maxsplit=1)[-1] for label in labels])
                if not self.QUIET: # pragma: no cover
                    print('Getting Classification Metrics...')
                self.get_classification_metrics()
                self.pvt_results.append(deepcopy(self.class_metrics_data_structures))

            except Exception as e:
                if not self.QUIET: # pragma: no cover
                    print('error during training/testing phase of test, remediating database for failed test, then raising error')
                if self.mongo_results:
                    if not self.QUIET: # pragma: no cover
                        print('about to remediate database')
                    self.mongo_results.deleteResults()
                    if not self.QUIET: # pragma: no cover
                        print('remediated database')

                if not self.QUIET: # pragma: no cover
                    print(f'raising error {str(e)}')
                raise e

            try:
                if self.dataset_location != 'mongodb':
                    if not self.QUIET: # pragma: no cover
                        print('Plotting Results...')
                    plot_confusion_matrix(test_num=test_num, class_metrics_data_structures=self.class_metrics_data_structures, QUIET=self.QUIET, results_dir=self.results_filepath)
            except Exception as e:
                if not self.QUIET: # pragma: no cover
                    print(f'error plotting results from classification pvt: {e}')
                    traceback.print_exc()
                pass

            response_dict = {'classification_counter': self.labels_counter,
                             'pvt_results': self.pvt_results,
                             'final_agent_status': self.agent.show_status()}
            result_msg = PVTMessage(status='finished',
                                    current_record=0,
                                    total_record_count=0,
                                    metrics=response_dict,
                                    cur_test_num=self.test_num,
                                    total_test_num=self.num_of_tests,
                                    test_id=self.test_id,
                                    user_id=self.user_id,
                                    test_type=self.test_type).toJSON()
            if self.sio: # pragma: no cover
                self.sio.emit(self.socket_channel,
                              result_msg,
                              to=self.user_id)

        if self.mongo_results:
            self.mongo_results.saveResults(result_msg)
        return

    def run_emotive_value_pvt(self):
        self.pvt_results = []
        for test_num in range(0, self.num_of_tests):

            if not self.QUIET: # pragma: no cover
                print(f'Conducting Test # {test_num}')
                print('\n---------------------\n')

            self.prepare_datasets()
            if self.sio: # pragma: no cover
                self.sio.emit(self.socket_channel,
                              PVTMessage(status='training',
                                         current_record=0,
                                         total_record_count=len(
                                             self.dataset.train_sequences),
                                         metrics={},
                                         cur_test_num=self.test_num,
                                         total_test_num=self.num_of_tests,
                                         test_id=self.test_id,
                                         user_id=self.user_id,
                                         test_type=self.test_type).toJSON(),
                              to=self.user_id)

            self.train_agent()

            if self.pct_res_4_train == 100:
                print(f'Complete!')
                return

            self.test_agent()
            
            self.emotive_value_results = self.get_emotives_value_metrics()
            self.pvt_results.append(deepcopy(self.emotive_value_results))
            if not self.QUIET: # pragma: no cover
                print('Plotting Results...')

            # don't try to plot emotive values if we're working to save in a mongo database
            # (its probably running without a jupyter GUI)
            if self.mongo_db is None:
                self.plot_emotives_value_charts()

        # send out finished socket message
        response_dict = {'pvt_results': self.pvt_results}

        final_msg = PVTMessage(status='finished',
                               current_record=0,
                               total_record_count=0,
                               metrics=response_dict,
                               cur_test_num=self.num_of_tests,
                               total_test_num=self.num_of_tests,
                               test_id=self.test_id,
                               user_id=self.user_id,
                               test_type=self.test_type).toJSON()
        if self.sio: # pragma: no cover
            self.sio.emit(self.socket_channel,
                          final_msg,
                          to=self.user_id)
        if self.mongo_results:
            self.mongo_results.saveResults(final_msg)
        return

    def run_emotive_polarity_pvt(self):
        self.pvt_results = []
        for test_num in range(0, self.num_of_tests):
            if not self.QUIET: # pragma: no cover
                print(f'Conducting Test # {test_num}')
                print('\n---------------------\n')
            self.prepare_datasets()

            if self.sio: # pragma: no cover
                self.sio.emit(self.socket_channel,
                              PVTMessage(status='training', current_record=0, total_record_count=len(self.dataset.train_sequences),
                                         metrics={}, cur_test_num=self.test_num, total_test_num=self.num_of_tests,
                                         test_id=self.test_id, user_id=self.user_id, test_type=self.test_type).toJSON(), to=self.user_id)

            if not self.QUIET: # pragma: no cover
                print("Training Agent...")
            self.train_agent()

            if self.pct_res_4_train == 100:
                print(f'Complete!')
                return

            if not self.QUIET: # pragma: no cover
                print("Testing Agent...")
            self.test_agent()

            if not self.QUIET: # pragma: no cover
                print('Getting Emotives Polarity Metrics...')
            if not self.QUIET: # pragma: no cover
                print('Saving results to pvt_results...')
            self.pvt_results.append(deepcopy(self.get_emotives_polarity_metrics()))

        # send out finished socket message
        response_dict = {'pvt_results': self.pvt_results}
        final_msg = PVTMessage(status='finished', current_record=0, total_record_count=0,
                                     metrics=response_dict, cur_test_num=self.num_of_tests, total_test_num=self.num_of_tests,
                                     test_id=self.test_id, user_id=self.user_id, test_type=self.test_type).toJSON()
        if self.sio: # pragma: no cover
            self.sio.emit(self.socket_channel,
                          final_msg, to=self.user_id)
        if self.mongo_results:
            self.mongo_results.saveResults(final_msg)
        return

    def conduct_pvt(self):
        """
        Function called to execute the PVT session. Determines test to run based on 'test_type' attribute

        Results from PVT is stored in the 'pvt_results' attribute

        .. note::

            A complete example is shown in the :func:`__init__` function above. Please see that documentation for further information about how to conduct a PVT test

        """
        try:
            self.test_num = 0
            self.pvt_results = []
            self.testing_log = []

            # Validate Test Type
            if self.test_type == 'classification':
                if not self.QUIET: # pragma: no cover
                    print("Conducting Classification PVT...\n")
                self.run_classification_pvt()

            elif self.test_type == 'emotives_value':
                if not self.QUIET: # pragma: no cover
                    print("Conducting Emotives Value PVT...\n")
                self.run_emotive_value_pvt()

            elif self.test_type == 'emotives_polarity':
                if not self.QUIET: # pragma: no cover
                    print("Conducting Emotives Polarity PVT...\n")
                self.run_emotive_polarity_pvt()

            else:
                raise Exception(
                    """
                    Please choose one of the test type:
                    - classification
                    - emotives_value
                    - emotives_polarity

                    ex.
                    --> pvt.test_type='emotives_value'
                    then, retry
                    --> pvt.conduct_pvt()
                    """
                )
        except Exception as e:
            if not self.QUIET: # pragma: no cover
                print('\n--------------------------------------------------------------\n')
                print(f'failed to conduct PVT test, test_type={self.test_type}: {str(e)}')
                print_exc()
                print('\n--------------------------------------------------------------\n')
            raise e
        
        #convert defaultdict to normal dict by dumping and loading pvt results
        self.pvt_results = json.loads(json.dumps(self.pvt_results))

    def train_agent(self):
        """
        Takes a training set of gdf files, and then trains an agent on those records.
        The user can turn prediction off if the topology doesn't have abstractions
        where prediction is needed to propagate data through the topology.
        """
        # Initialize
        if self.clear_all_memory_before_training is True:
            if not self.QUIET: # pragma: no cover
                print('Clearing memory of selected ingress nodes...')
            self.agent.clear_all_memory(nodes=self.ingress_nodes)

        self.labels_set.clear()
        self.labels_counter.clear()
        self.training_counter.clear()
        self.testing_counter.clear()
        self.emotives_set.clear()

        # Train Agent
        if self.turn_prediction_off_during_training is True:
            self.agent.stop_predicting(nodes=self.query_nodes)
        else:
            self.agent.start_predicting(nodes=self.query_nodes)
        if not self.QUIET: # pragma: no cover
            print('Preparing to train agent...')

        train_seq_len = len(self.dataset.train_sequences)

        train_metrics = {}
        if self.test_type == 'classification':
            train_metrics = {'classification_counter': self.labels_counter,
                             'training_label_counter': self.training_counter,
                             'testing_label_counter': self.testing_counter}
        elif self.test_type in ['emotives_polarity', 'emotives_value']:
            train_metrics = {'emotives_counter': self.labels_counter,
                             'training_emotive_counter': self.training_counter,
                             'testing_emotive_counter': self.testing_counter}
        
        train_progress_bar = tqdm(self.dataset.train_sequences, bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{remaining} {rate_fmt}{postfix}]", disable=None)
        train_progress_bar.set_description(f'Training (Test #{self.test_num})')
        train_progress_bar.unit = ' records'
        for j, _ in enumerate(train_progress_bar):


            if j % 10 == 0:
                if self.task:
                    if self.task.is_aborted():
                        self.abort_test_remediation(current_record=j, record_count=train_seq_len)
                        return

            if self.dataset_location in ['filepath', 'prepared']:
                with open(self.dataset.train_sequences[j], "r") as sequence_file:
                    sequence = sequence_file.readlines()
                    sequence = [json.loads(d) for d in sequence]
            elif self.dataset_location == 'prepared_obj':
                sequence = self.dataset.train_sequences[j]
            elif self.dataset_location == 'mongodb':
                sequence = self.dataset.getSequence(self.dataset.train_sequences[j])

            record_emotive_set = set()
            # observe training sequence
            for event in sequence:
                record_emotive_set.update(list(event['emotives'].keys()))
                self.agent.observe(data=event, nodes=self.ingress_nodes)
                if self.test_type in ['emotives_value', 'emotives_polarity']:
                    for node in self.ingress_nodes:
                        percept_emotives = list(self.agent.get_percept_data()[node]['emotives'].keys())
                        self.emotives_set[node].update(percept_emotives)
            
            # update label/emotive counters
            if self.test_type == 'classification':
                current_labels = [label.rsplit('|', maxsplit=1)[-1] for label in sequence[-1]['strings']]
                for node in self.ingress_nodes:
                    self.labels_set[node].update(current_labels)
                self.labels_counter.update(current_labels)
                self.training_counter.update(current_labels)
                train_metrics.update({'actual': current_labels})
            elif self.test_type in ['emotives_value', 'emotives_polarity']:
                self.labels_counter.update(record_emotive_set)
                self.training_counter.update(record_emotive_set)
                train_metrics.update({'actual': self.sum_sequence_emotives(sequence)})
            self.agent.learn(nodes=self.ingress_nodes)
            
            training_msg = PVTMessage(status='training', current_record=j + 1, total_record_count=train_seq_len,
                                      metrics=train_metrics, cur_test_num=self.test_num, total_test_num=self.num_of_tests,
                                      test_id=self.test_id, user_id=self.user_id, test_type=self.test_type)

            self.store_train_record(test_num=self.test_num, record=training_msg)
            
        if not self.QUIET: # pragma: no cover
            print('Finished training agent!')

    def test_agent(self):
        """
        Test agent on dataset test sequences provided in self.dataset.test_sequences
        """
        # Start Testing
        self.agent.start_predicting(nodes=self.query_nodes)
        self.predictions = []
        self.actuals     = []

        self.testing_log.append([])
        if self.test_type == 'classification':
            test_step_info = defaultdict(lambda: defaultdict(float))
        else:
            test_step_info = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        #     test_step_info = self.init_classification_info()
        test_seq_len = len(self.dataset.test_sequences)
        if test_seq_len == 0:
            if not self.QUIET: # pragma: no cover
                print('length of testing sequences is 0... returning\n')
            return
        test_progress_bar = tqdm(self.dataset.test_sequences, bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{remaining} {rate_fmt}{postfix}]", disable=None)
        test_progress_bar.unit = ' records'
        test_progress_bar.set_description(f'Testing (Test #{self.test_num})')
        for k, _ in enumerate(test_progress_bar):

            if k % 10 == 0:
                if self.task:
                    if self.task.is_aborted():
                        self.abort_test_remediation(current_record=k, record_count=test_seq_len)
                        return

            if self.dataset_location in ['filepath', 'prepared']:
                with open(self.dataset.test_sequences[k], "r") as sequence_file:
                    sequence = sequence_file.readlines()
                    sequence = [json.loads(d) for d in sequence]
            elif self.dataset_location == 'prepared_obj':
                sequence = self.dataset.test_sequences[k]
            elif self.dataset_location == 'mongodb':
                sequence = self.dataset.getSequence(self.dataset.test_sequences[k])
            else:
                raise Exception(f"dataset location {self.dataset_location} is unknown")

            self.agent.clear_wm(nodes=self.ingress_nodes)
            if self.test_type == 'classification':
                for event in sequence[:-1]:
                    self.agent.observe(data=event, nodes=self.ingress_nodes)
                # get and store predictions after observing events
                self.predictions.append(self.agent.get_predictions(nodes=self.query_nodes))
                # store answers in a separate list for evaluation
                classifications_split = [label.rsplit('|', maxsplit=1)[-1] for label in sequence[-1]['strings']]
                self.actuals.append(deepcopy(classifications_split))
                for node in self.ingress_nodes:
                    self.labels_set[node].update(sequence[-1]['strings'])
                self.labels_counter.update([label.rsplit('|', maxsplit=1)[-1] for label in sequence[-1]['strings']])
                self.testing_counter.update([label.rsplit('|', maxsplit=1)[-1] for label in sequence[-1]['strings']])
                
                # get predicted classification on the fly, so we can save to mongo individually
                pred_dict = {node: most_common_ensemble_model_classification(self.predictions[k][node]) for node in self.query_nodes}
                for key in pred_dict:
                    if pred_dict[key] is None:
                        pred_dict[key] = 'UNKNOWN'
                test_step_info.update({'idx': k,
                                       'predicted': pred_dict,
                                       'actual': self.actuals[k],
                                       'classification_counter': self.labels_counter,
                                       'training_classification_counter': self.training_counter,
                                       'testing_classification_counter': self.testing_counter})
                test_step_info = self.compute_incidental_probabilities(test_step_info=test_step_info)

                # observe answer
                self.agent.observe(sequence[-1], nodes=self.ingress_nodes)

            elif self.test_type in ['emotives_value', 'emotives_polarity']:
                record_emotive_set = set()
                for event in sequence:
                    self.agent.observe(data=event, nodes=self.ingress_nodes)
                    record_emotive_set.update(list(event['emotives'].keys()))
                    for node in self.ingress_nodes:
                        self.emotives_set[node].update(list(self.agent.get_percept_data()[node]['emotives'].keys()))
                
                # update counters with emotives from testing record
                self.testing_counter.update(record_emotive_set)
                self.labels_counter.update(record_emotive_set)
                
                # get and store predictions after observing events
                self.predictions.append(self.agent.get_predictions(nodes=self.query_nodes))
                # store answers in a separate list for evaluation
                self.actuals.append(self.sum_sequence_emotives(sequence))

                pred_dict = {node: prediction_ensemble_modeled_emotives(self.predictions[k][node]) for node in self.query_nodes}

                test_step_info.update({'idx': k,
                                       'predicted': pred_dict,
                                       'actual': self.actuals[-1],
                                       'emotives_counter': self.labels_counter,
                                       'training_emotive_counter': self.training_counter,
                                       'testing_emotive_counter': self.testing_counter})
                test_step_info = self.compute_incidental_probabilities(test_step_info=test_step_info)

            # prepare test step message
            test_step_msg = PVTMessage(status='testing',
                                       current_record=k + 1,
                                       total_record_count=test_seq_len,
                                       metrics=test_step_info,
                                       cur_test_num=self.test_num,
                                       total_test_num=self.num_of_tests,
                                       test_id=self.test_id,
                                       user_id=self.user_id,
                                       test_type=self.test_type)

            self.store_train_record(test_num=self.test_num,
                                    record=test_step_msg)

    def sum_sequence_emotives(self, sequence):
        """
        Sums all emotive values
        """
        emotives_seq = [event['emotives'] for event in sequence if event['emotives']]
        return dict(functools.reduce(operator.add, map(Counter, emotives_seq)))

    def get_classification_metrics(self):
        """
        Builds classification final results structure for each node
        """
        
        self.class_metrics_data_structures = defaultdict(lambda: defaultdict(list))
        
        this_test_log = self.testing_log[self.test_num]
        for record in this_test_log:
            record_metrics = record['metrics']
            for node in record_metrics['predicted'].keys():
                self.class_metrics_data_structures[node]['predictions'].append(record_metrics['predicted'][node])
        
        last_test_record = this_test_log[-1]
        for node in self.class_metrics_data_structures:
            self.class_metrics_data_structures[node]['actuals'] = self.actuals
            node_test_metrics = last_test_record['metrics']
            self.class_metrics_data_structures[node]['metrics'] = {}
            self.class_metrics_data_structures[node]['metrics']['response_counts']          = node_test_metrics['response_counts'][node]
            self.class_metrics_data_structures[node]['metrics']['true_positive']            = node_test_metrics['true_positive'][node]
            self.class_metrics_data_structures[node]['metrics']['false_positive']           = node_test_metrics['false_positive'][node]
            self.class_metrics_data_structures[node]['metrics']['false_discovery_rate']     = node_test_metrics['false_discovery_rate'][node]
            self.class_metrics_data_structures[node]['metrics']['f1']                       = node_test_metrics['f1'][node]
            self.class_metrics_data_structures[node]['metrics']['precision']                = node_test_metrics['precision'][node]
            self.class_metrics_data_structures[node]['metrics']['accuracy']                 = node_test_metrics['accuracy'][node]
            self.class_metrics_data_structures[node]['metrics']['response_percentage']      = node_test_metrics['response_percentage'][node]
            self.class_metrics_data_structures[node]['metrics']['unknown_percentage']       = node_test_metrics['unknown_percentage'][node]
            if node == 'hive':
                continue
            self.class_metrics_data_structures[node]['labels'] = list(set(list(self.labels_set[node]) + ['UNKNOWN']))
        
        hive_label_set = set()
        label_set: set
        for label_set in self.labels_set.values():
            hive_label_set.update(label_set)
        self.class_metrics_data_structures['hive']['labels'] = list(hive_label_set)

    def compute_incidental_probabilities(self, test_step_info: dict):
        """Keep track of how well each node is doing during the testing phase. To be used for live visualizations

        Args:
            test_step_info (dict, required): Dictionary containing information about the current predicted, actual answers, and other related metrics (e.g. precision, unknowns, residuals, response rate, etc.)

        Returns:
            dict: updated test_step_info with the statistics for the current timestep
        """
        idx = test_step_info['idx']

        if self.test_type == 'classification':

            # compute hive prediction for time idx
            hive_pred = hive_model_classification(ensembles=self.predictions[idx])
            if hive_pred is not None:
                hive_pred = hive_pred.most_common(1)[0][0]
            if hive_pred is None:
                hive_pred = 'UNKNOWN'
            test_step_info['predicted']['hive'] = hive_pred

            for k in test_step_info['predicted'].keys():
                if test_step_info['predicted'][k] != 'UNKNOWN':
                    test_step_info['response_counts'][k] += 1
                    
                    if test_step_info['predicted'][k] in test_step_info['actual']:
                        test_step_info['true_positive'][k]  += 1
                        test_step_info['false_positive'][k] += 0  # touch key in case it hasn't been initialized yet
                    else:
                        test_step_info['false_positive'][k] += 1
                        test_step_info['true_positive'][k]  += 0 # touch key in case it hasn't been initialized yet
                else:
                    test_step_info['response_counts'][k] += 0 # touch key in case it hasn't been initialized yet
                    test_step_info['true_positive'][k]   += 0
                    test_step_info['false_positive'][k]  += 0

                test_step_info['precision'][k] = update_precision(tp=test_step_info['true_positive'][k],
                                                                            tn=0,
                                                                            response_count=test_step_info['response_counts'][k])
  
                
                test_step_info['f1'][k] = f1_score(tp=test_step_info['true_positive'][k],
                                                   fp=test_step_info['false_positive'][k],
                                                   fn=0)
                test_step_info['false_discovery_rate'][k] = false_discovery_rate(tp=test_step_info['true_positive'][k],
                                                                                 fp=test_step_info['false_positive'][k])
                # test_step_info['false_positive_rate'][k] = false_positive_rate(fp=test_step_info['false_positive'][k],
                #                                                                tn=0)
                test_step_info['accuracy'][k] = update_accuracy(tp=test_step_info['true_positive'][k],
                                                                        tn=0,
                                                                        overall_count=idx+1)
                #(test_step_info['true_positive'][k] / (idx + 1)) * 100
                test_step_info['response_percentage'][k] = (test_step_info['response_counts'][k] / (idx + 1)) * 100
                test_step_info['unknown_percentage'][k] = 100 - test_step_info['response_percentage'][k]

        elif self.test_type == 'emotives_polarity':

            # compute hive prediction for time idx
            test_step_info['predicted']['hive'] = average_emotives(list(test_step_info['predicted'].values()))

            for k in test_step_info['predicted'].keys():
                for emotive in test_step_info['actual'].keys():

                    # catch new emotives, not yet seen on node {k}
                    if emotive not in test_step_info['true_positive'][k].keys():
                        init_emotive_on_node(emotive=emotive, test_step_info=test_step_info, node=k)
                    if emotive in test_step_info['predicted'][k].keys():
                        pred_sign = np.sign(test_step_info['predicted'][k][emotive])
                        actual_sign = np.sign(test_step_info['actual'][emotive])

                        # else:
                            # print(f'predicted val: {test_step_info["predicted"][k][emotive]}, actual: {test_step_info["actual"][emotive]}')
                        # Polarity error at for zero actual value
                        if actual_sign == 0:
                            raise Exception(f'Zero value found in polarity test at idx {idx}')

                        # If predicted value non-zero
                        if bool(pred_sign):
                            test_step_info['response_counts'][k][emotive] += 1

                        # True positive (correct)
                        if actual_sign > 0 and pred_sign > 0:
                            test_step_info['true_positive'][k][emotive] += 1

                        # True Negative (correct)
                        elif actual_sign < 0 and pred_sign < 0:
                            test_step_info['true_negative'][k][emotive] += 1

                        # False positive (incorrect)
                        elif actual_sign < 0 and not pred_sign < 0:
                            test_step_info['false_positive'][k][emotive] += 1

                        # False negative (incorrect)
                        elif actual_sign > 0 and not pred_sign > 0:
                            test_step_info['false_negative'][k][emotive] += 1

                        # Calculate precision value
                        test_step_info['precision'][k][emotive] = update_precision(tp=test_step_info['true_positive'][k][emotive],
                                                                                            tn=test_step_info['true_negative'][k][emotive],
                                                                                            response_count=test_step_info['response_counts'][k][emotive])
                        # try:
                        #     test_step_info['precision'][k][emotive] = ((test_step_info['true_positive'][k][emotive] + test_step_info['true_negative'][k][emotive]) / test_step_info['response_counts'][k][emotive]) * 100
                        # except ZeroDivisionError:
                        #     test_step_info['precision'][k][emotive] = 0.0

                        # test_step_info['accuracy'][k][emotive] = ((test_step_info['true_positive'][k][emotive] + test_step_info['true_negative'][k][emotive]) / (test_step_info['testing_emotive_counter'][emotive])) * 100
                        test_step_info['accuracy'][k][emotive] = update_accuracy(tp=test_step_info['true_positive'][k][emotive],
                                                                                         tn=test_step_info['true_negative'][k][emotive],
                                                                                         overall_count=test_step_info['testing_emotive_counter'][emotive])
                        
                    # Update response percentage and unknown percentage
                    test_step_info['response_percentage'][k][emotive] = (test_step_info['response_counts'][k][emotive] / (test_step_info['testing_emotive_counter'][emotive])) * 100
                    test_step_info['unknown_percentage'][k][emotive] = 100 - test_step_info['response_percentage'][k][emotive]

        elif self.test_type == 'emotives_value':
            test_step_info['predicted']['hive'] = average_emotives(list(test_step_info['predicted'].values()))

            for emotive in test_step_info['actual'].keys():
                for k in test_step_info['predicted'].keys():
                    if emotive in test_step_info['predicted'][k].keys():
                        test_step_info['residuals'][k][emotive] = compute_residual(actual=test_step_info['actual'][emotive],
                                                                                   predicted=test_step_info['predicted'][k][emotive])
                        test_step_info['abs_residuals'][k][emotive] = compute_abs_residual(actual=test_step_info['actual'][emotive],
                                                                                           predicted=test_step_info['predicted'][k][emotive])
                        test_step_info['squared_residuals'][k][emotive] = compute_squared_residual(actual=test_step_info['actual'][emotive],
                                                                                                   predicted=test_step_info['predicted'][k][emotive])

                        previous_rmse = test_step_info['rmse'][k][emotive]
                        previous_smape = test_step_info['smape'][k][emotive]
                        test_step_info['smape_prec'][k][emotive] # touch smape_prec
                        if test_step_info['predicted'][k][emotive] == np.nan:
                            continue

                        count = test_step_info['response_counts'][k][emotive]
                        # compute new_rmse
                        test_step_info['smape'][k][emotive] = smape(previous_smape=previous_smape,
                                                                    count=count,
                                                                    abs_residual=test_step_info['abs_residuals'][k][emotive],
                                                                    predicted=test_step_info['predicted'][k][emotive],
                                                                    actual=test_step_info['actual'][emotive])
                        test_step_info['rmse'][k][emotive] = rmse(previous_rmse=previous_rmse,
                                                                  count=count,
                                                                  squared_residual=test_step_info['squared_residuals'][k][emotive])
                        test_step_info['smape_prec'][k][emotive] = 100 - (test_step_info['smape'][k][emotive])
                        test_step_info['response_counts'][k][emotive] += 1

                    # Update response percentage and unknown percentage
                    test_step_info['response_percentage'][k][emotive] = (test_step_info['response_counts'][k][emotive] / (test_step_info['testing_emotive_counter'][emotive])) * 100
                    test_step_info['unknown_percentage'][k][emotive] = 100 - test_step_info['response_percentage'][k][emotive]

        return test_step_info

    def get_emotives_value_metrics(self):
        """
        Builds emotives value data structures for each node
        """
        # Build an emotives Metric Data Structure
        results = defaultdict(lambda: defaultdict(dict))
        # generate hive emotive set
        hive_emotive_set = set()
        label_set: set
        for label_set in self.emotives_set.values():
            hive_emotive_set.update(label_set)
        self.emotives_set['hive'] = hive_emotive_set
        
        if len(self.testing_log) == 0:
            return
        if len(self.testing_log[self.test_num]) == 0:
            return
        
        # init metrics structure for each node, emotive
        for node in self.emotives_set:
            for emotive in self.emotives_set[node]:
                results[node][emotive] = {}
                results[node][emotive]['actuals'] = []
                results[node][emotive]['predictions'] = []
                results[node][emotive]['residuals'] = []
                results[node][emotive]['abs_residuals'] = []
                results[node][emotive]['squared_residuals'] = []
        
        this_test_log = self.testing_log[self.test_num]
        for record in this_test_log:
            current_metrics = record['metrics']
            for node, node_predicted_emotives in current_metrics['predicted'].items():
                for emotive, predicted_value in node_predicted_emotives.items():
                    results[node][emotive]['predictions'].append(predicted_value)
                    results[node][emotive]['actuals'].append(current_metrics['actual'][emotive])
                    results[node][emotive]['residuals'].append(current_metrics['residuals'][node][emotive])
                    results[node][emotive]['abs_residuals'].append(current_metrics['abs_residuals'][node][emotive])
                    results[node][emotive]['squared_residuals'].append(current_metrics['squared_residuals'][node][emotive])

        last_test_record = this_test_log[-1]
        test_metrics = last_test_record['metrics']
        for node in results:
            for emotive in self.emotives_set[node]:
                
                results[node][emotive]['metrics'] = {}
                results[node][emotive]['metrics']['response_counts']            = test_metrics['response_counts'][node][emotive]
                results[node][emotive]['metrics']['response_percentage']        = test_metrics['response_percentage'][node][emotive]
                results[node][emotive]['metrics']['unknown_percentage']         = test_metrics['unknown_percentage'][node][emotive]
                results[node][emotive]['metrics']['response_percentage']        = test_metrics['response_percentage'][node][emotive]
                results[node][emotive]['metrics']['emotives_counter']           = test_metrics['emotives_counter'][emotive]
                results[node][emotive]['metrics']['training_emotive_counter']   = test_metrics['training_emotive_counter'][emotive]
                results[node][emotive]['metrics']['testing_emotive_counter']    = test_metrics['testing_emotive_counter'][emotive]
                results[node][emotive]['metrics']['rmse']                       = test_metrics['rmse'][node][emotive]
                results[node][emotive]['metrics']['smape']                      = test_metrics['smape'][node][emotive]
                results[node][emotive]['metrics']['smape_prec']                 = test_metrics['smape_prec'][node][emotive]

        return results

    def get_emotives_polarity_metrics(self):
        """
        Builds emotives polarity data structures for each node
        """
        template_dict = {'metrics': {'true_positive': 0.0,
                                     'false_positive': 0.0,
                                     'true_negative': 0.0,
                                     'false_negative': 0.0,
                                     'unknown_percentage': 0.0,
                                     'response_percentage':0.0,
                                     'response_counts': 0.0,
                                     'accuracy': 0.0,
                                     'precision': 0.0,
                                     'training_emotive_counter': 0.0,
                                     'testing_emotive_counter': 0.0,
                                     'emotives_counter': 0.0
                                     },
                         'predictions': [],
                         'actuals': []
                        }
        if len(self.testing_log[self.test_num]) == 0:
            return {}
        # lets flip the dictionary so that it is organized per node instead of per metric
        raw_test_results = deepcopy(self.testing_log[self.test_num][-1]['metrics'])

        flattened_emotive_set = set(chain(*[list(item) for item in self.emotives_set.values()]))
        hive_emotives = flattened_emotive_set
        emo_res2 = {k: {i: deepcopy(template_dict) for i in v } for k, v in self.emotives_set.items()}
        emo_res2['hive'] = {emo: deepcopy(template_dict) for emo in hive_emotives}
        print(f'{raw_test_results=}')
        for k, v in raw_test_results.items():
            if k not in ['true_positive',
                         'false_positive',
                         'true_negative',
                         'false_negative',
                         'unknown_percentage',
                         'response_percentage',
                         'response_counts',
                         'accuracy',
                         'precision']:
                continue

            for node, info in v.items():
                for emotive, emotive_data in info.items():
                    if emotive in emo_res2[node]:
                        emo_res2[node][emotive]['metrics'][k] = deepcopy(emotive_data)

        for node, results in emo_res2.items():
            for emotive, metrics in results.items():
                metrics['metrics']['training_emotive_counter'] = raw_test_results['training_emotive_counter'][emotive]
                metrics['metrics']['testing_emotive_counter'] = raw_test_results['testing_emotive_counter'][emotive]
                metrics['metrics']['emotives_counter'] = raw_test_results['emotives_counter'][emotive]

        for record in self.testing_log[self.test_num]:
            metrics = record['metrics']
            for emotive, val in metrics['actual'].items():
                for node, node_emotive_set in self.emotives_set.items():
                    if emotive in node_emotive_set:
                        emo_res2[node][emotive]['actuals'].append(val)
            for node, emotive_dict in metrics['predicted'].items():
                for emotive, val in emotive_dict.items():
                    emo_res2[node][emotive]['predictions'].append(val)
        return emo_res2


    def plot_emotives_value_charts(self):

        for node_name, node_emotive_metrics in self.emotive_value_results.items():
            if not self.QUIET: # pragma: no cover
                print(f'-----------------Test#{self.test_num}-{node_name}-Plots-----------------')
            for emotive_name, data in sorted(node_emotive_metrics.items()):
                labels = 'precision', 'miss'
                if data['metrics']['smape_prec'] is None:
                    sizes = [0, 100]
                else:
                    sizes = [data['metrics']['smape_prec'], 100 - data['metrics']['smape_prec']]
                explode = (0, 0)
                _, ax1 = plt.subplots()
                ax1.title.set_text(f'{node_name} - {emotive_name}')
                ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                        shadow=True, startangle=90)
                ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                colors = ['gray', 'skyblue']
                patches, texts = plt.pie(sizes, colors=colors, startangle=90)
                plt.legend(patches, labels, loc="best")
                supplementary_data = {'SMAPE Precision' : data['metrics']['smape_prec'],
                                      'RMSE' : data['metrics']['rmse']}
                plt.figtext(0, 0, f"{pd.Series(supplementary_data).round(1).to_string()}", ha="center", fontsize=18, bbox={"facecolor": "orange", "alpha": 0.5, "pad": 5})
                pie_plot_filepath = Path(f"{self.results_filepath}").joinpath(f"./test_{self.test_num}_{node_name}_{emotive_name}_pie.png")
                pva_plot_filepath = Path(f"{self.results_filepath}").joinpath(f"./test_{self.test_num}_{node_name}_{emotive_name}_pva.png")
                
                
                df = pd.DataFrame({'predicted': data['predictions'],
                                   'actuals': data['actuals']})
                predicted_vs_actual = go.Figure()
                predicted_vs_actual.update_layout(title=dict(text=f"Test #{self.test_num}: {emotive_name} values on {node_name}"),
                                                xaxis=dict(title="Testing Record"),
                                                yaxis=dict(title=f"{emotive_name} Value")
                                                )
                predicted_vs_actual.add_trace(go.Scatter(x=df.index, y=df.actuals, fill='tozeroy', name='Actual'))
                predicted_vs_actual.add_trace(go.Scatter(x=df.index, y=df.predicted, fill='tonexty', name='Predicted'))
                
                
                
                if self.results_filepath is not None:
                    try:
                        plt.savefig(pie_plot_filepath, dpi=300, bbox_inches='tight')
                        predicted_vs_actual.write_image(file=pva_plot_filepath)
                    except Exception as e:
                        if not self.QUIET: # pragma: no cover
                            print(f"Not able to save figure in assigned results directory! Please add an appropriate directory: {str(e)}")
                        pass
                if not self.QUIET: # pragma: no cover
                    plt.show()
                    predicted_vs_actual.show()

        plt.close('all')

    def abort_test_remediation(self, current_record, record_count):
        if not self.QUIET: # pragma: no cover
            print(f'about to abort {self.task.request.id =}, {self.test_id=}')
        if self.sio: # pragma: no cover
            if not self.QUIET: # pragma: no cover
                print('Sending abort message')
            abort_msg = PVTMessage(status='aborted', current_record=current_record + 1, total_record_count=record_count,
                                    metrics={}, cur_test_num=self.test_num, total_test_num=self.num_of_tests,
                                    test_id=self.test_id, user_id=self.user_id, test_type=self.test_type)
            self.sio.emit(self.socket_channel, abort_msg.toJSON(), to=self.user_id)
        if self.mongo_results:
            if not self.QUIET: # pragma: no cover
                print('cleaning up MongoDB')
            self.mongo_results.deleteResults()

        raise PVTAbortError(f"Aborting Test, at record {current_record} of {record_count}")

    def store_train_record(self, test_num, record: PVTMessage):
        
        if record.status == 'testing':
            self.testing_log[test_num].append(deepcopy(record.toJSON()))

        # insert into test_log in mongo, if using mongodb
        if self.mongo_results:
            self.mongo_results.addLogRecord(type=record.status, record=deepcopy(record.toJSON()))

        # emit socketIO message
        if self.sio: # pragma: no cover
            self.sio.emit(self.socket_channel, deepcopy(record.toJSON()), to=self.user_id)