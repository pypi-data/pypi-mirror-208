from mobio.libs.caching import LruCache
import os, requests


class StoreCacheType:
    LOCAL = 1
    REDIS = 2

class Cache:
    REDIS_URI = "{}?health_check_interval=30".format(os.environ.get("ADMIN_REDIS_URI", os.environ.get("REDIS_URI")))
    PREFIX = "m_abac"

lru_cache_redis = LruCache(
    store_type=StoreCacheType.REDIS,
    redis_uri=Cache.REDIS_URI,
    cache_prefix=Cache.PREFIX,
)

class Mobio:
    ADMIN_HOST = os.environ.get("ADMIN_HOST")
    MOBIO_TOKEN = "Basic {}".format(os.environ.get('YEK_REWOP', ''))



class APIRequest:
    TimeOut = 10
    ADMIN_GET_FULL_INFO_ACCOUNT = "{domain}/adm/api/v2.1/accounts/{account_id}/full-info"
    ADMIN_GET_LIST_ACTION_FOR_MERCHANT = "{domain}/adm/api/v2.1/policies/actions"
    ADMIN_GET_LIST_STATEMENT = "{domain}/adm/api/v2.1/statements"

class CallAPI:

    @lru_cache_redis.add()
    @staticmethod
    def admin_get_account_info(merchant_id, account_id):
        try:
            url = APIRequest.ADMIN_GET_FULL_INFO_ACCOUNT.format(domain=Mobio.ADMIN_HOST, account_id=account_id)
            authorization = Mobio.MOBIO_TOKEN
            data_res = requests.get(
                url,
                headers={
                    "Authorization": authorization,
                    "X-Merchant-ID": merchant_id,
                },
                timeout=APIRequest.TimeOut,
            )
            data = None
            if data_res.status_code == 200:
                if data_res.json().get("data"):
                    data = data_res.json().get("data")
            # print("admin_get_account_info: {}".format(data))
            return data
        except Exception as er:
            err_msg = "admin_get_account_info err: {}".format(er)
            print(err_msg)
            return {}

    @lru_cache_redis.add()
    @staticmethod
    def admin_get_json_action(merchant_id):
        try:
            url = APIRequest.ADMIN_GET_LIST_ACTION_FOR_MERCHANT.format(domain=Mobio.ADMIN_HOST)
            authorization = Mobio.MOBIO_TOKEN
            data_res = requests.get(
                url,
                headers={
                    "Authorization": authorization,
                    "X-Merchant-ID": merchant_id,
                },
                timeout=APIRequest.TimeOut,
                params={"page": "-1"}
            )
            data = {}
            if data_res.status_code == 200:
                if data_res.json().get("data"):
                    list_data = data_res.json().get("data")
                    for i in list_data:
                        data[i.get("key")] = i
            # print("admin_get_json_action: {}".format(data))
            return data
        except Exception as er:
            err_msg = "admin_get_json_action err: {}".format(er)
            print(err_msg)
            return {}

    @staticmethod
    @lru_cache_redis.add(expiration=900)
    def admin_get_list_statement(merchant_id, account_id, resource, action, service):
        """
        :param merchant_id:
        :param account_id:
        :param resource:
        :param action:
        :return: [{
            "effect": "allow",
            "action": [
                "DealViewReport"
            ],
            "resource": [
                "sale:deal"
            ],
            "condition": [
                {
                    "operator": "StringEquals",
                    "field": "user:block",
                    "values": [
                        "KHDN"
                    ],
                    "qualifier": "ForAnyValue",
                    "if_exists": False,
                    "ignore_case": False
                },
                {
                    "operator": "StringEquals",
                    "field": "deal:block",
                    "values": [
                        "${user:block}"
                    ],
                    "qualifier": "ForAnyValue",
                    "if_exists": False,
                    "ignore_case": False
                },
                {
                    "operator": "StringStartsWith",
                    "field": "deal:scope_code",
                    "values": [
                        "${user:scope_code}"
                    ],
                    "qualifier": "ForAnyValue",
                    "if_exists": False,
                    "ignore_case": False
                }
            ]
        }]
        """
        try:
            url = APIRequest.ADMIN_GET_LIST_STATEMENT.format(domain=Mobio.ADMIN_HOST)
            authorization = Mobio.MOBIO_TOKEN
            body_req = {
                'user_ids': [account_id],
                'team_ids': [],
                'merchant_ids': [merchant_id],
                'resources': [service + ":" + resource],
                'actions': [action]
            }
            data_res = requests.post(
                url,
                json=body_req,
                headers={
                    "Authorization": authorization,
                    "X-Merchant-ID": merchant_id,
                },
                timeout=APIRequest.TimeOut,
            )
            data = None
            if data_res.status_code == 200:
                if data_res.json().get("statements"):
                    data = data_res.json().get("statements")
            # print("admin_get_list_statement: {}".format(data))
            return data

            # return [
            #     {
            #         "effect": "allow",
            #         "action": [
            #             "ListFromSale"
            #         ],
            #         "resource": [
            #             "sale:deal"
            #         ],
            #         "condition": [
            #             {
            #                 "operator": "StringEquals",
            #                 "field": "deal:block",
            #                 "values": [
            #                     "${user:block}"
            #                 ],
            #                 "qualifier": "ForAnyValue",
            #                 "if_exists": False,
            #                 "ignore_case": False
            #             },
            #             {
            #                 "operator": "StringStartsWith",
            #                 "field": "deal:scope_code",
            #                 "values": [
            #                     "${user:scope_code}"
            #                 ],
            #                 "qualifier": "ForAnyValue",
            #                 "if_exists": False,
            #                 "ignore_case": False
            #             }
            #         ]
            #     },
            #             {
            #                 "effect": "allow",
            #                 "action": [
            #                     "ListFromSale"
            #                 ],
            #                 "resource": [
            #                     "sale:deal"
            #                 ],
            #                 "condition": [
            #                     {
            #                         "operator": "StringStartsWith",
            #                         "field": "deal:scope_code",
            #                         "values": [
            #                             "3#7", "3#8", "3#9"
            #                         ],
            #                         "qualifier": "ForAnyValue",
            #                         "if_exists": False,
            #                         "ignore_case": False
            #                     },
            #                     {
            #                         "operator": "StringEquals",
            #                         "field": "user:scope_code",
            #                         "values": [
            #                             "3#6"
            #                         ],
            #                         "qualifier": "ForAnyValue",
            #                         "if_exists": False,
            #                         "ignore_case": False
            #                     }
            #                 ]
            #             }
            # ]

        except Exception as er:
            err_msg = "admin_get_list_statement err: {}".format(er)
            print(err_msg)
            return []
