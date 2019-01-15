from midburn_dataflows.kubectl_flows import kubectl_get_all_flow
from midburn_dataflows.common_flows import run_dump_print


if __name__ == '__main__':
    run_dump_print(
        kubectl_get_all_flow(),
        'data/kubectl_get_all',
        fields=['name', 'kind', 'namespace']
    )
