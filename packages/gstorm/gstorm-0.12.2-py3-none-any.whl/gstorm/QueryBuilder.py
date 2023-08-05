from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from string import Template
from datetime import datetime
import inflect
from pygqlc import GraphQLClient
from gstorm.BaseGraphQLType import BaseGraphQLType
from gstorm.enums import QueryType
from gstorm.helpers.str_handling import remove_capital, contains_digits
from gstorm.helpers.date_helpers import get_utc_date, get_iso8601_str
from gstorm.helpers.typing_helpers import is_enum
from gstorm.helpers.gql import setup_gql
from gstorm.helpers.gql_schema_helpers import prettify_query

'''
# SIMPLEST
query {
  tanks {
    id
    insertedAt
    updatedAt
  }
}
# PARAMS
query {
  tanks (
    filter: {
      capacity: 10
      name: "hola"
      after: {
        attribute: INSERTED_AT
        date: "2020-01-01T00:00:00Z"
      }
    }
    orderBy: {
      desc: ID
    }
    limit: 10
  ){
    id
    name
    capacity
    insertedAt
    updatedAt
  }
}
'''


class BadQueryBuild(Exception):
    """This exception raises when the query returns with an error code 400.
      It may have an GQL sintax error or an invalid child.
    """
    pass


class InternalServerError(Exception):
    """This exception raises when the query returns with an error code 500.
      It may have some server issue.
    """
    pass


class QueryFailed(Exception):
    """This exception triggers all possible query errors.
    """
    pass


