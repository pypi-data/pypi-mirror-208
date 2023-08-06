"""Mr. Chef's core functionality."""

import re
import warnings
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime
from logging import DEBUG, ERROR, captureWarnings, getLogger
from pathlib import Path
from shutil import rmtree
from textwrap import dedent
from typing import Optional

import coloredlogs
import requests
import tomlkit
from plumbum import local
from plumbum.commands.processes import ProcessExecutionError

CONFIG_FILE = "mrchef.toml"
FREEZER_FILE = ".mrchef.freezer.toml"

logger = getLogger("mrchef")
coloredlogs.install(logger=logger)

# Combine with warnings
warnings_logger = getLogger("py.warnings")
coloredlogs.install(logger=warnings_logger)
captureWarnings(True)


class MrChefError(Exception):
    """Core MrChef exception.

    It will be handled and pretty-printed when raised to CLI.
    """

    def __init__(self, msg: str, trace_level=DEBUG):
        """Initialize the exception.

        Args:
            msg: The message to present to the user.
            trace_level: Level used to log the exception traceback.
        """
        self.msg = msg
        self.trace_level = trace_level


@dataclass
class Meal:
    """Store warm and frozen configurations for meals (sub-repositories)."""

    # From a human
    path: Path
    url: str
    branch: str

    # From the freezer
    rev: Optional[str] = None
    spices: list[str] = field(default_factory=list)


