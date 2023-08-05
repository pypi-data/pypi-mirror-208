# Terraform Linter CLI

This is a simple Terraform Linter CLI that checks your Terraform configuration files for compliance against specified rules. It supports input from Terraform folders or JSON files, and various rule types.

## Features

* Lint Terraform configurations in a folder or JSON file.
* Specify custom rule sets via YAML files.
* Add, modify or remove rules to suit your requirements.
* Easily extend the linter with additional custom rules.

## Installation

1. Make sure you have Python 3 installed on your computer.
2. Install the Terraform Linter CLI package using pip:

```
pip install simpleTFLinter
```
## Usage

After installing the `simpleTFLinter` package, you can use the `simple_tf_linter` command to run the linter.

1. Set up your rule YAML file with the desired rules. You can either create your own or use the default `.tf_linter_rule.yaml` provided in the `examples` directory.
2. Run the Terraform Linter CLI using the following command:

```
simple_tf_linter -p [input_path] -r [rule_yaml_path] -t [input_type]
```

* `input_path`: Path to the folder containing Terraform code or the JSON file you want to lint.
* `rule_yaml_path`: Path to the rule YAML file
* `input_type`: Input type, either `tf-folder` for a Terraform folder or `json-file` for a JSON file.

Example:

```
simple_tf_linter -p ./my_terraform_folder -r ./rule_file.yaml -t tf-folder
```

This will lint the Terraform files in `my_terraform_folder` using the rules specified in `rule_file.yaml`.

### Generating a JSON file from a Terraform Plan

You can also lint a JSON file generated from your Terraform plan. To create a JSON file, follow the steps below:

1. Initialize your Terraform working directory:

```
terraform init
```

2. Create a Terraform plan and save it to a file:

```
terraform plan -out tf.plan
```

3. Convert the Terraform plan to JSON format and save it to a file using the `terraform show -json` command, and optionally use `jq` to pretty-print the JSON:

```
terraform show -json tf.plan | jq > tf.json
```

Now you have a JSON file `tf.json` containing your Terraform plan, which can be used as an input for the Terraform Linter CLI.

To lint the JSON file, run the following command:

```
simple_tf_linter -p ./tf.json -r ./rule_file.yaml -t json-file
```

This will lint the `tf.json` file using the rules specified in `rule_file.yaml`.


## Custom Rules

You can add, modify or remove rules in the rule YAML file. Each rule consists of the following properties:

* `key`: The key to check.
* `regex`: The regular expression to match against the value of the key.
* `name`: (Optional) The name of the rule.
* `description`: (Optional) A brief description of the rule.
* `file_path`: (Optional) The file path where the rule should be applied. You can use `*` to match one level in the path and `**` to match zero, one, or multiple levels in the path.
* `dict_path`: (Optional) The dictionary path where the key should be checked. Similar to `file_path`, use `*` to match one level and `**` to match zero, one, or multiple levels in the path.
* `match_is_good`: (Optional) Set to `True` if the value should match the regex; set to `False` if the value should not match the regex.

Example of a rule in YAML format:


```yaml
- key: aws_instance_type
  regex: ^t2\..+$
  name: rule_for_aws_instance_type
  description: Check if the instance
  type is t2.*
  file_path: "**/*.tf"
  dict_path: resource/*/aws_instance_type
  match_is_good: true
  ```


In this example, the `file_path` is set to `**/*.tf`, which means that the rule should be applied to any `.tf` file at any level of the directory structure. The `dict_path` is set to `resource/*/aws_instance_type`, which means that the rule should be checked on the `aws_instance_type` key within any single level of the `resource` dictionary.

This rule checks if the `aws_instance_type` key has a value that starts with `t2.` and any characters following it.

## Extending the Linter

To create custom rules, you can extend the `Rule` class and implement the `check` method. Then, register the rule with the `TerraformLinter` instance.

Example:

```python
class CustomRule(Rule):
    def __init__(self, ...):
        super().__init__(name, description)
        # Initialize your rule properties here.

    def check(self, parsed_data, file_name, path, ignore_check_file_path=False):
        # Implement your custom rule logic and return the result.
        pass

linter = TerraformLinter()
custom_rule = CustomRule(...)
linter.register_rule(custom_rule)
```

For more examples of custom rules, refer to the source code provided.

## Popular Regex Patterns

Here are some popular regex patterns that can be used in the rule YAML file:

* For `trusted-arn`:

```yaml
- key: trusted-arn
  regex: "arn:aws:iam::\\d{12}:role(?:/.+)?$"
```

* For `stg` domain:

```yaml
- key: stg-domain
  regex: "\b(?:[A-Za-z0-9_]*\.*\s*)*stg\.[A-Za-z0-9_.-]+"
  match_is_good: False
```

Add these rules to your rule YAML file to easily check for these patterns in your Terraform configurations.

## Testing

The Terraform Linter CLI comes with a test suite to ensure its functionality. To run the tests, first, make sure you have `pytest` installed. If not, install it using:

```
pip install pytest
```

Then, run the tests using the following command:

```
pytest tests
```

This will execute the test suite and display the results.

## Contributing

If you find any issues or have suggestions for improvements, feel free to submit an issue or create a pull request. Your feedback is always welcome!