# ------------------------------------<Input>

null = None
false = False

# keys :
# fix 
# hardcode
# bug -> atender de inmediato
# refactorin
from distutils.log import ERROR

class CodeRalation:
    def __init__(self) -> None:
        pass

class TypeTransEnrichment:
    def __init__(self):
        self.NAME_SPACE_TRANS = {
            # delegar a MS-Report
            'user_uid': None,
            # delegar a MS-Report
            'transaction_uid': None,
            'message-type':None,
            'offset': None,
            'data': None,
            'dynamo': None
            }

    def get(self):
        return self.NAME_SPACE_TRANS

class TypeTransHomologated:
    def __init__(self):

        self.USER = dict()
        self.DYNAMO = dict()
        self.POSTGRES = dict()
        self.CASE = dict()
        self.NLP = dict()
        self.MODEL = dict()

        self.USER['transaction_uid'] = None
        self.USER['user_uid'] = None
        self.USER['account_uid'] = None
        self.USER['description'] = None
        self.USER['amount'] = None
        self.USER['raw'] = None
        # -------------------------------------<DynamoDB>
        self.DYNAMO['keys_user'] = None
        self.DYNAMO['keys_multicategory'] = None
        self.DYNAMO['details'] = None

        # --------------------------------------<Posgrest>
        self.POSTGRES['r_query_pgdb'] = None
        self.POSTGRES['tup_r_cat'] = None
        self.POSTGRES['tup_r_subcat'] = None

        # -------------------------------------<Hashing aka description embedding>
        # Model context
        # aka hashig embedding
        # ndarray to str for hashig
        self.MODEL['features_string'] = None
        self.MODEL['threshold'] = False
        self.MODEL['predict_value'] = None
        self.MODEL['info_subcategory'] = None
        self.MODEL['hash'] = None
        self.MODEL['collective'] = None
        self.MODEL['model_uid'] = None
        self.MODEL['version_model'] = None
        # ------------------------------------<Variables de NLP>
        # reset in reset_values_class


        # ------------------------------------<Case>
        self.CASE['options_merchant_names'] = None # lista de posibles merchant-namesl7f
        self.CASE['case'] = None # standar|custom|new|multicategory
        self.CASE['single_subcat'] = None #single or multicategory
        self.CASE['merchant_uid'] = None
        self.CASE['categorization'] = None # response de MSCategorization
        self.CASE['categorized'] = None #for re-categorized :false|flase

        
    # ------------------------------------<dict all context vars>

        self.NAME_SPACE_TRANS = {
                            # delegar a MS-Report
                            'user_uid':self.USER['user_uid'],
                            # delegar a MS-Report
                            'transaction_uid':self.USER['transaction_uid'],
                            'USER': self.USER,
                            'DYNAMO': self.DYNAMO,
                            'CASE':self.CASE,
                            'NLP':self.NLP,
                            'MODEL':self.MODEL}

    def get(self):
        return self.NAME_SPACE_TRANS

class ErrorProcess:
    """
    Mensaje de error enviado al type : 'transaction-process-error' 
    lo utiliza Backend para reenviar mensajes qe tuvieron error. 
    """
    def __init__(self):
        self.ERROR_ = dict()
        self.ERROR_['type'] = 'transaction-process-error' 
        self.ERROR_['data'] = {}
        self.ERROR_['data']['institution'] = None
        self.ERROR_['data']['user_uid'] = None
        self.ERROR_['data']['offset'] = None

    def get(self):
        return self.ERROR_

class Error:
    """
    Mensaje de error enviado al type :'report-error-ms-categorization'
    lo utiliza reporting (MS monitoring) para almacenar en Mongo los 
    errores y sus detalles
    """
    def __init__(self):
        self.item = dict()
        self.item['type'] = 'report-error-ms-categorization'
        self.item['data'] = None
        self.item['offset'] = None
        self.item['dt'] = None
        self.item['info_mixin'] = None
        self.item['error_type'] = None
        self.item['error_value'] = None
        self.item['traceback_info'] = None
        self.item['trans_context'] = None
    def get(self):
        return self.item

class JSONErrorTraceback:
    """
    JSON que almacena detalles de errores y los envía a los Logs y a Sentry
    """
    def __init__(self)->None:
        self.Item =  {
                'type': None,
                'error_type': None,
                'error_value': None,
                'traceback_info': None,
                'trans_context': None,
                'details' : JSONErrorDetails().get()
                }

    def get(self):
        return self.Item

