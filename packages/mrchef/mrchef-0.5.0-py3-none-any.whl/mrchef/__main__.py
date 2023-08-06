"""Module to handle CLI module usage (`python -m mrchef ...`)."""
from .cli import MrChef

# HACK https://github.com/nix-community/poetry2nix/issues/504
run = MrChef.run

run()
