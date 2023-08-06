"""Utility functions for interacting with GAIuS"""
import warnings
import json
import os
from itertools import chain
from collections import Counter
from copy import deepcopy

class GDFFormatError(BaseException):
    """Error raised when GDF is of improper format"""
    pass

def create_gdf(strings=None,
               vectors=None,
               emotives=None,
               metadata=None) -> dict:
    """Create GDF using supplied list of strings, vectors, emotives, and/or
    metadata

    Args:
        strings (list, optional): Used to provide symbols as string data
            to GAIuS. Defaults to None.
        vectors (list, optional): Used to input vector data to GAIuS.
            Defaults to None.
        emotives (dict, optional): Used to provide emotional data to GAIuS.
            Defaults to None.
        metadata (dict, optional): Used to provide miscellaneous data to GAIuS.
            Defaults to None.

    Returns:
        dict: A dictionary representing the GDF

    Example:
        .. code-block:: python

            from ia.gaius.utils import create_gdf
            gdf = create_gdf(strings=["hello"], emotives={"happy": 10.0})


    .. warning::
        If fields provided are not of the type expected, a GDFFormatError will be
        raised
    
    .. testsetup:: creategdf
        
        # here are the expected gdfs
        gdf1 = {"strings": [],
                "vectors": [],
                "emotives": {},
                "metadata": {}
                }
        gdf2 = {"strings": ["hello"],
                "vectors": [],
                "emotives": {},
                "metadata": {}
                }
        gdf3 = {"strings": ["hello"],
                "vectors": [[1, 2, 3, 4]],
                "emotives": {},
                "metadata": {}
                }
        gdf4 = {"strings": ["hello"],
                "vectors": [[1, 2, 3, 4]],
                "emotives": {"utility": 50},
                "metadata": {}
                }
        gdf5 = {"strings": ["hello"],
                "vectors": [[1, 2, 3, 4]],
                "emotives": {"utility": 50},
                "metadata": {"hello": "world"}
                }
        from ia.gaius.utils import create_gdf
        
    .. doctest:: creategdf
        :hide:
        
        >>> create_gdf() == gdf1
        True
        >>> create_gdf(strings=["hello"]) == gdf2
        True
        >>> create_gdf(strings=["hello"], vectors=[[1, 2, 3, 4]]) == gdf3
        True
        >>> create_gdf(strings=["hello"], vectors=[[1, 2, 3, 4]], emotives={"utility": 50}) == gdf4
        True
        >>> create_gdf(strings=["hello"], vectors=[[1, 2, 3, 4]], emotives={"utility": 50}, metadata={"hello": "world"}) == gdf5
        True

    """
    gdf = {
        "vectors": [] if vectors is None else vectors,
        "strings": [] if strings is None else strings,
        "emotives": {} if emotives is None else emotives,
        "metadata": {} if metadata is None else metadata
    }

    if not isinstance(gdf['vectors'], list):
        raise GDFFormatError(f"vectors field is of type \
                                  {type(gdf['vectors'])}, expected list")
    for v in gdf['vectors']:
        if not isinstance(v, list):
            raise GDFFormatError(f'Vector at index {gdf["vectors"].index(v)} is not a list')
    if not isinstance(gdf['strings'], list):
        raise GDFFormatError(f"strings field is of type \
                                  {type(gdf['strings'])}, expected list")
    if not isinstance(gdf['emotives'], dict):
        raise GDFFormatError(f"emotives field is of type \
                                  {type(gdf['emotives'])}, expected dict")
    if not isinstance(gdf['metadata'], dict):
        raise GDFFormatError(f"metadata field is of type \
                                  {type(gdf['metadata'])}, expected dict")

    return gdf


