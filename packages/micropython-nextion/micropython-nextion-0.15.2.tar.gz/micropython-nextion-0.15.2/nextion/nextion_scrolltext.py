#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
NexScrolltext

Functions to interact with a Nextion Scrolltext element
"""

# system packages
from time import sleep

# custom packages
# from .common import Common, CommonBackgroundColorMixin, \
#     CommonBackgroundPicMixin, CommonFontMixin, CommonPositionMixin, \
#     CommonTextMixin, CommonTimerMixin
from .common import Common, CommonBackgroundColorMixin, CommonFontMixin, \
    CommonPositionMixin, CommonTextMixin, CommonTimerMixin


class NexScrolltextError(Exception):
    """Base class for exceptions in this module."""
    pass


# class NexScrolltext(Common, CommonBackgroundColorMixin,
#                     CommonBackgroundPicMixin, CommonFontMixin,
#                     CommonPositionMixin, CommonTextMixin, CommonTimerMixin):
class NexScrolltext(Common, CommonBackgroundColorMixin, CommonFontMixin,
                    CommonPositionMixin, CommonTextMixin, CommonTimerMixin):
    """docstring for NexScrolltext"""
    def __init__(self, nh, pid: int, cid: int, name: str) -> None:
        """
        Init scrolltext

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

    def Get_scroll_dir(self) -> int:
        """
        Get dir attribute of component

        :returns:   The scroll direction
        :rtype:     int
        """
        cmd = "get {}.dir".format(self.name)
        self._nh.sendCommand(cmd)
        sleep(0.1)  # necessary, data might not be available otherwise
        return self._nh.recvRetNumber()

    def Set_scroll_dir(self, number: int) -> bool:
        """
        Set dir attribute of component

        :param      number:  The scroll directory
        :type       number:  int

        :returns:   True on success, false otherwise
        :rtype:     bool
        """
        cmd = "{}.dir={}".format(self.name, number)
        self._nh.sendCommand(cmd)
        cmd = "ref {}".format(self.name)
        self._nh.sendCommand(cmd)
        return self._nh.recvRetCommandFinished()

    def Get_scroll_distance(self) -> int:
        """
        Get dis attribute of component

        :returns:   The scroll distance
        :rtype:     int
        """
        cmd = "get {}.dis".format(self.name)
        self._nh.sendCommand(cmd)
        sleep(0.1)  # necessary, data might not be available otherwise
        return self._nh.recvRetNumber()

    def Set_scroll_distance(self, number: int) -> bool:
        """
        Set dis attribute of component

        :param      number:  The scroll distance
        :type       number:  int

        :returns:   True on success, false otherwise
        :rtype:     bool
        """
        if number < 2:
            number = 2

        cmd = "{}.dis={}".format(self.name, number)
        self._nh.sendCommand(cmd)
        cmd = "ref {}".format(self.name)
        self._nh.sendCommand(cmd)
        return self._nh.recvRetCommandFinished()
