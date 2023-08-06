# AnyArgs

Get script arguments from the CLI, .conf files, environment variables and/or .env files, with only one syntax!


| CLI  | .conf | .env | env vars | Functionality | 
| ---- | ----- | ---- | -------- | ------------- |
|  ✅  |  ✅   |  ✅  |    ✅    | Add groups & arguments everywhere at once        |
|  ✅  |  ✅   |  ✅  |    ✅    | Load arguments, no matter where they're set      |
|  ❌  |  ✅   |  ✅  |    ✅    | Save/export args                                 |
|  ❔  |  ❔   |  ❔  |    ❔    | Set list type/duplicate args                     |


✅: Implemented
❕: Implemented in a quirky little way
❔: Planned
❌: Not implemented

## How-To
### (Project) Install from pip
```bash
python3 -m pip install AnyArgs 
```

### (Code) Basic usage 
In just a few lines of code, you can allow your users to set args in whatever way they prefer
```python
# index.py
args = AnyArgs()
args.add_group("Config").add_argument("Username", help="Username for logging in")
args.load_args()
print("Provided username: " + args.get_argument("Username"))
```
<details>
<summary>That's it! With just these lines of code, you've allowed the following</summary>

- A help interface through `python3 index.py -h` or `python3 index.py --help`
- A CLI interface through `python3 index.py --username Denperidge` and `python3 index.py -u Denperidge`
- Allow configuring through a .env in the current working directory with `USERNAME=Denperidge`
- Allow configuring through environment variables with `export USERNAME=Denperidge`
- Allow configuring through a *.conf in the current working directory with 
    ```conf
    [Config]
    Username=Denperidge
    ```


</details>

### (Code) Booleans
```python
# index.py
args = AnyArgs()
args.add_group("Config").add_argument("Load on launch", typestring=ARGTYPE_BOOLEAN, help="Whether to load files on launch", default=False)
args.load_args()
```
And now, a simple `python3 index.py --load-on-launch` is enough to enable load-on-launch!

### (Code) Explicitly defining flags
While AnyArgs will auto-generate some flags, you can always define your own instead to override this behaviour!
```python
# index.py
args = AnyArgs()
args.add_group("Config").add_argument("Username", cli_flags=["--username", "--login", "--email"])
args.load_args()
```

### (Project) Clone & run tests
```bash
git clone https://github.com/Denperidge-Redpencil/AnyArgs.git
cd AnyArgs
python3 -m pip install -r requirements.txt
python3 -m src.tests
```

### (Project) Clone & run scripts locally
```bash
git clone https://github.com/Denperidge-Redpencil/AnyArgs.git
cd AnyArgs
python3 -m pip install -r requirements.txt
python3 src.AnyArgs
```

### (Project) Clone, build & install package locally
```bash
git clone https://github.com/Denperidge-Redpencil/AnyArgs.git
cd AnyArgs
python3 -m pip install --upgrade build setuptools
python3 -m build && python3 -m pip install --force-reinstall ./dist/*.whl
```
