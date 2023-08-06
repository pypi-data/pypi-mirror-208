
import os
import subprocess
from contextlib import contextmanager
from typing import Generator
from dwh_oppfolging.apis.secrets_api_v1 import get_dbt_oracle_secrets_for


@contextmanager
def create_dbt_oracle_context(username: str) -> Generator[None, None, None]:
    """
    use in with statement
    yields nothing
    but sets and unsets environment variables referenced by dbt profile
    """
    config = get_dbt_oracle_secrets_for(username)
    config |= {"ORA_PYTHON_DRIVER_TYPE": "thin"}
    os.environ.update(config)
    yield
    for k in config:
        os.environ.pop(k)
#    #secrets = get_dbt_oracle_secrets_for(username)
#    try:
#        file = open(file="profiles.yml", mode="wt", encoding="utf-8")
#        ... write to file
#        file.close()
#        yield
#    finally:
#        os.remove("profiles.yml")


def run_dbt(profiles_dir: str, project_dir: str) -> None:
    """
    executes dbt test and run as subprocess
    assuming profiles yaml file is located
    this should be done inside a dbt_oracle context
    """
    try:
        subprocess.run(
            ["dbt", "test", "--profiles-dir", profiles_dir, "--project-dir", project_dir],
            check=True, capture_output=True, encoding="utf-8"
        )
        subprocess.run(
            ["dbt", "run", "--profiles-dir", profiles_dir, "--project-dir", project_dir],
            check=True, capture_output=True, encoding="utf-8"
        )
    except subprocess.CalledProcessError as exc:
        errtext = exc.stdout + "\n" + exc.stderr
        raise Exception(errtext) from exc
