import os
import math
import datetime
import logging

from ..helpers import responsify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, or_, and_, cast, func
from sqlalchemy.sql import expression
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import (
    Date,
    String,
    Integer,
    Boolean,
    DateTime,
    Time,
    Numeric,
)

from zephony.exceptions import InvalidRequestData

from zephony.helpers import(
    is_valid_date,
    is_valid_datetime,
    get_rows_from_csv,
    serialize_datetime,
    time_format,
    date_format,
    datetime_format,
    datetime_with_microseconds_format,
)

db = SQLAlchemy()
logger = logging.getLogger(__name__)

class BaseModel(db.Model):
    __abstract__ = True

    id_ = db.Column('id', db.BigInteger, primary_key=True)
    token = db.Column(db.String, unique=True)
    is_deleted = db.Column(db.Boolean, server_default=expression.false())
    deleted_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime, server_default=func.now())
    last_updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    id_creator_user = db.Column(db.BigInteger)
    id_last_updated_user = db.Column(db.BigInteger)
    id_deleted_user = db.Column(db.BigInteger)

    readable_fields = []
    updatable_fields = []
    filterable_fields = []

    # TODO: Do assignments by doing datatype conversions for datetime, etc
    def __init__(self, data, from_seed_file=False):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.info(f'{type(self).__name__} Model has no attribute : {key}')

        self.created_at = serialize_datetime(
            datetime.datetime.now(),
            datetime_with_microseconds_format
        )
        if request and request.user and request.user.id_:
            self.id_creator_user = request.user.id_

        db.session.add(self)
        db.session.flush()

    # TODO: Needs refactoring
    @staticmethod
    def _add_key_from_csv_row(data, k, v, row):
        if type(v) == tuple:
            if len(v) == 1:  # Value hardcoded right in the index being sent
                data[k] = v[0]
            elif len(v) == 2:  # Value has to be type casted
                # Do nothing if value is empty
                if not row[v[0]].strip():
                    return

                if v[1] is int:
                    data[k] = int(row[v[0]].split('.')[0])
                elif v[1] is bool:
                    if row[v[0]] in ['true', 1, '1', '1.0', 'TRUE', 'True']:
                        data[k] = True
                    elif row[v[0]] in ['false', 0, '0', '0.0', 'FALSE', 'False']:
                        data[k] = False
                    else:
                        data[k] = None
                elif v[1] == 'datetime':
                    try:
                        date_str_format = '%d/%m/%Y' if '/' in row[v[0]] else '%Y-%m-%d'
                        data[k] = datetime.datetime.strptime(row[v[0]], date_str_format).isoformat()
                    except ValueError:
                        #TODO: Doing this only to make import work quickly
                        data[k] = None
                        # raise ValueError('`{}`: Cannot parse datetime'.format(row[v[0]]))
                elif v[1] == 'datetime_iso':
                    try:
                        date_str_format = '%d/%m/%Y' if '/' in row[v[0]] else '%Y-%m-%d'
                        data[k] = datetime.datetime.strptime(row[v[0]], date_str_format).isoformat()
                    except ValueError:
                        #TODO: Doing this only to make import work quickly
                        data[k] = None
                        # raise ValueError('`{}`: Cannot parse datetime'.format(row[v[0]]))
                elif callable(v[1]):
                    data[k] = v[1](row[v[0]])
                else:
                    raise ValueError('`{}`: Unsupported type to type case to'.format(v[1]))
            elif len(v) == 3:
                if v[2] == 'power_of_2':  # Used for permissions to calculate & store permission bit
                    # Permission bit cannot be empty
                    if not row[v[0]].strip():
                        raise ValueError('Permission bit value cannot be empty')

                    if v[1] is not int:
                        raise ValueError('`{}`: Cannot type cast to integer'.format(v[1]))

                    data[k] = str(2 ** ((int(row[v[0]].split('.')[0])) - 1))
                elif v[2] == 'boolean':
                    if row[v[0]].strip() == 'x':
                        data[k] = True
                    else:
                        data[k] = False
                elif v[2] == 'permission_tokens':
                    # Queries permissions table
                    from .permission import Permission
                    permissions_map = Permission.get_map()

                    permission_bit_sequence = 0
                    # Split by comma
                    if row[v[0]].strip():
                        permission_tokens = row[v[0]].strip().split(',')
                        for token in permission_tokens:
                            permission_bit_sequence |= int(permissions_map[token.strip()])

                    data[k] = str(permission_bit_sequence)
                elif v[2] == 'foreign_key':  # For foreign key relationships
                    cls = v[1]

                    # Query and get the object ID, if found, else, create new entry in the database and return the ID.
                    obj = cls.query.filter_by(
                        original_name=row[v[0]],
                        is_deleted=False
                        # status='active'
                    ).first()

                    if not obj:
                        obj = cls({
                            'original_name': row[v[0]]
                        })
                        db.session.add(obj)
                        db.session.commit()

                    data[k] = obj.id_
                else:
                    raise Exception('Invalid value: `{}`'.format(v[2]))
            else:
                raise Exception('Invalid tuple length: `{}`'.format(len(v)))
        else:
            data[k] = row[v]

    def _get_base_details(self):
        base_details = {
            'id': self.id_,
            'token': self.token,
            'created_at': serialize_datetime(
                self.created_at,
                datetime_with_microseconds_format,
            ),
        }
        if self.last_updated_at:
            base_details['last_updated_at'] = serialize_datetime(
                self.last_updated_at,
                datetime_with_microseconds_format,
            )
        else:
            base_details['last_updated_at'] = None

        return base_details

    @staticmethod
    def _convert_filters_map_to_list(filter_map):
        """
        Each filter parameter has a filter operator (starts_with,
        ends_with, etc.) and a field name. If a operator is not
        present, `equals` is used as the default operator.

        The filter parameter takes the following format:
            __<filter_operator>__<field_name>

        For example, if you want to get users who are younger than 20,
        you can use the filter parameter `__lesser_than__age` where
        `lesser_than` is the operator and `age` is the field name.

        The following filter parameter formats are allowed:

            1. Type: VARCHAR
                - __starts_with__<field_name>
                - __ends_with__<field_name>
                - __contains__<field_name>
                - __equals__<field_name>
            2. Type: INTEGER
                - __lesser_than__<field_name>
                - __greater_than__<field_name>
                - __equals__<field_name>
            3. Type: BOOLEAN
                - __equals__<field_name>
            4. Type: DATETIME
                - __from__<field_name>
                - __to__<field_name>
                - __equals__<field_name>

        Returns [{
            'key': <field_name>,
            'values': [<value1>, <value2>],
            'operator': <filter_operator>,
        }]
        """

        filters_list = []
        for filter_key_with_operator in filter_map:
            # If multiple values are present in the filter,
            # use a comma to separate them.
            filter_map[filter_key_with_operator] = filter_map[
                filter_key_with_operator
            ].strip('[] ')
            if ',' in filter_map[filter_key_with_operator]:
                values = filter_map[filter_key_with_operator].split(',')
            else:
                values = [ filter_map[filter_key_with_operator] ]

            filter_ = {
                'key': None,
                'values': [v.strip(' ') for v in values],
                'operator': None,
            }
            if filter_key_with_operator.startswith('__'):
                # First segment will be an empty string
                segments = filter_key_with_operator.split('__')[1:]
                filter_['operator'] = segments[0]
                filter_['key'] = segments[1]
            else:
                filter_['operator'] = 'equals'
                filter_['key'] = filter_key_with_operator

            filters_list.append(filter_)

        return filters_list

    # TODO: Needs refactoring
    @classmethod
    def load_from_csv(cls, f_path, column_index, delimiter=',', header=True,
            empty_check_col=1, repr_col=1, row_commit=False):
        """
        This function takes a relative path of a csv file and populates
        the database with the contents of the csv file.

        :param str f_path: The relative path to the file
        :param dict column_index: Model field_name, CSV index mapper
        :param bool header: Flag to determine whether to skip first line of CSV
        :param int empty_check_col: The column count if empty marks last line of CSV
        :param int repr_col: The value to be printed for each row in log messages
        :param bool row_commit: If True, commit immediately after adding to session

        :return bool: True
        """

        objects = []
        duplicates = []
        rows = get_rows_from_csv(
            f_path,
            delimiter=delimiter,
            header=header,
            empty_check_col=empty_check_col,
        )
        for row_index, row in enumerate(rows):
            # logger.debug('Loading {} `{}` from CSV..'.format(cls.__name__, row[repr_col]))
            data = {}
            for k, v in column_index.items():
                if type(v) == dict:  # Handling nested dictionary
                    data[k] = {}
                    for sk, sv in v.items():  # sk: sub_key, sv: sub_value :P
                        cls._add_key_from_csv_row(data[k], sk, sv, row)
                else:
                    cls._add_key_from_csv_row(data, k, v, row)

            # The following try-except block applies only for user
            # Skip row if error occurs
            try:
                obj = cls(data, from_seed_file=True)
            except InvalidRequestData as e:
                if hasattr(e, 'duplicate') and e.duplicate:
                    duplicates.append(e.duplicate.get_details())
                e.row = row_index
                continue
            db.session.add(obj)

            if row_commit:
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()

            objects.append(obj)

        res = {
            'objects': objects,
            'total_non_empty_rows': len(rows),
        }

        if duplicates:
            res['duplicates'] = duplicates

        return res

    @classmethod
    def add_filters_to_query(cls, q, filters_map, filterable_fields):
        # Convert filters map to filters list
        filters = cls._convert_filters_map_to_list(filters_map)

        if os.environ.get('APP_ENV', None) != 'live':
            logger.info('----------------------------------------')
            logger.info(f'Filters to be applied : {filters}')

        for filter_ in filters:
            if filter_['key'] in filterable_fields:
                filter_attr = filterable_fields[f"{filter_['key']}"]
                field_type = filter_attr.type
                logger.info(f'Trying to apply filter : {filter_}')
            else:
                logger.info(f'Ignoring invalid filter key : {filter_["key"]}')
                continue

            if isinstance(field_type, String):
                if not filter_['values']:
                    logger.info(f'Invalid filter value : {filter_["values"]}')
                    continue

                if filter_['operator'] == 'starts_with':
                    q = q.filter(
                        or_(
                            *[filter_attr.ilike(v+'%') for v in filter_['values']]
                        )
                    )
                elif filter_['operator'] == 'ends_with':
                    q = q.filter(
                        or_(
                            *[filter_attr.ilike('%'+v) for v in filter_['values']]
                        )
                    )
                elif filter_['operator'] == 'contains':
                    q = q.filter(
                        or_(
                            *[filter_attr.ilike('%'+v+'%') for v in filter_['values']]
                        )
                    )
                elif filter_['operator'] == 'equals':
                    q = q.filter(
                        or_(
                            *[func.lower(filter_attr) == v.lower() for v in filter_['values']]
                        )
                    )
                elif filter_['operator'] == 'contains_sequence':
                    values = []
                    for each_value in filter_['values']:
                        filter_string = '%'
                        for each_character in each_value:
                            filter_string += f'{each_character}%'
                        values.append(filter_string)
                    filter_['values'] = values
                    q = q.filter(
                        or_(
                            *[filter_attr.ilike(v) for v in filter_['values']]
                        )
                    )
                else:
                    logger.info(
                        f'Ignoring invalid operator : {filter_["operator"]}'
                    )
            elif isinstance(field_type, Integer):
                filter_['values'] = [
                    int(v) for v in filter_['values']
                    if v and v.isdigit()
                ]

                if not filter_['values']:
                    logger.info(f'Invalid filter value : {filter_["values"]}')
                    continue

                if filter_['operator'] == 'lesser_than':
                    q = q.filter(
                        or_(*[
                            (filter_attr < v for v in filter_['values']),
                        ])
                    )
                elif filter_['operator'] == 'greater_than':
                    q = q.filter(
                        or_(*[
                            (filter_attr > v for v in filter_['values']),
                        ])
                    )
                elif filter_['operator'] == 'equals':
                    q = q.filter(
                        or_(*[
                            (filter_attr == v for v in filter_['values']),
                        ])
                    )
                elif filter_['operator'] == 'in':
                    q = q.filter(
                        or_(
                            *[filter_attr.in_(filter_['values'])]
                        )
                    )
                elif filter_['operator'] == 'not_in':
                    q = q.filter(
                        or_(
                            *[filter_attr.not_in(filter_['values'])]
                        )
                    )
                else:
                    logger.info(
                        f'Ignoring invalid operator : {filter_["operator"]}'
                    )
            elif isinstance(field_type, Date):
                filter_['values'] = [
                    v for v in filter_['values']
                    if v and is_valid_date(v)
                ]

                if not filter_['values']:
                    logger.info(f'Invalid filter value : {filter_["values"]}')
                    continue

                if filter_['operator'] == 'from':
                    q = q.filter(
                        or_(*[
                            filter_attr >= v for v in filter_['values']
                        ])
                    )
                elif filter_['operator'] == 'to':
                    q = q.filter(
                        or_(*[
                            filter_attr <= v for v in filter_['values']
                        ])
                    )
                elif filter_['operator'] == 'equals':
                    q = q.filter(
                        or_(*[
                            filter_attr == v for v in filter_['values']
                        ])
                    )
                elif filter_['operator'] == 'not_in':
                    q = q.filter(
                        or_(
                            *[filter_attr.not_in(filter_['values'])]
                        )
                    )
                else:
                    logger.info(
                        f'Ignoring invalid operator : {filter_["operator"]}'
                    )
            elif isinstance(field_type, DateTime):
                filter_['values'] = [
                    v for v in filter_['values']
                    if v and is_valid_datetime(v)
                ]

                if not filter_['values']:
                    logger.info(f'Invalid filter value : {filter_["values"]}')
                    continue

                if filter_['operator'] == 'from':
                    q = q.filter(
                        or_(*[
                            filter_attr >= v for v in filter_['values']
                        ])
                    )
                elif filter_['operator'] == 'to':
                    q = q.filter(
                        or_(*[
                            filter_attr <= v for v in filter_['values']
                        ])
                    )
                elif filter_['operator'] == 'equals':
                    q = q.filter(
                        or_(*[
                            filter_attr == v for v in filter_['values']
                        ])
                    )
                else:
                    logger.warn(
                        f'Ignoring invalid operator : {filter_["operator"]}'
                    )
            elif isinstance(field_type, Boolean):
                boolean_values = {
                    'true': True,
                    'false': False,
                    'null': None,
                }
                filter_['values'] = [
                    boolean_values[v] for v in filter_['values']
                    if v and v in boolean_values
                ]

                if not filter_['values']:
                    logger.info(f'Invalid filter value : {filter_["values"]}')
                    continue

                q = q.filter(
                    or_(*[
                        (filter_attr == v for v in filter_['values']),
                    ])
                )
            else:
                logger.warn(f'Invalid column type : {filter_["key"]}')

        return q

    # NOTE: Doesn't do any joins
    @classmethod
    def get_one(cls, id_or_token):
        """
        Returns the object from the database based on whether the
        filter is the id or the token. Returns None if the object
        is not found.
        """

        # id_or_token contains the id
        if type(id_or_token) == int:
            obj = cls.query.get(id_or_token)

        # id_or_token contains the token
        elif type(id_or_token) == str:
            obj = cls.query.filter_by(token=id_or_token).first()

        else:
            obj = None

        return obj if obj and obj.is_deleted == False else None

    # NOTE: Doesn't do any joins
    @classmethod
    def filter_objects_by_keywords(cls, filters={}, first_one=False):
        filters['is_deleted'] = False
        try:
            if first_one:
                objects = cls.query.filter_by(**filters).first()
            else:
                objects = cls.query.filter_by(**filters).all()
        except Exception as e:
            logger.info(f'An exception was raised, while filtering objects by keyword')
            logger.debug(e)
            objects = None if first_one else []

        return objects

    # NOTE: Doesn't do any joins
    @classmethod
    def filter_objects_by_list_values(cls, column_, values=[]):
        if not column_:
            logger.info(f'Not a valid value for column')
            return None

        try:
            objects = cls.query.filter(
                cls.is_deleted == False,
                column_.in_(values)
            ).all()
        except Exception as e:
            logger.info(f'An exception was raised, while filtering objects by list values')
            logger.debug(e)
            objects = []

        return objects

    # NOTE: Doesn't do any joins
    @classmethod
    def get_all(cls):
        """
        Returns all the objects from the database.
        """

        return cls.query.filter_by(is_deleted=False).all()

    # TODO: Accept multiple statuses
    @classmethod
    def get_all_objects(
        cls, params={}, outerjoins=[], filterable_and_sortable_fields={},
    ):
        q = cls.query.filter(cls.is_deleted == False).add_entity(cls)

        # Do all necessary outerjoins
        # Joins in here must be of relation of 1 * 1
        for each_join in outerjoins:
            if len(each_join) == 3:
                q = (
                    q.outerjoin(
                        each_join[0],
                        and_(
                            each_join[1] == each_join[2],
                            each_join[0].is_deleted == False
                        )
                    ).add_entity(each_join[0])
                )
            if len(each_join) == 4:
                q = (
                    q.outerjoin(
                        each_join[0],
                        each_join[1] == each_join[2]
                    )
                )

        # Do any custom filtering
        q = cls.add_filters_to_query(
            q,
            params,
            filterable_and_sortable_fields
        )

        # Add ordering to query
        q = cls.add_ordering_to_query(
            q,
            filterable_and_sortable_fields,
            reverse=params.get('reverse', 'false'),
            order_by=params.get('order_by'),
        )

        return q

    # TODO: Accept multiple statuses
    @classmethod
    def get_all_objects_details(cls, joins=[], filters_map={}, status='active', pagination={}):
        """
        Pass status=None if you don't want the status filter to be
        applied.
        """

        # Do the status filtering
        if status is None:
            q = cls.query
        else:
            q = cls.query.filter(cls.status==status)

        # Do any custom filtering
        q = cls.add_filters_to_query(q, filters_map, [])

        # Do all necessary joins
        for join in joins:
            q = (
                q.outerjoin(join[0], getattr(cls, join[1]) == join[0].id_)
                .add_entity(join[0])
            )

        # Do the default ordering (using the `id` field)
        q = q.order_by(
            cls.id_,
        )

        # Get the total retrieved results
        count = q.count()

        # Get paginated_query
        (q, page, page_size) = cls.add_pagination_to_query(
            q=q,
            params={
                'page': pagination.get('page'),
                'page_size': pagination.get('page_size'),
            },
        )

        # Fetch the results
        results = q.all()

        objects_details = []
        for result in results:
            # If not joined, `result` represents the object else,
            # need to get the details via the attribute in the
            # result object
            if len(joins) > 0:
                details = getattr(result, cls.__name__).get_details()
            else:
                details = result.get_details()

            for join in joins:
                details[join[2]] = getattr(result, join[0].__name__).get_details()
            objects_details.append(details)

        # If the `with_summary` param is set, return the data with the
        # pagination details
        if pagination.get('with_summary'):
            return (objects_details, count)

        return objects_details

    @staticmethod
    def add_ordering_to_query(q, allowed_fields, order_by=None, reverse=False):
        """
        Function to add sorting to the given query

        :param q str: Constructed query
        :param sortable_fields dict: Map of fields allowed for sorting
        :param order_by str: Order by field
        :param reverse bool: Flag to decide whether to sort ascending or descending

        :return str: Constructed query
        """

        try:
            if reverse.lower() == 'true':
                reverse = True
            else:
                reverse = False
        except (TypeError, ValueError, AttributeError):
            reverse = False

        if order_by:
            if order_by in allowed_fields:
                logger.info(f'Order by field : {order_by}')
                param = allowed_fields[order_by]

                if reverse:
                    param = desc(param)

                q = q.order_by(param)
            else:
                logger.info(f'Invalid value for order by : {order_by}')

        return q

    @staticmethod
    def add_pagination_to_query(q, params):
        """
        This function is to add pagination related clauses to the
        given query.

        :param q str: Constructed query
        :param page int: Page number
        :param page_size int: Page size

        :return str: Constructed query
        """

        # Print the query
        print('query :', str(q.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )))
        logger.info(f'Number of records found : {q.count()}')

        if params.get('page') and params['page'].isdigit():
            page = int(params['page']) if int(params['page']) >= 1 else 0
        else:
            page = 0

        if params.get('page_size') and params['page_size'].isdigit():
            page_size = int(params['page_size']) if int(params['page_size']) >= 1 else 100
        else:
            page_size = 100

        # If page is 0, do not apply pagination
        if not page:
            return (q, page, page_size)

        # If page is valid, do pagination.
        q = (
            q.limit(page_size)
            .offset((page-1) * page_size)
        )

        return (q, page, page_size)

    @classmethod
    def return_with_summary(cls, objects=[], page=1, page_size=100, count=0):
        if page:
            total_pages = int(math.ceil(count/page_size))
            # Current page, standard page size, total pages
            pagination = (page, page_size, total_pages)
        else:
            pagination = None

        return (objects, pagination, (count,))

    # NOTE: This doesn't do any joins
    def get_details(self):
        base_details = self._get_base_details()
        main_details = self.main_details()

        return {**base_details, **main_details}

    def main_details(self):
        main_details = {}
        for field in self.readable_fields:
            try:
                getattr(self, field)
                field_type = type(self).__table__.c[field].type
            except Exception:
                logger.info(f'{type(self).__name__} Model has Invalid key in readable fields : {field}')
                continue
            if isinstance(field_type, DateTime):
                main_details[field] = serialize_datetime(getattr(self, field), datetime_format)
            elif isinstance(field_type, Date):
                main_details[field] = serialize_datetime(getattr(self, field), date_format)
            elif isinstance(field_type, Time):
                main_details[field] = serialize_datetime(getattr(self, field), time_format)
            elif isinstance(field_type, Numeric):
                main_details[field] = float(getattr(self, field)) if getattr(self, field) else None
            else:
                main_details[field] = getattr(self, field)

        return main_details


    def update(self, data):
        """
        This function directly updates all the elements in the `data`
        dictionary by copying their values into the corresponding
        object attribute with the same key name. All validations have
        to be take care of properly beforehand.
        """

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.info(f'{type(self).__name__} Model has no attribute : {key}')

        self.last_updated_at = serialize_datetime(datetime.datetime.now(), datetime_with_microseconds_format)
        if request and request.user and request.user.id_:
            self.id_last_updated_user = request.user.id_

        db.session.flush()

        base_details = self._get_base_details()
        return {**base_details, **data}

    def soft_delete(self):
        """
        This function sets the status of an object (row) to `deleted`
        and sets the value of the `deleted_at` to the current time.
        This function does not commit the changes to the database,
        that has to be taken care of in the actions layer.

        Only currently `active` objects can be deleted.
        """

        self.is_deleted = True
        self.deleted_data = self.get_details()
        self.token = None
        self.deleted_at = serialize_datetime(datetime.datetime.now(), datetime_with_microseconds_format)

        if request and request.user and request.user.id_:
            self.id_deleted_user = request.user.id_

        db.session.flush()

        return self

