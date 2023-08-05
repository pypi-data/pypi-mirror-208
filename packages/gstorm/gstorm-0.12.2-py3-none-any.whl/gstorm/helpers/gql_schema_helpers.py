import os
from typing import Union, List, TextIO, Dict
from gstorm.helpers.Logging import log, LogLevel
from pydash import camel_case


def inmemory_cleanup(src: Union[str, TextIO]) -> List[str]:
    """This method cleans and removes comments from the input, wether it is a text input/output
    or a string.

    Args:
        src (Union[str,TextIO]): Input schema on any of the available formats

    Returns:
        List[str]: List of strings on which each item is a line of the schema
    """
    if isinstance(src, str):
        src = src.splitlines()
    output = []
    for line in src:
        is_whitespace = not line.strip()
        if is_whitespace:
            output.append(line)
            continue
        line = line.rstrip()  # clean
        line = line.split('#')[0].rstrip()  # remove comment
        # append if not empty
        if line:
            output.append(line + '\n')
    output.append('\n')
    return output


def scalar_map(field_typename):
    return {
        'Boolean': 'Boolean',
        'Integer': 'Int',
        'Float': 'Float',
        'String': 'String',
        'Text': 'Text',
        'Json': 'map',
        'Jsonb': 'Jsonb',
        'Date': 'Date',
        'Time': 'Time',
        'Datetime': 'DateTime',
        'ID': 'ID'
    }[field_typename]


def get_field_kind(field_typename):
    scalar_types = [
        'Boolean',
        'Integer',
        'Float',
        'String',
        'Text',
        'Json',
        'Jsonb',
        'Date',
        'Time',
        'Datetime',
        'ID'
    ]
    if field_typename in scalar_types:
        return 'SCALAR'
    else:
        return 'OBJECT'


'''
Syntactic analizer for a graphql schema

things to consider:

# ! 1. general structure of a type
type TYPE_NAME @opts {
  ...
}
# ! 2. general structure of an enum
enum ENUM_TYPE @opts {
  ...
}
# ! 3. All basic types
type MyType {
  enabled: Boolean
  quantity: Int
  weight: Float
  name: String
  description: Text
  config: Json
  shipAt: Datetime
}
# ! 4. Complex type relations
# ? 4.1 ComplexType1.ListOf.ComplexType2 (Cannot be a list of BasicType)
# ? 4.2 ComplexType1.hasOne.ComplexType2 (Cannot be a hasOne of BasicType)
# ? 4.3 ComplexType1.ComplexType2 (ComplexType2 Must exist)
type User {
  name: String!
  address: Address @has_one
  posts: [Blogpost]
}

type Address {
  street: String
  city: String
  number: Integer
}

type Blogpost {
  author: User
  title: String @unique
}

type UserSkill {
  user: User
  skill: Skill
  level: Integer!
}

type Skill {
  name: String
}
'''


def string_bool_eval(str_bool: Union[str, bool]) -> Union[str, bool]:
    '''
    Function that takes a string or a bool, if a string is given, if the string
    is TRUE or FALSE when upper is used, returns the boolean equivalent,
    if not, returns the string
    if a boolean is passed, returns the boolean value passed

    Args
    --------
    str_bool: Union[str, bool], String or bool to be evaluated

    Returns
    --------
    Union[str, bool], bool if input is bool or if is a boolean in string form
                      else, string
    '''
    evaluation = str_bool
    if isinstance(str_bool, str):
        upper = str_bool.upper()
        match upper:
            case "FALSE":
                evaluation = False
            case "TRUE":
                evaluation = True
    return evaluation


