"""rename CLI command implementation."""
# dem/cli/command/rename_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup
import dem.core.data_management as data_management
from dem.cli.console import stderr

def check_dev_env_name_exist(dev_env_local_setup: DevEnvLocalSetup, dev_env_name: str) -> (int | None):
    if dev_env_local_setup.get_dev_env_by_name(dev_env_name) is None:
        stderr.print("[red]Error: The input Development Environment does not exist.[/]")
        return -1

def rename_given_dev_env(derserialized_local_dev_nev: dict, dev_env_name: str, 
                         new_dev_end_name: str) -> (int | None):
    for devenv in derserialized_local_dev_nev["development_environments"]: 
        if devenv["name"] == dev_env_name:
            devenv["name"] = new_dev_end_name
            return
    
    stderr.print("[red]Error: Unable to rename the Development Environment.[/]")
    return -1

def execute(dev_env_name: str, new_dev_env_name: str) -> None:
    derserialized_local_dev_nev = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(derserialized_local_dev_nev)
    if check_dev_env_name_exist(dev_env_local_setup,dev_env_name) != -1:
        rename_given_dev_env(derserialized_local_dev_nev,dev_env_name,new_dev_env_name)

        data_management.write_deserialized_dev_env_json(derserialized_local_dev_nev)