from midburn_dataflows.kubectl_flows import kubectl_get_volumes_flow
from midburn_dataflows.common_flows import run_dump_print


if __name__ == '__main__':
    run_dump_print(
        kubectl_get_volumes_flow(
            get_all_checkpoint_name='kubectl_get_all',
        ),
        'data/kubectl_get_volumes',
        fields=['name', 'source_kind', 'source_name']
    )