@dataclass
class QueryBuilder():
    _kind: BaseGraphQLType = None
    _type: QueryType = QueryType.PLURAL
    _filter: Dict = field(default_factory=dict)
    _findBy: Dict = field(default_factory=dict)
    _orderBy: Dict = field(default_factory=dict)
    _paginate: bool = False
    _pagesize: int = 100
    _npages: Optional[int] = None
    _limit: int = 0
    _offset: int = 0
    _page: int = 0
    _query: str = ''
    _children: dict = field(default_factory=dict)
    _isChild: bool = False
    _gql: GraphQLClient = field(default=setup_gql())

    def filter(self, **kwargs):
        self._filter = {**self._filter, **kwargs}
        return self

    def findBy(self, **kwargs):
        self._findBy = kwargs
        return self

    def orderBy(self, **kwargs):
        self._orderBy = kwargs
        return self

    def limit(self, count):
        self._limit = count
        return self

    def offset(self, count):
        self._offset = count
        return self

    def children(self, *args, **kwargs):
        """Appends child objects to query, accepts inputs in three formats:
          child(room=10, inventories=20)
          child({'room':10, 'inventories':20})
          child(**{'room':10, 'inventories':20})

        Returns
        -------
        QueryBuilder
          Same instance that called this method for chaining
        """
        if len(args) > 0:
            self._children = {**self._children, **args[0]}
        elif kwargs:
            self._children = {**self._children, **kwargs}
        for key in self._children.keys():
            self._children[key]._isChild = True
        return self

    def paginate(self,
                 page_size: int = 100,
                 n_pages: Optional[int] = None):
        self._paginate = True
        self._pagesize = page_size
        self._npages = n_pages
        return self

    def create(self):
        raise NotImplementedError('Child class should implement create method')

    def update(self):
        raise NotImplementedError('Child class should implement update method')

    def upsert(self):
        raise NotImplementedError('Child class should implement upsert method')

    def delete(self):
        raise NotImplementedError('Child class should implement delete method')

    def nested(self):
        raise NotImplementedError('Child class should implement nested method')

    def apply(self):
        raise NotImplementedError('Child class should implement apply method')

    def get(self):
        """Builds serialized query and returns data from GraphQL Endpoint

        Returns
        -------
        GraphQLType
          Instance of the GraphQLType class that created this QueryBuilder
        """
        _query = self.compile()
        data, errors = self._gql.query(_query)
        if errors:
            self._raising_errors(errors)
            return None

        if self._type == QueryType.SINGULAR:
            instance = self._kind(**data)
            instance.__sync__ = True
            return instance

        if self._paginate:

            # If query is run with pagination it will look for a next page
            # and end cursor
            has_next_page = data['pageInfo']['hasNextPage']
            end_cursor = int(data['pageInfo']['endCursor'])

            # Since paginated queries work differently, all outputs are
            # stored in 'edge'
            instances = [self._kind(**datum) for datum in data['edge']]
            if self._npages is None:
                # Currently pagination is implemented to get all available results
                while has_next_page:
                    _query = self.compile(cursor=end_cursor)
                    data, errors = self._gql.query(_query)
                    has_next_page = data['pageInfo']['hasNextPage']
                    end_cursor = int(data['pageInfo']['endCursor'])
                    instances.extend([self._kind(**datum)
                                     for datum in data['edge']])

                for i, instance in enumerate(instances):
                    instances[i].__sync__ = True
            else:
                for _ in range(self._npages - 1):
                    _query = self.compile(cursor=end_cursor)
                    data, errors = self._gql.query(_query)
                    has_next_page = data['pageInfo']['hasNextPage']
                    end_cursor = int(data['pageInfo']['endCursor'])
                    instances.extend([self._kind(**datum)
                                     for datum in data['edge']])

                for i, instance in enumerate(instances):
                    instances[i].__sync__ = True
            return instances

        else:
            # QueryType.PLURAL
            instances = [self._kind(**datum) for datum in data]
            # mark as synced (AKA: data ok)
            for i, instance in enumerate(instances):
                instances[i].__sync__ = True
            return instances

    def pretty_compile(self):
        return prettify_query(self.compile())

    def compile(self, defaultName=None, isChild=False, cursor: int = 0) -> str:
        """Compiles collected parameters into a serialized query

        Parameters
        ----------
        isChild : bool, optional
          If true, looses the external query boilerplate ("query { ... }"), by default False

        Returns
        -------
        str
          Serialized query ("query Type { getType{fields...}}")
        """
        self._isChild = isChild
        if self._paginate:
            if self._type == QueryType.PLURAL:
                return self.compile_plural_paginated(
                    defaultName=defaultName,
                    cursor=cursor
                )
            else:
                raise NotImplementedError(
                    "Pagination is not implemented on singular queries."
                )
        if self._type == QueryType.PLURAL:
            return self.compile_plural(
                defaultName=defaultName
            )
        else:
            return self.compile_singular(
                defaultName=defaultName
            )

    def compile_plural(self, defaultName=None):
        # get query name
        if not defaultName:
            engine = inflect.engine()
            query_name = engine.plural(remove_capital(self._kind.__name__))
        else:
            query_name = defaultName
        _query = 'query { $Q_NAME $Q_PARAMS{ $Q_FIELDS } }' if not self._isChild else '$Q_NAME $Q_PARAMS{ $Q_FIELDS }'
        has_params = any([self._filter, self._orderBy, self._limit])
        _query = _query.replace('$Q_NAME', query_name)
        if has_params:
            _query = _query.replace(
                '$Q_PARAMS', f'( {self.compile_plural_params()} )')
        else:
            _query = _query.replace('$Q_PARAMS', '')
        _query = _query.replace('$Q_FIELDS', self.compile_fields())
        return _query

    def compile_plural_paginated(self,
                                 defaultName: str = None,
                                 cursor: int = 0) -> str:
        '''
        Generates a paginated version of a plural query.

        Arguments
        ------------
        - defaultName (str): Overrideable query name
        - cursor (int): intial pagination position
        - pageSize (int): Page size limit

        Returns
        ------------
        - string: query string used on pagination
        '''
        if not defaultName:
            query_name = f"{remove_capital(self._kind.__name__)}sPaginate"
        else:
            query_name = f"{defaultName}sPaginate"

        # pagination should now only be supported on base query
        if self._isChild:
            query_name = query_name.replace("Paginate", "")

        _query = "query { $Q_NAME ( cursor: $CURSOR limit: $PAGESIZE $Q_PARAMS){ edge { $Q_FIELDS } pageInfo { endCursor hasNextPage } } }"\
            if not self._isChild else '$Q_NAME $Q_PARAMS{ $Q_FIELDS }'

        # Update name and cursor values
        _query = _query.replace('$Q_NAME', query_name)
        _query = _query.replace('$CURSOR', str(cursor))
        _query = _query.replace('$PAGESIZE', str(self._pagesize))

        # Complie any oter parameters if they exist
        has_params = any([self._filter, self._orderBy, self._limit])
        if has_params:
            _query = _query.replace(
                '$Q_PARAMS', f'{self.compile_plural_params()} ')

        else:
            _query = _query.replace('$Q_PARAMS', '')

        # compile base fields
        _query = _query.replace('$Q_FIELDS', self.compile_fields())
        return _query

    def compile_singular(self, defaultName=None):
        # get query name
        if not defaultName:
            query_name = remove_capital(self._kind.__name__)
        else:
            query_name = defaultName
        _query = 'query { $Q_NAME $Q_PARAMS{ $Q_FIELDS } }' if not self._isChild else '$Q_NAME $Q_PARAMS{ $Q_FIELDS }'
        has_params = any([self._findBy])
        _query = _query.replace('$Q_NAME', query_name)
        if has_params:
            _query = _query.replace(
                '$Q_PARAMS', f'( {self.compile_singular_params()} )')
        else:
            _query = _query.replace('$Q_PARAMS', '')
        _query = _query.replace('$Q_FIELDS', self.compile_fields())
        return _query

    def compile_fields(self):
        compiled_child_queries = ''
        if self._children:
            child_queries = [child.compile(
                defaultName=qname, isChild=True) for qname, child in self._children.items()]
            compiled_child_queries = ' ' + ' '.join(child_queries)
        return " ".join(self._kind.get_base_fields()) + compiled_child_queries

    def compile_plural_params(self):
        # apply filter params
        filter_params = self.gql_param_dumps(
            'filter', self._filter) if self._filter else ''
        # apply orderBy param
        orderby_params = self.gql_param_dumps(
            'orderBy', self._orderBy) if self._orderBy else ''
        # apply limit
        limit_params = f'limit: {self._limit}' if self._limit else ''
        all_params = [filter_params, orderby_params, limit_params]
        used_params = [p for p in all_params if not p == '']
        return f' '.join(used_params)

    def compile_singular_params(self):
        if 'id' in self._findBy:
            k = 'id'
            v = self._findBy['id']
            findby_params = self.gql_param_dumps(k, v)
        else:
            findby_params = self.gql_param_dumps('findBy', self._findBy)
        return findby_params

    def gql_param_dumps(self, k, v):
        """Converts GraphQL parameter pair (key, value) to it's serialized form
        Examples:
        - {'capacity': 10} -> 'capacity: 10'
        - {'enabled': True} -> 'enabled: true'
        - {'name': 'L101'} -> 'name: "L101"'
        - {'status': status.FINISHED} -> 'status: FINISHED'
        - {
            'after': {
              'attribute': 'INSERTED_AT',
              'date': datetime(2020, 4, 4, 9, 12, 47, 1662)
            }
          } -> 'after: { attribute: INSERTED_AT date: "2020-04-04T09:12:47.1662Z" }'

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
            # the query. If the item type is str, then it can pass, but if it's datetime or
            # bool, convert the values of the list first before pass to the next part
            if isinstance(single_item, bool):
                v = [["false", "true"][item] for item in v]
            if isinstance(single_item, datetime):
                v = [get_iso8601_str(get_utc_date(item)) for item in v]
            # Convert the list to a single and large string to pass it to the query.
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
        if type(v) == dict:
            subparams = " ".join([self.gql_param_dumps(subk, subv)
                                  for subk, subv in v.items()])
            return f'{k}: {{ {subparams} }}'
        if is_enum(v):
            return f'{k}: {v.value}'
    # ! Method aliases:
    # filter
    fil = filter
    # filter sub-aliases:
    # filter(after={'attribute': 'INSERTED_AT', 'date': "2020-02-27T23:01:44Z"})

    def after(self, **kwargs):
        _kwargs = {}
        if 'attr' in kwargs:
            _kwargs['attribute'] = kwargs['attr']
            _kwargs['date'] = kwargs.get('date')
        else:
            _kwargs = {**kwargs}
        return self.filter(after=_kwargs)
    # filter(before={'attribute': 'INSERTED_AT', 'date': "2020-02-27T23:01:44Z"})

    def before(self, **kwargs):
        _kwargs = {}
        if 'attr' in kwargs:
            _kwargs['attribute'] = kwargs['attr']
            _kwargs['date'] = kwargs.get('date')
        else:
            _kwargs = {**kwargs}
        return self.filter(before=_kwargs)
    # filter(nullAttribute={ 'isNull': true 'attribute': 'DESCRIPTION' })

    def isNull(self, **kwargs):
        _kwargs = {}
        if 'attr' in kwargs:
            _kwargs['attribute'] = kwargs['attr']
        else:
            _kwargs['attribute'] = kwargs.get('attribute')
        if 'value' in kwargs:
            _kwargs['isNull'] = kwargs['value']
        else:
            _kwargs['isNull'] = kwargs.get('isNull', True)  # Default to True
        return self.filter(nullAttribute=_kwargs)
    # findBy
    fb = findBy
    find = findBy
    # orderBy
    ob = orderBy
    order = orderBy
    # limit
    lim = limit
    # offset
    off = offset
    # children
    child = children
    ch = children
    # get
    run = get
    # paginate
    pgt = paginate
    # create
    # update
    # upsert
    # delete
    # nested
    # apply

    def _raising_errors(self, errors):
        """This function raises any error when is getting the data from a query.

        Args:
            errors (list): list with all errors.

        Raises:
            BadQueryBuild
            InternalServerError
            QueryFailed
        """
        for error in errors:
            message = error['message'].split('\n')[0]
            if 'returning code of 400.' in message:
                raise BadQueryBuild(message)
            elif 'returning code of 500.' in message:
                raise InternalServerError(message)
            else:
                raise QueryFailed(message)
