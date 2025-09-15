# Install

- Get Conda. I suggest using Miniforge by downloading the relevant
  installer from https://github.com/conda-forge/miniforge/releases, and executing
  it with the default parameters. Once installed, your shell will be prepped
  (close the terminal, open a new one). In Windows, you need to jump some hoops
  to get it in PowerShell and not just in the Command window (follow
  [this](https://github.com/conda-forge/miniforge/issues/516#issuecomment-1843709465)
  recommendation).

- Create the conda environment, and activate it. Do not forget to activate
  the environment in each window that you are using.

  ```bash
  conda env create -f environment.yml
  conda activate wscat
  ```

- Profit, you should have all binaries and libraries available in such a
  window. Ensure that VSCode knows about this --- for me the easiest way is to
  quit all VSCode windows, and from a terminal with Conda activated, start VSCode
  using

  ```
  code .
  ```

# Usage

* Run the server:

  ```bash
  doit run_server
  ```

* Run the clients:

  ```bash
  uv run wscat-add
  uv run wscat-game
  ```


# Key elements of the environment

* `environment.yml`: Config file for Conda.

  The channel specification (`conda-forge`) is critically important.
  `conda-forge` is a "community channel". Importantly, it's by far the most
  complete.

* [uv](https://docs.astral.sh/uv/): An extremely fast Python package and project
  manager, written in Rust.

  A single tool to replace pip, pip-tools, pipx, poetry, pyenv, twine,
  virtualenv, and more. The main offering: blazing fast creation of temporary
  environments, making it easy to create reproducible scripts.

  Our key interaction with it: `uv run <script name>`, see the
  `[project.scripts]` section in `pyproject.toml`.

  When one does not need complex dependencies, it is typical to forego using
  Conda at all, and only use `uv`. In that case, one needs to use `uv` a bit
  more intensively as we do, to install the dependencies, manage virtual
  environments, etc.

* `pyproject.toml`: New style config file for the whole Python ecosystem.

  Some of the `[foobar]` sections are standard, not tool specific, like
  `[project]` or `[project.scripts]`. Some are tool specific, like
  `[tool.hatch.build.targets.wheel]`. The idea is that ecosystem tools find
  the config all in one place.

  The `[project.scripts]` section contains the binaries, which the built
  package exposes for the user as commands in the standard binary path.
  During development, we use `uv run <script name>` to run them.

  Note: The dependencies in `pyproject.toml` are the runtime dependencies. `uv
  run` may create a completely new venv for each execution, or may reuse some,
  or may detect that Conda already has all dependencies --- I could not yet
  figure out the exact details.

  As a rule of thumb: I add all dependencies to the Conda config
  `environment.yml`, which exist in `conda-forge`. I also add all of the
  *runtime dependencies* to `pyproject.toml`. There may be situations when some
  of the runtime dependencies do not exist in Conda, in case adding them to
  `pyproject.toml` is enough, `uv` can take care of those via `uv pip install`.

* `dodo.py` and `doit`: A `Makefile` and `make` replacement.

* `hatchling`: A modern Python package build system.

  `hatchling` replaces the older `setuptools`. We are using it for its hook
  mechanism, that we configure in `tools/build_protos.py` to build the protos
  before building the distributable package. We do not really need it for
  development, during development we are using `doit build_protos` to build the
  protos, of which the logic is defined in `dodo.py`.


# Bootstrap

I have bootstrapped this project using the following commands:

```bash
conda env create -f environment.yml
conda activate wscat
uv init --name wscat --app
rm main.py
mkdir -p src/wscat/server
touch src/wscat/server/__init__.py
mv main.py src/wscat/server
```

...then added the rest. :)

Note: of course I didn't know in advance every single dependency that I'll have
in `environment.yml`. I bootstrapped it with some reasonable default content,
and then whenever I needed another one, I didn't start all over. For example,
when I needed to add `websockets`, I did `conda install websockets`, and I added
`websockets` to `environment.yml` to keep it in sync.
