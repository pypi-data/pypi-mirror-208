from __future__ import annotations
from typing import List, Union, ForwardRef
from dataclasses import dataclass, field
from string import Template
import json
from datetime import datetime, date, time
import inflect
from pygqlc import GraphQLClient
import gstorm
from gstorm.enums import QueryType
from gstorm.helpers.str_handling import remove_capital, capitalize
from gstorm.helpers.date_helpers import get_utc_date, get_iso8601_str
from gstorm.helpers.gql import setup_gql
from gstorm.helpers.typing_helpers import is_enum, attrs_with_hints
from gstorm.helpers.gql_schema_helpers import prettify_query
from gstorm.enums import MutationType, MutationMode

'''

# 1. generar mutations
MUT = MutationBuilder(prog)
# 2. Correr mutations
result, errors = gql.mutate(MUT)
# 3. Update de objeto de Planeacion
if errors:
  prog.set_errors(errors)
  prog.set_sync(false)
else:
  prog.set_sync(true)
  prog.id = result.id
if gstorm.validate(prog):
  send_notification('success')
else:
  send_notification('error')

'''


@dataclass
class MutationBuilder():
    data: Union[List[gstorm.GraphQLType], gstorm.GraphQLType] = None
    # _kind: Union[List[gstorm.GraphQLType], gstorm.GraphQLType] = None # ! IMPLICIT FROM DATA
    mode: MutationMode = MutationMode.BATCH
    _mutation: str = ''
    _children: dict = field(default_factory=dict)
    _isChild: bool = False
    _gql: GraphQLClient = field(default=setup_gql())
    # New parameter that tells the mutation builder which kind
    # of mutation it's going to create, seems useful since we're adding mutations other than create.
    Type: MutationType = MutationType.CREATE
    _type: str = field(default='create')
    findByKeys: List[str] = field(default=None)

    def __post_init__(self):
        self._type = self.Type.value.lower()
        if not self.findByKeys:
            self.findByKeys = ['guid', 'code', 'id']

    def setFindByKeys(self, keys: List[str]):
        """This method is called to setup the findByKeys required
        for the update or upsert operations, setsup the key or keys that
        the user intends to find on it's classes

        Args:
            keys (List[str]): List of keys that are going to be used
            whilst searching on the database for the specified item.
        """
        if keys:
            self.findByKeys = keys
        return self

    def children(self, *args, **kwargs):
        """Appends child objects to mutation, accepts inputs in several formats:
          children(['room', 'inventories']
                   ) # ! DEFAULTS TO SAME MUTATION (CREATE, UPDATE)
          children(
            room = MutationType.UNIQUE, # ! MODE, NO CHILDREN IMPLICIT
            inventories = MutationType.CREATE, # ! MODE, NO CHILDREN IMPLICIT
          )
          children({
            'room': MutationType.UNIQUE, # ! MODE, NO CHILDREN IMPLICIT
            'inventories': {
              '__mode': MutationType.CREATE, # ! MODE, CHILDREN EXPLICIT
              'tank': MutationType.UPSERT
            },
          })

        Returns
        -------
        QueryBuilder
          Same instance that called this method for chaining
        """
        if len(args) > 0:
            if type(args[0]) == str:
                self._children = {
                    **self._children,
                    **{args[0]: MutationType.LOCAL}
                }
            elif type(args[0]) == list:
                new_children = {ch: MutationType.LOCAL for ch in args[0]}
                self._children = {
                    **self._children,
                    **new_children
                }
            elif type(args[0]) == dict:
                self._children = {
                    **self._children,
                    **args[0]
                }
        elif kwargs:
            new_children = {ch: _type for ch, _type in kwargs.items()}
            self._children = {**self._children, **kwargs}
        for key in self._children.keys():
            self._children[key]._isChild = True
        return self

    def pretty_compile(self, result_type: str = 'complete'):
        compiled = self.compile(result_type)
        if type(compiled) == list:  # sequence of mutations
            return [prettify_query(compiled_item) for compiled_item in compiled]
        else:
            return prettify_query(self.compile(result_type))

    def compile(self, result_type: str = 'complete') -> str:
        '''
        Generates the string of the mutation to run

        Arguments
        ------------
        - result_type (str): form to provide results in the mutation. if results
                             is 'complete' it will provide the full results
                             field. If it is 'id', it will just return the id
                             in results, if None, the mutation will just be
                             built with successful and messages.
        Returns
        ------------
        - str: Mutation string to run
        '''
        # input validation for result_type
        if result_type not in ['complete', 'id', None]:
            raise ValueError('Result type must be "complete", "id" or None')

        if type(self.data) == list:
            return self.compile_plural(self.data, self._children, result_type=result_type)
        else:
            return self.compile_singular(self.data, self._children, result_type=result_type)

    def compile_plural(self, data, children, result_type: str = 'complete'):
        # Here we add the type of mutation to the text, prevously it was hardcoded to "create"
        # this happens throughout all the code.
        batch_items = [
            f'{self._type}{type(datum).__name__}_{i}: {self.compile_singular(data=datum, children=children, batch=True, result_type=result_type)}'
            for i, datum in enumerate(data)
        ]
        engine = inflect.engine()
        plural_name = engine.plural(remove_capital(type(data[0]).__name__))
        query_name = f"{self._type}" + capitalize(plural_name)
        mutation = f'mutation {query_name} {{ ' + " ".join(batch_items) + ' }'

        return mutation

    def compile_singular(self, data, children, batch=False, result_type: str = 'complete'):
        name = f'{self._type}{capitalize(type(data).__name__)}'
        if batch:
            _mutation = '$M_NAME $M_PARAMS{ $M_DEF_FIELDS }'
        else:
            # metaclass , instruction
            _mutation = 'mutation { $M_NAME $M_PARAMS{ $M_DEF_FIELDS } }'
        # ignore results if requested
        if result_type is not None:
            _m_def_fields = 'successful messages{ field message } result{ $M_FIELDS }'
        else:
            _m_def_fields = 'successful messages{ field message }'
        # get only id if requested
        if result_type == 'complete':
            fields = [
                k
                for k, hint in attrs_with_hints(type(data)).items()
                # filter params (only scalar ones)
                if (
                    not k.startswith('__')
                    and hint != List[gstorm.GraphQLType]
                    and not isinstance(hint, ForwardRef)
                )
            ]
        else:
            fields = ['id']
        typehints = attrs_with_hints(type(data))
        try:
            key = [key for key in self.findByKeys if key in typehints][0]
        except IndexError as error:
            raise KeyError(
                f"The type {type(data)} does not contain any of the findByKeys:\n{self.findByKeys}:\n{error}")
        singular_params = self.compile_singular_params(data)
        child_params = self.compile_child_params(data, children)
        params = singular_params if not child_params else f'{child_params} {singular_params}'
        # TODO: Add the key to the searchBy field
        searchby = '' if self.Type not in [
            MutationType.UPDATE, MutationType.UPSERT] else f'findBy: {{ {key}: "{data[key]}" }} {remove_capital(type(data).__name__)}: {{'
        # compiled result:
        _mutation = _mutation.replace('$M_DEF_FIELDS', _m_def_fields)
        _mutation = _mutation.replace('$M_NAME', name)
        _mutation = _mutation.replace('$M_FIELDS', " ".join(fields))
        if self.Type in [
                MutationType.UPDATE, MutationType.UPSERT] and key:
            _mutation = _mutation.replace(
                '$M_PARAMS', f'($S_PARAMS{params}'+' })')
        _mutation = _mutation.replace(
            '$M_PARAMS', f'( {params} )')
        _mutation = _mutation.replace('$S_PARAMS', f" {searchby} ")

        mutation_singular = _mutation
        # Process list children to include them in the mutation sequence:
        child_plural_mutations = []
        for children_field, _type in children.items():
            if _type == MutationType.CREATE:
                # ! Inject parent into children to include in mutations:
                for child_obj in data[children_field]:
                    # ! Example: Tank.get_object_fields('Room')[0]
                    parent_field = type(child_obj).get_object_fields(
                        type(data).__name__)[0]
                    child_obj[parent_field] = data
                child_plural_mutations.append(self.compile_plural(
                    data[children_field], {parent_field: MutationType.LOCAL}, result_type=result_type))
        if child_plural_mutations:
            return [mutation_singular, *child_plural_mutations]
        else:
            # ! single mutation, simplest case
            return mutation_singular

    def compile_singular_params(self, data):
        data_type = type(data)
        hints = attrs_with_hints(data_type)
        params = [
            (k, data[k])
            for k, hint in hints.items()
            # filter params (only scalar ones)
            if (
                not k.startswith('__')
                and not k in ['id', 'insertedAt', 'updatedAt']
                and hint != List[gstorm.GraphQLType]
                and not isinstance(hint, ForwardRef)
            )
        ]
        return ' '.join([self.gql_param_dumps(k, v) for k, v in params])

    def compile_child_params(self, data, children):
        params = []
        local_children = [
            child
            for child, mtype in children.items()
            if mtype == MutationType.LOCAL
        ]
        for child in local_children:
            child_obj = data[child]
            if not child_obj:
                continue
            # If the Children are a list, then iterate over each item
            if isinstance(child_obj, list):
                # Obtain the ids from all the objects in the list of children
                _ids = [next(iter(obj.get_unique_identifiers()))
                        for obj in child_obj]
                # Just take one ID to get the key
                key = f'{child}{capitalize(_ids[0])}'
                params += [self.gql_param_dumps(key, obj[_id])
                           for _id in _ids for obj in child_obj]
                continue
            # get first non-empty unique identifier:
            _id = next(iter(child_obj.get_unique_identifiers()))
            key = f'{child}{capitalize(_id)}'
            params.append(self.gql_param_dumps(key, child_obj[_id]))
        return ' '.join(params)

    def gql_param_dumps(self, k, v):
        """Converts GraphQL parameter pair (key, value) to it's serialized form
        Examples:
        - {'capacity': 10} -> 'capacity: 10'
        - {'enabled': True} -> 'enabled: true'
        - {'name': 'L101'} -> 'name: "L101"'
        - {'status': 'FINISHED'} -> 'status: FINISHED'

        Parameters
        ----------
        k : param key
            left-hand side id for graphql parameter pair
        v : param value
            right-hand side value for graphql parameter pair
        """
        if type(v) == int:
            return f'{k}: {v}'
        if type(v) == float:
            return f'{k}: {v}'
        if type(v) == str:
            # regular case, this means it's a string, include double quotes
            return f'{k}: "{v}"'
        if type(v) == list:
            # To know how to return the values inside of the list, we've to know
            # the type of the elements inside. Take one element and check which type is.
            single_item = v[-1]
            if isinstance(single_item, (int, float)):
                # Don't do anything. Return this as normal as it'll work
                return f'{k}: {v}'
            # If it's not int or float, need to do a conversion to obtain a correct type for
            # the mutation. If the item type is str, then it can pass, but if it's datetime or
            # bool, convert the values of the list first before pass to the next part
            if isinstance(single_item, bool):
                v = [["false", "true"][item] for item in v]
            if isinstance(single_item, datetime):
                v = [get_iso8601_str(get_utc_date(item)) for item in v]
            # Convert the list to a single and large string to pass it to the mutation.
            # Create the template to fill the values
            string_values = Template('"$value"')
            items = '['  # Initialize the string
            for item in v:
                items += string_values.substitute(value=item)+','
            # Erase the last comma and close the brackets
            items = items[:-1]+']'
            # return the string with all the items together
            return f'{k}: {items}'
        if type(v) == bool:
            return f'{k}: {["false","true"][v]}'  # short-hand for inline if
        if type(v) == datetime:
            utc_date = get_utc_date(v)
            return f'{k}: "{get_iso8601_str(utc_date)}"'
        if type(v) == date:
            return f'{k}: "{v.strftime("%Y-%m-%d")}"'
        if type(v) == time:
            return f'{k}: "{v.strftime("%H:%M:%S")}"'
        if type(v) == dict:
            quote = '"'
            scape = '\\'
            return f'{k}: "{json.dumps(v).replace(quote, scape + quote)}"'
        if is_enum(v):
            return f'{k}: {v.value}'
        if v is None:
            return f'{k}: null'
        raise ValueError(
            f'Unknown type {type(v)} for value {v} of key {k} at {self.__class__.__name__}')

    def run(self, result_type: str = 'complete') -> dict:
        '''
        Builds a mutation string, runs the mutation through the class gql client
        and returns the results as a dictionary.

        Arguments
        ------------
        - result_type (str): form to provide results in the mutation. if results
                             is 'complete' it will provide the full results
                             field. If it is 'id', it will just return the id
                             in results, if None, the mutation will just be
                             built with successful and messages.
        Returns
        ------------
        - dict: response from the GQL API in dictionary form
        '''
        _mutation = self.compile(result_type)
        if type(_mutation) == str:
            # ! SINGLE MUTATION
            data, errors = self._gql.mutate(_mutation)
            if not data:
                # This return only works when the query is badly written
                return {
                    'successful': False,
                    'result': None,
                    'messages': [{'message': error['message']} for error in errors]
                }
            if not data.get('result'):
                data['result'] = {}
            if type(self.data) == list:
                # ! BATCH MUTATION
                full_response = {'result': [],
                                 'messages': [], 'successful': []}
                for i, item in enumerate(self.data):
                    # If the Data to upload is higher to 1 element
                    # choose the element to inspect in this iteration
                    if len(self.data) > 1:
                        label = f'{self._type}{type(item).__name__}_{i}'
                        # data for this specific item:
                        item_response = data.get(label)
                    else:
                        # If not, then just select the data. In this cases
                        # Maybe the qty of objects to upload is odd, so is highly
                        # probably that at some point, self.data it's equal to [Object]
                        # and data={info} without labels (cause it's just one element).
                        item_response = data
                    # append to full response:
                    full_response['successful'].append(
                        item_response.get('successful', False))
                    full_response['messages'].extend(
                        item_response.get('messages', []))
                    full_response['result'].append(
                        item_response.get('result', {}))
                    item.__errors__ = item_response['messages'] if len(
                        item_response.get('messages', [])) > 0 else []
                    if 'result' in item_response:
                        item.update(item_response.get('result') or {})
                        item.__sync__ = True
                    else:
                        item.__errors__.extend(
                            [{'message': 'No data for this item'}])
                return full_response
            else:
                # ! SIMPLE MUTATION
                self.data.__errors__ = errors
                if not errors:
                    # rebuilds object adding data from DB
                    self.data.update(data['result'])
                    self.data.__sync__ = True
                return data
        elif type(_mutation) == list:
            _mutations = _mutation
            # ! SEQUENTIAL MUTATION
            sequence = [self.data]
            sequence.extend([
                self.data[child]
                for child, _type in self._children.items()
                if _type == MutationType.CREATE
            ])
            full_response = {'result': [], 'messages': [], 'successful': []}
            for mutation, seq_obj in zip(_mutations, sequence):
                # ! Run every mutation sequentially
                data, errors = self._gql.mutate(mutation)
                if type(seq_obj) == list:
                    # ! SEQUENCE - BATCH MUTATION ITEM
                    for i, item in enumerate(seq_obj):
                        label = f'{self._type}{type(item).__name__}_{i}'
                        # data for this specific item:
                        item_response = data.get(label)
                        # append to full response:
                        full_response['successful'].append(
                            item_response.get('successful', False))
                        full_response['messages'].extend(
                            item_response.get('messages', []))
                        full_response['result'].append(
                            item_response.get('result', {}))
                        item.__errors__ = item_response['messages'] if len(
                            item_response.get('messages', [])) > 0 else []
                        if 'result' in item_response:
                            item.update(item_response['result'])
                            item.__sync__ = True
                        else:
                            item.__errors__.extend(
                                [{'message': 'No data for this item'}])
                else:
                    # ! SEQUENCE - SINGULAR MUTATION ITEM
                    seq_obj.__errors__ = errors
                    if not errors:
                        # rebuilds object adding data from DB
                        seq_obj.update(data['result'])
                        seq_obj.__sync__ = True
            return full_response
        else:
            raise Exception(
                'Compiled mutation should be either a string or a list of strings')
