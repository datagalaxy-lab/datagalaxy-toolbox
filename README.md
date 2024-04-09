# Toolbox

[![Build status](../../workflows/CI/badge.svg)](../../actions?query=workflow%3ACI)

Toolbox allows you to perform admin operations on [DataGalaxy](https://www.datagalaxy.com). 

## Features
- **Copy attributes** from a source client space to a target client space.
- **Delete attributes** on client space.
- **Copy technologies** from a source client space to a target client space.
- **Copy screens** from a source client space or workspace to a target client space or workspace.
- **Copy glossary** properties from a workspace to another.
- **Copy dictionary** objects from a workspace to another.
- **Copy dataprocessings** from a workspace to another.
- **Copy usages** from a workspace to another.
- **Copy links** from a workspace to another.

## Installation

For now we provide an executable file `datagalaxy-toolbox.exe` which makes Toolbox usable only on Windows.
You can download it from the `Assets` section of the [Releases page](https://github.com/datagalaxy-lab/datagalaxy-toolbox/releases).
If you want to use Toolbox on Mac or Linux you need to build a binary file following the [development](#development) section.

## Usage

### CLI

##### Flags
- [optional arguments] `-h`, `--help`- show help message  
- `--url` - URL 
- `--token` - Integration token 
- `--url-source`- URL source environnement
- `--url-target` - URL target environnement 
- `--token-source` - Integration token from source environnement
- `--token-target` - Integration token from target environnement
- `--workspace-source` - Workspace source name
- `--workspace-target` - Workspace target name





#### delete-attributes

Toolbox checks that there is no identical attribute on the target client space before running the copy from the source. It raises an exception and stops the program if it finds duplicate attributes.
To delete attributes from the target client space to allow copying run: 
```
datagalaxy-toolbox.exe delete-attributes [-h] --url URL --token TOKEN
```

#### copy-attributes

```
datagalaxy-toolbox.exe copy-attributes [-h] --url-source URL_SOURCE --url-target URL_TARGET --token-source TOKEN_SOURCE --token-target TOKEN_TARGET
```

#### copy-technologies

```
datagalaxy-toolbox.exe copy-technologies [-h] --url-source URL_SOURCE --url-target URL_TARGET --token-source TOKEN_SOURCE --token-target TOKEN_TARGET
```

#### copy-screens

```
datagalaxy-toolbox.exe copy-screens [-h] --url-source URL_SOURCE [--url-target URL_TARGET] --token-source TOKEN_SOURCE [--token-target TOKEN_TARGET] [--workspace-source WORKSPACE_SOURCE] [--workspace-target WORKSPACE_TARGET]
```
 `--url-target` and `--token-target` are optional if the copy is made on the same client space.

 `--workspace-source` is optional if the copy is made from a client space.

 `--workspace-target` is optional if the copy is made to a client space.
 
 4 scenarios are possible:
  - Copy screens from a client space to another client space (different client spaces)
  - Copy screens from a workspace to a client space (can be on the same client space or not)
  - Copy screens from a client space to a workspace (can be on the same client space or not)
  - Copy screens from a workspace to another workspace (can be on the same client space or not)

#### copy-glossary

```
datagalaxy-toolbox.exe copy-glossary [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET
```
 `--url-target` and `--token-target` are optional if the copy is made on the same client space.

#### copy-dictionary

```
datagalaxy-toolbox.exe copy-dictionary [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET
```
 `--url-target` and `--token-target` are optional if the copy is made on the same client space.

#### copy-dataprocessings

```
datagalaxy-toolbox.exe copy-dataprocessings [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET
```
 `--url-target` and `--token-target` are optional if the copy is made on the same client space.

#### copy-usages

```
datagalaxy-toolbox.exe copy-usages [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET
```
 `--url-target` and `--token-target` are optional if the copy is made on the same client space.

#### copy-links

```
datagalaxy-toolbox.exe copy-links [-h] --url-source URL_SOURCE --token-source TOKEN_SOURCE [--url-target URL_TARGET] [--token-target TOKEN_TARGET] --workspace-source WORKSPACE_SOURCE --workspace-target WORKSPACE_TARGET
```
 `--url-target` and `--token-target` are optional if the copy is made on the same client space.


## Development 

### Prerequisites

Toolbox requires:

- Python >= 3.9

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

### Testing

To run tests
```
python -m pytest
```

### Linter

We use [Flake8](https://pypi.org/project/flake8/) as a linter
```
python -m flake8 .
```
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

## Contributing

This project welcomes contributions and suggestions.
Please have a look at our [Guidelines](CONTRIBUTING.md) for contributing.

## License

See the [LICENCE](LICENSE) file for details.