class JSONErrorDetails:
    """
    JSON que almacena detalles de errores y los envía a los Logs y a Sentry
    """
    def __init__(self)->None:
        self.Item =  {
            'uid': None,
            'user_uid': None,
            'transaction_uid': None,
            'level_processing': None,
            'description_embedding': None,
            'DYNAMO':None
				}

    def get(self):
        return self.Item

class MsgCatCompleted :
    def __init__(self):
        self.COMPLETED = dict()
        self.COMPLETED['type'] = 'transaction-categorized-completed'
        self.COMPLETED['data']= {}
        self.COMPLETED['data']['institution'] = None
        self.COMPLETED['data']['user_uid'] = None
    def get(self):
        return self.COMPLETED

class TypeDB:
    def __init__(self):

        self.DYNAMO = dict()
        self.POSTGRES = dict()
        self.LANG = dict()

        # ------------------------------<languaje>
        self.LANG['lang_code_trans'] = None
        self.LANG['lang_code_app'] = None
        self.LANG['country_code'] = None
        # -------------------------------------<DynamoDB>
        self.DYNAMO['keys_user'] = None
        self.DYNAMO['keys_multicategory'] = None
        self.DYNAMO['details'] = None

        # --------------------------------------<Posgrest>
        self.POSTGRES['r_query_pgdb'] = None
        self.POSTGRES['tup_r_cat'] = None
        self.POSTGRES['tup_r_subcat'] = None

        self.NAME_SPACE_DB = {'DYNAMO': self.DYNAMO,
                              'POSTGRES': self.POSTGRES,
                              'LANG': self.LANG}

    def get(self):
        return self.NAME_SPACE_DB

class CategorizationObject:
    """
    Estructura del objeto categorization 
    dentro de los mensajes de Kafka 
    topic : "transaction"
    type : "transaction-categorized"

    """
    def __init__(self)->None:
        self.Item =  {
            "subcategory_uid": None, #ID subcategoría
            "category_uid": None, # ID categoría
            "merchant_name": None, # nombre del comerción
            "description": None, # Nickname del comerción.
            "clean_description": None, # Descripción limpia
            "kw_group": None, # Keyword asociado al grupo(segmento) al que pertence la transacción
            "asset_uid": None,  # 
            "business_uid": None, #
            "person_uid": None, # ID de la persona asociada a la transacción
            "special_moment_uid": None, # ID de el momento especial asociado a la transacción
            "frequency_uid": None, # ID de la frecuencia asociada a la transacción
            "is_essential": None, # True| False  si el gasto es escencial
            "is_membership": None, # True| False si el gasto pertence a un menbresía
            "income_source_uid":None,
            "is_loan_received":None,
            "is_loan_requested": None,
            "collective_subcategory_uid":None,
            "collective_description":None,
            "collective_is_essential":None,
            "collective_is_membership" : None
			}

    def get(self):
        return self.Item

class Message:
    def __init__(self) -> None:

        self.msj = {
            'data': [],
            'type':None
                    }
    def get(self):
        return self.msj

class MsgReportStatus :
    def __init__(self):
        self.item = dict()
        self.item['type'] = 'report-message-ok'
        self.item['data']= {}
        self.item['data']['offset'] = None
        self.item['data']['type'] = None
        self.item['data']['status'] = 'ok'

    def get(self):
        return self.item

