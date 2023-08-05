"""
Utility tools for snews_pt
"""
import dotenv
from dotenv import load_dotenv
from collections import namedtuple
import os, json, click
import sys


from .core.logging import getLogger

log = getLogger(__name__)

def set_env(env_path=None):
    """ Set environment parameters

    Parameters
    ----------
    env_path : `str`, (optional)
        path for the environment file.
        Use default settings if not given

    """
    dirname = os.path.dirname(__file__)
    default_env_path = dirname + '/auxiliary/test-config.env'
    env = env_path or default_env_path
    load_dotenv(env)


def set_topic_state(which_topic, env_path=None):
    """ Set the topic path based on which_topic

    Parameters
    ----------
    which_topic : `str`
        single-letter string indicating the topic [O/H/A]
        If an environment was defined, it uses the topics
        specified in that environment. If not, it looks
        for the env_path parameter
    env_path : `str`
        The path to the environment configuration file

    """
    if os.getenv("ALERT_TOPIC") is None:
        set_env(env_path)
    Topics = namedtuple('Topics', ['topic_name', 'topic_broker'])
    topics = {
        'A': Topics('ALERT', os.getenv("ALERT_TOPIC")),
        'O': Topics('OBSERVATION', os.getenv("OBSERVATION_TOPIC")),
        'H': Topics('HEARTBEAT', os.getenv("OBSERVATION_TOPIC"))
    }
    return topics[which_topic.upper()]


def retrieve_detectors(detectors_path=os.path.dirname(__file__) + "/auxiliary/detector_properties.json"):
    """ Retrieve the name-ID-location of the participating detectors.

        Parameters
        ----------
        detectors_path : `str`, optional
            path to detector proporties. File needs to be
            in JSON format

        Returns
        -------
        None

    """
    if not os.path.isfile(detectors_path):
        os.system(f'python {os.path.dirname(__file__)}/auxiliary/make_detector_file.py')

    with open(detectors_path) as json_file:
        detectors = json.load(json_file)

    # make a namedtuple
    Detector = namedtuple("Detector", ["name", "id", "location"])
    for k, v in detectors.items():
        detectors[k] = Detector(v[0], v[1], v[2])
    return detectors


def get_detector(detector, detectors_path=os.path.dirname(__file__) +
                                          "/auxiliary/detector_properties.json"):
    """ Return the selected detector properties

    Parameters
    ----------
    detector : `str`
        The name of the detector. Should be one of the predetermined detectors.
        If the name is not in that list, returns TEST detector.
    detectors_path : `str`
        path for the json file with all detectors. By default this is
        /auxiliary/detector_properties.json

    """
    Detector = namedtuple("Detector", ["name", "id", "location"])
    if isinstance(detector, Detector): return detector  # not needed?
    # search for the detector name in `detectors`
    detectors = retrieve_detectors(detectors_path)
    if isinstance(detector, str):
        try:
            return detectors[detector]
        except KeyError:
            print(f'{detector} is not a valid detector!')
            return detectors['TEST']


def coincidence_tier_data(machine_time=None, neutrino_time=None, p_val=None, meta=None):
    """ Formats data for CoincidenceTier as dict object

        Parameters
        ----------
        machine_time : `str`
            The machine time at the time of execution of command
        neutrino_time : `str`
            The neutrino arrival time
        p_val : `float`
            If determined, the p value of the observation
        meta : `dict`
            Any other key-value pair desired to be published.

        Returns
        -------
            coincidence_tier_dict : `dict`
                dictionary of the complete CoincidenceTier data

    """
    keys = ['machine_time', 'neutrino_time', 'p_val', 'meta']
    values = [machine_time, neutrino_time, p_val, meta]
    zip_iterator = zip(keys, values)
    coincidence_tier_dict = dict(zip_iterator)
    return coincidence_tier_dict


def sig_tier_data(machine_time=None, neutrino_time=None, p_values=None, t_bin_width=None, meta=None):
    """ Formats data for SigTier as dict object

        Parameters
        ----------
        t_bin_width : `float`
        machine_time : `str`
            The machine time at the time of execution of command
        neutrino_time : `str`
            The neutrino arrival time
        p_values : `list`
            If determined, the p values of the observation
        meta : `dict`
            Any other key-value pair desired to be published.

        Returns
        -------
            sig_tier_dict : `dict`
                dictionary of the complete observation data

    """
    keys = ['machine_time', 'neutrino_time', 'p_values', 't_bin_width', 'meta']
    values = [machine_time, neutrino_time, p_values, t_bin_width, meta]
    zip_iterator = zip(keys, values)
    sig_tier_dict = dict(zip_iterator)
    return sig_tier_dict


def time_tier_data(machine_time=None, neutrino_time=None, p_val=None, timing_series=None, meta=None):
    """ Formats data for TimingTier as dict object

        Parameters
        ----------
        machine_time : `str`
            The machine time at the time of execution of command
        nu_time : `str`
            The neutrino arrival time
        timing_series : `array-like`
            Time series of the detected signal
        meta : `dict`
            Any other key-value pair desired to be published.

        Returns
        -------
            data_dict : `dict`
                dictionary of the TimingTier data

    """
    keys = ['machine_time', 'neutrino_time', 'timing_series', 'p_val', 'meta']
    values = [machine_time, neutrino_time, timing_series, p_val, meta]
    zip_iterator = zip(keys, values)
    time_tier_dict = dict(zip_iterator)
    return time_tier_dict


