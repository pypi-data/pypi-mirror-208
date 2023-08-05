"""
This submodule provides functionality for the conversion of NumPy arrays to other formats.
"""

import numpy as np

import dito.core
import dito.exceptions


#
# PySide6
#


def to_PySide6_QPixmap_format(image):
    """
    Determine the QImage.Format which is compatible with the given image.

    Parameters
    ----------
    image : np.ndarray
        The input image.

    Returns
    -------
    PySide6.QtGui.QImage.Format
        The QImage.Format which is compatible with the given image.

    Raises
    ------
    ImportError
        If PySide6 is not installed.
    dito.exceptions.ConversionError
        If the given image cannot be converted to a compatible QImage.Format.
    """
    import PySide6.QtGui

    dtype = image.dtype
    if dito.core.is_gray(image):
        if dtype == np.uint8:
            return PySide6.QtGui.QImage.Format_Grayscale8
        elif dtype == np.uint16:
            return PySide6.QtGui.QImage.Format_Grayscale16
        else:
            raise dito.exceptions.ConversionError("Conversion of grayscale image with dtype '{}' to QPixmap is not supported".format(dtype))

    elif dito.core.is_color(image):
        if dtype == np.uint8:
            return PySide6.QtGui.QImage.Format_BGR888
        else:
            raise dito.exceptions.ConversionError("Conversion of color image with dtype '{}' to QPixmap is not supported".format(dtype))

    else:
        raise dito.exceptions.ConversionError("Conversion image with shape {} to QPixmap is not supported".format(image.shape))


def to_PySide6_QImage(image):
    """
    Convert a numpy.ndimage to PySide6.QtGui.QImage.QImage.

    Parameters
    ----------
    image : np.ndarray
        The input image.

    Returns
    -------
    PySide6.QtGui.QImage
        The QImage representation of the input image.

    Raises
    ------
    ImportError
        If PySide6 is not installed.
    """
    import PySide6.QtGui
    return PySide6.QtGui.QImage(
        np.require(image, requirements="C"),
        image.shape[1],
        image.shape[0],
        to_PySide6_QPixmap_format(image),
    )


def to_PySide6_QPixmap(image):
    """
    Convert a numpy.ndimage to PySide6.QtGui.QImage.QPixmap.

    Parameters
    ----------
    image : np.ndarray
        The input image.

    Returns
    -------
    PySide6.QtGui.QPixmap
        The QPixmap representation of the input image.

    Raises
    ------
    ImportError
        If PySide6 is not installed.
    """
    import PySide6.QtGui
    q_image = to_PySide6_QImage(image)
    return PySide6.QtGui.QPixmap(q_image)