def log_progress(sequence, every=None, size=None, name='Items'): # pragma: no cover
    """
    A nice little Jupyter progress bar widget from:
    https://github.com/alexanderkuk/log-progress
    """
    from ipywidgets import IntProgress, HTML, VBox
    from IPython.display import display

    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)     # every 0.5%
    else:
        assert every is not None, 'sequence is iterator, set every'

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, record in enumerate(sequence, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = '{name}: {index} / ?'.format(
                        name=name,
                        index=index
                    )
                else:
                    progress.value = index
                    label.value = u'{name}: {index} / {size}'.format(
                        name=name,
                        index=index,
                        size=size
                    )
            yield record
    except Exception as e:
        print(f'Error in log_progress function: {str(e)})')
        progress.bar_style = 'danger'
        raise
    else:
        progress.bar_style = 'success'
        progress.value = index
        label.value = "{name}: {index}".format(
            name=name,
            index=str(index or '?')
        )


def abstract_names(ensemble: list) -> list:
    """Get a set of model names from a prediction ensemble

    Args:
        ensemble (list): a prediction ensemble

    Returns:
        list: list of models from predictions in the prediction ensemble

    Example:

        .. code-block:: python

            from ia.gaius.agent_client import AgentClient
            from ia.gaius.utils import abstract_names
            ...
            agent = AgentClient(agent_info)
            agent.connect()
            ...
            ensemble = agent.get_predictions(nodes=['P1'])
            models = abstract_names(ensemble)

    .. testsetup:: abstract_names
    
        # example prediction sequences
        ensemble1 = []
        ensemble2 = [{"name": "MODEL|1"},
                     {"name": "MODEL|2"},
                     {"name": "MODEL|3"},
                     {"name": "MODEL|4"},
                     {"name": "MODEL|5"}]
        ensemble3 = [{"name": "MODEL|0"},
                     {"name": "MODEL|0"},
                     {"name": "MODEL|0"},
                     {"name": "MODEL|0"},
                     {"name": "MODEL|0"}]
        from ia.gaius.utils import abstract_names

    .. doctest:: abstract_names
        :hide:
        
        >>> abstract_names(ensemble1) == []
        True
        >>> sorted(abstract_names(ensemble2)) == sorted(["MODEL|1", "MODEL|2", "MODEL|3", "MODEL|4", "MODEL|5"])
        True
        >>> abstract_names(ensemble3) == ['MODEL|0']
        True

    """
    return list(set([pred['name'] for pred in ensemble]))


def write_gdf_to_file(directory_name: str,
                      filename: str,
                      sequence: list) -> str:
    """Write a GDF sequence to a file

    Args:
        directory_name (str, required): directory to save GDFs to
        filename (str, required): filename to save to
        sequence (list, required): list of individual GDF events
            making up a sequence

    Example:
        .. code-block:: python

            from ia.gaius.utils import write_gdf_to_file, create_gdf
            sequence = [create_gdf(strings=["hello"]),
                        create_gdf(strings=["world"])]
            filename = 'hello_world'
            directory_name = '/example/dir'
            write_gdf_to_file(directory_name, filename, sequence)

    .. warning::
        Will overwrite the file at ``<directory_name>/<filename>``.
        Please ensure it is acceptable to do so.
        No safety checks are performed in this function

    """
    gdf_file_path = os.path.join(directory_name, filename)
    with open(gdf_file_path, 'w') as f:
        for event_idx, event in enumerate(sequence):
            json.dump(event, f)
            if event_idx != len(sequence) - 1:
                f.write('\n')

    return 'success'


def retrieve_bottom_level_records(traceback: dict) -> list:
    """Retrieve all records from a traceback
    (:func:`ia.gaius.agent_client.AgentClient.investigate_record`)
    call that have bottomLevel=True

    Args:
        traceback (dict): the dictionary pertaining to the output
            of an investigate call

    Returns:
        list: list of records from the traceback

    Example:
        .. code-block:: python

            from ia.gaius.agent_client import AgentClient
            from ia.gaius.utils import retrieve_bottom_level_records
            ...
            agent = AgentClient(agent_info)
            ...
            traceback_output = agent.investigate_record(record=record,
                                                        node=['P1'])
            bottom_level = retrieve_bottom_level_records(traceback_output)

    """
    bottom_level_records = []
    if traceback['bottomLevel'] is not True:
        for item_list in traceback['subitems']:
            for item in item_list:
                if isinstance(item, dict):
                    bottom_level_records.extend(retrieve_bottom_level_records(deepcopy(item)))
    else:
        bottom_level_records.append(traceback)

    return bottom_level_records

def merge_gdfs(gdf1: dict, gdf2: dict) -> dict:
    """Merge two GDFs into a single gdf, accumulating the values in each field

    Args:
        gdf1 (dict): First GDF
        gdf2 (dict): Second GDF

    Raises:
        Exception: When vectors are of differing lengths

    Returns:
        dict: Merged GDF
    """

    merge_strings = list(chain(gdf1["strings"], gdf2["strings"]))

    merge_vecs = list(chain(gdf1["vectors"], gdf2["vectors"]))
    print(f"{merge_vecs=}")
    if len(merge_vecs) > 0:
        if not all([len(vec) == len(merge_vecs[0]) for vec in merge_vecs]):
            raise Exception(f"Vectors not all of same length!!!")

    merge_emotives = Counter()
    merge_emotives.update(gdf1["emotives"])
    merge_emotives.update(gdf2["emotives"])
    merge_emotives = dict(merge_emotives)

    # no way to get around conflicts here, just going to add keys from gdf1, then update with keys from gdf2
    merge_metadata = dict()
    merge_metadata.update(gdf1.get("metadata", {}))
    merge_metadata.update(gdf2.get("metadata", {}))

    return create_gdf(strings=merge_strings, vectors=merge_vecs, emotives=merge_emotives, metadata=merge_metadata)
