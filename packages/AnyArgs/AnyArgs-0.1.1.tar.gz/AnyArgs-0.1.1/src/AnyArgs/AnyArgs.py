# Built-in importd
from os import environ, getcwd
from os.path import exists, join
from glob import glob
from pathlib import Path
from typing import Dict, List, Union
from argparse import ArgumentParser
from configparser import ConfigParser

# Package imports
from dotenv import load_dotenv

# Local imports
from . import Group, conf_id_from_string, env_id_from_string


def _glob_from_cwd(glob_string: str):
    """Runs the provided glob_string joined with the current working directory"""
    cwd = getcwd()
    return glob(join(cwd, glob_string))

class AnyArgs:
    """The AnyArgs main class, to allow args to be added & loaded through CLI .conf, .env, env variables and/or CLI"""
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

    """GROUP & ARG ADDING/DEFINITIONS"""
    def add_group(self, group_name):
        """Creates a new Group with the provided group_name and adds it to the AnyArgs object"""
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
        "Add new argument. Wrapper for AnyArgs.get_group and Group.add_argument. See the latter for more information"
        return self.get_group(group_name).add_argument(
            name=argument_name, 
            typestring=typestring, 
            help=help, 
            cli_flags=cli_flags,
            default=default)
    
    def get_group(self, group_name) -> Union[Group, None]:
        """Get a group from the AnyArgs object"""
        return self.groups.get(group_name, None)

    def get_argument(self, group_name, argument_name):
        """
        Get the value of provided argument_name under the group of the provided group_name.
        
        Wraps AnyArgs.get_group and Group.get_argument
        """
        group = self.get_group(group_name)
        if group is not None:
            return group.get_argument(argument_name)
        else:
            return None
    

    """ARG LOADING"""
    def _load_conf_file(self, filepath):
        """Load args from provided conf filepath into the AnyArgs configparser"""
        self._config_parser.read(filepath)
    
    def _load_env_file(self, filepath):
        """Load args from provided .env filepath into the process Environ. Wraps dotenv.load_dotenv"""
        load_dotenv(filepath)

    def _determine_args_type_and_load(self, filepath):
        """Determines what type of file a provided filepath is, and subsequently loads it using the correct function"""
        filepath = Path(filepath)
        filename = filepath.name.lower()
        if filename.endswith("conf"):
            self._load_conf_file(filepath)
        elif filename.startswith(".env"):
            self._load_env_file(filepath)
            

    @property
    def _load_argument_parser(self):
        """Load & return argument_parser values"""
        return self.argument_parser.parse_args()
        

    def load_args(self, load_from_cwd = True, filepaths: Union[str, List[str]]= []):
        """
        Load arg data into the AnyArgs object. Call after adding/defining the args that have to be loaded

        - load_from_cwd: (default:True)             whether to look for files in the current working directory
        - filepaths:     (optional, default:empty)  one or multiple strings that point to .env/.conf files that are to be loaded
        """
        self._argument_parser.parse_args()
        if isinstance(filepaths, str):
            filepaths = [filepaths]
        

        if load_from_cwd:
            filepaths += _glob_from_cwd("*.conf")
            filepaths += _glob_from_cwd(".env*")

        for filepath in filepaths:
            if exists(filepath):
                self._determine_args_type_and_load(filepath)
        

    """SAVING/EXPORTING"""
    def save_to(self, conf_filepath=None, env_filepath=None, env_vars=False):
        """
        Save passed args to a .conf, .env and/or environment variables

        - conf_filepath: if defined, location where .conf file will be saved
        - env_filepath: if defined, location where .env file will be saved
        - env_vars: (default:False) if True, export to environment variables using os.environ
        """
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


            
            
            

