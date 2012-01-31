# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
:mod:`engine.console` -- Console Prxy to set up VM console access (i.e. with xvp)
=====================================================

.. automodule:: engine.console
   :platform: Unix
   :synopsis: Wrapper around console proxies such as xvp to set up
              multitenant VM console access
.. moduleauthor:: Monsyne Dragon <mdragon@rackspace.com>
"""
from engine.console.api import API
