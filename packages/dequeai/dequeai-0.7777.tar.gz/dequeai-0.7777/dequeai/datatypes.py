from PIL import Image as PILImage
import PIL
import pickle
import json
import time
import dequeai.util as util
import numpy as np
from dequeai.util import DEQUE_IMAGE,DEQUE_HISTOGRAM,DEQUE_AUDIO, DEQUE_TEXT, DEQUE_TABLE, DEQUE_VIDEO, DEQUE_BOUNDING_BOX, DEQUE_PLOT
from dequeai.util import *
#import altair

class BoundingBox2D():
    _type = DEQUE_BOUNDING_BOX
    def __init__(self, coordinates, domain=None, scores=None, caption=None):
        self.coordinates = coordinates
        if domain is None:
            self.domain = "relative"
        else:
            self.domain = domain
        self.scores = scores
        self.caption = caption


    def _validate(self):
        pass

    def to_json(self):
        return {"coordinates":self.coordinates,"domain":self.domain,"scores":self
                .scores,"caption":self.caption}


class Image:
    _type = DEQUE_IMAGE

    def __init__(self, data, box_data=None, mode=None):
        self._images = []
        self._box_data = None

        if isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Empty list. The list must have one or more images of type numpy, tensor or pil")

            if box_data is not None:
                raise ValueError(
                    "Bounding boxes cannot be set with data of array type. In order to use bounding box, "
                    "please pass data of type pil image, tensor or numpy array")

            for d in data:
                if isinstance(data, PILImage.Image):
                    self._images.append(d)
                    # print("I am PIL image")
                elif util.is_type_torch_tensor(util.get_full_typename(data)):
                    torch_module = util.get_module(
                        "torch", "torch is required to render images"
                    )
                    _image = self._tensor_to_pil_image(torch_module=torch_module, pic=d, mode=mode)
                    self._images.append(_image)
                    # print("I used to be tensor image")
                else:
                    if hasattr(d, "numpy"):  # TF data eager tensors
                        d = d.numpy()
                    if d.ndim > 2:
                        d = d.squeeze()  # get rid of trivial dimensions as a convenience
                    _image = PILImage.fromarray(
                        self.to_uint8(d), mode=mode or self.guess_mode(d)
                    )
                    self._images.append(_image)
                    # print("I used to be numpy image")

        else:
            if isinstance(data, PILImage.Image):
                self._images.append(data)
                # print("I am PIL image")
            elif util.is_type_torch_tensor(util.get_full_typename(data)):
                torch_module = util.get_module(
                    "torch", "torch is required to render images"
                )
                self._images.append(self._tensor_to_pil_image(torch_module=torch_module, pic=data, mode=mode))
                # print("I used to be tensor image")
            else:
                if hasattr(data, "numpy"):  # TF data eager tensors
                    data = data.numpy()
                if data.ndim > 2:
                    data = data.squeeze()  # get rid of trivial dimensions as a convenience
                self._images.append(PILImage.fromarray(
                    self.to_uint8(data), mode=mode or self.guess_mode(data)
                ))

        if box_data is not None:
            if not isinstance(box_data, list):
                raise ValueError("box_data must be a list of BoundingBox2d objects")
            for b in box_data:
                if not isinstance(b, BoundingBox2D):
                    raise ValueError("box_data array must have BoundingBox2d objects")

        self._box_data = box_data
        self._validate_size()


    def _validate_size(self):
        pass

    def _tensor_to_pil_image(self, torch_module, pic, mode):

        if not (isinstance(pic, torch_module.Tensor) or isinstance(pic, np.ndarray)):
            raise TypeError(f"pic should be Tensor or ndarray. Got {type(pic)}.")

        elif isinstance(pic, torch_module.Tensor):
            if pic.ndimension() not in {2, 3}:
                raise ValueError(f"pic should be 2/3 dimensional. Got {pic.ndimension()} dimensions.")

            elif pic.ndimension() == 2:
                # if 2D image, add channel dimension (CHW)
                pic = pic.unsqueeze(0)

            # check number of channels
            if pic.shape[-3] > 4:
                raise ValueError(f"pic should not have > 4 channels. Got {pic.shape[-3]} channels.")

        elif isinstance(pic, np.ndarray):
            if pic.ndim not in {2, 3}:
                raise ValueError(f"pic should be 2/3 dimensional. Got {pic.ndim} dimensions.")

            elif pic.ndim == 2:
                # if 2D image, add channel dimension (HWC)
                pic = np.expand_dims(pic, 2)

            # check number of channels
            if pic.shape[-1] > 4:
                raise ValueError(f"pic should not have > 4 channels. Got {pic.shape[-1]} channels.")

        npimg = pic
        if isinstance(pic, torch_module.Tensor):
            if pic.is_floating_point() and mode != "F":
                pic = pic.mul(255).byte()
            npimg = np.transpose(pic.cpu().numpy(), (1, 2, 0))

        if not isinstance(npimg, np.ndarray):
            raise TypeError("Input pic must be a torch.Tensor or NumPy ndarray, not {type(npimg)}")

        if npimg.shape[2] == 1:
            expected_mode = None
            npimg = npimg[:, :, 0]
            if npimg.dtype == np.uint8:
                expected_mode = "L"
            elif npimg.dtype == np.int16:
                expected_mode = "I;16"
            elif npimg.dtype == np.int32:
                expected_mode = "I"
            elif npimg.dtype == np.float32:
                expected_mode = "F"
            if mode is not None and mode != expected_mode:
                raise ValueError(
                    f"Incorrect mode ({mode}) supplied for input type {np.dtype}. Should be {expected_mode}")
            mode = expected_mode

        elif npimg.shape[2] == 2:
            permitted_2_channel_modes = ["LA"]
            if mode is not None and mode not in permitted_2_channel_modes:
                raise ValueError(f"Only modes {permitted_2_channel_modes} are supported for 2D inputs")

            if mode is None and npimg.dtype == np.uint8:
                mode = "LA"

        elif npimg.shape[2] == 4:
            permitted_4_channel_modes = ["RGBA", "CMYK", "RGBX"]
            if mode is not None and mode not in permitted_4_channel_modes:
                raise ValueError(f"Only modes {permitted_4_channel_modes} are supported for 4D inputs")

            if mode is None and npimg.dtype == np.uint8:
                mode = "RGBA"
        else:
            permitted_3_channel_modes = ["RGB", "YCbCr", "HSV"]
            if mode is not None and mode not in permitted_3_channel_modes:
                raise ValueError(f"Only modes {permitted_3_channel_modes} are supported for 3D inputs")
            if mode is None and npimg.dtype == np.uint8:
                mode = "RGB"

        if mode is None:
            raise TypeError(f"Input type {npimg.dtype} is not supported")

        return PILImage.fromarray(npimg, mode=mode)

    def guess_mode(self, data: "np.ndarray") -> str:
        """
        Guess what type of image the np.array is representing
        """
        # TODO: do we want to support dimensions being at the beginning of the array?
        if data.ndim == 2:
            return "L"
        elif data.shape[-1] == 3:
            return "RGB"
        elif data.shape[-1] == 4:
            return "RGBA"
        else:
            raise ValueError(
                "Un-supported shape for image conversion %s" % list(data.shape)
            )

    @classmethod
    def to_uint8(cls, data: "np.ndarray") -> "np.ndarray":
        """
        Converts floating point image on the range [0,1] and integer images
        on the range [0,255] to uint8, clipping if necessary.
        """
        np = util.get_module(
            "numpy",
            required="Deque.Image requires numpy if not supplying PIL Images: pip install numpy",
        )

        dmin = np.min(data)
        if dmin < 0:
            data = (data - np.min(data)) / np.ptp(data)
        if np.max(data) <= 1.0:
            data = (data * 255).astype(np.int32)

        # assert issubclass(data.dtype.type, np.integer), 'Illegal image format.'
        return data.clip(0, 255).astype(np.uint8)


