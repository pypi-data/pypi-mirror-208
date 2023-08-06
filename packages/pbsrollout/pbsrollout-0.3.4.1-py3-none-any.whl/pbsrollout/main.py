import os
import sys
from subprocess import TimeoutExpired

from botocore.exceptions import ClientError
from kubernetes.client import ApiException
from rich.console import Console
from rich.markdown import Markdown
from simple_term_menu import TerminalMenu

from pbsrollout.internal.utils import notify, get_latest_version, is_dev

VERSION = ""
try:
    import importlib.metadata

    VERSION = importlib.metadata.version("pbsrollout")
except:
    pass


def print_help(console):
    mk = """
    Supported features:
    - Check that no other version are present
    - Launch pods + cutover
    - Check the service version + daemonset version
    - Clean pods

    Unsupported features (for now):
    - Rollback + remove old pods
    """

    md = Markdown(mk)
    console.print(md)


def check_latest_version(console: Console):
    if is_dev():
        return
    latest_version = get_latest_version()
    if latest_version != "":
        if latest_version != VERSION:
            terminal_menu = TerminalMenu(["[y] yes", "[n] It's okay I want to keep an outdated version"],
                                         title=f"You pbsrollout version is outdated!\n- Current version: {VERSION}\n- Latest version: {latest_version}\nDo you want to update?",
                                         raise_error_on_interrupt=True)
            menu_entry_index = terminal_menu.show()
            if menu_entry_index == 0:
                console.print(f"Please run: [grey66]python3 -m pip install --upgrade pbsrollout\n")
                exit(0)


def print_changelog(console: Console):
    txt = """[bold gold1]What's new?[/bold gold1]
[bold misty_rose1]Big features (v/0.3)[/bold misty_rose1]:
- Support for [italic]staging[/italic]! You can now release/sync/migrate staging envs!
- staging tags now include github PR description + author

[bold thistle1]Changelog (v[VERSION])[/bold thistle1]:
- fix: add staging 20 to the list of available stagings 
"""
    console.print(txt.replace("[VERSION]", VERSION))


def print_welcome(console: Console):
    """
    Print the welcome message.
    Message format:

                                          Better Rollout (vXXX)
    """
    if VERSION != "":
        console.print(
            f"\n[blink underline italic dark_orange3]Better[/blink underline italic dark_orange3] [bold medium_purple3]Rollout[/bold medium_purple3] (v{VERSION})\n",
            justify="center")
    else:
        console.print(
            "\n[blink underline italic dark_orange3]Better[/blink underline italic dark_orange3] [bold medium_purple3]Rollout[/bold medium_purple3]\n",
            justify="center")


def choose_action(console: Console):
    terminal_menu = TerminalMenu(["[p] release prebid", "[s] act on staging (release, sync db, ...)"],
                                 title="What do you want to do?",
                                 raise_error_on_interrupt=True)
    menu_entry_index = terminal_menu.show()

    # switch view depending on action
    if menu_entry_index == 0:
        # release_prebid
        from pbsrollout.pbs_release.main_view import entrypoint
        entrypoint(console)
    elif menu_entry_index == 1:
        from pbsrollout.stg_release.main_view import entrypoint
        entrypoint(console)


def main():
    """
    This main doesn't is not responsible for the main logic of the program.
    Instead, we:
    - parse cli flags
    - display welcome screen
    - check for updates
    - process and display any error from the "true" main func (`_main`)
    :return:
    """

    # First we are going to init the Console (responsible for the display of all text elements)
    # compared to a "print", this object allow us to style text output.
    # see: https://github.com/Textualize/rich to be amazed
    console = Console()

    # We display the welcome message
    print_welcome(console)
    print_changelog(console)

    # We parse some cli arguments.
    # The only one we accept for now is "help". Let's extend this in the future
    if 'help' in sys.argv:
        print_help(console)
    print("\n\n")

    # We finally call the main logic of the program
    try:
        check_latest_version(console)
        choose_action(console)

    # Here we process any possible exception. We use a different print depending on them.
    except Exception as e:
        notify("Error during script!", "PBS Rollout", sound=True)
        if (isinstance(e, ApiException) and e.reason == 'Unauthorized') or (
                isinstance(e, ClientError) and 'ExpiredTokenException' in str(e)):
            console.print("[bold red]\nerror: please run `zaws_ctv_engineer` to login")
            return 1
        elif isinstance(e, RuntimeError):
            console.print(f"[bold red]\nError: {e}")
        elif isinstance(e, TimeoutExpired):
            console.print(f"[bold red]\nerror: {e}")
        else:
            console.print_exception()
            console.print('[orange3]please send this to Dimitri Wyzlic on Slack!')
            return 1
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Interrupted by user (CTRL-C)")
    return 0


# entrypoint of the program. We just call the `main` func
if __name__ == '__main__':
    sys.exit(main())