# RedShift DataWare House
class DimTransactions:
    """
    For RedShift Dimension Transactions
    """
    def __init__(self) -> None:
        self.Item = {
            "approved_asset": None,
            "approved_business": None,
            "approved_category": None,
            "approved_frequency": None,
            "approved_income_source": None,
            "approved_is_essential": None,
            "approved_is_loan_received": None,
            "approved_is_loan_requested": None,
            "approved_is_membership": None,
            "approved_nickname": None,
            "approved_person": None,
            "approved_special_moment": None,
            "approved_subcategory": None,
            "asset_uid_collective": None,
            "asset_uid_custom": None,
            "asset_uid_recommended": None,
            "business_uid_collective": None,
            "business_uid_custom": None,
            "business_uid_recommended": None,
            "category_custom_type": None,
            "category_uid_collective": None,
            "category_uid_custom": None,
            "category_uid_recommended": None,
            "classified_date": None,
            "clean_description": None,
            "country_code": None,
            "created_at": None,
            "created_homologation_date": None,
            "deleted_at": None,
            "flow_type": None,
            "frequency_uid_collective": None,
            "frequency_uid_custom": None,
            "frequency_uid_recommended": None,
            "income_source_uid_collective": None,
            "income_source_uid_custom": None,
            "income_source_uid_recommended": None,
            'is_autocategorized':None,
            "is_essential_collective": None,
            "is_essential_custom": None,
            "is_essential_recommended": None,
            "is_loan_received_collective": None,
            "is_loan_received_custom": None,
            "is_loan_received_recommended": None,
            "is_loan_requested_collective": None,
            "is_loan_requested_custom": None,
            "is_loan_requested_recommended": None,
            "is_membership_collective": None,
            "is_membership_custom": None,
            "is_membership_recommended": None,
            "language_code": None,
            "message_type": None,
            "model_classification_version": None,
            "model_collective_version": None,
            "model_nickname_version": None,
            "model_nlp_version": None,
            "nickname_collective": None,
            "nickname_custom": None,
            "nickname_recommended": None,
            "original_created_date": None,
            "person_uid_collective": None,
            "person_uid_custom": None,
            "person_uid_recommended": None,
            "source_description": None,
            "special_moment_uid_collective": None,
            "special_moment_uid_custom": None,
            "special_moment_uid_recommended": None,
            "subcategory_custom_type": None,
            "subcategory_uid_collective": None,
            "subcategory_uid_custom": None,
            "subcategory_uid_recommended": None,
            "transaction_uid": None,
            "updated_at": None,
            "updated_date": None,
            "validated": None,
            "validated_date": None
            }
    def get(self):
        return self.Item

class DimAccount:
    """
    """
    def __init__(self) -> None:
        self.Item = {
    "account_uid":None,
    "bank_name":None,
    "account_type":None,
    "bank_type":None,
    "created_at":None,
    "updated_at":None,
    "deleted_at" : None
    }
    def get(self):
        return self.Item

# fix
class DimUser:
    """
    """
    def __init__(self) -> None:
        self.Item = {
    "user_uid":None,
    # "postcode":None,
    # "created_at":None,
    # "updated_at":None,
    # "deleted_at" : None
    }
    def get(self):
        return self.Item
    
class DimDates:
    """
    """
    def __init__(self) -> None:
        self.Item = {
    "transaction_date":None,# validated or updated
    "day_of_month":None,
    "month_of_year":None,
    "month_name": None,
    "year":None,
    "week_of_month":None,
    "quarter_of_year":None,
    # "created_at":None,
    # "updated_at":None,
    # "deleted_at" : None
    }
    def get(self):
        return self.Item

# fix
class FactTransactions:

    def __init__(self) -> None:
        
        self.Item = {
            "transaction_date": None,
            "transaction_uid": None,
            "user_uid": None,
            "account_uid": None
        }

    def get(self):
        return self.Item


# MongoDB History Facts
class TransactionFact:
    """
    For mongoDB 
    """
    def __init__(self) -> None:
        self.Item = {
            "_id": None,
            "user_uid": None,
            "idx": None,
            "offset": None,
            "hash": None,
            "amount": None,
            "currency": None,
            "account_institution_name": None,
            "account_institution_type": None,
            "source_category": null,
            "account_type": None,
            "account_name": None,
            "account_number": None,
            "account_bank_product_id": None,
            "account_internal_identification": None,
            "account_public_identification_value": None,
            "account_public_identification_name": None,
            "account_category": None,
            "source_merchant": None,
            "source_description": None,
            "value_date": None,
            "collected_at": None,
            "message_type": None,
            "original_created_at": None,
            "lang_code": None,
            "country_code": None,
            "created_at_homologation": None,
            "type_flow": None,
            "history-track":[]
            }
    def get(self):
        return self.Item

class PreCategorized:
    """
    """
    def __init__(self) -> None:
        self.Item = {
            "subcategory_uid": None, #ID subcategoría
            "category_uid": None, # ID categoría
            "merchant_name": None, # nombre del comerción
            "nickname": None, # Nickname del comerción.
            "clean_description": None, # Descripción limpia
            "kw_group": None, # Keyword asociado al grupo(segmento) al que pertence la transacción
            "asset_uid": None,  # 
            "business_uid": None, #
            "person_uid": None, # ID de la persona asociada a la transacción
            "special_moment_uid": None, # ID de el momento especial asociado a la transacción
            "frequency_uid": None, # ID de la frecuencia asociada a la transacción
            "is_essential": None, # True| False  si el gasto es escencial
            "is_membership": None, # True| False si el gasto pertence a un menbresía
            "income_source_uid":None,
            "is_loan_received":None,
            "is_loan_requested": None,
            "status": None,
            "categorized": None,
            "replica_type": None,
            "message_type": None,
            "classified_at": None,
            "model_nlp_version": None,
            "model_classification_version": None,
            "model_nickname_version": None,
            "model_collective_version": None,
        }
    def get(self):
        return self.Item
    
