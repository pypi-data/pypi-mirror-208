# Mr. Chef

👨‍🍳 Meta-Repo Chef. Culinary git helper to work with code buffets.

## Why

It has features that no other meta-repo manager has:

-   Code is 100% reproducible.
-   Full freeze-warmup-freeze coding cycle.
-   Upstream patching supported.
-   Downstream patching supported.
-   Mixed and multi-patching repo supported.
-   Automated updates.
-   Automatic disk space economization with [git-autoshare][].
-   Food! 🥘

Let's dive in. Imagine you need to create an app that requires many unrelated modules to
be properly glued together. How would you organize your source code?

There are multiple answers to that question:

-   Use separate repos and glue them together through packaging. But what if some code
    you need isn't properly packaged? What if some dependencies need more than 1 patch
    to work?
-   Use [a monorepo](https://en.wikipedia.org/wiki/Monorepo). However, what happens if
    some parts are open source and you need to upstream or review changes?
-   Use [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules). However,
    that requires that every time you do a `git checkout`... or almost any git
    command..., you need to use some `--recurse-submodules` flag. Also it gives _a lot_
    of headaches when you move files around and perform basically any operation. And
    what if you need to merge 2 upstream patches?
-   Use [git subtrees](https://www.atlassian.com/git/tutorials/git-subtree). But then,
    you need even more deep knowledge than with submodules to be able to review or
    publish patches. And again, how to merge more than one patch?
-   Use [Pijul](https://pijul.org/posts/2022-01-07-monorepos/). But the world isn't
    ready for it yet. Still we need Git.

The solution is to [use a meta-repo](https://notes.burke.libbey.me/metarepo/). There are
many meta-repo managers out there, but none of them has all the features that I already
told you about Mr. Chef.

## Glossary

Mr. Chef introduces a new code management concept based on the metaphor of a buffet. Use
this glossary to understand the rest of the recipe... readme! Sorry...

-   _Buffet_ is the main git repository that contains all the instructions to build it.
-   The _config file_ is a file named `mrchef.toml` that stands in the root of your
    _buffet_ and configures what Mr. Chef should do.
-   The _kitchen_ is the root folder, inside the _buffet_, where you can find the
    _meals_. It's configured inside the _config file_.
-   A _meal_ is like a git submodule: another git repo inside your _kitchen_.
-   A _spice_ is a patch that is added to a _meal_.
-   The _freezer_ is where we store the gory details needed to make the kitchen 100%
    reproducible. Mr. Chef saves it in a file called `.mrchef.freezer.toml`.
-   _Warming up_ means getting meals outside of the _freezer_ and putting them in the
    _kitchen_, ready to cook!
-   _Freezing_ means writing a new _freezer_ that can reproduce what's currently _warmed
    up_ in the _kitchen_.

## How

### Using CLI

Install it:

```sh
pipx install mrchef
```

Usually you start by creating a new configuration file:

```sh
mrchef init
```

It will create a new `mrchef.toml` file with some comments about how to use it. You can
delete them once you know how to do it.

Now, you will need to add a meal:

```sh
mrchef meal-add kitchen/hello https://github.com/octocat/Hello-World master
```

💡 Mr. Chef uses [git-autoshare][] automatically. It will help you if you need to clone
huge repos! But you have to configure it before adding the meals.

You can add more meals just like that.

Maybe you need to apply a couple of spices to the meal? OK:

```sh
mrchef spice-add kitchen/hello https://github.com/octocat/Hello-World/pull/2256
mrchef spice-add kitchen/hello https://github.com/octocat/Hello-World/pull/34
```

Did `master` get new commits? Or did those PRs get updated? Update everything:

```sh
mrchef update
```

Cool, huh? 😏 Mr. Chef can do more things! To see all commands and what they do:

```sh
mrchef --help-all
```

### Using Python

Install it:

```sh
pip install mrchef
```

Use it:

```python
import mrchef
```

### Using Nix

Install it:

```sh
nix profile install gitlab:moduon/mrchef
```

Did I say buffets are 100% reproducible? Nothing better than [Nix](https://nixos.org/)
for that job.

Go read [the flake](./flake.nix). You'll find helpers ready to convert a buffet into
aggregated source code. Read [the minimal test](./tests/nix/testMinimal.nix) to
understand how to use them. Ready to replace git submodules?

Keep in mind this if using nix:

-   You should enable flakes. At least, until https://github.com/NixOS/nix/issues/5541
    or https://github.com/NixOS/nix/issues/5119 are fixed.

## Who

Created and maintained by [Moduon Team](https://www.moduon.team/).

Original idea by [Jairo Llopis](https://www.recallstack.icu/).

## Where

Anywhere you want! 🎁 It's [GPL 3.0+](./LICENSE).

[git-autoshare]: https://github.com/acsone/git-autoshare
