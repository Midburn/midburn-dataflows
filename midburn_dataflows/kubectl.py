import subprocess
import json
import yaml


def kubectl(action='get', obj_type='all', kubectl_args=None):
    if not kubectl_args or len(kubectl_args) == 0:
        kubectl_args = ('--all-namespaces',)
    extra_args = ' '.join(kubectl_args)
    cmd = f'kubectl {action} {obj_type} -o json {extra_args}'
    print(f'Executing shell script: "{cmd}"')
    res = subprocess.check_output(f'kubectl {action} {obj_type} -o json {extra_args}', shell=True)
    res = json.loads(res)
    assert res['kind'] == 'List', 'invalid object kind: {}'.format(res['kind'])
    for row in res['items']:
        metadata = row.pop('metadata')
        spec = row.pop('spec')
        row.update(metadata)
        row.update(spec)
        yield row


def get(what, namespace, required=True):
    try:
        return yaml.load(subprocess.check_output(
            f'kubectl -n {namespace} get {what} -o yaml', shell=True
        ))
    except subprocess.CalledProcessError:
        if required:
            raise
        else:
            return None


def get_item_detailed_status(item):
    item_status = {"true_status_last_transitions": {}}
    for condition in item["status"].get("conditions", []):
        assert condition["type"] not in item_status["true_status_last_transitions"]
        if condition["status"] == "True":
            item_status["true_status_last_transitions"][condition["type"]] = condition["lastTransitionTime"]
        else:
            item_status.setdefault("errors", []).append({
                "kind": "failed_condition",
                "status": condition["status"],
                "reason": condition["reason"],
                "message": condition["message"],
                "last_transition": condition["lastTransitionTime"]
            })
    return item_status


def get_deployment_detailed_status(deployment, pod_label_selector, main_container_name,
                                   namespace):
    status = get_item_detailed_status(deployment)
    ready = len(status.get('error', [])) == 0
    status['pods'] = []
    pods = get(f'pods -l {pod_label_selector}', namespace=namespace, required=False)
    if pods:
        for pod in pods['items']:
            pod_status = get_item_detailed_status(pod)
            pod_status['other-containers'] = []
            for container in pod['spec']['containers']:
                container_name = container['name']
                container_status = {'name': container_name}
                status_code, output = subprocess.getstatusoutput(
                    f'kubectl -n {namespace} logs {pod["metadata"]["name"]} '
                    f'-c {main_container_name} --tail 5',
                )
                if status_code == 0:
                    container_status['logs'] = output
                else:
                    if container_name == main_container_name: ready = False
                    container_status['logs'] = ''
                container_status['image'] = container['image']
                if container_name == main_container_name:
                    pod_status['main-container'] = container_status
                else:
                    pod_status['other-containers'].append(container_status)
            status['pods'].append(pod_status)
    return dict(status, ready=ready, namespace=deployment['metadata']['namespace'])