class Histogram:
    """
    This object works just like numpy's histogram function
    https://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
    Examples:
        Generate histogram from a sequence
        ```python
        dequeapp.Histogram([1,2,3])
        ```
        Efficiently initialize from np.histogram.
        ```python
        hist = np.histogram(data)
        dequeapp.Histogram(np_histogram=hist)
        ```
    Arguments:
        sequence: (array_like) input data for histogram
        np_histogram: (numpy histogram) alternative input of a precomputed histogram
        num_bins: (int) Number of bins for the histogram.  The default number of bins
            is 64.  The maximum number of bins is 512
    Attributes:
        bins: ([float]) edges of bins
        histogram: ([int]) number of elements falling in each bin
    """

    MAX_LENGTH: int = 512
    _type = DEQUE_HISTOGRAM

    def __init__(
        self,

        np_histogram=None,

    ):
       if np_histogram:
            if len(np_histogram) == 2:
                self._histogram = (
                    np_histogram[0].tolist()
                    if hasattr(np_histogram[0], "tolist")
                    else np_histogram[0]
                )
                self._bins = (
                    np_histogram[1].tolist()
                    if hasattr(np_histogram[1], "tolist")
                    else np_histogram[1]
                )
            else:
                raise ValueError(
                    "Expected np_histogram to be a tuple of (values, bin_edges) or sequence to be specified"
                )

       if len(self._histogram) > self.MAX_LENGTH:
            raise ValueError(
                "The maximum length of a histogram is %i" % self.MAX_LENGTH
            )
       if len(self._histogram) + 1 != len(self._bins):
            raise ValueError("len(bins) must be len(histogram) + 1")



    @classmethod
    def from_sequence(cls, sequence, num_bins):
        np = util.get_module(
            "numpy", required="Auto creation of histograms requires numpy"
        )

        np_histogram = np.histogram(sequence, bins=num_bins)

        #histogram = np_histogram.tolist()


        #if len(histogram) > cls.MAX_LENGTH:
            #raise ValueError(
               #"The maximum length of a histogram is %i" % cls.MAX_LENGTH
            #)
        #if len(histogram) + 1 != len(bins):
            #raise ValueError("len(bins) must be len(histogram) + 1")

        return cls(np_histogram=np_histogram)

