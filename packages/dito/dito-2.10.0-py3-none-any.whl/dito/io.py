"""
This submodule provides functionality for low-level image input/output functions.
"""

import functools
import glob
import os.path
import pathlib
import tempfile
import time
import uuid

import cv2
import numpy as np

import dito.utils


def load(filename, color=None):
    """
    Load image from file given by `filename` and return NumPy array.

    It supports all file types that can be loaded by OpenCV (via `cv2.imread`),
    plus arrays that can be loaded by NumPy (file extensions ".npy" and ".npz",
    via `numpy.load`).

    Parameters
    ----------
    filename : str or pathlib.Path
        Path of the image file to be loaded.
    color : bool or None, optional
        Whether to load the image as color (True), grayscale (False), or as is (None). Default is None.
        Is ignored if the image is loaded via NumPy (i.e., for file extensions ".npy" and ".npz").

    Returns
    -------
    numpy.ndarray
        The loaded image as a NumPy array.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    RuntimeError
        If the file exists, but could not be loaded.
    TypeError
        If the file exists, but its type is not a NumPy array.
    ValueError
        If the specified file is neither a NumPy file nor an image file with
        extension supported by OpenCV (".jpg", ".png", ".bmp", ".tiff", etc.).

    Notes
    -----
    The bit-depth (8 or 16 bit) of the image file will be preserved.
    """

    if isinstance(filename, pathlib.Path):
        filename = str(filename)

    # check if file exists
    if not os.path.exists(filename):
        raise FileNotFoundError("Image file '{}' does not exist".format(filename))

    # load image
    if filename.endswith(".npy"):
        # use NumPy
        image = np.load(file=filename)
    elif filename.endswith(".npz"):
        # use NumPy
        with np.load(file=filename) as npz_file:
            npz_keys = tuple(npz_file.keys())
            if len(npz_keys) != 1:
                raise ValueError("Expected exactly one image in '{}', but got {} (keys: {})".format(filename, len(npz_keys), npz_keys))
            image = npz_file[npz_keys[0]]
    else:
        # use OpenCV
        if color is None:
            # load the image as it is
            flags = cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED
        else:
            # force gray/color mode
            flags = cv2.IMREAD_ANYDEPTH | (cv2.IMREAD_COLOR if color else cv2.IMREAD_GRAYSCALE)
        image = cv2.imread(filename=filename, flags=flags)

    # check if loading was successful
    if image is None:
        raise RuntimeError("Image file '{}' exists, but could not be loaded".format(filename))
    if not isinstance(image, np.ndarray):
        raise TypeError("Image file '{}' exists, but has wrong type (expected object of type 'np.ndarray', but got '{}'".format(filename, type(image)))

    return image


def load_multiple_iter(*args, color=None):
    """
    Iterator that loads all images whose filenames match a specified glob pattern.

    Parameters
    ----------
    *args : str
        Arguments that, when joined with `os.path.join`, give the file pattern of the images to load.
    color : bool or None, optional
        Whether to load the images as color (True), grayscale (False), or as is (None). Default is None. See `load`.

    Yields
    ------
    numpy.ndarray
        The loaded image as a NumPy array.
    """
    filename_pattern = os.path.join(*args)
    filenames = sorted(glob.glob(filename_pattern))
    for filename in filenames:
        image = load(filename=filename, color=color)
        yield image


def load_multiple(*args, color=None):
    """
    Load all images whose filenames match a specified glob pattern.

    Parameters
    ----------
    *args : str
        Arguments that, when joined with `os.path.join`, give the file pattern of the images to load.
    color : bool or None, optional
        Whether to load the images as color (True), grayscale (False), or as is (None). Default is None. See `load`.

    Returns
    -------
    list of numpy.ndarray
        A list of NumPy arrays, each corresponding to an image that was loaded.
    """
    return list(load_multiple_iter(*args, color=color))


def save(filename, image, mkdir=True):
    """
    Save a NumPy array `image` as an image file at `filename`.

    Supported file formats are those supported by OpenCV (via `cv2.imwrite`,
    e.g., ".jpg", ".png", ".tif", etc.) and uncompressed or compressed NumPy
    binary files (via `numpy.save` for ".npy" or via `np.savez_compressed` for
    ".npz").

    If `mkdir` is `True`, create the parent directories of the given filename
    before saving the image.

    Parameters
    ----------
    filename : str or pathlib.Path
        Path to the file where the image should be saved. The extension is used
        to determine whether to use NumPy (".npy", ".npz") or OpenCV (any other
        case).
    image : numpy.ndarray
        The image data to be saved.
    mkdir : bool, optional
        Whether to create the parent directories of the given filename if they
        do not exist. Default is True.

    Raises
    ------
    RuntimeError
        If `image` is not a NumPy array.
    """

    if isinstance(filename, pathlib.Path):
        filename = str(filename)

    if not isinstance(image, np.ndarray):
        raise RuntimeError("Invalid image (type '{}')".format(type(image).__name__))

    # create parent dir
    if mkdir:
        dito.utils.mkdir(dirname=os.path.dirname(filename))

    if filename.endswith(".npy"):
        # use NumPy
        np.save(file=filename, arr=image)
    elif filename.endswith(".npz"):
        # use NumPy
        np.savez_compressed(file=filename, arr_0=image)
    else:
        # use OpenCV
        cv2.imwrite(filename=filename, img=image)


