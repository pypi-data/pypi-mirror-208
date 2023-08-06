import ast
import re


class ParseETL:
    def parse(self, string):
        current_dict = {}
        key = ''
        value = ''
        count = 0
        for char in string:
            if char == '(':
                if count == 0:
                    key = re.sub(r'^\.', '', value)
                    value = ''
                else:
                    value += char
                count += 1
            elif char == ')':
                count -= 1
                if count == 0:
                    key, current_dict, value = self._get_context(
                        key, current_dict, value
                    )
                    value = ''
                else:
                    value += char
            else:
                value += char
        if not key:
            current_dict = self._parse_value(value)
        return current_dict

    def _validate_key(self, key):
        if key != 'ETL':
            if key.startswith('set'):
                key = '_'.join(self._split_camel_case(key[3:]).split())
            return key
        return None

    def __get_objects_by_pattern(self, value):
        try:
            platform_pattern = re.compile(
                r"PlatformFactory\(['\"]([^'\"]+)['\"]\).create\(name=['\"]([^'\"]+)['\"]\,configs=(\[(.*?)\])"
            )
            [factory, name, config, *
                args] = platform_pattern.search(value).groups()
            return {
                'factory': factory,
                'name': name,
                'config': ast.literal_eval(config)
            }
        except AttributeError:
            platform_pattern = re.compile(
                r"PlatformFactory\(['\"]([^'\"]+)['\"]\).create\(name=['\"]([^'\"]+)['\"]\)"
            )
            factory, name = platform_pattern.search(value).groups()
            return {
                'factory': factory,
                'name': name,
            }

    def _process_platform_key(self, key, value):
        if key == 'platform':
            return self.__get_objects_by_pattern(value)
        return None

    def _process_etl_keys(self, key, current_dict, value):
        if key == 'ETL':
            if key not in current_dict:
                current_dict[key] = []
            current_dict[key].append(self.parse(value))
        else:
            current_dict[key] = self.parse(value)
        return current_dict[key]

    def _swap_key_value(self, key, value):
        if not value:
            value = 'factory'
        if value == 'factory':
            key, value = value, key
        elif key in ['extract', 'load', 'transform', 'validate']:
            if key == 'transform':
                value = f'.setType({key}).setName({value})'
            else:
                value = f'.setType({key})' + value
            key = 'ETL'
        return key, value

    def _get_context(self, key, current_dict, value):
        key = self._validate_key(key)
        processed_value = self._process_platform_key(key, value)
        if processed_value:
            current_dict[key] = processed_value
        elif key:
            key, value = self._swap_key_value(key, value)
            current_dict[key] = self._process_etl_keys(
                key, current_dict, value
            )
        return key, current_dict, value

    def _split_camel_case(self, name):
        return (
            re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name))
            .lower()
            .strip()
        )

    def _parse_value(self, value):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
