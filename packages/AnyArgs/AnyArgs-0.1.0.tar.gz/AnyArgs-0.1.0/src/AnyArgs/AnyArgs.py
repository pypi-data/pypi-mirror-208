from argparse import ArgumentParser
from configparser import ConfigParser
from dotenv import load_dotenv
from os import environ, getcwd
from os.path import exists, join
from glob import glob
from typing import Dict, List, Union
from pathlib import Path

from . import Group, conf_id_from_string, env_id_from_string


def _glob_from_cwd(glob_string: str):
    cwd = getcwd()
    return glob(join(cwd, glob_string))

class AnyArgs:
    """A class to allow args to be configured through .conf, .env, env variables OR """
    def __init__(self) -> None:
        self._argument_parser = ArgumentParser()
        self._config_parser = ConfigParser()
        self._env = environ

        self.groups: Dict[str, Group] = dict()


    def __str__(self) -> str:
        output_str = "Args:\n"
        for group_name in self.groups:
            output_str += str(self.groups[group_name])
        return output_str

    """GROUP & ARG DEFINITIONS"""
    def add_group(self, group_name):
        """"""
        group = Group(self._argument_parser, self._config_parser, group_name)
        self.groups[group_name] = group

        return group

    def add_argument(self, 
                     group_name:str, 
                     argument_name: str, 
                     typestring: str="", 
                     help: str="", 
                     cli_flags=[], 
                     default=None):
        return self.get_group(group_name).add_argument(
            name=argument_name, 
            typestring=typestring, 
            help=help, 
            cli_flags=cli_flags,
            default=default)
    
    def get_group(self, group_name) -> Union[Group, None]:
        return self.groups.get(group_name, None)

    def get_argument(self, group_name, argument_name):
        group = self.get_group(group_name)
        if group is not None:
            return group.get_argument(argument_name)
        else:
            return None
    

    """ARG LOADING"""
    def _load_conf_file(self, filepath):
        self._config_parser.read(filepath)
    
    def _load_env_file(self, filepath):
        load_dotenv(filepath)

    def _determine_args_type_and_load(self, filepath):
        filepath = Path(filepath)
        filename = filepath.name.lower()
        if filename.endswith("conf"):
            self._load_conf_file(filepath)
        elif filename.startswith(".env"):
            self._load_env_file(filepath)
            

    @property
    def _load_argument_parser(self):
        """Get argument_parser args"""
        return self.argument_parser.parse_args()
        

    def load_args(self, load_from_cwd = True, filepaths: Union[str, List[str]]= []):
        """Load data from passed file paths, if they exist"""
        self._argument_parser.parse_args()
        if isinstance(filepaths, str):
            filepaths = [filepaths]
        

        if load_from_cwd:
            filepaths += _glob_from_cwd("*.conf")
            filepaths += _glob_from_cwd(".env*")

        for filepath in filepaths:
            if exists(filepath):
                self._determine_args_type_and_load(filepath)
        

    """SAVING"""

    def save_to(self, conf_filepath=None, env_filepath=None, env_vars=False):
        save_to_conf = conf_filepath is not None
        save_to_env = env_filepath is not None
        if save_to_env:
            env_contents = ""

        for group_name in self.groups:
            group = self.groups[group_name]

            if save_to_env:
                env_contents += "# " + group_name + "\n"

            for arg_name in group.set_arg_names:
                arg_value = group.get_argument(arg_name)
                if save_to_conf:
                    key = conf_id_from_string(arg_name)
                    group._set_conf_value(key, arg_value)
                if save_to_env:
                    key = env_id_from_string(arg_name)
                    env_contents += f"{key}={arg_value}\n"
                if env_vars:
                    key = env_id_from_string(arg_name)
                    environ[key] = arg_value

                

        if save_to_conf:
            with open(conf_filepath, "w", encoding="UTF-8") as conf:
                    self._config_parser.write(conf)
        
        if save_to_env:
            with open(env_filepath, "w", encoding="UTF-8") as env:
                env.write(env_contents)


            
            
            

