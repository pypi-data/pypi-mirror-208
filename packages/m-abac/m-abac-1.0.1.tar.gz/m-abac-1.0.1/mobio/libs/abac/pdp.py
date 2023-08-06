"""
    Policy decision point implementation
"""

from copy import deepcopy

from .call_api import CallAPI
from .policy import PolicySchema, AccessType
from .policy.utils import Utils
from .result_access import ResultAccess


class PolicyDecisionPoint(object):
    """
        Policy decision point
    """

    class AccountType:
        SYSTEM = "system"
        NORMAL = "normal"

    class AccessLevel:
        LIST = "list"
        READ = "read"
        ADD = "add"
        EDIT = "edit"
        DELETE = "delete"
        OTHER = "other"

    class AuthorizationType:
        BASIC = 'basic'
        BEARER = 'bearer'
        DIGEST = 'digest'

    def __init__(self,
                 merchant_id: str = None, resource: str = None, action: str = None, account_id: str = None,
                 user_info: dict = None, data_before: dict = None, data_after: dict = None, environment: dict = None,
                 account_type=AccountType.NORMAL):
        if not resource:
            raise ValueError("resource required")
        if not action:
            raise ValueError("action required")
        if not merchant_id or not account_id:
            auth_type, json_token = Utils.get_info_jwt()
            if auth_type == self.AuthorizationType.BEARER:
                merchant_id = json_token.get("merchant_id")
                account_id = json_token.get("account_id")
            else:
                account_type = self.AccountType.SYSTEM
        if account_type == PolicyDecisionPoint.AccountType.NORMAL:
            if not merchant_id:
                raise ValueError("merchant_id required")
            if not account_id:
                raise ValueError("account normal account_id required")
            if not user_info:
                user_info = CallAPI.admin_get_account_info(merchant_id, account_id)

        self.account_type = account_type
        self.merchant_id = merchant_id
        self.account_id = account_id
        self.resource = resource
        self.action = action
        self.request_access = {}
        self.result_access = ResultAccess()
        self.request_access.update({
            "user": user_info if user_info else {},
            "env": self.get_info_environment(environment),
            self.resource: data_before if data_before else {}
        })
        self.data_after = data_after if data_after else {}
        self.data_before = data_before if data_before else {}
        self.access_level = ""
        self.service = ""

    def get_policy_statement_for_target(self):
        return CallAPI.admin_get_list_statement(self.merchant_id, self.account_id,
                                                self.resource, self.action, self.service)

    def is_allowed(self):
        """
            Check if authorization request is allowed

            :param request: request object
            :return: True if authorized else False
        """
        try:
            if self.account_type == PolicyDecisionPoint.AccountType.SYSTEM:
                self.result_access.set_allow_access(True)
                return self.result_access
            action_info = CallAPI.admin_get_json_action(merchant_id=self.merchant_id)
            if not action_info:
                raise ValueError("action for merchant_id {} not found".format(self.merchant_id))
            if not action_info.get(self.action):
                raise ValueError("action {} not found".format(self.action))
            self.access_level = action_info.get(self.action, {}).get("access_level", "").lower()
            if not self.access_level:
                raise ValueError("access_level {} not valid".format(self.action))
            self.service = action_info.get(self.action, {}).get("service", "")
            if not self.service:
                raise ValueError("service {} not valid".format(self.service))

            list_statement = self.get_policy_statement_for_target()
            if list_statement:

                if self.access_level == PolicyDecisionPoint.AccessLevel.ADD:
                    self.data_after.update(self.data_before)
                statement_check_allow, statement_check_deny = self.get_statement_by_type(list_statement)
                if statement_check_deny:
                    if self.check_list_statement_is_deny(statement_check_deny):
                        self.result_access.set_allow_access(False)
                        return self.result_access
                if statement_check_allow:
                    self.result_access.set_allow_access(self.check_list_statement_is_allow(statement_check_allow))
                else:
                    self.result_access.set_allow_access(False)
            else:
                self.result_access.set_allow_access(False)
        except Exception as err:
            print("Exception: {}".format(err))
            self.result_access.set_allow_access(False)

        return self.result_access

    def get_info_environment(self, environment):
        if not environment:
            environment = Utils.get_info_from_header_request()
            if environment:
                if environment.get("env:user_agent"):
                    environment.update(Utils.parse_user_agent(environment.get("env:user_agent")))
        environment = environment if environment else {}
        environment.update({"env:current_time": Utils.get_date_utcnow()})
        return environment

    def get_value_from_variable(self, str_variable):
        variables = Utils.get_field_key_from_variable(str_variable)
        if variables:
            if len(variables) == 1 and Utils.check_field_is_variable(variables[0]):
                field_value = self.get_value_from_field(variables[0])
                return field_value
            for field_key in variables:
                field_value = self.get_value_from_field(field_key)
                if field_value is not None:
                    field_value = str(field_value)
                    str_variable = Utils.replace_variable_to_value(field_key, field_value, str_variable)
        return str_variable

    def get_value_from_field(self, field_key):
        resource_name, resource_key = Utils.split_delemiter_resource(field_key)
        if resource_name and resource_key:
            if self.request_access.get(resource_name) and isinstance(self.request_access.get(resource_name), dict):
                data_resource = self.request_access.get(resource_name)
                value = Utils.get_nested_value(data_resource, resource_key)
                return value
        return None

    def get_statement_by_type(self, list_statement: list):
        statement_check_allow, statement_check_deny = [], []
        for statement in list_statement:
            statement_copy = deepcopy(statement)
            fields = []
            if statement_copy.get("resource_field") and statement_copy.get("resource_field").get(self.resource):
                fields = statement_copy.get("resource_field").get(self.resource)
            if fields:
                statement_copy["fields"] = fields
            if self.access_level == PolicyDecisionPoint.AccessLevel.LIST:
                condition_check = []
                condition_filter = []
                for item_cond in statement_copy.get("condition"):
                    if item_cond.get("field").startswith("user") or item_cond.get("field").startswith("env"):
                        condition_check.append(item_cond)
                    else:
                        values = [self.get_value_from_variable(i) for i in item_cond.get("values")]
                        item_cond["values"] = values
                        condition_filter.append(item_cond)

                if statement_copy.get("effect") == AccessType.ALLOW_ACCESS:
                    # chỉ xử lý các điều kiện bộ lọc với effect allow
                    if condition_filter:
                        statement_copy["condition_filter"] = condition_filter
                    statement_check_allow.append({
                        **statement_copy,
                        "condition": condition_check
                    })
                else:
                    statement_check_deny.append({
                        **statement_copy,
                        "condition": condition_check
                    })

            elif self.access_level == PolicyDecisionPoint.AccessLevel.READ:
                if statement_copy.get("effect") == AccessType.ALLOW_ACCESS:
                    statement_check_allow.append(statement_copy)
                else:
                    statement_check_deny.append(statement_copy)

            else:
                if fields:
                    statement_copy["check_field"] = 1
                if statement_copy.get("effect") == AccessType.ALLOW_ACCESS:
                    statement_check_allow.append(statement_copy)
                else:
                    statement_check_deny.append(statement_copy)
        return statement_check_allow, statement_check_deny

    def check_list_statement_is_deny(self, list_statement: list):
        result_deny = False
        try:
            for statement in list_statement:
                statement["request_access"] = self.request_access
                policy_schema = PolicySchema().load(statement)
                if policy_schema.is_allowed():
                    if self.access_level == PolicyDecisionPoint.AccessLevel.READ:
                        # tìm tất cả các cấu hình ẩn hiện field nếu có
                        if statement.get("fields"):
                            self.result_access.add_display_config({
                                "effect": statement.get("effect"),
                                "fields": statement.get("fields"),
                            })
                            continue
                    else:
                        # nếu ko có field nào ở cấu hình policy nằm trong dữ liệu gửi lên thì cho qua
                        if statement.get("check_field") and statement.get("fields"):
                            if not Utils.field_in_body_request(statement.get("fields"), self.data_after):
                                continue
                    result_deny = True
                    break
        except Exception as err:
            print("check_list_statement_is_deny err: {}".format(err))
            result_deny = False
        return result_deny

    def check_list_statement_is_allow(self, list_statement: list):
        result_allow = False
        try:
            for statement in list_statement:
                statement["request_access"] = self.request_access
                policy_schema = PolicySchema().load(statement)
                if policy_schema.is_allowed():
                    result_allow = True
                    if self.access_level == PolicyDecisionPoint.AccessLevel.READ:
                        # tìm tất cả các cấu hình ẩn hiện field nếu có
                        if statement.get("fields"):
                            self.result_access.add_display_config({
                                "effect": statement.get("effect"),
                                "fields": statement.get("fields"),
                            })
                            continue
                    elif self.access_level == PolicyDecisionPoint.AccessLevel.LIST:
                        # tìm tất cả các điều kiện bộ lọc với action list
                        if statement.get("condition_filter"):
                            self.result_access.add_filter_config(
                                {"effect": statement.get("effect"),
                                 "condition": statement.get("condition_filter")})
                            continue
                    else:
                        # kiểm tra thông tin field dữ liệu gửi lên với cấu hình field trong policy,
                        # nếu field gửi lên ko nằm trong tập con của cấu hình field thì reject statement
                        if statement.get("check_field") and statement.get("fields"):
                            list_field_data_after = list(self.data_after.keys())
                            if not set(list_field_data_after).issubset(statement.get("fields")):
                                result_allow = False
                                continue
                        break

        except Exception as err:
            print("check_list_statement_is_allow err: {}".format(err))
            result_allow = False
        return result_allow