class Audio:
    _type = DEQUE_AUDIO
    def __init__(self, data, sample_rate=None, caption=None):
        """Accepts a path to an audio file or a numpy array of audio data."""

        self._duration = None
        self._sample_rate = sample_rate
        self._caption = caption


        if sample_rate is None:
                raise ValueError(
                    'Argument "sample_rate" is required when instantiating deque.Audio with raw data.'
                )


        self._validate_size()
        self._data = data

    def _validate_size(self):
        pass
class Video:
    _type = DEQUE_VIDEO

class Text:
    _type = DEQUE_TEXT



class Table:
    _type = DEQUE_TABLE

    '''
    'col1': [1, 2], 'col2': [3, 4]}
    >>> df = pd.DataFrame(data=d)
    >>> df
       col1  col2
    0     1     3
    1     2     4

    
    '''


    '''
    
    df2 = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    ...                    columns=['a', 'b', 'c'])
    >>> df2
       a  b  c
    0  1  2  3
    1  4  5  6
    2  7  8  9
    '''

    '''
    
    Constructing DataFrame from a numpy ndarray that has labeled columns:
    >>> data = np.array([(1, 2, 3), (4, 5, 6), (7, 8, 9)],
    ...                 dtype=[("a", "i4"), ("b", "i4"), ("c", "i4")])
    >>> df3 = pd.DataFrame(data, columns=['c', 'a'])
    ...
    >>> df3
       c  a
    0  3  1
    1  6  4
    2  9  7
    
    
    '''

    def __init__(self, data, columns=None):
        self._data = data
        self._columns=columns
        self._validate_data(data)
        self._validate_columns(columns)

    def _validate_data(self, data):

        if not isinstance(data, list):
            raise TypeError("data argument must be a list (rows) of list (column values)")

        for row in data:
            if not isinstance(row, list):
                raise TypeError("data argument must be a list (rows) of list (column values)")

            for column_val in row:
                if not isinstance(column_val,(Image,Audio,Video,Text,Histogram)) and not column_val.__class__.__module__ == 'builtins':
                    print("checking whether it is builtin datatype")
                    print(column_val.__class__.__module__)
                    print("checking whether it is deque datatype")
                    print(isinstance(column_val,(Image,Audio,Video,Text,Histogram)))
                    raise TypeError("Each column value must be a deque datatype or a builtin python type")


    def _validate_columns(self, columns):
        pass
'''
class Plot:
    _type = DEQUE_PLOT

    def __init__(self, data: Table=None, altair_chart=None,plot_type=BAR, plot_attributes=None):

        self._data=data
        self._altair_chart = altair_chart

        self._plot_type=plot_type
        self._plot_attributes = plot_attributes
        self._validate_plot()
        if self._altair_chart is not None:
            self._vega_json = self._read_vega_json()
        else:
            self._vega_json = None


    def _validate_plot(self):
        if self._altair_chart is None and self._data is None:
            raise ValueError("Plot needs either a Deque Table or an Altair chart to initialize")

    def _read_vega_json(self):

        js_rep = self._altair_chart.properties(background="#61537B").to_json()
        return js_rep

    def to_vega_json(self):
        return self._vega_json

    def to_json(self):
        return {"data":self._data,"plot_type":self._plot_type,"plot_attributes":self._plot_attributes,"vega_json":self._vega_json,"datatype":Plot._type}
'''

if __name__ == "__main__":
    #bins = [0,1, 2, 3]
    #h = np.histogram([1,2,1], bins=bins)
    import matplotlib.pyplot as plt

    #plt.hist(h)
    #plt.hist(h, bins=bins)
    #plt.show()
    #dh = Histogram(np_histogram=h)
    #dh=Histogram.from_sequence(sequence=[0,2,1], num_bins=[0,1,2,3])
    import altair as alt
    import pandas as pd

    source = pd.DataFrame({
        'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
    })

    chart = alt.Chart(source).mark_bar().encode(
        x='a',
        y='b'
    )

    #pl =Plot(altair_chart=chart)
    #print(pl.to_vega_json())


