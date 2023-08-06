import pprint
import click
import yaml
from linkml_runtime import SchemaView


@click.command()
@click.option("--schema-path", "-s", required=True, help="Filesystem or URL path to the schema file")
@click.option("--class-name", "-c", required=True, help="Schema class that the instance should be checked against")
@click.option("--instance-yaml-file", "-i", type=click.File('r'), required=True, help="Path to the instance YAML file")
@click.option("--output-yaml-file", "-o", default="report.yaml",
              help="Output file name for the report (default: report.yaml)")
def validate_instance(schema_path, class_name, instance_yaml_file, output_yaml_file):
    # check recursively?

    print("Loading schema")
    schema_view = SchemaView(schema_path)
    print("Schema loaded")

    print("Checking class")
    class_slots_obj = schema_view.class_induced_slots(class_name)
    print("Class checked")

    class_all_slots_names = [slot.name for slot in class_slots_obj]
    class_required_slots_names = [slot.name for slot in class_slots_obj if slot.required]
    class_recommended_slots_names = [slot.name for slot in class_slots_obj if slot.recommended]
    class_optional_slots_names = [slot.name for slot in class_slots_obj if not slot.required and not slot.recommended]

    instance_dict = yaml.safe_load(instance_yaml_file)

    instance_keys = list(instance_dict.keys())

    used_but_undefined = list(set(instance_keys) - set(class_all_slots_names))
    used_but_undefined.sort()

    required_not_present = list(set(class_required_slots_names) - set(instance_keys))
    required_not_present.sort()

    recommended_not_present = list(set(class_recommended_slots_names) - set(instance_keys))
    recommended_not_present.sort()

    optional_not_present = list(set(class_optional_slots_names) - set(instance_keys))
    optional_not_present.sort()

    report = {
        "used_but_undefined": used_but_undefined,
        "required_not_present": required_not_present,
        "recommended_not_present": recommended_not_present,
        "optional_not_present": optional_not_present,
    }

    with open(output_yaml_file, "w") as file:
        yaml.safe_dump(report, file)


if __name__ == "__main__":
    validate_instance()
