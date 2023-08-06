from unittest import TestCase


class Test(TestCase):
    def test_remove_old_pods(self):
        pass
        # path = os.environ['GOPATH'] + '/src/github.com/publica-project/prebid-kube-manifests/aws.us-east-1-eks-23-v3'
        # api_client = config.new_client_from_config(config_file=import_kube_config(path + '/.k8s-assets/kubeconfig'))
        #
        # remove_old_pods('tesk_k8s', path, api_client)
        # self.assertEqual('', err)
