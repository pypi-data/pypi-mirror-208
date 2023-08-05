import json
import time
import grpc
from .utils import *
from .protocol import records_pb2_grpc as pb2_grpc
from .protocol import records_pb2 as pb2


class RecordsClient(object):
    def __init__(self, debug=False, host=None):
        if not host:
            host = "medsenger.ru"

        self.host = host
        self.server_port = 50051
        self.__categories_by_id = {}
        self.__categories_by_name = {}
        self.__debug = debug

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port), options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024)
            ])

        # bind the client and the server
        self.stub = pb2_grpc.RecordsStub(self.channel)

        if self.__debug:
            print("Connected to GRPC")

    def __find_category_by_id(self, id):
        if not self.__categories_by_id or id not in self.__categories_by_id:
            print("Loading categories")
            self.get_categories()

        return self.__categories_by_id.get(id)

    def __find_category_by_name(self, name):
        if not self.__categories_by_name or name not in self.__categories_by_name:
            print("Loading categories")
            self.get_categories()

        return self.__categories_by_name.get(name)

    def __find_ids_for_categories(self, category_names):
        if not self.__categories_by_name:
            print("Loading categories")
            self.get_categories()

        return [self.__categories_by_name[name].id for name in category_names if name in self.__categories_by_name]

    def __present_category(self, category):
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "unit": category.unit,
            "type": category.type,
            "default_representation": category.default_representation,
            "is_legacy": category.is_legacy,
            "subcategory": category.subcategory if category.subcategory else None
        }

    def __present_file(self, file):
        return {
            "id": file.id,
            "name": file.name,
            "type": file.type,
        }

    def __convert_value(self, value, category):
        if category.type == 'integer':
            return int(float(value))
        if category.type == 'float':
            return float(value)
        return value

    def __present_record(self, record, with_category=False):
        category = self.__find_category_by_id(record.category_id)

        presentation = {
            "id": record.id,
            "value": self.__convert_value(record.value, category),
            "timestamp": record.created_at,
            "uploaded": record.updated_at,
            "source": {
                "id": record.source.id if record.source.id else None,
                "name": record.source.name
            },
            "group": record.group if record.group else None,
            "params": json.loads(record.params),
            "additions": json.loads(record.additions),
            "attached_files": [self.__present_file(file) for file in record.attached_files],
        }

        if with_category:
            presentation['category_info'] = self.__present_category(category)

        return presentation

    @safe
    def get_categories(self):
        request = pb2.Empty()
        result = self.stub.GetCategoryList(request)

        for category in result.categories:
            self.__categories_by_id[category.id] = category
            self.__categories_by_name[category.name] = category

        return [self.__present_category(category) for category in result.categories]

    @safe
    def get_categories_for_user(self, user_id):
        request = pb2.User(id=user_id)
        result = self.stub.GetCategoryListForUser(request)

        return [self.__present_category(category) for category in result.categories]

    @safe
    def get_record_by_id(self, record_id):
        request = pb2.RecordRequest(id=record_id)
        result = self.stub.GetRecordById(request)

        return [self.__present_record(record) for record in result]

    def __aggregate_records(self, method, user_id, category_name, from_timestamp=0, to_timestamp=int(time.time()),
                            offset=0,
                            limit=None, group=False, inner_list=False):
        full_list = not category_name or ',' in category_name or inner_list

        category_names = category_name.split(',')
        category_ids = self.__find_ids_for_categories(category_names)

        if category_names and not category_ids:
            return None

        request = pb2.RecordQuery(user_id=user_id, category_ids=category_ids, from_timestamp=from_timestamp,
                                  to_timestamp=to_timestamp, offset=offset, limit=limit, with_group=group)

        result = method(request)

        if full_list:
            result = [self.__present_record(record, with_category=True) for record in result.records]

            if not result:
                return None
        else:
            result = {
                "category": self.__present_category(self.__categories_by_name.get(category_name)),
                "values": [self.__present_record(record, with_category=False) for record in result.records]
            }

        return result

    @safe
    def get_records(self, user_id, category_name, from_timestamp=0, to_timestamp=int(time.time()), offset=0,
                    limit=None, group=False, inner_list=False):
        return self.__aggregate_records(self.stub.GetRecords, user_id, category_name, from_timestamp, to_timestamp,
                                        offset, limit, group, inner_list)

    @safe
    def count_records(self, user_id, category_name, from_timestamp=0, to_timestamp=int(time.time()), offset=0,
                      limit=None, group=False, inner_list=False):

        return self.__aggregate_records(self.stub.CountRecords, user_id, category_name, from_timestamp, to_timestamp,
                                        offset, limit, group, inner_list)
