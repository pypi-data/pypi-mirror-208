#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
NexCrop

Functions to interact with a Nextion Crop element
"""

# custom packages
from .common import Common, CommonBackgroundPicMixin, CommonPictureMixin


class NexCropError(Exception):
    """Base class for exceptions in this module."""
    pass


class NexCrop(Common, CommonBackgroundPicMixin, CommonPictureMixin):
    """docstring for NexCrop"""
    def __init__(self, nh, pid: int, cid: int, name: str) -> None:
        """
        Init crop

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
            "Get_background_image_pic",
            "Set_background_image_pic",
        ]
        for attr_name in CommonBackgroundPicMixin_unsupported_functions:
            delattr(CommonBackgroundPicMixin, attr_name)
