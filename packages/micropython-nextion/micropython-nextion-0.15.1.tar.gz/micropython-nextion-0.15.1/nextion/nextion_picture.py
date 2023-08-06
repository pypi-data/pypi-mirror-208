#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
NexPicture

Functions to interact with a Nextion Picture element
"""

# custom packages
from .common import Common, CommonBackgroundPicMixin, CommonPictureMixin


class NexPictureError(Exception):
    """Base class for exceptions in this module."""
    pass


class NexPicture(Common, CommonBackgroundPicMixin, CommonPictureMixin):
    """docstring for NexPicture"""
    def __init__(self, nh, pid: int, cid: int, name: str) -> None:
        """
        Init picture

        :param      nh:    The Nextion hardware interface object
        :type       nh:    NexHardware
        :param      pid:   The page ID
        :type       pid:   int
        :param      cid:   The component ID
        :type       cid:   int
        :param      name:  The component name
        :type       name:  str
        """
        super().__init__(nh, pid, cid, name)

        CommonBackgroundPicMixin_unsupported_functions = [
            "Get_background_crop_picc",
            "Set_background_crop_picc",
        ]
        for attr_name in CommonBackgroundPicMixin_unsupported_functions:
            delattr(CommonBackgroundPicMixin, attr_name)
