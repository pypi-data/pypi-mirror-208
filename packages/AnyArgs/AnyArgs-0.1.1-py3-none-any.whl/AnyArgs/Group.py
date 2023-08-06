from argparse import ArgumentParser
from configparser import ConfigParser
from typing import Dict, List
from os import environ
from re import findall, sub

from . import ARGTYPE_BOOLEAN, ARGTYPE_STRING, ARGTYPE_LIST

def conf_id_from_string(string: str):
    """Transform provided string into the conf-standard PascalCase"""
    id = ""
    for word in findall(r"[a-zA-Z0-9]+", string):
        id += word.capitalize()
    return id

def env_id_from_string(string: str):
    """Convert a string to a FULL UPPERCASE environment key ID, based on examples provided at https://www.dotenv.org/docs/security/env.html"""
    return "_".join(findall(r"[a-zA-Z0-9]+", string)).upper()


class Group:
    """The Group class, which groups arguments together for the AnyArgs class"""
    def __init__(self, argument_parser: ArgumentParser, config_parser: ConfigParser, group_name: str) -> None:
        self.group_name = group_name
        self.argument_parser = argument_parser
        self.arg_group = self.argument_parser.add_argument_group(self.group_name)
        
        self.config_parser = config_parser
        self.conf_group = self.group_name
        self.config_parser.add_section(self.conf_group)

        self.cli_flags = ["-h", "--help"]  # By default, argparse sets -h and --help, so exclude those from usage
        self.set_arg_names = []
        
        self.defaults = dict()

    @property
    def argparse_args(self):
        """Load & return argument_parser args"""
        return self.argument_parser.parse_args()
        

    def add_argument(self, 
                     name: str, 
                     typestring: str=ARGTYPE_STRING, 
                     help: str="", 
                     cli_flags: List = [], 
                     default: any = None):
        """
        Add/define a new argument in this group

        - name: human readable argument name
        - typestring: (optional, default:ARGTYPE_STRING). Defines what sort of argument is being stored. Expects literals from argtypes.py
        - help: (optional, default:"") Help text when calling the script CLI with -h or --help
        - cli_flags: (optional, default:see README.md) Which flags can be used in the CLI to set the arg
        - default: (optional, default:None) Default value for the arg  

        
        """
        self.set_arg_names.append(name)
        # simply using cli_flags or flags = cli_flags breaks it idk who cares
        flags = [flag for flag in cli_flags]
        if typestring == ARGTYPE_BOOLEAN:
            action = "store_true"
            if default is None:
                default = False
        elif typestring == ARGTYPE_LIST:
            action = "append"
        else:
            # Argtype string and default
            action = "store"
        
        
        # If no CLI flags are defined, auto generate
        if len(flags) < 1:
            # e.g. -
            first_letters_dasherised = "".join(findall(r"^[a-z]|(?<=[^a-z])[a-z]", name.lower()))
            only_letters = "".join(findall(r"[a-z ]", name.lower()))
            
            short_flag = "-" + first_letters_dasherised
            long_flag = "--" + only_letters.replace(" ", "-")

            if long_flag not in self.cli_flags:
                flags.append(long_flag)
            
            if short_flag not in self.cli_flags:
                flags.append(short_flag)

        try:
            arg = self.arg_group.add_argument(*flags,
                                        dest=name,
                                        action=action,
                                        help=help,
                                        default=None)  # Set Default none, as defaults are handled by AnyArgs
            if typestring == ARGTYPE_LIST:
                arg.nargs = "*"

            self.cli_flags += flags
        except ValueError as e:
            print("[ERR] ValueError raised when adding argument. Double check that you're not adding duplicate cli_flags")
            raise e
        
        # If a default is defined, save it
        if default is not None:
            self.defaults[name.lower()] = default

        return self



    def _get_conf_value(self, argument_name: str):
        """Get arg value by name from config_parser"""
        argument_name = conf_id_from_string(argument_name)
        return self.config_parser[self.conf_group][argument_name] if argument_name in self.config_parser[self.conf_group] else None

    def _set_conf_value(self, argument_name: str, value: any):
        """Set arg value by name in config_parser"""
        argument_name = conf_id_from_string(argument_name)
        value = str(value)
        self.config_parser.set(self.conf_group, argument_name, value)

    def _get_argparse_value(self, argument_name: str):
        """Get arg value by name from the argparse_args/CLI"""
        args = self.argparse_args
        return getattr(args, argument_name) if hasattr(args, argument_name) else None

    def _get_env_value(self, argument_name: str):
        """Get arg value by name from environment variables. First try with env_id_from_string, otherwise with straight argument name"""        
        id = env_id_from_string(argument_name)
        value = environ.get(id, None)
        
        if value is None:
            value = environ.get(argument_name, None)

        return value

    def _set_env_value(self, argument_name: str, value:any):
        """Set arg value by name into environment variables"""
        argument_name = env_id_from_string(argument_name)
        value = str(value)
        environ.update(argument_name, value)


    def get_argument(self, human_readable_name: str):
        """
        Load the argument value, no matter where it comes from

        Priority:
        - Highest: CLI arg
        - Middle: env variable/.env
        - Lower: conf file
        - Fallback: internal default dict
        """

        # CLI arg
        value = self._get_argparse_value(human_readable_name)
        # env variable/.env
        if value is None:
            value = self._get_env_value(human_readable_name)
        # conf file
        if value is None:
            value = self._get_conf_value(human_readable_name)
        # default
        if value is None:
            value = self.defaults.get(human_readable_name.lower(), None)
            
        return value
    
    def __str__(self) -> str:
        output_str = self.group_name + "\n"
        
        for arg_name in self.set_arg_names:
            output_str += f"\t- {arg_name}: {self.get_argument(arg_name)}\n"
        return output_str
    