class Worker:
    """Get meta-repo status and do stuff with it."""

    def __init__(self, starting_folder: Optional[Path] = None):
        """Load configuration from starting path upwards.

        Starts traversing directories upwards, looking for a `mrchef.toml` file,
        and loads it.
        """
        if starting_folder is None:
            starting_folder = Path()
        assert starting_folder.is_dir()
        current = starting_folder.absolute()
        top = Path(current.root)
        while current > top:
            current_file = current / CONFIG_FILE
            try:
                fd = current_file.open("r")
            except FileNotFoundError:
                current = current.parent
                continue
            self.path = current
            self.config_file = current_file
            self.config_user = tomlkit.load(fd)
            break
        else:
            raise MrChefError(f"No {CONFIG_FILE} file found here or in parent folders.")
        # Attempt to merge normal config with frozen one
        self.freezer_file = self.path / FREEZER_FILE
        try:
            with self.freezer_file.open("r") as fd:
                self.config_frozen = tomlkit.load(fd)
        except FileNotFoundError:
            warnings.warn("Freezer file not found.", stacklevel=2)
            self.config_frozen = {}
        # Setup self and do some checks
        assert self.config_user["version"] == 1
        self.kitchen = self.path / self.config_user["kitchen"]
        self.config_frozen.setdefault("meals", {})
        self.config_frozen.setdefault("patch2spice", {})
        self.config_frozen.setdefault("spices", {})
        self.config_frozen.setdefault("version", 1)

    def _cache_spices(self):
        """Make sure all spices cache is updated."""
        for meal_value in self.config_user.get("meals", {}).values():
            for spice_url in meal_value.get("spices", []):
                self._get_spice_content(spice_url)

    def _get_meal_key_by_path(self, meal_path: Path, meal_menu: dict[str, Meal]) -> str:
        """Find a meal in the menu that matches the given path."""
        meal_abs = meal_path.absolute()
        for key, meal in meal_menu.items():
            if meal.path.absolute() == meal_abs:
                return key
        raise MrChefError(f"Couldn't find meal {meal_path}")

    def _get_spice_content(self, spice_url: str, force_update=False) -> str:
        """Get spice content.

        Return the raw text of the patch.

        If the spice wasn't in the freezer, download it automatically and cache it.

        Args:
            meal_key: Key of the meal in the config file.
            spice_url: Patch URL.
            force_update: Ignore cached contents in the freezer.
        """
        if force_update:
            # Locate local patch
            local_patch = Path(spice_url)
            if not local_patch.is_absolute():
                local_patch = self.path / local_patch
            # Get content from local patch or from the Internet
            content = (
                local_patch.read_text()
                if local_patch.is_file()
                else requests.get(spice_url_autoconvert(spice_url)).text
            )
            self.config_frozen["spices"][spice_url] = content
            for patch_id in git_get_patch_ids_map(self.path, content):
                self.config_frozen["patch2spice"][patch_id] = spice_url
        try:
            # Get cached content
            return self.config_frozen["spices"][spice_url]
        except KeyError:
            # Cached content not found, get it from the Internet
            logger.info(f"Spice was not frozen, downloading: {spice_url}")
            return self._get_spice_content(spice_url, True)

    @classmethod
    def init(cls, where: Path):
        """Initialize a new kitchen."""
        where.joinpath(CONFIG_FILE).write_text(
            dedent(
                """\
                version = 1
                kitchen = "kitchen"

                # Add meals like this:
                # [meals.starter]
                # url = "https://gitlab.example.com/menu/starter.git"
                # branch = "delicacy"

                # You can add special spices to your version of this meal:
                # spices = [
                #     # Special shared spices for this metarepo
                #     "https://gitlab.example.com/menu/starter/-/merge_requests/1.patch",
                #     "https://gitlab.example.com/menu/starter/-/commit/14ebafa278a28a08b9660e6ccab33fc72bbccd17.patch",
                #     "https://github.com/menu/starter/pull/45.patch",
                #     "https://github.com/menu/starter/commit/430e53b9de9cf986d8236061eeb77ae35fd03f55",
                #     # This special spice is only for us
                #     "./local-extra-spicy.patch",
                # ]

                # Add more meals:
                # [meals.dessert]
                # url = "git@github.com/menu/dessert.git"
                # branch = "pudding"

                # After you're done adding meals, get them:
                # $ mrchef warmup

                # After you're done cooking, put them in the freezer, for reproducibility:
                # $ mrchef freeze
                """
            )
        )
        where.joinpath(FREEZER_FILE).touch()
        return cls(where)

    def cold_meals(self) -> dict[str, Meal]:
        """Get meals info from the freezer."""
        return {
            key: Meal(
                path=self.kitchen / key,
                url=value["url"],
                branch=value["branch"],
                rev=value.get(
                    "rev", self.config_frozen["meals"].get(key, {}).get("rev")
                ),
                spices=value.get("spices", []),
            )
            for key, value in self.config_user.get("meals", {}).items()
        }

    def hot_meals(self) -> dict[str, Meal]:
        """Get info from the hot meals found in the kitchen."""
        result = {}
        if not self.kitchen.is_dir():
            return result
        self._cache_spices()
        for meal_path in self.kitchen.glob("**/.git/.."):
            meal_path = meal_path.resolve()
            if not git_is_repo(meal_path):
                continue
            key = str(meal_path.relative_to(self.kitchen))
            branch = git_branch(meal_path)
            url = self.config_user.get(key, {}).get("url") or git_origin(meal_path)
            remote_head = git_remote_head(meal_path, url, branch)
            meal = Meal(
                path=meal_path,
                url=url,
                branch=branch,
                # Revision is not the current commit; it's the closest common
                # parent between local and remote commits
                rev=git_merge_base(meal_path, remote_head, "HEAD"),
            )
            # Build spices from local changes
            for hot_commit in git_commits_diff(meal_path, meal.rev, "HEAD"):
                hot_patch_id = git_commit_patch_id(meal_path, hot_commit)
                try:
                    # Get patch URL from freezer
                    hot_spice_url = self.config_frozen["patch2spice"][hot_patch_id]
                except KeyError:
                    # The patch is local; store it locally
                    local_path = self.kitchen / f"mrchef-{hot_patch_id}.patch"
                    local_contents = git_get_commit_patch(meal_path, hot_commit)
                    hot_spice_url = str(local_path.relative_to(self.path))
                    local_path.write_text(local_contents)
                    # Cache patch contents in the freezer
                    self.config_frozen["spices"][hot_spice_url] = local_contents
                    self.config_frozen["patch2spice"][hot_patch_id] = hot_spice_url
                    # Store patch in user configuration
                    self.config_user["meals"][key].setdefault("spices", [])
                    self.config_user["meals"][key]["spices"].append(hot_spice_url)
                # A spice can contain various commits, so it could exist already
                if hot_spice_url not in meal.spices:
                    meal.spices.append(hot_spice_url)
            result[key] = meal
        return result

    def all_meals(self) -> dict[str, dict[str, Optional[Meal]]]:
        """Obtain all meals, both warmed up and frozen.

        Useful to compare meals in both states.

        Returns:
            Dict with all meals and their states.

            The dict key will be the meal name (relative path to kitchen root).

            The dict value will be another dict with keys "hot" and "cold".
            Each of those keys will contain `None` if the meal is not found in
            that state, or a [Meal][] object if found.

            !!! example

                ```python
                {
                    "sashimi": {
                        "hot": None,
                        "cold": Meal(...),
                    },
                    "pizza/pepperoni": {
                        "hot": Meal(...),
                        "cold": Meal(...),
                    },
                }
                ```
        """
        cold, hot = self.cold_meals(), self.hot_meals()
        all_keys = sorted(set(cold) | set(hot))
        return {key: {"cold": cold.get(key), "hot": hot.get(key)} for key in all_keys}

    def update_user_config(self):
        """Update user config."""
        tomlkit.dump(self.config_user, self.config_file.open("w"))

    def check(self):
        """Check freezer and oven are in sync."""
        errors = []
        for key, value in self.all_meals().items():
            hot, cold = value["hot"], value["cold"]
            if cold is None:
                errors.append(f"Meal {key} is hot but not frozen")
                continue
            if hot is None:
                errors.append(f"Meal {key} is frozen but not hot")
                continue
            if hot.url != cold.url:
                errors.append(
                    f"Meal {key} is frozen with origin {cold.url}, but hot with origin {hot.url}"
                )
            if hot.rev != cold.rev:
                errors.append(
                    f"Meal {key} is frozen with rev {cold.rev}, but hot with rev {hot.rev}"
                )
            if hot.spices != cold.spices:
                errors.append(
                    f"Meal {key} spices are different. frozen={cold.spices} warm={hot.spices}"
                )
        try:
            if self.config_frozen != tomlkit.load(self.freezer_file.open()):
                errors.append("Freezer is outdated.")
        except FileNotFoundError:
            errors.append("Freezer not found.")
        if errors:
            raise MrChefError("🔪 Found errors:\n" + "\n".join(errors))
        logger.info("All frozen and hot meals are ready! 👨‍🍳")

    def warmup(self, *meal_paths: Path, force: bool = False):
        """Get meals out from freezer, warm them up in the kitchen.

        Args:
            *meal_paths: Meals to warm up. Skip to select all.
            force: Continue warming up meal if it is dirty.
        """
        cold_meals = self.cold_meals()
        meal_keys = {
            self._get_meal_key_by_path(meal_path, cold_meals)
            for meal_path in meal_paths
        }
        for key, value in self.all_meals().items():
            # Skip unselected meals
            if meal_paths and key not in meal_keys:
                continue
            hot, cold = value["hot"], value["cold"]
            # Nothing to do if something is not in the freezer
            if not cold:
                continue
            if hot == cold:
                logger.info("Matches frozen status, skipping meal: %s", key)
                continue
            # Clone if meal is not in the kitchen
            if not hot:
                logger.info("Cloning %s", key)
                local["git-autoshare-clone"](
                    "--recursive",
                    "--filter",
                    "blob:none",
                    "--branch",
                    cold.branch,
                    cold.url,
                    cold.path,
                )
            _git = git(cold.path)
            was_dirty = git_is_dirty(cold.path)
            if was_dirty:
                if not force:
                    raise MrChefError(f"Meal {key} is dirty.")
                logger.info("Stashing dirty changes at %s")
                _git(
                    "stash",
                    "push",
                    "--all",
                    "--message",
                    f"MrChef dirty meal - {hot.branch} - {datetime.now()}",
                )
            logger.info(
                "Updating %s: remote=%s branch=%s rev=%s",
                key,
                cold.url,
                cold.branch,
                cold.rev,
            )
            remote_head = git_remote_head(cold.path, cold.url, cold.rev or cold.branch)
            _git("switch", "--force-create", cold.branch, cold.rev or remote_head)
            for spice in cold.spices:
                logger.info("Applying spice to %s: %s", key, spice)
                content = self._get_spice_content(spice)
                self.spice_apply(cold.path, content)

    def freeze(self):
        """Get meals from the kitchen and put them in the freezer."""
        new_freezer = {"version": 1, "meals": {}, "spices": {}, "patch2spice": {}}
        for name, meal in sorted(self.hot_meals().items()):
            assert meal.rev
            new_freezer["meals"][name] = {
                "rev": meal.rev,
            }
            for spice_url in meal.spices:
                spice_content = self._get_spice_content(spice_url)
                new_freezer["spices"][spice_url] = spice_content
                for patch_id in git_get_patch_ids_map(meal.path, spice_content):
                    new_freezer["patch2spice"][patch_id] = spice_url
        with self.freezer_file.open("w") as fd:
            fd.write("# MrChef's freezer. MANUAL CHANGES WILL BE OVERRIDDEN.\n")
            tomlkit.dump(new_freezer, fd)
        # Because maybe we detected hot patches in the mean time
        self.update_user_config()

    def meal_add(
        self, meal_path: Path, url: str, branch: str, rev: Optional[str] = None
    ):
        """Add a new meal to the kitchen and the freezer."""
        meal_path = meal_path.absolute()
        kitchen = self.kitchen.absolute()
        if not meal_path.is_relative_to(kitchen):
            raise MrChefError(
                f"The meal path must be inside the configured kitchen {kitchen}"
            )
        key = str(meal_path.relative_to(kitchen))
        self.config_user.setdefault("meals", {})
        logger.info(
            "Adding meal %s: remote=%s branch=%s rev=%s",
            key,
            url,
            branch,
            rev,
        )
        self.config_user["meals"][key] = {"url": url, "branch": branch}
        if rev:
            self.config_user["meals"][key]["rev"] = rev
        self.update_user_config()
        self.warmup(meal_path)
        self.freeze()

    def meal_rm(self, meal_path: Path):
        """Remove a meal from the kitchen."""
        meals = self.cold_meals()
        key = self._get_meal_key_by_path(meal_path, meals)
        del self.config_user["meals"][key]
        logger.info("Removing meal %s", key)
        with suppress(FileNotFoundError):
            rmtree(meals[key].path)
        self.update_user_config()
        self.freeze()

    def spice_add(self, meal_path: Path, url: str, freeze: bool = True):
        """Download a patch and spice up meal with it."""
        if git_is_dirty(meal_path):
            raise MrChefError("Cannot add spice to dirty meal {meal_path}")
        menu = self.hot_meals()
        key = self._get_meal_key_by_path(meal_path, menu)
        meal = menu[key]
        content = self._get_spice_content(url, True)
        if self.spice_is_applied(meal, content):
            raise MrChefError(f"Spice already exists: {url}")
        self.spice_apply(meal_path, content)
        self.config_user["meals"][key].setdefault("spices", [])
        self.config_user["meals"][key]["spices"].append(url)
        self.update_user_config()
        self.freeze()

    def spice_rm(self, meal_path: Path, url: str):
        """Remove a patch from a meal.

        After successfully removing it, the meal will be re-warmed up and the
        config and freezer files will be updated.

        Args:
            meal_path: Where to find the meal.
            url: Spice URL to remove.
        """
        if git_is_dirty(meal_path):
            raise MrChefError("Cannot remove spice from dirty meal {meal_path}")
        menu = self.hot_meals()
        key = self._get_meal_key_by_path(meal_path, menu)
        logger.info("Removing spice from %s: %s", key, url)
        try:
            self.config_user["meals"][key]["spices"].remove(url)
        except ValueError as error:
            raise MrChefError(
                f"Cannot remove spice, not found in meal {key}: {url}"
            ) from error
        self.warmup(meal_path)
        self.update_user_config()
        self.freeze()

    def spice_export(self, url: str) -> str:
        """Export spice contents from the freezer.

        Args:
            url: The url that was frozen.
        """
        return self.config_frozen["spices"][url]

    def spice_is_applied(self, meal: Meal, spice_content: str) -> bool:
        """Check if a spice is already appled."""
        # See https://stackoverflow.com/a/66755317/1468388
        check = git(meal.path)["apply", "--reverse", "--check"] << spice_content
        try:
            check()
        except ProcessExecutionError:
            # Patch cannot be reversed, so it was never applied
            return False
        return True

    def spice_apply(self, meal_path: Path, spice_content: str):
        """Spice up a meal."""
        _git = git(meal_path)
        apply = _git["am", "--keep-non-patch", "--3way"] << spice_content
        try:
            apply()
        except ProcessExecutionError as error:
            _git("am", "--abort")
            raise MrChefError("Failed to apply spice.", ERROR) from error

    def update(self, *meal_paths: Path, force: bool = False):
        """Update hot meals, store changes in the freezer.

        Args:
            *meal_paths: Meals to update. Skip to select all.
            force: Continue warming up meal if it is dirty.
        """
        hot_meals = self.hot_meals()
        meal_keys = {
            self._get_meal_key_by_path(meal_path, hot_meals) for meal_path in meal_paths
        }
        for key in hot_meals:
            # Skip unselected meals
            if meal_paths and key not in meal_keys:
                continue
            # Clear meal cache
            with suppress(KeyError):
                del self.config_frozen["meals"][key]
            for spice in self.config_user["meals"].get(key, {}).get("spices", []):
                with suppress(KeyError):
                    del self.config_frozen["spices"][spice]
        # Warm up again without cache
        self.warmup(*meal_paths, force=force)
        # Write changes to freezer
        self.freeze()


