from .AnyArgs.AnyArgs import AnyArgs
from .AnyArgs.argtypes import ARGTYPE_BOOLEAN, ARGTYPE_STRING

args = AnyArgs()
args.add_group("Login").add_argument("Username", typestring=ARGTYPE_STRING).add_argument("Handle")
save_conf = args.add_group("Save Configuration")
save_conf.add_argument("To .env", typestring=ARGTYPE_BOOLEAN)
save_conf.add_argument("To .conf", typestring=ARGTYPE_BOOLEAN)


print(args)
args.load_args()

print(args)
print(args.get_argument("Save Configuration", "To conf"))

if args.get_argument("Save Configuration", "To .conf"):
    args.save_to(conf_filepath="conf.conf")

if args.get_argument("Save Configuration", "To .env"):
    args.save_to(env_filepath=".env")
