import subprocess

from kubernetes import client, config
from kubernetes.client import ApiClient
from rich.console import Console
from shellpython.helpers import Dir

from pbsrollout.internal.k8s_utils import import_kube_config
from pbsrollout.internal.utils import clean_stderr, Error, print_error_body


def check_cluster_ready(name: str, path: str, api_client: ApiClient) -> bool:
    console = Console()
    print(f'\tChecking cluster {name}')
    daemonset_check = dict()
    daemonset_check['pbs'] = check_only_one_daemonset(path, 'pbs-prod')
    daemonset_check['pbs_vmap'] = check_only_one_daemonset(path, 'pbs-vmap-prod')
    daemonset_check['pblog'] = check_only_one_daemonset(path, 'pblog-prod')
    daemonset_check['pblog_vmap'] = check_only_one_daemonset(path, 'pblog-vmap-prod')

    direnv_check_err = check_direnv_allowed(path)

    for check_name in daemonset_check:
        if daemonset_check[check_name]:
            console.print(f"\t\t[grey66]~{check_name}~ only one daemonset[/grey66]:................. [bold green]SUCCESS")
        else:
            console.print(f"\t\t[grey66]~{check_name}~ only one daemonset[/grey66]:................. [bold red]FAILED")
            return False

    if direnv_check_err is None:
        console.print("\t\t[grey66]direnv allowed[/grey66]:..................... [bold green]SUCCESS")
    else:
        console.print("\t\t[grey66]direnv allowed[/grey66]:..................... [bold red]FAILED")
        print_error_body(direnv_check_err)
        return False

    return True


def check_only_one_daemonset(path: str, prefix: str) -> bool:
    console = Console()

    config.load_kube_config(config_file=import_kube_config(path + '/.k8s-assets/kubeconfig'))

    v1 = client.AppsV1Api()
    daemonsets = v1.list_namespaced_daemon_set(namespace='api')
    if len(daemonsets.items) == 0:
        console.print('\t\t[bold red]error: no daemonset found')
        return False

    pbs_daemonsets = []
    for d in daemonsets.items:
        name = d.metadata.name
        if name.startswith(prefix):
            pbs_daemonsets.append(name)
    if len(pbs_daemonsets) == 0:
        return True
    if len(pbs_daemonsets) == 1:
        return True
    else:
        console.print(f'\t\t[bold red]error: more than 1 daemonset found:[/bold red] {pbs_daemonsets}')
        return False


def check_direnv_allowed(path: str) -> Error:
    with Dir(path):
        # force direnv allow
        ret = subprocess.run("direnv allow".split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             timeout=10)
        ret.stderr = clean_stderr(ret.stderr)
        if ret.returncode != 0:
            return f'returncode: {ret.returncode}\nstderr:{ret.stderr}'
        if ret.stderr != "":
            return f'stderr:{ret.stderr}'
        return None
