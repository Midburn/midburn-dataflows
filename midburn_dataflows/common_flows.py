from dataflows import Flow, dump_to_path, printer, checkpoint


def dump_print_flow(flow, dump_path, num_rows=1, fields=None, checkpoint_name=None):
    return Flow(
        flow,
        checkpoint(checkpoint_name) if checkpoint_name else None,
        dump_to_path(dump_path),
        printer(num_rows=num_rows, fields=fields)
    )


def run_dump_print(flow, dump_path, num_rows=1, fields=None):
    print(dump_print_flow(flow, dump_path, num_rows, fields).process()[1])
