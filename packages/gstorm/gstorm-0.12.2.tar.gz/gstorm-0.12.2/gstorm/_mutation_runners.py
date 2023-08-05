from __future__ import annotations
from typing import Union, List
from gstorm.enums import MutationMode, MutationType
import pydash as _pd
import gstorm


def create(
    data: Union[gstorm.GraphQLType, List[gstorm.GraphQLType]],
    mode: MutationMode = MutationMode.BATCH
) -> gstorm.MutationBuilder:
    """Builds instance of MutationBuilder to sync GraphQLType objects created locally with the remote DB.

    Parameters
    ----------
    data : Union[gstorm.GraphQLType, List[gstorm.GraphQLType]]
      GraphQLType instance(s) to create in the DB
    mode : MutationMode, optional
      allows to upload data by different upload mechanisms, by default MutationMode.BATCH

    Returns
    -------
    MutationBuilder
      Instance of MutationBuilder class, responsible of building mutation string and communication with DB.
    """
    return gstorm.MutationBuilder(data=data, mode=mode)


def save_multi_create(
    to_be_published: List[GraphQLType],
    children_list: List[str],
    api_limit: int = 100
):
    '''Gstorm 'create' method with slicing for batch-size-limited API.\n
    E. g.:\n
    # Where plan1 & plant2 are instances of a GraphQL-schema-based class (e. g. BbtPlan)\n
    plans = [plan1, plan2]
    errors = multi_create(plans, ['program', 'brightBeer', 'tank'])\n
    # Equivalent to:
    gstorm.create(plans).children(['program', 'brightBeer', 'tank']).run()
    # But sliced...
    '''
    # Since each element amounts for len(children_list),
    # the maximum size an upload batch may have is api_limit//to_be_published
    max_batch_size = api_limit if not children_list else api_limit//len(
        children_list)

    # We need a variable to report any errors when posting items.
    response = {'errors': [], 'messages': []}

    chunked = _pd.chunk(to_be_published, max_batch_size)

    # Iterate over the chunked guy:
    for chunk in chunked:

        # Post the batch
        result = create(chunk).children(children_list).run()

        # Errors, if any, are to be reported
        response['errors'].extend([s for s in result['successful'] if not s])
        response['messages'].extend([s for s in result['messages']])

    # Report errors
    return response


def update(data: Union[gstorm.GraphQLType, List[gstorm.GraphQLType]],
           mode: MutationMode = MutationMode.BATCH,
           findByKeys: List[str] = None
           ) -> gstorm.MutationBuilder:
    """Builds instance of MutationBuilder to sync GraphQLType objects created locally with the
       remote DB.

    Parameters
    ----------
    data : Union[gstorm.GraphQLType, List[gstorm.GraphQLType]]
      GraphQLType instance(s) to update in the DB
    mode : MutationMode, optional
      allows to upload data by different upload mechanisms, by default MutationMode.BATCH
    keys: List[str], optonal
      Allows the user to set keys to be used for the findby method within the database
    Returns
    -------
    MutationBuilder
      Instance of MutationBuilder class, responsible of building mutation string and
      communication with DB.
    """
    return gstorm.MutationBuilder(data=data, mode=mode, Type=MutationType.UPDATE, findByKeys=findByKeys)


def upsert(data: Union[gstorm.GraphQLType, List[gstorm.GraphQLType]],
           mode: MutationMode = MutationMode.BATCH,
           findByKeys: List[str] = None) -> gstorm.MutationBuilder:
    """Builds instance of MutationBuilder to sync GraphQLType objects created locally with the
       remote DB.

    Parameters
    ----------
    data : Union[gstorm.GraphQLType, List[gstorm.GraphQLType]]
      GraphQLType instance(s) to update in the DB
    mode : MutationMode, optional
      allows to upload data by different upload mechanisms, by default MutationMode.BATCH
    keys: List[str], optonal
      Allows the user to set keys to be used for the findby method within the database
    Returns
    -------
    MutationBuilder
      Instance of MutationBuilder class, responsible of building mutation string and
      communication with DB.
    """
    return gstorm.MutationBuilder(data=data, mode=mode, Type=MutationType.UPSERT, findByKeys=findByKeys)


def delete():
    raise NotImplementedError('gstorm.delete not implemented')
