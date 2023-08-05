import os
import hcl2
import json


def iterate_folder(start_folder):
    for root, dirs, files in os.walk(start_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, start_folder)
            yield file_path, file_name, relative_path


class Rule:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def check(self, parsed_data, file_name, path, ignore_check_file_path=False):
        raise NotImplementedError("You need to implement the 'check' method for each rule.")


class TerraformLinter:
    def __init__(self):
        self.rules = []
    
    def register_rule(self, rule: Rule):
        self.rules.append(rule)
    
    def parse_file(self, file_path):
        parsed_data = None
        with open(file_path, "r") as f:
            try:
                parsed_data = hcl2.load(f)
            except:
                pass
        return parsed_data

    def lint_json(self, json_file_path):
        ok = True
        error_logs = []
        with open(json_file_path, 'r') as file:
            parsed_data = json.load(file)
            for rule in self.rules:
                current_ok, current_error_logs = rule.check(parsed_data, None, json_file_path, True)
                ok = ok and current_ok
                error_logs = error_logs + current_error_logs
        return ok, error_logs
    
    def lint_file(self, file_path, file_name, relative_path):
        ok = True
        error_logs = []
        
        parsed_data = self.parse_file(file_path)
        if not parsed_data:
            return ok, error_logs
        for rule in self.rules:
            current_ok, current_error_logs = rule.check(parsed_data, file_name, relative_path)
            
            ok = ok and current_ok
            if current_error_logs:
                error_logs += current_error_logs
        return ok, error_logs
    
    def lint_directory(self, folder_path=None):
        ok = True
        error_logs = []
        
        if folder_path is None:
            folder_path = os.getcwd()
        for file_path, file_name, path in iterate_folder(folder_path):
            current_ok, current_error_logs = self.lint_file(file_path, file_name, path)
            
            ok = ok and current_ok
            if current_error_logs:
                error_logs += current_error_logs
        return ok, error_logs

