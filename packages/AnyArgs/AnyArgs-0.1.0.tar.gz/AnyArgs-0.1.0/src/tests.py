from .AnyArgs import AnyArgs
from unittest import TestCase, main

from os import system, getcwd, remove, environ, path
from os import environ

def test_load_from_file(test_class, file_path, file_content=None):
    """Tests if Argument == Set after reading. If file_content is passed, write that to the provided file"""
    if "/" not in file_path:
        file_path = getcwd() + "/" + file_path

    args = setup_test(add_default_arg=True)
    
    test_class.assertIsNone(args.get_argument("Arguments", "Argument"))
    if file_content is not None:
        with open(file_path, "w", encoding="UTF-8") as file:
            file.write(file_content)
    
    args.load_args()
    test_class.assertEqual(args.get_argument("Arguments", "Argument"), "Set")

    cleanup_test()


def test_save_to(test_class, conf=False, env_file=False):
    args = setup_test(add_default_arg=True)

    args.load_args()
    # By default, None
    test_class.assertIsNone(args.get_argument("Arguments", "Argument"))

    # Now hypothetically what if it was set
    args.get_group("Arguments")._set_conf_value("Argument", "Set")

    # Save that Set to ...
    if conf:
        args.save_to(conf_filepath="args.conf")
    if env_file:
        args.save_to(env_filepath=".env")

    # Reset AnyArgs
    args = setup_test(add_default_arg=True)
    # By default, None
    test_class.assertIsNone(args.get_argument("Arguments", "Argument"))
    args.load_args()
    test_class.assertEqual(args.get_argument("Arguments", "Argument"), "Set")

    cleanup_test()

def setup_test(add_default_arg = True) -> AnyArgs:
    args = AnyArgs()
    if add_default_arg:
        args.add_group("Arguments").add_argument("Argument")
    return args

def cleanup_test():
    if path.exists("args.conf"):
        remove("args.conf")
    if path.exists(".env"):
        remove(".env")
    if "Argument" in environ.keys():
        environ.pop("Argument")

class Tests(TestCase):
    def test_group_adding(self):
        args = setup_test(add_default_arg=False)
        self.assertIsNone(args.groups.get("Group That doesn't exist"))

        args.add_group("Group that does exist")
        self.assertIsNotNone(args.groups.get("Group that does exist"))

        cleanup_test()
        
    def test_arg_adding(self):
        assert_text = "You should be able to add & access arguments set in {0} from {1}"

        args = setup_test(add_default_arg=False)
        group = args.add_group("Group")

        args.add_argument(
            group_name="Group",
            argument_name="Arg from AnyArgs",  
            cli_flags=["--Arg"],
            default=False)

        group.add_argument( 
            name="Arg from Group",
            cli_flags=["--ArgTwo"],
            default=False
            )

        self.assertIsNotNone(args.groups["Group"].get_argument("Arg from group"),  
                      assert_text.format("Group", "AnyArgs"))
        
        self.assertIsNotNone(group.get_argument("Arg from AnyArgs"),
                      assert_text.format("AnyArgs", "Group"))

        cleanup_test()



    def test_load_arg_from_file_conf(self):
        test_load_from_file(self, "args.conf", "[Arguments]\nArgument = Set")
    
    def test_load_arg_from_file_env(self):
        test_load_from_file(self, ".env", "Argument=Set")
    
    def test_load_arg_from_env_vars(self):
        args = setup_test(add_default_arg=True)

        args.load_args()
        
        self.assertIsNone(args.get_argument("Arguments", "Argument"))

        environ["Argument"] = "Set"

        args.load_args()
        self.assertEqual(args.get_argument("Arguments", "Argument"), "Set")

        cleanup_test()
    

    def test_save_to_conf(self):
        test_save_to(self, conf=True)
        
    def test_save_to_env_file(self):
        test_save_to(self, env_file=True)
    
    def test_save_to_env_vars(self):
        args = setup_test(add_default_arg=True)
        args.get_group("Arguments")._set_conf_value("Argument", "Set")

        self.assertIsNone(environ.get("Argument", None))
        args.get_group("Arguments")._set_conf_value("Argument", "Set")
        self.assertIsNone(environ.get("Argument", None))
        
        args.save_to(env_vars=True)
        self.assertEqual(environ.get("Argument", None), "Set")

        cleanup_test()
        



if __name__ == "__main__":
    main()