class ValidatedInfo:
    """
    """
    def __init__(self) -> None:
        self.Item = {
        {
     
        }

        }
    def get(self):
        return self.Item
       
class UpdatedInfo:
    """
    """
    def __init__(self) -> None:
        self.Item = {
        {
      
        }

        }
    def get(self):
        return self.Item
# DynamoDB
class DetailsUser:
    """
    Objeto  DetailsUser, el cual es un objeto anidado del super Objeto ItemUser
    """

    def __init__(self) -> None:
        self.Item = {

        "cat_uid_def_algo": None,
        "cat_uid_def_usr": None,
        "cat_uid_def_collect": None,

        "nickname_algo": None,
        "nickname_usr": None,
        "nickname_collect": None,

        "subcat_uid_def_algo": None,
        "subcat_uid_def_usr": None,
        "subcat_uid_def_collect": None,

        "frequency_uid_def_algo": None,
        "frequency_uid_def_usr": None,
        "frequency_uid_def_collect": None,

        "is_essential_def_algo": None,
        "is_essential_def_usr": None,
        "is_essential_def_collect": None,

        "is_membership_def_algo": None,
        "is_membership_def_usr": None,
        "is_membership_def_collect": None,

        "person_uid_def_usr": None,
        "person_uid_def_algo": None,
        "person_uid_def_collect": None,

        "special_moment_uid_def_algo": None,
        "special_moment_uid_def_usr": None,
        "special_moment_uid_def_collect": None,

        "business_uid_def_algo": None,
        "business_uid_def_usr": None,
        "business_uid_def_collect": None,

        "asset_uid_def_algo": None,
        "asset_uid_def_usr": None,
        "asset_uid_def_collect": None,

        "income_source_uid_def_algo": None,
        "income_source_uid_def_usr": None,
        "income_source_uid_def_collect": None,

        "is_loan_received_def_algo": None,
        "is_loan_received_def_usr": None,
        "is_loan_received_def_collect": None,

        "is_loan_requested_def_algo": None,
        "is_loan_requested_def_usr": None,
        "is_loan_requested_def_collect": None,

        "created_at": None,#  None for transactio-categorized, type:expense-created
        "updated_at": None,#  None for transactio-categorized, type:expense-updated
        
        "is_autocategorized":None, # categorización automática

        "message_type": None, # None for transactio-categorized, save expense/income created/updated
        "clean_description": None,
        "merchant_name": None,
        "classified_at": None, # type:transaction-categorized
        "source_embedding": None,
        "kw_group":None

        }

    def get(self):
        return self.Item

class ItemUser:
    """
     Obtejo ItemUser, el cual representa un documento en la colección 
     User de DynamoDB en AWS.+


    """
    def __init__(self) -> None:
        self.Item = {
            "user_uid": None, #Clave de partición
            "description_embedding": None, # Clave de búsqueda

            "approved_cat": None,
            "approved_nickname": None,
            "approved_subcat": None,
            "approved_is_essential": None,
            "approved_is_membership": None,
            "approved_person": None,
            "approved_special_moment": None,
            "approved_frequency": None,
            "approved_business": None,
            "approved_asset": None,
            "approved_is_loan_received": None,
            "approved_is_loan_requested": None,
            "approved_income_source_uid": None,

            "change_asset": None,
            "change_business": None,
            "change_cat": None,
            "change_frequency": None,
            "change_income_source_uid": None,
            "change_is_essential": None,
            "change_is_loan_received": None,
            "change_is_loan_requested": None,
            "change_is_membership": None,
            "change_nickname": None,
            "change_person": None,
            "change_special_moment": None,
            "change_subcat": None,

            "validated": None,
            "language_code": None,
            "categorized": None,
            "replica_type": None,# agregar a variables *
            "message_type": None, #typo de mensaje kafka
            "flow_type": None,# inflow|outflow
            "created_at_homologation": None, # type:transacton-homologated
            
            "case_type": None,
            
            "model_nlp_version": None,
            "model_classification_version": None,
            "model_nickname_version": None,
            "model_collective_version": None,
            "details": None # NestedDict type DetailsUser()
            }
    def get(self):
        return self.Item