def save_tmp(image):
    """
    Save a NumPy array `image` as a temporary image file and return the file path.

    The image file is saved in the temporary directory returned by `tempfile.gettempdir()`.
    The file name is constructed from the current time and a random UUID to ensure uniqueness.

    Parameters
    ----------
    image : numpy.ndarray
        The image data to be saved.

    Returns
    -------
    str
        The file path of the saved temporary image.
    """
    filename = os.path.join(tempfile.gettempdir(), "dito.save_tmp", "{}__{}.png".format(dito.utils.now_str(mode="readable"), str(uuid.uuid4()).split("-")[0]))
    save(filename=filename, image=image, mkdir=True)
    return filename


def decode(b, color=None):
    """
    Decode the image data from the given byte array `b` and return a NumPy array.

    The byte array should contain the *encoded* image data, which can be obtained
    with the `encode` function or by loading the raw bytes of an image file.

    Parameters
    ----------
    b : bytes
        The byte array containing the encoded image data.
    color : bool or None, optional
        Whether to load the image as color (True), grayscale (False), or as is (None). Default is None. See `load`.

    Returns
    -------
    numpy.ndarray
        The loaded image as a NumPy array.

    See Also
    --------
    `cv2.imdecode` : OpenCV function used for the decoding.
    """

    # byte array -> NumPy array
    buf = np.frombuffer(b, dtype=np.uint8)

    # flags - select grayscale or color mode
    if color is None:
        flags = cv2.IMREAD_UNCHANGED
    else:
        flags = cv2.IMREAD_ANYDEPTH | (cv2.IMREAD_COLOR if color else cv2.IMREAD_GRAYSCALE)

    # read image
    image = cv2.imdecode(buf=buf, flags=flags)

    return image


def encode(image, extension="png", params=None):
    """
    Encode the given `image` into a byte array which contains the same bytes
    as if the image would have been saved to a file.

    Parameters
    ----------
    image : numpy.ndarray
        The image to be encoded.
    extension : str, optional
        The file extension (with or without leading dot) to use for encoding the
        image. Default is "png".
    params : int or None, optional
        Parameters to pass to the encoder. These are encoder-dependent and can
        be found in the OpenCV documentation (see `cv2.imencode`). Default is
        None.

    Returns
    -------
    bytes
        A byte array which contains the encoded image data.

    See Also
    --------
    `cv2.imencode` : OpenCV function used for the encoding.
    """

    # allow extensions to be specified with or without leading dot
    if not extension.startswith("."):
        extension = "." + extension

    # use empty tuple if no params are given
    if params is None:
        params = tuple()

    (_, array) = cv2.imencode(ext=extension, img=image, params=params)

    return array.tobytes()


class CachedImageLoader():
    """
    A class that wraps the `load` function and caches the results.

    If `CachedImageLoader.load` is called with the same arguments again, the
    result is returned from cache and not loaded from disk.

    Notes
    -----
    The cache is only valid for the lifetime of the object. When the object is
    deleted, the cache is destroyed and all memory used by the cache is freed.

    See Also
    --------
    `functools.lru_cache` : The wrapper
    `dito.io.load` : The function that is wrapped by this class.
    """

    def __init__(self, max_count=128):
        """
        Create a new `CachedImageLoader` instance.

        Parameters
        ----------
        max_count : int, optional
            The maximum number of items that can be stored in the cache. This
            defaults to 128.
        """
        # decorate here, because maxsize can be specified by the user
        self.load = functools.lru_cache(maxsize=max_count, typed=True)(self.load)

    def load(self, filename, color=None):
        """
        Load an image from the specified file and return it as a NumPy array.

        This method is a wrapper around the `dito.load` function. The first time
        it is called with a given set of arguments, it loads the image from disk
        and returns it. Subsequent calls with the same arguments will return
        the result from cache.

        Parameters
        ----------
        filename : str or pathlib.Path
            The path to the file containing the image to load.
        color : bool or None, optional
            Whether to load the image as color (True), grayscale (False), or as is (None). Default is None. See `load`.

        Returns
        -------
        numpy.ndarray
            The loaded image as a NumPy array.

        See Also
        -----
        `dito.io.load` : The wrapped function used for image loading.
        """
        return load(filename=filename, color=color)

    def get_cache_info(self):
        """
        Get information about the cache used by this `CachedImageLoader` instance.

        Returns
        -------
        collections.namedtuple
            A named tuple with the following fields:
            - hits: number of cache hits
            - misses: number of cache misses
            - maxsize: maximum size of the cache
            - currsize: current size of the cache
        """
        return self.load.cache_info()

    def clear_cache(self):
        """
        Remove all items from the cache used by this `CachedImageLoader` instance.
        """
        self.load.cache_clear()


