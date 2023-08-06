#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path

scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

from Shared.certoraUtils import find_jar


def gambit_entry_point(mutation_conf: str) -> None:
    mutation_test_jar = find_jar("MutationTest.jar")
    if not mutation_test_jar.exists():
        sys.exit("MutationTest.jar does not exist. Try to reinstall certora-cli.")
    try:
        exitcode = subprocess.run(["java", "-jar", str(mutation_test_jar), mutation_conf]).returncode
        if exitcode:
            raise Exception("MutationTest.jar execution failed, exitcode: ", exitcode)
    except Exception:
        print("Something went wrong when running mutation testing. Make sure you have the jar."
              " If not, reinstall certora-cli.")
    else:
        print("Successfully ran mutation testing.")


def ext_gambit_entry_point() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: certoraMutate CONFIG.conf. Missing conf file.")
    elif len(sys.argv) > 2:
        sys.exit("Usage: certoraMutate CONFIG.conf. Provided unrecognized arguments.")
    elif not Path(sys.argv[1]).exists():
        sys.exit(f"Conf file {sys.argv[1]} does not exist.")
    elif Path(sys.argv[1]).suffix != ".conf":
        sys.exit("Conf file must end with .conf extension.")
    gambit_entry_point(sys.argv[1])


if __name__ == '__main__':
    ext_gambit_entry_point()