class ItemMulty:
    def __init__(self) -> None:

        self.Item = {
            'description_embedding': None,
            'popular_subcategories': 
                        {   
                        1: None,
                        2: None,
                        3:None
                         },
            'categories': 
                        {
                        1: None,
                        2: None,
                        3:None
                        },
            'collective_nickname': None,
            'nickname': None,
            'merch_uid': None,
            'subcat_uid': None
            }
    def get(self):
        return self.Item

class ItemTrans:
    # Tabla Transaction en DynamoDB
    def __init__(self) -> None:

        self.Item = {
            'user_uid': None,
            'transaction_uid': None,
            'hash': None
                    }
    def get(self):
        return self.Item
# Dims Diccionarios
class Transaction_Map_DWH:

    def __init__(self) -> None:

        self.Item = {
            'approved_asset': None,
            'approved_business': None,
            'approved_category': None,
            'approved_frequency': None,
            'approved_income_source': None,
            'approved_is_essential': None,
            'approved_is_loan_received': None,
            'approved_is_loan_requested': None,
            'approved_is_membership': None,
            'approved_nickname': None,
            'approved_person': None,
            'approved_special_moment': None,
            'approved_subcategory': None,
            'asset_uid_def_collect': None,
            'asset_uid_def_algo': None,
            'asset_uid_def_usr': None,
            'business_uid_def_collect': None,
            'business_uid_def_algo': None,
            'business_uid_def_usr': None,
            'category_custom_type': None,
            'cat_uid_def_collect': None,
            'cat_uid_def_algo': None,
            'cat_uid_def_usr': None,
            'classified_at': None,
            'clean_description': None,
            'country_code': None,
            'created_at': None,
            'created_at_homologation': None,
            'flow_type': None,
            'frequency_uid_def_collect': None,
            'frequency_uid_def_algo': None,
            'frequency_uid_def_usr': None,
            'income_source_uid_def_collect': None,
            'income_source_uid_def_algo': None,
            'income_source_uid_def_usr': None,
            'is_autocategorized':None,
            'is_essential_def_collect': None,
            'is_essential_def_algo': None,
            'is_essential_def_usr': None,
            'is_loan_received_def_collect': None,
            'is_loan_received_def_algo': None,
            'is_loan_received_def_usr': None,
            'is_loan_requested_def_collect': None,
            'is_loan_requested_def_algo': None,
            'is_loan_requested_def_usr': None,
            'is_membership_def_collect': None,
            'is_membership_def_algo': None,
            'is_membership_def_usr': None,
            'language_code': None,
            'message_type': None,
            'model_classification_version': None,
            'model_collective_version': None,
            'model_nickname_version': None,
            'model_nlp_version': None,
            'nickname_algo': None,
            'nickname_collect': None,
            'nickname_usr': None,
            'original_created_date': None,
            'person_uid_def_collect': None,
            'person_uid_def_algo': None,
            'person_uid_def_usr': None,
            'source_description': None,
            'special_moment_uid_def_collect': None,
            'special_moment_uid_def_algo': None,
            'special_moment_uid_def_usr': None,
            'subcategory_custom_type': None,
            'subcat_uid_def_usr': None,
            'subcat_uid_def_collect': None,
            'subcat_uid_def_algo': None,
            'updated_at': None,
            'validated': None,
            'transaction_uid': None,
            }
    
    def get(self):
        return self.Item
    
class Visualization_Map_DWH:

    def __init__(self) -> None:

        self.Item = {
        'asset_uid': None,
        'business_uid':None,
        'category_uid': None,
        'classified_at': None,
        'clean_description':None,
        'country_code': None,
        'created_at': None, #validate ()
        'created_at_homologation': None,
        'description': None,
        'flow_type':None,
        'frequency_uid': None,
        'income_source_uid': None,
        'is_autocategorized':None,
        'is_essential':None,
        'is_loan_received': None,
        'is_loan_requested': None,
        'is_membership':None,
        'language_code':None,
        'message_type': None,
        'original_created_date':None,
        'person_uid': None,
        'source_description': None,
        'special_moment_uid': None,
        'subcategory_uid': None,
        'transaction_uid':None,
        'updated_at': None, #update expense or income 
        'validated':None,
        }
    
    def get(self):
        return self.Item


    