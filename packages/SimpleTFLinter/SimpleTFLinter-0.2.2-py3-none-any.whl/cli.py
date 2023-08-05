import argparse
import os
import yaml
from simple_tf_linter import TerraformLinter, load_key_regex_rule_to_linter


def read_rules_from_yaml(file_path):
    rules = []
    with open(file_path, 'r') as yaml_file:
        rules = yaml.safe_load(yaml_file)
    return rules


def main():
    # Set up and parse command-line arguments
    parser = argparse.ArgumentParser(description='Terraform Linter CLI', add_help=True)
    parser.add_argument('-p', '--path', default='.', help='Path to folder where the Terraform code is, or JSON file (default: current folder)')
    parser.add_argument('-r', '--rule_yaml', default=None, help='Path to the rule YAML file (default: search for .tf_linter_rule.yaml in current folder, then in ~/)')
    parser.add_argument('-t', '--type', choices=['tf-folder', 'json-file'], required=True, help='Input type: "tf-folder" for Terraform folder, "json-file" for JSON file')

    args = parser.parse_args()

    # Get the Terraform code path or JSON file path
    input_path = os.path.abspath(args.path)

    # Get the rule YAML location
    if args.rule_yaml:
        rule_yaml_path = os.path.abspath(args.rule_yaml)
    else:
        current_folder_yaml = os.path.join(os.getcwd(), '.tf_linter_rule.yaml')
        home_folder_yaml = os.path.join(os.path.expanduser('~'), '/.tf_linter_rule.yaml')
        if os.path.exists(current_folder_yaml):
            rule_yaml_path = os.path.abspath(current_folder_yaml)
        elif os.path.exists(home_folder_yaml):
            rule_yaml_path = home_folder_yaml
        else:
            raise FileNotFoundError('.tf_linter_rule.yaml file not found in the current folder or ~/.')
        
    # Print the paths for demonstration purposes
    print("Input Path:", input_path)
    print("Rule YAML Path:", rule_yaml_path)

    # Add your linter logic here
    linter = TerraformLinter()
    rules = read_rules_from_yaml(rule_yaml_path)
    load_key_regex_rule_to_linter(rules, linter)

    ok = False
    errors = []
    if args.type == 'tf-folder':
        ok, errors = linter.lint_directory(input_path)
    elif args.type == 'json-file':
        ok, errors = linter.lint_json(input_path)
    print(f"ok status is {ok}")
    for error in errors:
        print(error)
        
        
if __name__ == "__main__":
    main()
    