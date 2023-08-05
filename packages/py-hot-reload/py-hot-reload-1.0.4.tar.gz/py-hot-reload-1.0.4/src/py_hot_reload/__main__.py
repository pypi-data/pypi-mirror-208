import os
import sys
import click
import subprocess


__author__ = "Heppa Soft"
__copyright__ = "Copyright (C) 2023 Heppa Soft"
__license__ = "MIT License"
__version__ = "1.0.4"


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version {}".format(__version__))
    ctx.exit()


def print_copyright(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__copyright__)
    ctx.exit()


def run_shell_command(args: list, verbose: bool = False):
    if verbose:
        print("")
        subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr).communicate()
    else:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        return p


@click.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True,"help_option_names":['-h', '--help']})
@click.argument("python_file")
@click.option("-V", "--version", is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show the version and exit.")
@click.option("-C", "--copyright", is_flag=True, callback=print_copyright,
              expose_value=False, is_eager=True, help="Show the copyright and exit.")
@click.option("-v", "--verbose", is_flag=True, type=click.BOOL, default=True, help="Verbose.")
@click.option("-ep", "--extra-patterns", type=click.STRING, help="Extra patterns")
@click.option("-ip", "--ignore-patterns", type=click.STRING, help="Ignore patterns")
@click.option("-i", "--interval", type=click.INT, default=1, help="Interval")
@click.option("--add-current-folder-to-patterns", is_flag=True, type=click.BOOL, default=True, help="Add current folder to patterns.")
@click.option("--ignore-venv-and-python-lib", is_flag=True, type=click.BOOL, default=True, help="Ignore venv and python lib.")
@click.pass_context
def hot_reload(ctx, python_file, verbose, extra_patterns, ignore_patterns, interval, add_current_folder_to_patterns, ignore_venv_and_python_lib):
    args = ctx.args
    if len(args) <= 0: args = None
    
    if ignore_patterns is not None:
        ignore_patterns = ignore_patterns.split(";")
    
    if extra_patterns is not None:
        extra_patterns = extra_patterns.split(";")
    
    venv = os.getenv("VIRTUAL_ENV")
    executable = "python"
    if venv != None:
        executable = f"{venv}/bin/python" if os.name == "posix" else f"{venv}/Scripts/python.exe"
    
    exit_code = subprocess.call([executable,"-c",f"import py_hot_reload;py_hot_reload.file_run_with_reloader('{python_file}', {args}, {extra_patterns}, {ignore_patterns}, {interval}, {verbose}, {add_current_folder_to_patterns}, {ignore_venv_and_python_lib})"], env=os.environ.copy(), close_fds=False)
    
    if exit_code != 3:
        return exit_code

def main():
    hot_reload()

if __name__ == "__main__":
    main()