from dataflows import Flow, update_resource, add_field, checkpoint
from midburn_dataflows.kubectl import kubectl, get_item_detailed_status


def kubectl_get_all_flow(resource_name='kubectl_get_all'):

    def add_status(rows):
        if rows.res.name == resource_name:
            for row in rows:
                status = get_item_detailed_status(row)
                row.update(**status)
                row['num_errors'] = len(row['errors']) if row.get('errors') else 0
                row['num_containers'] = len(row['containers']) if row.get('containers') else 0
                yield row
        else:
            yield from rows

    return Flow(
        kubectl(),
        update_resource('res_1', name=resource_name, path='kubectl_get_all.csv'),
        add_field('true_status_last_transitions', 'object', resources=[resource_name]),
        add_field('errors', 'array', resources=[resource_name]),
        add_field('num_errors', 'integer', resources=[resource_name]),
        add_field('num_containers', 'integer', resources=[resource_name]),
        add_status
    )


def kubectl_get_volumes_flow(source_resource_name='kubectl_get_all',
                             resource_name='kubectl_get_volumes',
                             get_all_checkpoint_name=None):

    volume_object_fields = ['hostPath', 'secret', 'configMap', 'emptyDir', 'gcePersistentDisk',
                            'nfs']

    def get_volumes(rows):
        for row in rows:
            volumes = row.get('volumes')
            for volume in (volumes if volumes else []):
                yield {
                    'name': volume.pop('name'),
                    'source_name': row['name'],
                    'source_kind': row['kind'],
                    'source_namespace': row['namespace'],
                    **{field: volume.pop(field, None) for field in volume_object_fields},
                }
                assert len(volume) == 0, volume

    def add_volumes(package):
        package.pkg.remove_resource(source_resource_name)
        package.pkg.add_resource({
            'name': resource_name,
            'path': f'{resource_name}.csv',
            'schema': {
                'fields': [
                    {'name': 'name', 'type': 'string'},
                    {'name': 'source_kind', 'type': 'string'},
                    {'name': 'source_name', 'type': 'string'},
                    {'name': 'source_namespace', 'type': 'string'},
                    *[{'name': field, 'type': 'object'} for field in volume_object_fields],
                ]
            }
        })
        yield package.pkg
        for rows in package:
            if rows.res.name == source_resource_name:
                yield get_volumes(rows)

    def filter_volumes(rows):
        if rows.res.name == resource_name:
            for row in rows:
                if row['source_namespace'] == 'kube-system': continue
                if any((row.get(f) or row.get(f) == {}) for f in ['secret', 'configMap', 'emptyDir']): continue
                assert row.get('nfs', None) or row.get('gcePersistentDisk', None), row
                yield row
        else:
            yield from rows

    return Flow(
        kubectl_get_all_flow(),
        checkpoint(get_all_checkpoint_name) if get_all_checkpoint_name else None,
        add_volumes,
        filter_volumes
    )
