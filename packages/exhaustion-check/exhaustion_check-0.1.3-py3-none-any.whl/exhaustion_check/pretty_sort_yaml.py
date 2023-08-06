import click
import sys
import pprint
import yaml


def process_yaml_data(yaml_data, output):
    if output:
        with open(output, 'w') as output_file:
            yaml.dump(yaml_data, stream=output_file, sort_keys=True)
    else:
        print(yaml.dump(yaml_data, sort_keys=True))


@click.command()
@click.option('--input', '-i', type=click.Path(exists=True), help='Input file path')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def load_yaml_file(input, output):
    if input:
        with open(input, 'r') as file:
            try:
                yaml_data = yaml.safe_load(file)
                process_yaml_data(yaml_data, output)
            except yaml.YAMLError as e:
                print(f"Error while loading YAML file: {e}", file=sys.stderr)
    else:
        try:
            yaml_data = yaml.safe_load(sys.stdin)
            process_yaml_data(yaml_data, output)
        except yaml.YAMLError as e:
            print(f"Error while loading YAML from stdin: {e}", file=sys.stderr)


if __name__ == '__main__':
    load_yaml_file()