def spice_url_autoconvert(spice_url: str) -> str:
    """Autoconvert common spice URLs.

    Supports these:

    - Gitlab merge request, like https://gitlab.com/moduon/mrchef/-/merge_requests/1
    - Gitlab commit, like https://gitlab.com/moduon/mrchef/-/commit/4699372d84f7f67b52fc7548f606e9a42559b5c2
    - Github pull request, like https://github.com/octocat/Hello-World/pull/1
    - Github commit, like https://github.com/octocat/Hello-World/commit/7fd1a60b01f91b314f59955a4e4d4e80d8edf11d
    """
    if spice_url.endswith(".patch"):
        return spice_url
    result = spice_url.rstrip("/")
    if spice_url.startswith("https://github.com/") or re.match(
        r"https://[^/]*gitlab[^/]*/", spice_url
    ):
        result = f"{result}.patch"
    if result != spice_url:
        logger.debug("Transformed spice URL: %s ➡️ %s", spice_url, result)
    return result


def git(folder: Optional[Path] = None) -> str:
    """Get a git executable ready to operate in `folder`."""
    _git = local["git"]
    if folder:
        _git = _git["-C", folder]
    return _git


def git_branch(folder: Path) -> str:
    """Get current branch name in that git folder."""
    return git(folder)("rev-parse", "--abbrev-ref", "HEAD").strip()


