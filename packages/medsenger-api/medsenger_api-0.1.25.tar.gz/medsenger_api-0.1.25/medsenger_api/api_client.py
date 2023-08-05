from .grpc_client import RecordsClient
from .rest_client import RestApiClient


class AgentApiClient:
    def __init__(self, api_key, host="https://medsenger.ru", agent_id=None, debug=False, use_grpc=False):
        self.rest_client = RestApiClient(api_key, host, agent_id, debug)
        self.grpc_client = None
        self.user_cache = {}
        self.categories_cache = {}

        if use_grpc:
            self.grpc_client = RecordsClient()

    def get_categories(self):
        if not self.grpc_client:
            return self.rest_client.get_categories()
        else:
            categories = self.grpc_client.get_categories()

            for category in categories:
                self.categories_cache[category['name']] = category

            return categories

    def get_available_categories(self, contract_id):
        if not self.grpc_client:
            return self.rest_client.get_available_categories(contract_id)
        else:
            if contract_id not in self.user_cache:
                self.get_patient_info(contract_id)

            if contract_id in self.user_cache:
                return self.grpc_client.get_categories_for_user(self.user_cache[contract_id])

            return []

    def get_patient_info(self, contract_id):
        result = self.rest_client.get_patient_info(contract_id)

        if result.get('id'):
            self.user_cache[contract_id] = result.get('id')

        return result

    def get_clinics_info(self):
        return self.rest_client.get_clinics_info()

    def get_records(self, contract_id, category_name=None, time_from=None, time_to=None, limit=None, offset=None,
                    group=False, return_count=False, inner_list=False):

        if not self.grpc_client:
            return self.rest_client.get_records(contract_id, category_name, time_from, time_to, limit, offset, group,
                                                return_count, inner_list)
        else:
            if contract_id not in self.user_cache:
                self.get_patient_info(contract_id)

            if return_count:
                method = self.grpc_client.count_records
            else:
                method = self.grpc_client.get_records

            return method(self.user_cache[contract_id], category_name, time_from, time_to, offset, limit, group, inner_list)

    def get_record_by_id(self, contract_id, record_id):
        if not self.grpc_client:
            return self.rest_client.get_record_by_id(contract_id, record_id)
        else:
            return self.grpc_client.get_record_by_id(record_id)

    def add_hooks(self, contract_id, names):
        return self.rest_client.add_hooks(contract_id, names)

    def remove_hooks(self, contract_id, names):
        return self.rest_client.remove_hooks(contract_id, names)

    def send_addition(self, contract_id, record_id, addition):
        return self.rest_client.send_addition(contract_id, record_id, addition)

    def add_record(self, contract_id, category_name, value, record_time=None, params=None, files=None, return_id=False):
        return self.rest_client.add_record(contract_id, category_name, value, record_time, params, files, return_id)

    def add_records(self, contract_id, values, record_time=None, params={}, return_id=False):
        return self.rest_client.add_records(contract_id, values, record_time, params, return_id)

    def send_message(self, contract_id, text, action_link=None, action_name=None, action_onetime=True,
                     only_doctor=False,
                     only_patient=False, action_deadline=None, is_urgent=False, need_answer=False,
                     attachments=None, action_big=True, send_from=None, forward_to_doctor=True, action_type='action'):
        return self.rest_client.send_message(contract_id, text, action_link, action_name, action_onetime,
                                             only_doctor,
                                             only_patient, action_deadline, is_urgent, need_answer,
                                             attachments, action_big, send_from, forward_to_doctor, action_type)

    def finish_task(self, contract_id, task_id):
        return self.rest_client.finish_task(contract_id, task_id)

    def delete_task(self, contract_id, task_id):
        return self.rest_client.delete_task(contract_id, task_id)

    def add_task(self, contract_id, text, target_number=1, date=None, important=False, action_link=None):
        return self.rest_client.add_task(contract_id, text, target_number, date, important, action_link)

    def request_payment(self, inv_id, amount, title):
        return self.rest_client.request_payment(inv_id, amount, title)

    def send_order(self, contract_id, order, receiver_id=None, params=None):
        return self.rest_client.send_order(contract_id, order, receiver_id, params)

    def get_agent_token(self, contract_id):
        return self.rest_client.get_agent_token(contract_id)

    def download_file(self, *args, **kwargs):
        return self.get_file(*args, **kwargs)

    def download_attachment(self, *args, **kwargs):
        return self.get_attachment(*args, **kwargs)

    def download_image(self, *args, **kwargs):
        return self.get_image(*args, **kwargs)

    def get_file(self, contract_id, file_id):
        return self.rest_client.get_file(contract_id, file_id)

    def get_attachment(self, attachment_id):
        return self.rest_client.get_attachment(attachment_id)

    def get_image(self, image_id, size):
        return self.rest_client.get_image(image_id, size)

    def update_cache(self, contract_id):
        return self.rest_client.update_cache(contract_id)

    def set_info_materials(self, contract_id, materials):
        return self.rest_client.set_info_materials(contract_id, materials)

    def ajax_url(self, action, contract_id, agent_token):
        # TODO fix
        return self.host.replace('8001',
                                 '8000') + "/api/client/agents/{agent_id}/?action={action}&contract_id={contract_id}&agent_token={agent_token}".format(
            agent_id=self.agent_id, action=action, contract_id=contract_id, agent_token=agent_token
        )


