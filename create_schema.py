def open_figure_bracket(writer, tabs_count):
    writer.write(f'{"\t" * tabs_count}{{\n')


def close_figure_bracket(writer, tabs_count):
    writer.write(f'{"\t" * tabs_count}}}')


def write_schema_name(writer, name):
    writer.write('\t"schemaName": "' + name + '",\n')


def write_dimension_field(writer, name, type):
    open_figure_bracket(writer, 2)
    writer.write('\t\t\t"name": "' + name + '",\n')
    writer.write('\t\t\t"dataType": "' + type + '"\n')
    close_figure_bracket(writer, 2)


def write_field_specs_header(writer, header):
    writer.write(f'\t"{header}": [\n')


def write_metric_field(writer, name, type):
    open_figure_bracket(writer, 2)
    writer.write('\t\t\t"name": "' + name + '",\n')
    writer.write('\t\t\t"dataType": "' + type + '"\n')
    close_figure_bracket(writer, 2)


def close_square_bracket(writer):
    writer.write('\t]')


def write_new_line(writer):
    writer.write('\n')


def write_comma_and_new_line(writer):
    writer.write(',\n')


def write_data_time_field_specs(writer):
    writer.write('\t"dataFieldSpecs": [\n')
    open_figure_bracket(writer, 2)
    writer.write('\t\t\t"name": "data_time",\n')
    writer.write('\t\t\t"dataType": "STRING",\n')
    writer.write('\t\t\t"format": "yyyy-MM-dd HH:mm:ss",\n')
    close_figure_bracket(writer, 2)
    close_square_bracket(writer)


def delete_last_char(writer):
    writer.delete(writer.tell() - 1, writer.tell())


schema = ''

schema_file = 'schema.json'

with open(schema_file, 'w') as writer:
    open_figure_bracket(writer, 0)
    write_schema_name(writer, 'electricity')
    write_field_specs_header(writer, 'dimensionFieldSpecs')
    close_square_bracket(writer)
    write_comma_and_new_line(writer)
    write_field_specs_header(writer, 'metricFieldSpecs')
    for i in range(1, 371):
        write_metric_field(writer, f'MT_{i}', 'DOUBLE')
        if i != 370:
            write_comma_and_new_line(writer)
    write_new_line(writer)
    close_square_bracket(writer)
    write_data_time_field_specs(writer)
    close_figure_bracket(writer, 0)
