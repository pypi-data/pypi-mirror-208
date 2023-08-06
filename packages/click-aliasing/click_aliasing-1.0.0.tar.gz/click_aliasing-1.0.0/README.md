# click-aliasing

Add (multiple) aliasing to a click_ group or command.

In your [click](http://click.pocoo.org/) app:

``` python
import click
from click_aliasing import ClickAliasedGroup


@click.group(cls=ClickAliasedGroup)
def cli():
    pass


@cli.command(aliases=["bar", "baz", "qux"])
def foo():
    """Run a command."""
    click.echo("foo")
```

Will result in:

``` bash
Usage: cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  foo (bar,baz,qux)  Run a command.
```

Command can also be called with a unique short match:

``` bash
cli f

>>foo
```
