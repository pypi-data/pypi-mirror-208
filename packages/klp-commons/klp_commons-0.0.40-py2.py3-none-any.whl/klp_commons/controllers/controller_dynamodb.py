from logging import getLogger
from fastapi.responses import JSONResponse
from os import getenv
from boto3 import resource
# User CRUD
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from klp_commons.log.structuredMessage import StructuredMessage
fmt = StructuredMessage
message = 'dynamoDBController'


class ControllerDynamoDB:
    """
    comment
    """
    def __init__(self):

        self.dyn_resource = None
        self.table_name_conection = None
        self.active_conection_table = None
        self.error = False
        self.aws_access_key_uid = None
        self.aws_secret_access_key = None
        self.region_name = None
        self.dyn_resource = None
        self.AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_DEFAULT_REGION = getenv("AWS_DEFAULT_REGION")
        self.prefix = getenv("NODE_ENV") + '_'

        # module_name.TopicKafka_name
        self.logger = getLogger(message)

        # Init ()
        # MicroService_name.TopicKafka_name.module_name.MainClass_name
        self.logger.info("donde init method of ControllerDynamoDB ")
    
    def get_all_items_table(self):

        response = self.active_conection_table.scan(FilterExpression='attribute_not_exists(details.cat_uid_def_algo) and attribute_exists(info.income_source_uid)')
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = self.active_conection_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])

        return data

    def get_conection(self, table_name: str) -> None:

        self.logger.info("call get_conection() method of ControllerDynamoDB ")

        try:
            self.table_name_conection = self.prefix + table_name

            if self.dyn_resource is None:
                self.dyn_resource = resource(
                    "dynamodb",
                    aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                    region_name=self.AWS_DEFAULT_REGION)

            self.active_conection_table = self.dyn_resource.Table(
                self.table_name_conection
            )
        except ClientError as err:
            self.logger.error(
                "Couldn't conected to table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            self.logger.error(
                fmt("table_name ", json={'user_uid': table_name}))

        self.logger.info("done get_conection() method of ControllerDynamoDB ")

    def get_update_params(self, body, key_sorted, key_partition = 'user_uid'):
        """Given a dictionary we generate an update expression and a dict of values
        to update a dynamodb table.

        Params:
            body (dict): Parameters to use for formatting.

        Returns:
            update expression, dict of values.
        """
        keys_search = dict()
        update_expression = ["set "]
        update_values = dict()

        keys_search[key_partition] = body[key_partition]
        keys_search[key_sorted] = body[key_sorted]

        del body[key_partition]
        del body[key_sorted]
        
        for key, val in body.items():
            update_expression.append(f" {key} = :{key},")
            update_values[f":{key}"] = val

        return keys_search,"".join(update_expression)[:-1], update_values

    def update(self, body, key_sorted, key_partition = 'user_uid'):
        """
        
        
        """
        s, a, v = self.get_update_params(body, key_sorted, key_partition )
        
        response = self.active_conection_table.update_item(
            Key = s,
            UpdateExpression = a,
            ExpressionAttributeValues = dict(v)
            )
        return response

    def insert_hash_in_userTable(self, transaction: dict) -> dict:
        """
        transaction =  {
            "user_uid":"soyYai3q09Anhi1vzxJhgmqOMTLS5eXiKOWbTWsA",
            "description_embedding":"0101510102030101010101010101010101001",
            "data":
            {
                'subcat_uid_def_usr':"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
                'subcat_uid_def_algo':"U7CnAFNoegobBd4wvRu948iiqzCZ7glvIkB6PIxM",
                'subcat_uids_def_collect':{},
                'category_uid':"QsizWDPMOedPEzA5pvLaDEcxGqjHpInp1rOODZ9W"
            }
            }
        """

        try:
            self.r_query_dydb = self.active_conection_table.put_item(
                Item={
                    "user_uid": transaction["user_uid"],
                    "description_embedding": transaction["description_embedding"],
                    "language_code": transaction["language_code"],
                    "data": transaction["detail"],
                },
                ReturnConsumedCapacity="TOTAL"
                )

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(fmt("transaction : ", json=transaction))

    def insert_batch_hash_in_userTable(self, items_list: list) -> dict:

        try:
            with self.active_conection_table.batch_writer(overwrite_by_pkeys=["user_uid", "description_embedding"]) as writer:
                for item in items_list:
                    writer.put_item(Item=item)
            self.logger.info("Loaded data into table %s.",
                             self.active_conection_table.name)
        except ClientError:
            self.logger.exception(
                "Couldn't load data into table %s.", self.active_conection_table.name)
            Exception('error  insert_batch_hash_in_userTable DynamoDB!')

    def get_all_info_in_userTable(  self, 
                                partition_key_value: str
                                ) -> None:
        """
        partition_key_name: user_uid

        sort_key_name: hash resultaante de transformar la descripción (texto) de un atransacción
        (aka description_enbedding)
        """

        self.partition_key_name = "user_uid"
        try:

            self.r_query_dydb = self.active_conection_table.query(
                KeyConditionExpression=Key(self.partition_key_name).eq(
                    partition_key_value
                )
            )

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(fmt("user iud ", json={
                'partition_key_value': partition_key_value}))

    def get_info_in_userTable(  self, 
                                partition_key_value: str,
                                sort_key_value: str
                            ) -> None:
        """
        partition_key_name: hash del user (user_ui)

        sort_key_name: hash resultaante de transformar la descripción (texto) de un atransacción
        (aka description_enbedding)

        Response :
        {'Items': [{'language_code': 'es-MX',
        'details': {'merch_name': 'Obrien-Miller',
            'subcat_uid_def_collect': '',
            'subcat_uid_def_algo': 'WIIxmmfsivKM4vBGbZCf3YcAAHFYDV48S8py15Np',
            'nickname': 'gimnasio',
            'cat_uid': 'csI1MhFMuv7Gp4URVyiCXWSIzSSXOzUN8MIWHVtP',
            'subcat_uid_def_usr': '',
            'stem': 'gimnasio taco'},
        'user_uid': '9ZM5VDfrDJ9NjE6nvYrbd04qvgdSgS04rQbvAylI',
        'description_embedding': '0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000'}],
        'Count': 1,
        'ScannedCount': 1,
        'ResponseMetadata': {'RequestId': '0QIC45SH70CL8FAS1PJ3EHHK17VV4KQNSO5AEMVJF66Q9ASUAAJG',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {'server': 'Server',
        'date': 'Wed, 10 Aug 2022 05:04:16 GMT',
        'content-type': 'application/x-amz-json-1.0',
        'content-length': '724',
        'connection': 'keep-alive',
        'x-amzn-requestid': '0QIC45SH70CL8FAS1PJ3EHHK17VV4KQNSO5AEMVJF66Q9ASUAAJG',
        'x-amz-crc32': '1412129221'},
        'RetryAttempts': 0}}
        """

        self.partition_key_name = "user_uid"
        self.sort_key_name = "description_embedding"
        try:

            self.r_query_dydb = self.active_conection_table.query(
                KeyConditionExpression=Key(self.partition_key_name).eq(
                    partition_key_value
                )
                & Key(self.sort_key_name).eq(sort_key_value),
            )

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(fmt("user iud ", json={
                'partition_key_value': partition_key_value,
                "sort_key_value": sort_key_value}))

    def insert_popular_categories_in_multicategoryTable(
            self, transaction: dict) -> dict:
        """
        send in this format:

        transaction =  {
            "description_embedding":"0101510102030101010101010101010101001",
            "popular_subcategories": {1:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            2:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            3:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"

            },
            "categories": {1:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            2:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            3:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"

            }


            store format in AWS DynamoDB:

                        {
              "description_embedding": {
                "S": "0101510102030101010101010101010101001"
              },
              "categories": {
                "M": {
                  "1": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "2": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "3": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  }
                }
              },
              "popular_subcategories": {
                "M": {
                  "1": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "2": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "3": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  }
                }
              }
            }

        """
        self.logger.info(
            "call insert_popular_categories_for_transaction() method of ControllerDynamoDB ")

        try:
            self.r_query_dydb = self.active_conection_table.put_item(
                Item={
                    "description_embedding": transaction["description_embedding"],
                    "popular_subcategories": transaction["popular_subcategories"],
                    "categories": transaction["categories"],
                })
        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500)
            self.logger.error(fmt("transaction :", json=transaction))

        self.logger.info(
            "done insert_popular_categories_in_multicategoryTable() method of ControllerDynamoDB ")

    def insert_bacth_in_multicategoryTable(self, items_list: list) -> dict:
        """
        send in this format:

        transaction =  {
            "description_embedding":"0101510102030101010101010101010101001",
            "popular_subcategories": {1:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            2:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            3:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"

            },
            "categories": {1:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            2:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz",
            3:"JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"}

            store format in AWS DynamoDB:

                        {
              "description_embedding": {
                "S": "0101510102030101010101010101010101001"
              },
              "categories": {
                "M": {
                  "1": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "2": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "3": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  }
                }
              },
              "popular_subcategories": {
                "M": {
                  "1": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "2": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  },
                  "3": {
                    "S": "JxdCwO7AA5iuQUeuc1M2o2XQZJsIq0iaucoai9Kz"
                  }
                }
              }
            }

        """
        self.logger.info(
            "call insert_popular_categories_for_transaction() method of ControllerDynamoDB ")


        try:
            with self.active_conection_table.batch_writer(overwrite_by_pkeys=["user_uid", "description_embedding"]) as writer:
                for item in items_list:
                    writer.put_item(Item=item)

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500)
            self.logger.error(fmt("transaction :", json=items_list))


        self.logger.info(
            "donde insert_bacth_in_multicategoryTable() method of ControllerDynamoDB ")

    def get_popular_categories_in_multicategoryTable(
            self, partition_key_value: str) -> None:
        """
        partiton_key_name: hash de la descripción de un atransacción (description_enbedding)
        """

        self.logger.info(
            "call get_popular_categories_in_transactionTable() method of ControllerDynamoDB ")

        self.partition_key_name = "description_embedding"
        self.column = "popular_subcategories"
        try:

            self.r_query_dydb = self.active_conection_table.query(
                KeyConditionExpression=Key(self.partition_key_name).eq(
                    partition_key_value
                ),
                ProjectionExpression=self.column,
            )

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(
                fmt("user iud ", json={'partition_key_value': partition_key_value}))

        self.logger.info(
            "done get_popular_categories_in_multicategoryTable() method of ControllerDynamoDB ")

    def insert_info_in_transactionTable(self, transaction: dict) -> dict:
        """
        transaction =  {
            "user_uid":"soyYai3q09Anhi1vzxJhgmqOMTLS5eXiKOWbTWsA",
            "transaction_uid":"0101510102030101010101010101010101001",
            "hash": "0101510102030101010101010101010101001"
                        }
        """
        self.logger.info(
            "call insert_hash_in_userTable_user() method of ControllerDynamoDB ")
        try:
            self.r_query_dydb = self.active_conection_table.put_item(
                Item={
                    "user_uid": transaction["user_uid"],
                    "transaction_uid": transaction["transaction_uid"],
                    "hash": transaction["hash"],
                    "nickname": transaction["nickname"],
                },
                ReturnConsumedCapacity="TOTAL"
            )

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(fmt("user iud ", json=transaction))


        self.logger.info(
            "done insert_info_in_transactionTable method of ControllerDynamoDB ")

    def insert_bacth_in_transactionTable(self, items_list: list) -> dict:
        """
        transaction =  {
            "user_uid":"soyYai3q09Anhi1vzxJhgmqOMTLS5eXiKOWbTWsA",
            "transaction_uid":"0101510102030101010101010101010101001",
            "hash": "0101510102030101010101010101010101001"
            "nickname": ""
                        }
        """
        self.logger.info(
            "call insert_bacth_in_transactionTable method of ControllerDynamoDB ")
        try:
            with self.active_conection_table.batch_writer(overwrite_by_pkeys=["user_uid", "transaction_uid"]) as writer:
                for item in items_list:
                    writer.put_item(Item=item)

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(fmt("user iud ", json=items_list))


        self.logger.info(
            "done insert_bacth_in_transactionTable() method of ControllerDynamoDB ")

    def get_all_hashes_in_transactionTable(
        self,
        partition_key_value: str,
        hash:str
    ) -> None:
        """
        : hash del user (user_uid)

        """
        self.logger.info(
            "call get_hash_transaction_table() method of ControllerDynamoDB ")

        self.partition_key_name = "user_uid"

        try:

            self.r_query_dydb = self.active_conection_table.query(
                KeyConditionExpression=Key(self.partition_key_name).eq(partition_key_value),
                FilterExpression=Attr('hash').eq(hash)

                )

        except ClientError as e:
            self.r_query_dydb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(fmt("user iud ", json={
                'partition_key_value': partition_key_value,'content':self.r_query_dydb}))

        self.logger.info(
            "done get_all_hashes_in_transactionTable method of ControllerDynamoDB ")

    def get_hash_in_transactionTable(
        self,
        partition_key_value: str,
        sort_key_value: str,
    ) -> None:
        """
        : hash del user (user_uid)

        : hash resultaante de transformar la descripción (texto) de un atransacción
        (aka description_enbedding)

        """
        self.logger.info(
            "call get_hash_transaction_table() method of ControllerDynamoDB ")

        self.partition_key_name = "user_uid"
        self.sort_key_name = "transaction_uid"

        try:

            self.r_query_dydb = self.active_conection_table.query(
                KeyConditionExpression=Key(self.partition_key_name).eq(
                    partition_key_value
                )
                & Key(self.sort_key_name).eq(sort_key_value),
                # ProjectionExpression = self.hash
            )

        except ClientError as e:
            self.r_query_dydb = e.response["Error"]

            self.logger.error(fmt("error:  user iud ", json={
                'partition_key_value': partition_key_value, 'sort_key_value': sort_key_value,"error":e.response["Error"]}))

        self.logger.info(
            "done get_hash_in_transactionTable method of ControllerDynamoDB ")

    def created_info_in_userTable(self, info: dict = None):
        """
        Updates user table.
        """
        
        self.logger.info(
            "call created_info_in_userTable() method of ControllerDynamoDB ")

        try:
            self.r_query_dydb = self.active_conection_table.update_item(
                Key={
                    "user_uid": info["user_uid"],
                    "description_embedding": info["description_embedding"],
                },
                UpdateExpression =  "set validated=:a,\
                                        approved_nickname=:b,\
                                        approved_cat=:c,  \
                                        approved_subcat=:d, \
                                        #det.subcat_uid_def_usr=:l,\
                                        #det.subcat_uid_def_algo=:m,\
                                        #det.nickname_algo=:n,\
                                        #det.nickname_usr=:o,\
                                        #det.cat_uid_def_algo=:p,\
                                        #det.cat_uid_def_usr=:q,\
                                        #det.updated_at=:r\
                                        ",
                                        
                ExpressionAttributeNames={
                    "#det": "details"},
                ExpressionAttributeValues={

                    ":a": info['validated'],
                    ":b": info['approved_nickname'],
                    ":c": info['approved_cat'],
                    ":d": info['approved_subcat'],

                    ":l": info['details']['subcat_uid_def_usr'],
                    ":m": info['details']['subcat_uid_def_algo'],
                    ":n": info['details']['nickname_algo'],
                    ":o": info['details']['nickname_usr'],
                    ":p": info['details']['cat_uid_def_algo'],
                    ":q": info['details']['cat_uid_def_usr'],
                    ":r": info['details']["updated_at"],
                },
                ReturnValues="UPDATED_NEW",
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "ValidationException":
                # Creating new top level attribute `info` (with nested props)
                # if the previous query failed
                self.r_query_dydb = self.active_conection_table.update_item(
                    Key={
                        "user_uid": info["user_uid"],
                        "description_embedding": info["description_embedding"],
                    },
                    UpdateExpression="set validated=:a,\
                                        approved_nickname=:b,\
                                        approved_cat=:c,  \
                                        approved_subcat=:d, \
                                        #det = :attrValue",
                    ExpressionAttributeNames={
                        "#det": "details"},
                    ExpressionAttributeValues={
                        ":a": info['validated'],
                        ":b": info['approved_nickname'],
                        ":c": info['approved_cat'],
                        ":d": info['approved_subcat'],
                            ":attrValue": {
                                "subcat_uid_def_usr": info['details']["subcat_uid_def_usr"],
                                "subcat_uid_def_algo": info['details']["subcat_uid_def_algo"],
                                "nickname_algo": info['details']["nickname_algo"],
                                "nickname_usr": info['details']["nickname_usr"],
                                "cat_uid_def_algo": info['details']["cat_uid_def_algo"],
                                "cat_uid_def_usr": info['details']["cat_uid_def_usr"],
                                "updated_at": info['details']["updated_at"]                                        }
                        },
                    ReturnValues="UPDATED_NEW",
                )
            else:
                self.logger.exception(
                    fmt("message created_info_in_userTable", json=info))

        self.logger.info(
            "done created_info_in_userTable() method of ControllerDynamoDB")

    def update_info_in_userTable(self, info: dict = None):
        """
        Updates user table.

        """

        self.logger.info(
            "call update_info_in_userTable() method of ControllerDynamoDB ")

        try:
            self.r_query_dydb = self.active_conection_table.update_item(
                Key={
                    "user_uid": info["user_uid"],
                    "description_embedding": info["description_embedding"],
                },
                UpdateExpression="set #det.subcat_uid_def_usr=:l, \
                                        #det.cat_uid_def_usr=:m,\
                                        #det.nickname_usr=:n,\
                                        #det.updated_at=:o",
                ExpressionAttributeNames={
                    "#det": "details"},
                ExpressionAttributeValues={
                    ":l": info['details']['subcat_uid_def_usr'],
                    ":m": info['details']['cat_uid_def_usr'],
                    ":n": info['details']['nickname_usr'],
                    ":o": info['details']['updated_at'],
                },
                ReturnValues="UPDATED_NEW",
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "ValidationException":
                # Creating new top level attribute `info` (with nested props)
                # if the previous query failed
                self.r_query_dydb = self.active_conection_table.update_item(
                    Key={
                        "user_uid": info["user_uid"],
                        "description_embedding": info["description_embedding"],
                    },
                    UpdateExpression="set #det = :attrValue",
                    ExpressionAttributeNames={
                        "#det": "details"},
                    ExpressionAttributeValues={
                        ":attrValue": {
                            "subcat_uid_def_usr": info['details']["subcat_uid_def_usr"],
                            "cat_uid_def_usr": info['details']["cat_uid_def_usr"],
                            "nickname_usr": info['details']["nickname_usr"],
                            "updated_at": info['details']["updated_at"],
                                    }
                        },
                    ReturnValues="UPDATED_NEW",
                )
            else:
                self.logger.exception(
                    fmt("message update_info_in_userTable", json=info))


        self.logger.info(
            "done update_info_in_userTable() method of ControllerDynamoDB")

    def delete_register_userTable(self, user_uid, description_embedding):
        """ 

        """

        self.logger.info(
            "call delete_register_userTable() method of ControllerDynamoDB")
        try:
            self.r_query_dydb = self.active_conection_table.delete_item(
                Key={
                    "user_uid": user_uid,
                    "description_embedding": description_embedding,
                }
            )

        except ClientError as err:
            self.logger.error(
                "Couldn't delete register for User table %s. Here's why: %s: %s",
                user_uid,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            self.logger.exception(
                fmt("user iud ", json={'user_uid': user_uid}))

        self.logger.info(
            "done delete_register_userTable() method of ControllerDynamoDB")

    def delete_register_transactionTable(self, user_uid, transaction_uid):
        """

        """

        self.logger.info(
            "call delete_register_transactionTable() method of ControllerDynamoDB")

        try:
            self.r_query_dydb = self.active_conection_table.delete_item(
                Key={"user_uid": user_uid, "transaction_uid": transaction_uid})

        except ClientError as err:
            self.logger.error(
                "Couldn't delete register for Transaction table %s. Here's why: %s: %s",
                user_uid,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            self.logger.error(
                fmt("user iud ", json={'user_uid': user_uid}))

        self.logger.info(
            "donde delete_register_transactionTable() method of ControllerDynamoDB")

    def get_batch_info_in_userTable(self, items) -> None:
        """
        """

        try:
            if self.dyn_resource is None:
                self.dyn_resource = resource(
                    "dynamodb",
                    aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                    region_name=self.AWS_DEFAULT_REGION)

            self.result_query_dynamodb = self.dyn_resource.batch_get_item(
                RequestItems=items)

        except ClientError as e:
            self.result_query_dynamodb = JSONResponse(
                content=e.response["Error"], status_code=500
            )
            self.logger.error(fmt("items ", json=items))
   
    def get_batch_info_in_multicategoryTable(self, items) -> None:
        """

        """
        try:
            if self.dyn_resource is None:
                self.dyn_resource = resource(
                    "dynamodb",
                    aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                    region_name=self.AWS_DEFAULT_REGION)

            self.result_query_dynamodb = self.dyn_resource.batch_get_item(
                RequestItems=items)

        except ClientError as e:
            self.result_query_dynamodb = JSONResponse(
                content=e.response["Error"], status_code=500)
            self.logger.error(fmt("items ", json=items))

    def get_batch_info_in_collectiveTable(self, items) -> None:
        """
        # ["subcategory_uid"]
        # ["category_uid"]
        # ["collective_category_uid"]
        # ["collective_subcategory_uid"]
        # ["merchant_name"]
        # ['merch_uid']
        # ["description"]
        # ["collective_description"]
        # ['nickname']

        """
        try:
            if self.dyn_resource is None:
                self.dyn_resource = resource(
                    "dynamodb",
                    aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                    region_name=self.AWS_DEFAULT_REGION)

            self.result_query_dynamodb = self.dyn_resource.batch_get_item(
                RequestItems=items)

        except ClientError as e:
            self.result_query_dynamodb = JSONResponse(
                content=e.response["Error"], status_code=500)
            self.logger.error(fmt("items ", json=items))

    def insert_bacth_hash_in_collectiveTable(self, items_list: list) -> dict:

        try:
            with self.active_conection_table.batch_writer(overwrite_by_pkeys=["user_uid", "description_embedding"]) as writer:
                for item in items_list:
                    writer.put_item(Item=item)
            self.logger.info("Loaded data into table %s.",
                            self.active_conection_table.name)
        except ClientError:
            self.logger.error(
                "Couldn't load data into table %s.", self.active_conection_table.name)

