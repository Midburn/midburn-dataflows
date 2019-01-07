from dataflows import Flow, printer, dump_to_path, add_field, update_resource
from midburn_dataflows.kubectl import kubectl, get_item_detailed_status


def add_status(row):
    status = get_item_detailed_status(row)
    row.update(**status)
    row['num_errors'] = len(row['errors']) if row.get('errors') else 0
    row['num_containers'] = len(row['containers']) if row.get('containers') else 0


if __name__ == '__main__':
    print(Flow(
        kubectl(),
        update_resource('res_1', name='kubectl_get_all', path='kubectl_get_all.json'),
        add_field('true_status_last_transitions', 'object'),
        add_field('errors', 'array'),
        add_field('num_errors', 'integer'),
        add_field('num_containers', 'integer'),
        add_status,
        dump_to_path('data/kubectl_get_all'),
        printer(num_rows=1, fields=['kind', 'name', 'namespace', 'nodeName'])
    ).process()[1])