def gql_schema_parse(schema_file_lines: Union[TextIO, List[str]]) -> dict:
    '''
    Function that takes a file or a list of strings and generates a schema

    Args
    -------
    schema_file_lines: Union[TextIO, List[str]], An open text file or a list
                       of strings

    Returns
    -------
    dict, dict that has the schema found in the input
    '''
    # known states: TYPE_SEARCH, PARSING_TYPE, PARSING_ENUM, PARSING_INDEX
    state = 'TYPE_SEARCH'
    schema = {
        'types': {},
        'enums': {},
        'indexes': {}
    }  # dict of types, enums and indexes
    known_labels = ['public', "opt-out"]
    # context
    current_type = None
    current_field = None
    for originalLine in schema_file_lines:
        line = originalLine.strip()
        tokens = line.split()
        if (state == 'TYPE_SEARCH'):
            current_type = {'labels': {
                label: False for label in known_labels}}
            for i, token in enumerate(tokens):
                if tokens[i] == 'type':
                    state = 'PARSING_TYPE'
                    current_type['kind'] = 'TYPE'
                    current_type['fields'] = []
                    continue
                elif token.startswith("@"):
                    label = token.split('@')
                    if label[-1] not in known_labels:
                        raise ValueError(
                            f"The type label {label[-1]} is not a known label, check: {originalLine}")
                    current_type['labels'][label[1]] = True
                    continue
                elif tokens[i] == 'enum':
                    state = 'PARSING_ENUM'
                    current_type['kind'] = 'ENUM'
                    current_type['enumValues'] = []
                elif tokens[i] == 'index':
                    state = 'PARSING_INDEX'
                    current_type['kind'] = 'INDEX'
                    current_type['indexes'] = []
                elif token != "{":
                    current_type['name'] = token
                    continue
                continue
        elif (state == 'PARSING_TYPE'):
            if len(tokens) == 0:
                # blank line inside the type
                continue
            elif tokens[0] == '}':
                # end of type definition
                state = 'TYPE_SEARCH'
                schema['types'][current_type['name']] = current_type
                current_type = None
            else:
                # type body (should be a field definition)
                # known labels are camelCased (hasOne and has_one are the same)
                known_labels_fields = [
                    'hasOne', 'unique', 'default', "hasManyThrough", "hasMany", "public", "optOut"]
                field_is_list = False
                field_typename = None
                current_field = {label: False for label in known_labels_fields}
                current_field['default'] = None
                for i, token in enumerate(tokens):
                    if ":" in token and i == 0:
                        current_field['name'] = token.strip(':')
                    elif "!" in token and token[-1] == '!':
                        current_field['is_required'] = True
                        field_typename = token.strip(
                            '!').strip('[]').strip('!')
                    elif token.startswith("@"):
                        label = camel_case(token.strip('@'))
                        if "id" in label:
                            continue
                        if not any([knownLabel in label for knownLabel in known_labels_fields]):
                            raise ValueError(
                                f"The field label '{token}' is not a known label, check: {originalLine}")
                        label = [
                            knownLabel for knownLabel in known_labels_fields if knownLabel in label][0]
                        current_field[label] = True
                        if 'default' in label:
                            default = tokens[i + 1][:-1].strip('"').strip("'")
                            default_proccesed = string_bool_eval(default)
                            current_field[label] = default_proccesed
                        if 'hasManyThrough' in label:
                            current_field[label] = tokens[i+1][:-1]
                    else:
                        field_typename = token.strip(
                            '!').strip('[]').strip('!') if not field_typename else field_typename
                        if '[' in token and ']' in token:
                            field_is_list = True
                    if i < len(tokens)-1:
                        continue
                    field_kind = get_field_kind(field_typename)
                    current_field['type'] = {
                        'name': field_typename if field_kind == 'OBJECT' else scalar_map(field_typename),
                        'kind': 'LIST' if field_is_list else field_kind
                    }
                    current_type['fields'].append(current_field)
        elif (state == 'PARSING_ENUM'):
            if len(tokens) == 0:
                # blank line inside the enum
                continue
            elif tokens[0] == '}':
                # end of enum definition
                state = 'TYPE_SEARCH'
                # we put the enum in both types and enums, so we can check if a type is an enum
                schema['types'][current_type['name']] = current_type
                schema['enums'][current_type['name']] = current_type
                current_type = None
            else:
                # enum body (should be a EnumValue definition)
                current_type['enumValues'].append(tokens[0].strip())
        elif (state == 'PARSING_INDEX'):
            if len(tokens) == 0:
                # blank line inside the index
                continue
            elif tokens[0] == '}':
                # end of index definition
                state = 'TYPE_SEARCH'
                schema['indexes'][current_type['name']] = current_type
                current_type = None
            else:
                # index body (should be a IndexValue definition)
                current_type['indexes'].append(
                    {tokens[0].strip(':'): tokens[1]})
    # we now know every schema type, we need to update the fields type kind to ENUM if needed:
    for typename, item in schema['types'].items():
        if item['kind'] == 'ENUM':
            continue
        for index, field in enumerate(item['fields']):
            if not field['type']['name'] in schema['types']:
                # may be an error, but leave it to the validation function
                continue
            if (
                field['type']['kind'] == 'OBJECT'
                and schema['types'][field['type']['name']]['kind'] == 'ENUM'
            ):
                schema['types'][typename]['fields'][index]['type']['kind'] = 'ENUM'
    return schema


def load_schema_from_string(src: str) -> Dict:
    """This function recieves a schema in string form, removes comments and returns it
    as a dictionary.

    Args:
        src (str): string containing the schema to be parsed into a dictionary

    Returns:
        Dict: Dictionary containing the parsed schema.
    """
    clean_schema_lines = inmemory_cleanup(src)
    return gql_schema_parse(clean_schema_lines)


def load_schema_from_file(src: str) -> Dict:
    """This function loads a schema from a given path, removes it's comments and parses it
    into a dictoinary

    Args:
        src (str): input path for the file

    Returns:
        Dict: Dictionary representation of the parsed schema
    """
    try:
        src_path = os.path.join(os.getcwd(), src)
        with open(src_path, 'r') as src_file:
            clean_schema_lines = inmemory_cleanup(src_file)
        return gql_schema_parse(clean_schema_lines)
    except FileNotFoundError:
        log(LogLevel.ERROR, f'File {src} not found')
        return


def prettify_query(query):
    tabs = 0
    pretty_query = ''
    parsing_string = False
    inside_brackets = False
    for i, ch in enumerate(query):
        # get context
        prev_ch = query[i-1] if i > 0 else ''
        next_ch = query[i+1] if i < len(query) - 1 else ''
        if not inside_brackets and ch == '{':
            inside_brackets = True
        elif not inside_brackets:
            pretty_query += ch
            continue
        if not parsing_string and ch == '"':
            parsing_string = True
            pretty_query += ch
            continue
        if parsing_string and ch != '"':
            pretty_query += ch
            continue
        if parsing_string and ch == '"':
            parsing_string = False
            pretty_query += ch
            continue
        tabs += 1 if ch in ['{', '('] else (-1 if next_ch in ['}', ')'] else 0)
        if ch != ' ' or prev_ch == ':':
            pretty_query += ch
            continue
        if next_ch in ['{', '(']:
            pretty_query += ch  # add whitespace normally
        elif next_ch in ['}', ')']:
            pretty_query += f"\n{'  ' * tabs}"
        else:
            pretty_query += f"\n{'  ' * tabs}"
    return pretty_query
