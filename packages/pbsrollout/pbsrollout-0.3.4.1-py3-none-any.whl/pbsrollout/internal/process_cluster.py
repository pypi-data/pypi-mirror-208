import subprocess
from enum import Enum

from kubernetes.client import ApiClient
from rich.console import Console
from rich.padding import Padding
from rich.table import Table
from shellpython.helpers import Dir
from simple_term_menu import TerminalMenu

from pbsrollout.internal.k8s_utils import get_all_pbs_daemonset, get_all_pblog_daemonset, get_services, \
    get_all_prebid_daemonset_V2, delete_namespaced_daemonset
from pbsrollout.internal.utils import Error, print_error_body, clean_stderr


def launch_pods(name: str, path: str, api_client: ApiClient) -> bool:
    with Dir(path):
        print(f'\tLaunching new pods for cluster {name}')
        # run make clean deploy-new-pbs-prod
        cmd = "direnv exec . make clean deploy-new-pbs-prod"
        ret = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
        ret.stderr = clean_stderr(ret.stderr)
        if ret.returncode != 0 or ret.stderr != "":
            print_error_body(f"ERROR:\n\nstdout:\n{ret.stdout}\nstderr:\n{ret.stderr}")
            return False

    return True


def format_pods_status(desired: int, value: int) -> str:
    if desired != value:
        return f"[red bold] {value}"
    return f"[bold green] {value}"


def gen_row_daemonset(table, name, daemonset):
    desired = daemonset.status.desired_number_scheduled
    table.add_row(
        name,
        format_pods_status(desired, daemonset.status.desired_number_scheduled),  # Desired
        format_pods_status(desired, daemonset.status.current_number_scheduled),  # Current
        format_pods_status(desired, daemonset.status.updated_number_scheduled),  # Up-To_Date
        format_pods_status(desired, daemonset.status.number_ready),  # Ready
        format_pods_status(desired, daemonset.status.number_available),  # Available
    )


class Status(Enum):
    SUCCESS = 1
    WAIT = 2
    FAIL = 3


def display_daemonsets_informations(name: str, api_client: ApiClient) -> bool:
    console = Console()
    # 1. get all services
    # pbs
    pbs_daemonsets = get_all_pbs_daemonset(api_client)
    pbs_daemonsets_names = [d.metadata.name for d in pbs_daemonsets]
    if len(pbs_daemonsets_names) != 2:
        console.print(f"\t\t[bold red]error: should have 2 pbs daemonsets, got: {pbs_daemonsets_names}")
        return False

    pbs_daemonsets_names = [p.replace("pbs-prod-", "") for p in pbs_daemonsets_names]

    # pblog
    pblog_daemonsets = get_all_pblog_daemonset(api_client)
    pblog_daemonsets_names = [d.metadata.name for d in pblog_daemonsets]
    if len(pblog_daemonsets_names) != 2:
        console.print(f"\t\t[bold red]error: should have 2 pblog daemonsets, got: {pblog_daemonsets_names}")
        return False

    pblog_daemonsets_names = [p.replace("pblog-prod-", "") for p in pblog_daemonsets_names]

    # current service
    services = get_services(api_client, 'pbs-prod')
    services_names = [d.metadata.name for d in services]
    if services is None or len(services) != 1:
        console.print(f"\t\t[bold red]error: should have 1 service, got: {services_names}")
        return False

    # check that service is same as old pods and that next service will be same as new pods
    old_service_version = int(services[0].metadata.labels['version'])
    if old_service_version != int(pbs_daemonsets_names[0].replace("v", "")):
        console.print(f"\t\t[bold red]error: expected old pbs to have service version ({old_service_version}), got: {pbs_daemonsets_names[0]}")
        return False
    if old_service_version + 1 != int(pbs_daemonsets_names[1].replace("v", "")):
        console.print(f"\t\t[bold red]error: expected new pbs to have service version ({old_service_version + 1}), got: {pbs_daemonsets_names[1]}")
        return False

    console.print(f'\t\tswitching service {pbs_daemonsets_names[0]}->{pbs_daemonsets_names[1]}')
    console.print(f'\t\t[grey66]current service: {old_service_version}')

    # 2. Display pods infos for each daemonset
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Daemonset", style="bold", width=12)
    table.add_column("Desired", style="bold")
    table.add_column("Current")
    table.add_column("Up-To-Date")
    table.add_column("Ready")
    table.add_column("Available")

    # pbs
    gen_row_daemonset(table, f"[grey66]pbs-{pbs_daemonsets_names[0]}", pbs_daemonsets[0])
    gen_row_daemonset(table, f"pbs-{pbs_daemonsets_names[1]}", pbs_daemonsets[1])
    # pblog
    gen_row_daemonset(table, f"[grey66]pblog-{pblog_daemonsets_names[0]}", pblog_daemonsets[0])
    gen_row_daemonset(table, f"pblog-{pblog_daemonsets_names[1]}", pblog_daemonsets[1])

    padded_table = Padding(table, (0, 0, 0, 16))
    console.print(padded_table)

    return True


