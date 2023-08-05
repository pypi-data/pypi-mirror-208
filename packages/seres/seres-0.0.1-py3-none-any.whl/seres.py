import click

@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-v', '--version', is_flag=True, help='Print version info and exit')
@click.option('--list', 'list_commands', is_flag=True, help='List installed commands')
@click.pass_context
def cli(ctx, version, list_commands):
    if ctx.invoked_subcommand is None:
        if version:
            click.echo('Version 1.0.0')
        elif list_commands:
            click.echo(cli.list_commands(ctx))
        else:
            click.echo(ctx.get_help())
@cli.command()
@click.option('-g', '--global', 'global_', is_flag=True, help='Use global package')
def install(global_):
    """Install a new binary"""
    if global_:
        click.echo('global test')
    else:
        click.echo('local test')

@cli.command()
def build():
    """Build a new package"""
    click.echo('Compiling the current package')

@cli.command()
@click.argument("package_name")
def new(package_name):
    """Create a new package"""
    click.echo(f"Creating package {package_name}...")

@cli.command()
def run():
    """Run a new package"""
    click.echo(f'Running of the local package')


# if __name__ == '__main__':
#     cli()

