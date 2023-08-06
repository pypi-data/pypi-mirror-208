import tempfile
from typing import List

from kubernetes import client
from kubernetes.client import ApiClient, V1DaemonSet, V1Service

data_to_append = """      env:
        - name: AWS_PROFILE
          value: "ctv_engineer"
"""


# Add aws env vars to the kubeconfig file. save it in a temp place and return the new path
def import_kube_config(path: str) -> str:
    """
    Before importing kube config file, we need to modify it
    We need to add the AWS_PROFILE value to it. (see `data_to_append`)
    In order to do that, let's copy the file to a temp location, modify it and return this temp file path
    :param path:
    :return:
    """
    with open(path) as fp:
        lines = fp.readlines()[:-1]
        for d in data_to_append.split('\n'):
            lines.append(d + '\n')
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            tmp.writelines(lines)
            tmp.close()
            return tmp.name


# return ordered list of daemonset
def get_all_daemonset_filtered_by_name(api: ApiClient, startwith: str):
    v1 = client.AppsV1Api(api_client=api)

    daemonsets = v1.list_namespaced_daemon_set(namespace='api')
    if len(daemonsets.items) == 0:
        return []

    pbs_daemonsets = []
    for d in daemonsets.items:
        name = d.metadata.name
        if name.startswith(startwith):
            pbs_daemonsets.append(d)
    return sorted(pbs_daemonsets, key=lambda x: x.metadata.name)


def get_all_daemonset_filtered_by_label(api: ApiClient, label_selector: str):
    v1 = client.AppsV1Api(api_client=api)

    daemonsets = v1.list_namespaced_daemon_set(namespace='api', label_selector=label_selector)
    if len(daemonsets.items) == 0:
        return []

    return sorted(daemonsets.items, key=lambda x: x.metadata.name)


def get_all_pbs_daemonset(api: ApiClient) -> List[V1DaemonSet]:
    return get_all_daemonset_filtered_by_name(api, 'pbs-prod')


# filter by selector (app in (pbs, pblog))
# return -> pbs, vmp-pbs, pblog, vmap-pblog
def get_all_prebid_daemonset_V2(api: ApiClient) -> List[V1DaemonSet]:
    return get_all_daemonset_filtered_by_label(api, 'app in (pbs,pblog),env=prod')


def get_all_pblog_daemonset(api: ApiClient) -> List[V1DaemonSet]:
    return get_all_daemonset_filtered_by_name(api, 'pblog-prod')


def delete_pbs_daemonset(api: ApiClient, version: int):  # DEPRECATED
    v1 = client.AppsV1Api(api_client=api)
    # delete pbs daemonset
    v1.delete_namespaced_daemon_set(namespace='api', name=f'pbs-prod-v{version}')
    # delete pblog daemonset
    v1.delete_namespaced_daemon_set(namespace='api', name=f'pblog-prod-v{version}')


def delete_namespaced_daemonset(api: ApiClient, name: str):
    v1 = client.AppsV1Api(api_client=api)
    v1.delete_namespaced_daemon_set(namespace='api', name=name)


def get_pods_for_daemonsets(api: ApiClient, daemonset_versions: List[int]):
    core = client.CoreV1Api(api_client=api)
    pods = core.list_namespaced_pod(namespace='api')
    output = {}
    for d in daemonset_versions:
        output[d] = []
    wanted = [f'pbs-prod-v{v}' for v in daemonset_versions]
    for p in pods.items:
        name = p.metadata.name
        for i, w in enumerate(wanted):
            if name.startswith(w):
                output[daemonset_versions[i]].append(p)
                break
    return output


def get_services(api: ApiClient, startwith: str) -> List[V1Service]:
    core = client.CoreV1Api(api_client=api)
    services = core.list_namespaced_service(namespace='api')
    if startwith == "":
        return services
    output = []
    for s in services.items:
        if s.metadata.name.startswith(startwith):
            output.append(s)
    return sorted(output, key=lambda x: x.metadata.name)
