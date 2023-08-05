from importlib import import_module
from dequeai.deque_environment import AGENT_API_SERVICE_URL
_not_importable = set()

DEQUE_IMAGE = "deque_image"
DEQUE_HISTOGRAM = "deque_histogram"
DEQUE_AUDIO="deque_audio"
DEQUE_VIDEO="deque_video"
DEQUE_TABLE="deque_table"
DEQUE_TEXT="deque_text"
DEQUE_BOUNDING_BOX="deque_bounding_box"
DEQUE_PLOT="deque_plot"
MODEL="model"
DATA="data"
PYTORCH="pytorch"
TENSORFLOW="tensorflow"
ENVIRONMENT="environment"
CODE="code"
RESOURCES = "resources"


# chart types
BAR ="bar",
STACKED_BAR = "stacked_bar"
GROUPED_BAR = "grouped_bar"
NESTED_BAR = "nested_bar"
HEATMAP="heatmap"
POPULATION_PYRAMID = "population_pyramid"
LINE="line"
AREA="area"
STACKED_AREA="stacked_area"
HORIZON="horizon"
JOB_VOYAGER="job_voyager"
PIE="pie"
DONUT="donut"
RADIAL="radial"
RADAR="radar"
SCATTER="scatter"
SCATTER_WITH_NULL_VALUES="scatter_with_null_values"
CONNECTED_SCATTER="connected_scatter"
ERROR_BARS ="error_bars"
BARLEY_TRELLIS="barley_trellis"
REGRESSION="regression"
LABELLED_SCATTER="labelled_scatter"
TOP_K="top_k"
HISTOGRAM="histogram"
DOT="dot"
PROBABILITY_DENSITY="probability_density"
BOX="box"
VIOLIN="violin"
BINNED_SCATTER="binned_scatter"
CONTOUR="contour"
WHEAT="wheat"
TREE="tree"
FORCE_DIRECTED_LAYOUT="forced_directed_layout"
REORDERABLE_MATRIX="reorderable_matrix"
ARC_DIAGRAM="arc_diagram"

WORD_CLOUD="word_cloud"
BEESWARM="beeswarm"
PACKED_BUBBLE="packed_bubble"

TRACKING_ENDPOINT = AGENT_API_SERVICE_URL+"/fex/python/track/"

def get_full_typename(o):

    instance_name = o.__class__.__module__ + "." + o.__class__.__name__
    if instance_name in ["builtins.module", "__builtin__.module"]:
        return o.__name__
    else:
        return instance_name


def is_type_torch_tensor(typename):
    return typename.startswith("torch.") and (
            "Tensor" in typename or "Variable" in typename
    )


def get_module(name, required=None):
    """
    Return module or None. Absolute import is required.
    :param (str) name: Dot-separated module path. E.g., 'scipy.stats'.
    :param (str) required: A string to raise a ValueError if missing
    :return: (module|None) If import succeeds, the module will be returned.
    """
    if name not in _not_importable:
        try:
            return import_module(name)
        except Exception as e:
            _not_importable.add(name)
            msg = "Error importing optional module {}".format(name)

    if required and name in _not_importable:
        raise Exception("required")