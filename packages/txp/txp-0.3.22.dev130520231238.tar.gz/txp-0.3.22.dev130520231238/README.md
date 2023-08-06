# TXP

## Development
The following tools are used for this project:

- [Poetry](https://python-poetry.org/) is used for dependency and package managment
- [Nox](https://nox.thea.codes/en/stable/) is used as automation tool, mainly for testing
- [Black](https://black.readthedocs.io/en/stable/) is the mandatory formatter tool
- [PyEnv](https://github.com/pyenv/pyenv) is recommended as a tool to handle multiple python versions in developers machines. 

### Setup the development environment

1. Install a supported Python version on your machine (compatible Python versions ^3.8). The recommended way is to use [PyEnv](https://github.com/pyenv/pyenv).

2. Install the global Python required dependencies: 

    ```
    pip install poetry nox
    ```

3. Clone this repository, and execute the following command in the repository root folder:

    ```
    poetry install
    ``` 
    This will install all the dependencies for `txp` in a virtual enviroment created by Poetry for your project. 
    All the required dependencies for development are installed in that virtual enviroment. 

4. Configure your IDE to work with the virtual enviroment or the command line if you use an editor. 

    To activate the virtual enviroment on your terminal (MacOS, Linux) you can execute:
    ```
    source /path/to/poetry/cache/virtualenvs/test-O3eWbxRl-py3.7/bin/activate
    ```

    The path to your virtual enviroment location can be found with `poetry env info` [command](https://python-poetry.org/docs/managing-environments#displaying-the-environment-information). 

### Testing
