import os
from unittest import TestCase

from kubernetes import config

from pbsrollout.internal.k8s_utils import import_kube_config, get_pods_for_daemonsets, get_all_pbs_daemonset, get_services


class Test(TestCase):
    def test_get_pods_for_daemonset(self):
        path = os.environ['GOPATH'] + '/src/github.com/publica-project/prebid-kube-manifests/aws.eu-west-1-eks-16-v3'
        api_client = config.new_client_from_config(config_file=import_kube_config(path + '/.k8s-assets/kubeconfig'))

        pods = get_pods_for_daemonsets(api_client, [802, 803])
        print(pods)

    def test_get_all_pbs_daemonset(self):
        path = os.environ['GOPATH'] + '/src/github.com/publica-project/prebid-kube-manifests/aws.eu-west-1-eks-16-v3'
        api_client = config.new_client_from_config(config_file=import_kube_config(path + '/.k8s-assets/kubeconfig'))

        get_all_pbs_daemonset(api_client)

    def test_get_services(self):
        path = os.environ['GOPATH'] + '/src/github.com/publica-project/prebid-kube-manifests/aws.eu-west-1-eks-16-v3'
        api_client = config.new_client_from_config(config_file=import_kube_config(path + '/.k8s-assets/kubeconfig'))

        get_services(api_client, 'pbs-prod')