def git_commit_patch_id(folder: Path, commit_id: str) -> str:
    """Get the patch ID from a commit ID.

    And what is a patch ID? See https://git-scm.com/docs/git-patch-id
    """
    commit_patch = git_get_commit_patch(folder, commit_id)
    patch_id_map = git_get_patch_ids_map(folder, commit_patch)
    assert len(patch_id_map) == 1
    return list(patch_id_map)[0]


def git_commits_diff(folder: Path, rev1: str, rev2: str) -> list[str]:
    """Get differential commits between rev1 and rev2."""
    return git(folder)(
        "log", "--topo-order", "--reverse", "--format=%H", f"{rev1}...{rev2}"
    ).splitlines()


def git_get_commit_patch(folder: Path, commit: str) -> str:
    """Get patch text contents from a git commit."""
    return git(folder)("format-patch", "-1", "--stdout", "--binary", commit)


def git_get_patch_ids_map(folder: Path, patch_text: str) -> dict:
    """Get patch ids from patch text."""
    patch_id_map = git(folder)["patch-id", "--stable"] << patch_text
    return {
        patch_id: commit_id
        for patch_id, commit_id in (
            line.split() for line in patch_id_map().splitlines()
        )
    }


def git_is_repo(folder: Path) -> bool:
    """Know if the folder is a git repository."""
    try:
        git(folder)("status", "--porcelain")
        return True
    except ProcessExecutionError:
        return False


