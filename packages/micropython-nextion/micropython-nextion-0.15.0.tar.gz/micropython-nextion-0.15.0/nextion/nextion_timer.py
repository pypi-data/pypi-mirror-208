#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
NexTimer

Functions to interact with a Nextion Timer element
"""

# custom packages
from .common import Common, CommonTimerMixin


class NexTimerError(Exception):
    """Base class for exceptions in this module."""
    pass


class NexTimer(Common, CommonTimerMixin):
    """docstring for NexTimer"""
    def __init__(self, nh, pid: int, cid: int, name: str) -> None:
        """
        Init timer

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

        self.__cb_push = None
        self.__cb_pop = None
        self.__cbpop_ptr = None
        self.__cbpush_ptr = None

    def attachTimer(self, cb):
        raise NexTimerError("Not yet implemented")

    def detachTimer(self):
        raise NexTimerError("Not yet implemented")

    def getCycle(self) -> int:
        """
        Get timer cycle value

        :returns:   The timer cycle
        :rtype:     int
        """
        return self.getTimer()

    def setCycle(self, number: int) -> bool:
        """
        Set timer cycle value

        :param      number:  The timer cycle
        :type       number:  int

        :returns:   True on success, false otherwise
        :rtype:     bool
        """
        return self.setTimer(number, 50)