def retraction_data(machine_time=None, retract_latest=0, retraction_reason=None, meta=None):
    """ Formats data for Retraction as dict object

        Parameters
        ----------
        machine_time : `str`
            The machine time at the time of execution of command
        retract_latest: 'int' or 'str'
            Tells retraction methods to look for N  latest message sent by a detector. can also pass 'ALL'
            to retract all messages in a OBS tier.
        retraction_reason: 'str"
            Reason for message(s) retraction
       meta : `dict`
            Any other key-value pair desired to be published.


        Returns
        -------
            retraction_dict : `dict`
                dictionary of the retraction data

    """
    keys = ['machine_time', 'retract_latest', 'retraction_reason', 'meta']
    values = [machine_time, retract_latest, retraction_reason, meta]
    zip_iterator = zip(keys, values)
    retraction_dict = dict(zip_iterator)
    return retraction_dict


def heartbeat_data(machine_time=None, detector_status=None, meta=None):
    """ Formats data for Heartbeat as dict object

        Parameters
        ----------
        machine_time : `str`
            The machine time at the time of execution of command
        detector_status : 'str'
            ON or OFF
         meta : `dict`
            Any other key-value pair desired to be published.

        Returns
        -------
            heartbeat_dict : `dict`
                dictionary of the Heartbeat data

    """
    keys = ['machine_time', 'detector_status', 'meta']
    values = [machine_time, detector_status, meta]

    zip_iterator = zip(keys, values)
    heartbeat_dict = dict(zip_iterator)
    return heartbeat_dict


# used in message schema display, keep for now
def _check_aliases(tier):
    tier = tier.lower()
    coincidence_aliases = ['coincidence', 'c', 'coincidencetier', 'coinc']
    significance_aliases = ['significance', 's', 'significancetier', 'sigtier']
    timing_aliases = ['timing', 'time', 'timingtier', 'timetier', 't']
    false_aliases = ['false', 'falseobs', 'retraction', 'retract', 'r', 'f']
    heartbeat_aliases = ['heartbeat', 'hb']

    if tier in coincidence_aliases:
        tier = 'CoincidenceTier'
    elif tier in significance_aliases:
        tier = 'SigTier'
    elif tier in timing_aliases:
        tier = 'TimeTier'
    elif tier in false_aliases:
        tier = 'FalseOBS'
    elif tier in heartbeat_aliases:
        tier = 'Heartbeat'
    else:
        click.secho(f'"{tier}" <- not a valid argument!', fg='bright_red')
        sys.exit()
    return [tier]


def _parse_file(filename):
    """ Parse the file to fetch the json data

    """
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def isnotebook():
    """ Tell if the script is running on a notebook

    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def display_gif():
    """ Some fun method to display an alert gif
        If running on notebook.

    """
    if isnotebook():
        from IPython.display import HTML, display
        giphy_snews = "https://raw.githubusercontent.com/SNEWS2/hop-SNalert-app/snews2_dev/hop_comms/auxiliary/snalert.gif"
        display(HTML(f'<img src={giphy_snews}>'))


def set_name(detector_name='TEST'):
    """ set your detector's name
        messages sent with detector_name="TEST" will be
        ignored in the server
        messages can still be subscribed to as "TEST"
    """

    envpath = os.path.join(os.path.dirname(__file__), 'auxiliary/test-config.env')
    load_dotenv(envpath)
    detectors = list(retrieve_detectors().keys())
    if detector_name=="TEST":
        if int(os.getenv("HAS_NAME_CHANGED")) == 0:
            for i,d in enumerate(detectors):
                click.secho(f"[{i:2d}] {d}")
            inp = input(click.secho("Please put select your detector's index\n", bold=True))
            selected_name = detectors[int(inp)]
            os.environ["DETECTOR_NAME"] = selected_name
            os.environ["HAS_NAME_CHANGED"] = "1"
            dotenv.set_key(envpath, "DETECTOR_NAME", os.environ["DETECTOR_NAME"])
            dotenv.set_key(envpath, "HAS_NAME_CHANGED", os.environ["HAS_NAME_CHANGED"])
        else:
            click.secho(f'You are {os.environ["DETECTOR_NAME"]}')
    else:
        if not detector_name in detectors:
            raise KeyError(f"{detector_name} is not a valid detector. \nChoose from {detectors}")
        os.environ["DETECTOR_NAME"] = detector_name
        os.environ["HAS_NAME_CHANGED"] = "1"
        dotenv.set_key(envpath, "DETECTOR_NAME", os.environ["DETECTOR_NAME"])
        dotenv.set_key(envpath, "HAS_NAME_CHANGED", os.environ["HAS_NAME_CHANGED"])


def get_name():
    """ Get the name of the detector from the
        env file

    """
    return os.getenv("DETECTOR_NAME")

def prettyprint_dictionary(dictionary, indent=0):
    """ tabulate the message in prettier form
    """
    for key, value in dictionary.items():
        if isinstance(value, dict):
            print("\t" * indent + f'{key:<19}:', end="\n" + "\t" * indent)
            prettyprint_dictionary(value, indent + 1)
        else:
            print("\t" * indent + f'{key:<19}:{value}')