def git_is_dirty(folder: Path) -> bool:
    """Know if the folder is a dirty git repository."""
    return bool(git(folder)("status", "--porcelain"))


def git_origin(folder: Path) -> str:
    """Know the git origin URL for Mr. Chef's default origin."""
    _git = git(folder)
    # See https://stackoverflow.com/a/60297250/1468388
    status = _git("status", "--branch", "--porcelain=v2")
    origin = re.search(r"^# branch.upstream (.*)/.*$", status, re.MULTILINE)[1]
    return _git("remote", "get-url", origin).strip()


def git_merge_base(folder: Path, rev1: str, rev2: str) -> str:
    """Know the closest common ancestor commit of 2 git revisions.

    Args:
        folder: Path to git repo.
        rev1: First commit to compare.
        rev2: Second commit to compare.
    """
    return git(folder)("merge-base", rev1, rev2).strip()


def git_remote_head(folder: Path, remote_url: str, remote_ref: str) -> str:
    """Get latest commit sha from remote url and ref combination.

    Args:
        folder: Path to git repo.
        remote_url: Absolute URL to remote.
        remote_ref: Branch or revision to fetch from remote.
    """
    _git = git(folder)
    try:
        _git("remote", "add", "_mrchef", remote_url)
        _git("fetch", "--write-fetch-head", "_mrchef", remote_ref)
        result = _git("rev-parse", "FETCH_HEAD").strip()
    finally:
        _git("remote", "rm", "_mrchef")
    return result


def git_rev(folder: Path) -> str:
    """Know the commit where a git repository is currently checked out."""
    return git(folder)("rev-parse", "--verify", "HEAD").strip()


def git_root(folder: Path) -> Path:
    """Know the root of the git repository that owns a folder."""
    return Path(git(folder)("rev-parse", "--show-toplevel").strip())