class VideoSaver():
    """
    Convenience wrapper for `cv2.VideoWriter`.

    Main differences compared to `cv2.VideoWriter`:
    * the parent dir of the output file is created automatically
    * the codec can be given as a string
    * the frame size is taken from the first provided image
    * the sizes of all following images are checked - if they do not match the size of the first image, an exception is
      raised
    * images are converted to gray/color mode automatically
    """

    def __init__(self, filename, codec="MJPG", fps=30.0, color=True):
        """
        Initialize the `VideoSaver` object.

        Parameters
        ----------
        filename : str or pathlib.Path
            Path to the output video file.
        codec : str, optional
            FourCC code or codec name to use for the video compression. Default is "MJPG".
        fps : float, optional
            Frames per second of the output video. Default is 30.0.
        color : bool, optional
            Whether to save the video in color (True) or grayscale (False). Default is True.

        Raises
        ------
        ValueError
            If the `codec` argument is not a string of length 4.
        """
        self.filename = filename
        self.codec = codec
        self.fps = fps
        self.color = color

        if isinstance(self.filename, pathlib.Path):
            self.filename = str(self.filename)

        if (not isinstance(self.codec, str)) or (len(self.codec) != 4):
            raise ValueError("Argument 'codec' must be a string of length 4")

        self.frame_count = 0
        self.image_size = None
        self.writer = None

    def __enter__(self):
        """
        Enter the context.

        Returns
        -------
        self
            This object.
        """
        return self

    def __exit__(self, *args, **kwargs):
        """
        Exit the context.

        Parameters
        ----------
        *args, **kwargs
            Arguments passed to the `exit` function. These are ignored.
        """
        self.save()

    def get_fourcc(self):
        """
        Return the FourCC code of the video codec.

        Returns
        -------
        int
            The FourCC code.
        """
        return cv2.VideoWriter_fourcc(*self.codec)

    def init_writer(self, image_size):
        """
        Initialize the writer object.

        Parameters
        ----------
        image_size : tuple of int
            The size of the images in the video (width, height).
        """
        self.image_size = image_size
        dito.utils.mkdir(os.path.dirname(self.filename))
        self.writer = cv2.VideoWriter(
            filename=self.filename,
            fourcc=self.get_fourcc(),
            fps=self.fps,
            frameSize=self.image_size,
            isColor=self.color,
        )

    def append(self, image):
        """
        Add a frame to the video.

        Parameters
        ----------
        image : numpy.ndarray
            The image data of the frame to add.

        Raises
        ------
        ValueError
            If the size of the image is different from the size of the previous images.
        """
        image_size = dito.core.size(image=image)

        # create writer if this is the first frame
        if self.writer is None:
            self.init_writer(image_size=image_size)

        # check if the image size is consistent with the previous frames
        if image_size != self.image_size:
            raise ValueError("Image size '{}' differs from previous image size '{}'".format(image_size, self.image_size))

        # apply correct color mode
        if self.color:
            image = dito.core.as_color(image=image)
        else:
            image = dito.core.as_gray(image=image)

        self.writer.write(image=image)
        self.frame_count += 1

    def save(self):
        """
        Finish writing the video and release the writer object.

        This method should be called after all frames have been appended to the
        video. If the `VideoSaver` object is used via a context manager, this
        method is called automatically when the context is exited.
        """
        if self.writer is not None:
            self.writer.release()

    def file_exists(self):
        """
        Check whether the output file already exists.

        Returns
        -------
        bool
            True if the output file exists, False otherwise.
        """
        return os.path.exists(path=self.filename)

    def get_file_size(self):
        """
        Get the size of the output file.

        Returns
        -------
        int
            The size of the output file in bytes.
        """
        return os.path.getsize(filename=self.filename)

    def print_summary(self, file=None):
        """
        Print a summary of the output video to the given file object or to the console.

        Parameters
        ----------
        file : file object or str, optional
            The file object to which the summary should be written, or a string
            representing the path of the file. Default is None, meaning stdout.

        Notes
        -----
        The summary includes the following information:
        * the codec
        * the filename
        * whether the output file exists
        * the size of the output file
        * the date and time the output file was last modified
        * the image size and color mode
        * the number, size, and color info of frames in the video
        """
        file_exists = self.file_exists()
        rows = [
            ["Output", ""],
            ["..Codec", self.codec],
            ["..Filename", self.filename],
            ["..Exists", file_exists],
            ["..Size", dito.utils.human_bytes(byte_count=self.get_file_size()) if file_exists else "n/a"],
            ["..Modified", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filename=self.filename))) if file_exists else "n/a"],
            ["Frames", ""],
            ["..Size", self.image_size],
            ["..Color", self.color],
            ["..Count", self.frame_count],
        ]
        dito.utils.ptable(rows=rows, print_kwargs={"file": file})