def cutover_service(name: str, path: str, api_client: ApiClient) -> Status:
    console = Console()
    console.print(f'\tCutting over {name} to new service')
    with Dir(path):
        ok = display_daemonsets_informations(name, api_client)
        if not ok:
            return Status.FAIL

        terminal_menu = TerminalMenu(["[y] yes", "[n] no, let's wait 30s"], title=f"Should we cutover?",
                                     raise_error_on_interrupt=True)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index == 1:
            return Status.WAIT

        # do the cutover
        # make next-pbs-prod-service
        cmd = "direnv exec . make deploy-new-pbs-prod-service"
        ret = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90, input='y')
        ret.stderr = clean_stderr(ret.stderr)
        if ret.returncode != 0 or ret.stderr != "":
            print_error_body(f"ERROR:\n\nstdout:\n{ret.stdout}\nstderr:\n{ret.stderr}")
            return Status.FAIL
    return Status.SUCCESS


# return error
def remove_old_pods(name: str, path: str, api_client: ApiClient) -> Error:
    console = Console()
    with Dir(path):
        console.print(f'\tremoving old pods/daemonset for cluster {name}')

        # 1. Get pbs service selected version
        services = get_services(api_client, 'pbs-prod')
        if services is None or len(services) != 1:
            return "should have 1 service, got: {services_names}"
        selected_version = int(services[0].metadata.labels["version"])
        console.print(f'\t\t[grey66]currently selected version: {selected_version}')

        # 2. Get all daemonsets
        pbs_daemonsets = get_all_prebid_daemonset_V2(api_client)
        pbs_daemonsets_names = [d.metadata.name for d in pbs_daemonsets]
        pbs_daemonsets_names_by_version = dict()
        for name in pbs_daemonsets_names:
            # name is like: 'pblog-prod-v1104'.
            version = name.split('-')[-1]
            if version not in pbs_daemonsets_names_by_version:
                pbs_daemonsets_names_by_version[version] = []
            pbs_daemonsets_names_by_version[version].append(name)

        console.print(f'\t\tdaemonsets found:\n' + '\n'.join(f'\t- {version}: {pbs_daemonsets_names_by_version[version]}' for version in pbs_daemonsets_names_by_version))
        if len(pbs_daemonsets_names_by_version) != 2:
            return f'2 pbs daemonset expected (old version/new version). found:\n' + '\n'.join(f'\t- {version}: {pbs_daemonsets_names_by_version[version]}' for version in pbs_daemonsets_names_by_version)

        all_versions = list(pbs_daemonsets_names_by_version.keys())
        version1 = int(all_versions[0].replace('v', ''))
        version2 = int(all_versions[1].replace('v', ''))

        # remove the oldest version THAT IS NOT SELECTED
        if version1 == selected_version and version2 > selected_version:
            return f'selected version {selected_version} should be greater than the other version: {version2}'
        if version2 == selected_version and version1 > selected_version:
            return f'selected version {selected_version} should be greater than the other version: {version1}'
        if selected_version != version1 and selected_version != version2:
            return f'selected version {selected_version} doesnt match the 2 existing versions: {[version1, version2]} from {pbs_daemonsets_names}'


        # remove the oldest version
        version_to_remove = version1 if selected_version == version2 else version2
        pbs_daemonsets_to_remove = pbs_daemonsets_names_by_version['v' + str(version_to_remove)]

        terminal_menu = TerminalMenu(["[y] yes", "[n] no"],
                                     title=f"Can we delete those this service {version_to_remove} containing those daemonset? {pbs_daemonsets_to_remove}",
                                     raise_error_on_interrupt=True)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index != 0:
            return f'User input: Cancelled removing service {version_to_remove} with daemonset: {pbs_daemonsets_to_remove}'

        console.print(f'\t\tremoving old version {version_to_remove}: {pbs_daemonsets_to_remove}')

        for daemonset in pbs_daemonsets_to_remove:
            delete_namespaced_daemonset(api_client, daemonset)

        return None
