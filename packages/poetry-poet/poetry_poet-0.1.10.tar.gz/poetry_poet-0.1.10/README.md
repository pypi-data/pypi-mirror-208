# Poet: Poetic Poetry Tools

Poetry alias and plugin example.
- Further development TBD.

## Usage

```shell
poetry add poetry-poet
```

The `poet` command is an alias for `poetry`.
- Subject to change: `poetry run` or something else.

```shell
poet run ...
```

## Features

Currently, there are two placeholder Poetry
plugins:
- A generic plugin that handles all commands.
- An application plugin that provides the
  `poetry poet` command (as an example).

Use `poetry self add poetry-poet` to add
these plugins to your Poetry installation.

Adding only to `self` does not provide
the global `poet` command.
