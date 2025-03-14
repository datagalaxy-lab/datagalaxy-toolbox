# DataGalaxy Toolbox

[![Build status](../../workflows/CI/badge.svg)](../../actions?query=workflow%3ACI)

Welcome to the DataGalaxy Toolbox!

This is an opensource command-line tool that allows to perform admin operations on [DataGalaxy](https://www.datagalaxy.com). 

## Features
### Clientspace operations
- **Copy custom attributes** from a clientspace to another.
- **Delete custom attributes** on a clientspace.
- **Copy technologies** from a clientspace to another.

### Clientspace / workspace operations
- **Copy screens** from a clientspace (or workspace) to another clientspace (or workspace).

### Workspace operations
Note that the workspaces can be on different clientspaces.
- **Copy glossary** objects from a workspace to another.
- **Copy dictionary** objects from a workspace to another.
- **Copy dataprocessings** objects from a workspace to another.
- **Copy usages** objects from a workspace to another.
- **Copy links** from a workspace to another.
- **Delete glossary** objects of a workspace.
- **Delete dictionary** objects of a workspace.
- **Delete dataprocessings** objects of a workspace.
- **Delete usages** objects of a workspace.

#### General remarks
- As DataGalaxy do not support link creation when the objects do not already exist in the target workspace, we suggest that you run the copy commands in this order:
  1. `copy-glossary`, `copy-dictionary`, `copy-usages` (order doesn't matter)
  2. `copy-dataprocessings` (as they can have dataProcessingItems that connect dictionary elements, this command might fail if you run it before copying the dictionary)
  3. `copy-links` (this command will fail if you haven't copied all the objects before)
- All module copy commands will fail if the source objects have a custom technology value that do not exist in the target clientspace (there is no issue if you run the module copy in the same clientspace). As a consequence, we suggest that you run `copy-technologies` before copying modules. 
- All copy module commands will fail if the source objects have a custom tag value that do not exist in the target clientspace (there is no issue if you run the module copy in the same clientspace). As a consequence, we suggest that you run `copy-attributes` before copying modules. 
- If you have a versioned workspace (source or target), please enter the according option with `--version-target` and/or `--version-target`.

## Installation

An executable file `datagalaxy-toolbox.exe` is provided, which makes the DataGalaxy Toolbox usable only on Windows.
You can download it from the `Assets` section of the [Releases page](https://github.com/datagalaxy-lab/datagalaxy-toolbox/releases).

If you want to use the DataGalaxy Toolbox on MacOS or Unix, you need to build a binary file following the [development](#development) section.

## How to use

##### Parameters
- [optional arguments] `-h`, `--help`- show help message  
- `--url` - The API URL of your DataGalaxy environment
- `--token` - A DataGalaxy Token, either an Integration Token or a Personal Access Token
- `--url-source`- The API URL of the source environnement
- `--url-target` - The API URL of the target environnement 
- `--token-source` - A DataGalaxy Token from the source environnement
- `--token-target` - A DataGalaxy Token from the Token from target environnement
- `--workspace-source` - The name of the source workspace
- `--workspace-target` - The name of the target workspace
- `--version-source` - The name of the version of the source workspace
- `--version-target` - The name of the version of the target workspace
- `--tag-value` - Filter objects on a specific tag



### Clientspace operations

#### copy-attributes

```
datagalaxy-toolbox.exe copy-attributes [-h] --url-source URL_SOURCE --url-target URL_TARGET --token-source TOKEN_SOURCE --token-target TOKEN_TARGET
```

#### copy-technologies

```
datagalaxy-toolbox.exe copy-technologies [-h] --url-source URL_SOURCE --url-target URL_TARGET --token-source TOKEN_SOURCE --token-target TOKEN_TARGET
```

#### delete-attributes

```
datagalaxy-toolbox.exe delete-attributes [-h] --url URL --token TOKEN
```

### Clientspace / Workspace operations

#### copy-screens

```
datagalaxy-toolbox.exe copy-screens [-h] --url-source URL_SOURCE [--url-target URL_TARGET] --token-source TOKEN_SOURCE [--token-target TOKEN_TARGET] [--workspace-source WORKSPACE_SOURCE] [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] 
```
 `--url-target` and `--token-target` are optional if the copy is made on the same clientspace.

 `--workspace-source` is optional if the copy is made from a clientspace.

 `--workspace-target` is optional if the copy is made to a clientspace.

 `--version-source` and `--version-target` are only for versioned workspaces.
 
 4 scenarios are possible:
  - Copy screens from a clientspace to another clientspace (different clientspaces)
  - Copy screens from a workspace to a clientspace (can be on the same clientspace or not)
  - Copy screens from a clientspace to a workspace (can be on the same clientspace or not)
  - Copy screens from a workspace to another workspace (can be on the same clientspace or not)



### Workspace operations

#### copy-glossary

```
datagalaxy-toolbox.exe copy-glossary [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] [--tag-value TAG_NAME]
```
 `--url-target` and `--token-target` are optional if the copy is made on the same clientspace.

 `--version-source` and `--version-target` are only for versioned workspaces.


#### copy-dictionary

```
datagalaxy-toolbox.exe copy-dictionary [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] [--tag-value TAG_NAME]
```
 `--url-target` and `--token-target` are optional if the copy is made on the same clientspace.

 `--version-source` and `--version-target` are only for versioned workspaces.


#### copy-dataprocessings

```
datagalaxy-toolbox.exe copy-dataprocessings [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] [--tag-value TAG_NAME]
```
 `--url-target` and `--token-target` are optional if the copy is made on the same clientspace.

 `--version-source` and `--version-target` are only for versioned workspaces.


#### copy-usages

```
datagalaxy-toolbox.exe copy-usages [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] [--tag-value TAG_NAME]
```
 `--url-target` and `--token-target` are optional if the copy is made on the same clientspace.

 `--version-source` and `--version-target` are only for versioned workspaces.


#### copy-links

```
datagalaxy-toolbox.exe copy-links [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] 
```
 `--url-target` and `--token-target` are optional if the copy is made on the same clientspace.

 `--version-source` and `--version-target` are only for versioned workspaces.


#### delete-glossary

```
datagalaxy-toolbox.exe delete-glossary [-h] --url URL --token TOKEN --workspace WORKSPACE [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] 
```
 `--version-source` and `--version-target` are only for versioned workspaces.


#### delete-dictionary

```
datagalaxy-toolbox.exe delete-dictionary [-h] --url URL --token TOKEN --workspace WORKSPACE [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] 
```
 `--version-source` and `--version-target` are only for versioned workspaces.


#### delete-dataprocessings

```
datagalaxy-toolbox.exe delete-dataprocessings [-h] --url URL --token TOKEN --workspace WORKSPACE [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] 
```
 `--version-source` and `--version-target` are only for versioned workspaces.


#### delete-usages

```
datagalaxy-toolbox.exe delete-usages [-h] --url URL --token TOKEN --workspace WORKSPACE [--workspace-target WORKSPACE_TARGET] [--version-source VERSION_SOURCE] [--version-target VERSION_TARGET] 
```
 `--version-source` and `--version-target` are only for versioned workspaces.



## Development 

### Prerequisites

The DataGalaxy Toolbox requires:

- Python >= 3.9

### Steps

1. Clone the repository
2. Create a [virtual env](https://docs.python.org/3/tutorial/venv.html) in the `.venv` folder 
```
python -m venv .venv
```
3. activate the virtual env
```
source .venv/bin/activate
```
4. Install packages
````
pip install -r requirements.txt
````

### Build a binary file

run the command
```
pyinstaller -n datagalaxy-toolbox --onefile --console toolbox/__main__.py
```

This creates a **`dist`** folder with the binary file.

#### run the binary

````
./dist/datagalaxy-toolbox --help
````
### Testing

To run tests
```
python -m pytest
```

### Linter

[Flake8](https://pypi.org/project/flake8/) is used as a linter
```
python -m flake8 .
```

## Contributing

This project is not officially supported by DataGalaxy. We welcome contributions and suggestions.
Please have a look at our [Guidelines](CONTRIBUTING.md) for contributing.

## License

See the [LICENCE](LICENSE) file for details.