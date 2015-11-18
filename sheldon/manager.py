# -*- coding: utf-8 -*-

"""
Manager for plugins: importing and loading

@author: Seva Zhidkov
@contact: zhidkovseva@gmail.com
@license: The MIT license

Copyright (C) 2015
"""

import importlib

from sheldon.utils import logger
from sheldon.hooks import find_hooks
from sheldon.config import parse_config


class PluginsManager:
    def __init__(self, config):
        """
        Create plugins manager

        :param config: Config object with bot information
        :return:
        """
        self.config = config
        self.plugins = []

    def load_plugins(self):
        """
        Load plugins from 'installed_plugins.txt' file

        :return: list of Plugin objects
        """
        plugin_names = self.config.installed_plugins
        for plugin_name in plugin_names:
            self.load_plugin(plugin_name)

    def reload_plugins(self):
        """
        Reload all imported and loaded plugins

        :return:
        """
        for plugin in self.plugins:
            plugin.reload_plugin()

    def load_plugin(self, plugin_name):
        """
        Parse config, find hooks and create new Plugin object.

        :param plugin_name: name for plugin import
        :return:
        """
        plugin_module = import_plugin(plugin_name)
        if not plugin_module:
            logger.error_message("'{}' plugin didn't load".format(
                plugin_name
            ))
            return
        plugin_config = parse_config(plugin_module)
        hooks = find_hooks(plugin_module)

        plugin = Plugin(plugin_name, plugin_module, plugin_config, hooks)
        self.plugins.append(plugin)


class Plugin:
    def __init__(self, name, module, config, hooks):
        """
        Create new plugin

        :param name: string, module name
        :param module: module, imported plugin module
        :param config: ModuleConfig object, parsed plugin config
        :param hooks: list of Hook objects
        :return:
        """
        self.name = name
        self.module = module
        self.config = config
        self.hooks = hooks

    def reload_plugin(self):
        """
        Reload plugin (import it and find hooks again)

        :return:
        """
        self.module = importlib.reload(self.module)
        self.config = parse_config(self.module)
        self.hooks = find_hooks(self.module)


def import_plugin(plugin_name):
    """
    Import plugin using importlib

    :param plugin_name: full name of plugin, ex. 'plugins.console'
    :return: module object or None if plugin not found
    """
    try:
        return importlib.import_module(plugin_name)
    except ImportError as error:
        logger.error_message('Error with loading {}: \n {}'.format(
            plugin_name, str(error)
        ))
        return None
