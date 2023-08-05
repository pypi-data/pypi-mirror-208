import re
from .linter_basic import Rule
from .iterate_dict import value_path_pairs
from .compare_path import check_file_path


class KeyValueCheckRule(Rule):
    def __init__(self, key, is_value_match_func, name, description, file_path=None, dict_path=None, match_is_good=True):
        super().__init__(name, description)
        self.key = key
        self.is_value_match_func = is_value_match_func
        self.file_path = file_path
        self.dict_path = dict_path
        self.match_is_good = match_is_good
        if self.dict_path is not None:
            self.dict_path += '/' + self.key
        
    def is_valid_file_path(self, file_name, file_path):
        if self.file_path is None:
            return True
        file_path = file_path + "/" + file_name
        return check_file_path(self.file_path, file_path)
    
    def is_valid_key_in_dict_path(self, dict_path):
        if not dict_path:
            return False
        key = dict_path.split('/')[-1]
        return key == self.key
        
    def is_valid_dict_path(self, dict_path):
        if self.dict_path is None:
            return True
        return check_file_path(self.dict_path, dict_path)
    
    def check(self, parsed_data, file_name, path, ignore_check_file_path=False):
        ok = True
        error_logs = []
        for value, dict_path in value_path_pairs(parsed_data):
            if not ignore_check_file_path and not self.is_valid_file_path(file_name, path):
                continue
            if not self.is_valid_key_in_dict_path(dict_path):
                continue
            if not self.is_valid_dict_path(dict_path):
                continue
            if self.is_value_match_func(value) ^ self.match_is_good:
                error = f"Invalid value for key '{self.key}': {value} in file {path} in {dict_path}"
                print(error)
                error_logs.append(error)
                ok = False
        return ok, error_logs
                

def _form_pair(key, regex, name=None, description=None, file_path=None, dict_path=None, match_is_good=True):
    return key, regex, name, description, file_path, dict_path, match_is_good


def _load_key_regex_rule_to_linter(pairs, linter):
    for key, regex, rule_name, description, file_path, dict_path, match_is_good in pairs:
        rule_name = rule_name or 'rule_for_' + key
        description = description or '_with_regex_' + regex
        rule = KeyValueCheckRule(key, lambda val: bool(re.match(regex, val)),
                                 rule_name, description, file_path, dict_path, match_is_good)
        linter.register_rule(rule)


def load_key_regex_rule_to_linter(key_regex_pairs, linter):
    pairs = [_form_pair(**pair) for pair in key_regex_pairs]
    _load_key_regex_rule_to_linter(pairs, linter)
    
