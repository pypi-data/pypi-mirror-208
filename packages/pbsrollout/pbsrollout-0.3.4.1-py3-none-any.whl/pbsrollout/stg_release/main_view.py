import os
import subprocess
from copy import copy
from typing import Tuple, Callable, List, Any

from rich.console import Console
from shellpython.helpers import Dir
from simple_term_menu import TerminalMenu

from pbsrollout.internal.aws_utils import get_ecr_images
from pbsrollout.internal.utils import clean_stderr, print_error_body
from pbsrollout.internal.utils_gh import get_pr_titles_and_author_from_commit_hash, does_gh_cli_exist

NB_STAGINGS = 20

def get_and_enforce_go_path(console: Console) -> str:
    # Let's enforce having a gopath
    if 'GOPATH' not in os.environ or os.environ['GOPATH'] == '':
        console.print('GOPATH should be set in your environ! Contact a publica engineer for help')
        raise RuntimeError('GOPATH should be set in your environ! Contact a publica engineer for help')
    return os.environ['GOPATH']


def choose_staging_idx(console: Console) -> List[str]:
    idx = str(input('What is your staging idx? 1, 2, 18. Input "all" for all staging! '))
    possible_stagings = [str(i) for i in range(1, NB_STAGINGS + 1)]
    possible_stagings.append('all')
    if idx not in possible_stagings:
        console.print(f'[red]your choice must be in [/red]: {possible_stagings}')
        return choose_staging_idx(console)
    if idx == 'all':
        return [str(i).zfill(3) for i in range(1, NB_STAGINGS + 1)]
    return [idx.zfill(3)]


def launch_staging_pod(stg_idx: str, dir_path: str) -> bool:
    with Dir(dir_path):
        print(f'\tLaunching staging pods for stg: {stg_idx}')
        # run make clean deploy-new-pbs-prod
        cmd = f"direnv exec . make clean deploy-stg-idx-{stg_idx.lstrip('0')}"
        ret = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
        ret.stderr = clean_stderr(ret.stderr)
        if ret.returncode != 0 or ret.stderr != "":
            print_error_body(f"ERROR:\n\nstdout:\n{ret.stdout}\nstderr:\n{ret.stderr}")
            return False

    return True


def release_staging(console: Console, stg_idx: List[str], go_path: str):
    # step 1: choose and write tags for .tag files
    # load tags

    gh_cli_exist = does_gh_cli_exist()
    if not gh_cli_exist:
        console.print('[bold gold1]you should install the gh cli to add more informations about the tags!\n[italic]brew install gh[/italic][/bold gold1]')

    with console.status("[bold green]Fetching tags for 'pbs'...") as status:
        images = get_ecr_images('pbs')
        full_img = copy(images)
        images = [x[17:] for x in images]

        # enrich tags with github data

        # let's only display tags with open PR!
        github_infos = []
        if gh_cli_exist:
            status.update("[bold green]Fetching github description for those tags...")
            github_infos = get_pr_titles_and_author_from_commit_hash(images)
            biggest_name_len = 0
            for g in github_infos:
                biggest_name_len = max(biggest_name_len, len(g[0]))

            enriched_data = []
            for g in github_infos:
                for idx, tag in enumerate(images):
                    if g[2] == tag:
                        enriched_data.append(f'{tag}  {g[0].ljust(biggest_name_len + 4)} {g[1]}')
            if len(enriched_data) > 0:
                images = enriched_data

    # choose image
    images.append("manual input")
    terminal_menu = TerminalMenu(images, title="Select tag:",
                                 raise_error_on_interrupt=True)
    menu_entry_index = terminal_menu.show()
    tag = images[menu_entry_index]

    if tag == 'manual input':
        tag = str(input('enter your image tag: '))
    else:
        for f in full_img:
            if f.endswith(tag[:len('cd1ef6b73')]):
                tag = f
                break

    # put it in the file
    dir_path = go_path + '/src/github.com/publica-project/prebid-kube-manifests/namespace/stg/'
    for stg in stg_idx:
        console.print(f"Updating tag to [bold blue_violet]{tag}[/bold blue_violet] in file:")
        for pod in ['pbs', 'logger', 'console-api']:
            tag_file_path = dir_path + f"z{stg}-{pod}.tag"
            console.print(f"[bold light_steel_blue1]{tag_file_path}[/bold light_steel_blue1]")
            with open(tag_file_path, "w") as f:
                f.write(tag)

    # step 2: release pods
    for stg in stg_idx:
        launch_staging_pod(stg,
                           go_path + '/src/github.com/publica-project/prebid-kube-manifests/aws.us-east-1-eks-27-v3/')
        console.print('\t[bold green]success!')


def exit_fn(console: Console, stg_idx: List[str], go_path: str):
    return


def migrate_staging_db(console: Console, stg_idx: List[str], go_path: str):
    for stg in stg_idx:
        dir_path = go_path + '/src/github.com/publica-project/prebid-kube-manifests/aws.us-east-1-eks-27-v3/'
        with Dir(dir_path):
            print(f'\tMigrating staging db for stg: {stg}')
            # run make clean deploy-new-pbs-prod
            cmd = f"direnv exec . ../scripts/migrate-staging-db {stg.lstrip('0')}"
            ret = subprocess.run(cmd.split(" "), stderr=subprocess.PIPE, text=True, timeout=200)
            ret.stderr = clean_stderr(ret.stderr)
            if ret.returncode != 0 or ret.stderr != "":
                print_error_body(f"ERROR:\n\nstdout:\n{ret.stdout}\nstderr:\n{ret.stderr}")
                return False


def sync_staging_db(console: Console, stg_idx: List[str], go_path: str):
    for stg in stg_idx:
        dir_path = go_path + '/src/github.com/publica-project/prebid-kube-manifests/aws.us-east-1-eks-27-v3/'
        with Dir(dir_path):
            print(f'\tSyncing staging db for stg: {stg}')
            # run make clean deploy-new-pbs-prod
            cmd = f"direnv exec . ../scripts/sync-staging-db {stg.lstrip('0')}"
            ret = subprocess.run(cmd.split(" "), stderr=subprocess.PIPE, text=True, timeout=200)
            ret.stderr = clean_stderr(ret.stderr)
            if ret.returncode != 0 or ret.stderr != "":
                print_error_body(f"ERROR:\n\nstdout:\n{ret.stdout}\nstderr:\n{ret.stderr}")
                return False


def choose_another_staging_idx(console: Console, stg_idx: List[str], go_path: str) -> List[str]:
    stg_idx = choose_staging_idx(console)
    return stg_idx


actions = [
    ('release staging', release_staging),
    ('migrate staging db', migrate_staging_db),
    ('sync staging db with master', sync_staging_db),
    ('choose another staging idx', choose_another_staging_idx),
    ('exit', exit_fn),
]  # type: List[Tuple[str, Callable[[Console, List[str], str], Any]]]


def entrypoint(console: Console):
    go_path = get_and_enforce_go_path(console)
    stg_idx = choose_staging_idx(console)
    while True:
        terminal_menu = TerminalMenu([o[0] for o in actions],
                                     title=f"What do you want to do for staging: {' '.join(stg_idx)}?",
                                     raise_error_on_interrupt=True)
        menu_entry_index = terminal_menu.show()

        if actions[menu_entry_index][0] == 'exit':
            return

        ret = actions[menu_entry_index][1](console, stg_idx, go_path)
        if actions[menu_entry_index][0] == 'choose another staging idx':
            stg_idx = ret
