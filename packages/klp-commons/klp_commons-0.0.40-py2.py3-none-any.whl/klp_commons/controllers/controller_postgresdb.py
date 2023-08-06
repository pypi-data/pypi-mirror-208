 
from psycopg import connect
from os import getenv
from datetime import datetime, timezone
from klp_commons.log.structuredMessage import StructuredMessage
from nanoid import generate
from logging import getLogger

fmt = StructuredMessage
message = 'postgresDBController'

class ControllerPostgresDB:

    def __init__(self, conf = None):

        self.conn = None
        self.logger = getLogger('categorization.ControllerPosgrestDB')

        # Init ()
        self.logger.info('ControllerPosgrestDB.init()')
        self.logger.info('creating an instance of ControllerPosgrestDB')
        if conf is None:
            self.PG_HOST = getenv('PG_HOST')
            self.PG_DATABASE = getenv('PG_DATABASE')
            self.PG_USER = getenv('PG_USER')
            self.PG_PASSWORD = getenv('PG_PASSWORD')
            self.PG_PORT = getenv('PG_PORT')
        else :
            self.PG_HOST = conf['PG_HOST']
            self.PG_DATABASE = conf['PG_DATABASE']
            self.PG_USER = conf['PG_USER']
            self.PG_PASSWORD = conf['PG_PASSWORD']
            self.PG_PORT = conf['PG_PORT']
        
        self.format_exter = '%Y-%m-%dT%H:%M:%S' # .%f%z'
        self.format_inter = '%Y-%m-%dT%H:%M:%S'
        self.logger.info('donecreating an instance of ControllerPosgrestDB')

    def get_conection(self) -> None:
        self.logger.info('call get_conection method ')

        try:
            self.conn = connect(
                host=self.PG_HOST,
                dbname=self.PG_DATABASE,
                user=self.PG_USER,
                password=self.PG_PASSWORD,
                port=self.PG_PORT,
            )

        except BaseException as e:
            self.conn.rollback()
            self.logger.exception(e, exc_info=True)
            self.logger.error('Error conection postgres DB ', self.conn)

        self.logger.info('done call get_conection')

    def execute_query(
            self, query=None) -> None:

        self.logger.info('call execute_query ')
        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:

                cur.execute(query)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            return obj

    def execute_query_(
            self, query=None) -> None:

        self.logger.info('call execute_query ')
        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:

                cur.execute(query)
                colnames = [desc[0] for desc in cur.description]

                obj = cur.fetchall()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            return obj,colnames
        

    def get_subcategory_info_by_mappingCode(
            self, clase_predict: int = None) -> None:

        self.logger.info('call get_subcategory_info_by_mappingCode method ')
        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:

                postgres_select_query = '''

                            SELECT uid, name, keywords, category_uid, icon_uid
                            FROM public.subcategory
                            WHERE mapping_code=%(clase_predict)s;
                            '''

                param_select = {'clase_predict': clase_predict}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()

            if obj is None:
                    self.logger.info(fmt('No found code subcategory: ',
                                    json={'code : ': clase_predict}))
                    return 0

            else :
                self.logger.info('done call get_subcategory_info_by_mappingCode')
                return obj



    def get_subcategory_info_by_mappingCode(
            self, clase_predict: int = None) -> None:

        self.logger.info('call get_subcategory_info_by_mappingCode method ')
        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:

                postgres_select_query = '''

                            SELECT uid, name, keywords, category_uid, icon_uid
                            FROM public.subcategory
                            WHERE mapping_code=%(clase_predict)s;
                            '''

                param_select = {'clase_predict': clase_predict}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()

            if obj is None:
                    self.logger.info(fmt('No found code subcategory: ',
                                    json={'code : ': clase_predict}))
                    return 0

            else :
                self.logger.info('done call get_subcategory_info_by_mappingCode')
                return obj

    def get_subcategory_info_batch_by_mappingCode(self, codes_predict) -> None:

        self.logger.info(
            'call get_subcategory_info_batch_by_mappingCode method ')
        self.get_conection()
        obj = None  

        try : 
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                            SELECT uid, name, keywords, category_uid, icon_uid, mapping_code
                            FROM public.subcategory
                            WHERE mapping_code = ANY(%s);
                            '''
                cur.execute(postgres_select_query, (codes_predict,))
                # cur.execute('SELECT * FROM subcategory WHERE mapping_code = ANY (ARRAY[62,64])')
                # SELECT * FROM subcategory WHERE mapping_code = ANY (ARRAY[0,62,64])
                obj = cur.fetchall()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
                    
            if obj is None:
                self.logger.info(fmt('No found code subcategory: ',
                                json={'code : ': codes_predict}))
                return 0

            else :
                self.logger.info(' done call get_subcategory_info_batch_by_mappingCode')
                return obj

    def get_category_info_by_uid(self, category_uid: str = None) -> None:

        self.logger.info('call get_category_info_by_uid method ')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                        SELECT name, keywords, color_uid, icon_uid, mapping_code
                        FROM public.category
                        WHERE uid=%(cat_uid)s;
                                        '''

                param_select = {'category_uid': category_uid}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()

            if obj is None:
                self.logger.warning
                (
                    fmt('No found category_uid (get_category_info_by_uid): ', json={'category_uid': category_uid})
                )
                return 0
            else :
                self.logger.info('done call get_category_info_by_uid method ')
                return obj

    def get_subcategory_info_by_uid(self, subcategory_uid: str = None) -> None:

        self.logger.info('call get_subcategory_info_by_uid method ')

        self.get_conection()
        obj = None
        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                            SELECT mapping_code,
                                    name,
                                    keywords,
                                    category_uid
                            FROM public.subcategory
                            WHERE uid=%(subcategory_uid)s;
                            '''

                param_select = {'subcategory_uid': subcategory_uid}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()
            # reveal_type(obj) would return 'Optional[Person]' here

            if obj is None:
                self.logger.warning(fmt('No found subcategory_uid(get_subcategory_info_by_uid): ',json={'subcategory_uid': subcategory_uid})
                )
                return 0
            else :
                self.logger.info('done call get_subcategory_info_by_uid method ')
                return obj

    def get_subcategory_info_by_parent(self, uid: str = None) -> None:

        self.logger.info('call get_subcategory_info_by_parent method ')

        self.get_conection()
        obj = None

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                            SELECT uid,
                                    name
                            FROM public.subcategory
                            WHERE category_uid=%(uid)s;
                            '''

                param_select = {'uid': uid}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()
            # reveal_type(obj) would return 'Optional[Person]' here

            if obj is None:
                self.logger.warning(fmt('No found subcategory_uid(get_subcategory_info_by_parent): ',json={'subcategory_uid': uid}))
                return 0
            else :
                self.logger.info('done call get_subcategory_info_by_parent method ')
                return obj

    def get_lang_subcategory_by_uid(self, subcategory_uid: str = None) -> None:

        self.logger.info('call get_lang_subcategory_by_uid method ')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT uid, name, keywords, language_code, subcategory_uid
                    FROM public.subcategory_translation
                    WHERE subcategory_uid = %(subcatrgory_uid)s;
                                        '''
                param_select = {'subcategory_uid': subcategory_uid}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            if obj is None:
                self.logger.warning(fmt('No found uid subcategory: ',json={'uid': subcategory_uid}))
                return 0
            else :
                self.logger.info('done call get_lang_subcategory_by_uid')
                return obj

    def get_bank_names(self, lang_code: str = 'es-MX') -> None:

        self.logger.info('call get_bank_names method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT name
                    FROM public.bank_name
                    WHERE lang_code = %(lang_code)s;
                                        '''

                param_select = {'lang_code': lang_code}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            if obj is None:
                self.logger.info(fmt('No found get_bank_names for language code : ',json={'lang_code': lang_code}))
                return 0

            else :
                self.logger.info('done call get_bank_names')
                return obj

    def get_proper_name(self, lang_code: str = None) -> None:

        self.logger.info('call get_proper_name method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT name
                    FROM public.proper_name
                    WHERE lang_code = %(lang_code)s;
                                        '''

                param_select = {'lang_code': lang_code}
                cur.execute(postgres_select_query, param_select)
                # iterador ()
                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found proper_name for language code : ',
                        json={'lang_code': lang_code},
                    )
                )
                return 0
            else :
                self.logger.info('done call proper_name')
                return obj

    def get_nicknames(self, country_code: str = None) -> None:

        self.logger.info('call get_nicknames method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT name
                    FROM public.nickname
                    WHERE country_code = %(country_code)s;
                                        '''
                
                param_select = {'country_code': country_code}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found  nicknames for country code : ',
                        json={'country_code': country_code},
                    )
                )
                return 0
            else :
                self.logger.info('done call get_nicknames')
                return obj

    def get_months(self, lang_code: str = None) -> None:

        self.logger.info('call get_months method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT name
                    FROM public.month
                    WHERE lang_code = %(lang_code)s;
                                        '''
                param_select = {'lang_code': lang_code}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found months for country code : ',
                        json={'country_code': lang_code},
                    )
                )
                return 0
            else :
                self.logger.info('done call get_months')
                return obj

    def get_places(self, lang_code: str = None) -> None:

        self.logger.info('call get_places method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT name
                    FROM public.place
                    WHERE lang_code = %(lang_code)s;
                                        '''
                param_select = {'lang_code': lang_code}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found places for country code : ',
                        json={'country_code': lang_code},
                    )
                )
                return 0
            else :
                self.logger.info('done call get_places')
                return obj

    def get_keywords(self, country_code: str = None) -> None:

        self.logger.info('call get_keywords method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT name
                    FROM public.keyword
                    WHERE country_code = %(country_code)s;
                                        '''
                param_select = {'country_code': country_code}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found keywords for country code : ',
                        json={'country_code': country_code},
                    )
                )
                return 0
            else:
                self.logger.info('done call get_keywords')
                return obj

    def get_stopword_context(self, lang_code: str = None) -> None:

        self.logger.info('call get_stopword_context method')

        self.get_conection()
        obj = None  

        try: 
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT name
                    FROM public.sw_context
                    WHERE lang_code = %(lang_code)s;
                                        '''
                param_select = {'lang_code': lang_code}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found stopwords on context banking for language code : ',
                        json={'lang_code': lang_code},
                    )
                )
                return 0
            else:
                self.logger.info('done call get_stopword_context')
                return obj

    def get_catalog_merchant(self, country_code: str = None) -> None:

        self.logger.info('call get_catalog_merchant method')

        self.get_conection()
        obj = None  

        try:
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT nickname, collective_nickname, merchant_name,description
                    FROM public.merchant
                    WHERE country_code = %(country_code)s;
                                        '''
                param_select = {'country_code': country_code}
                cur.execute(postgres_select_query, param_select)
                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()            
            if obj is None:
                self.logger.warning(
                    fmt(
                        'No found catalog merchant for country code : ',
                        json={'country_code': country_code},
                    )
                )
                return 0
            else :
                self.logger.info('done call get_catalog_merchant')
                return obj

    def get_info_merchant_by_nickname(self, nickname, country_code):

        self.logger.info('call get_merchant_name method')

        self.get_conection()
        obj = None  
        try:
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT collective_nickname,
                            merchant_name,
                            description,uid
                    FROM public.merchant
                    WHERE nickname = %(nickname)s AND
                        country_code = %(country_code)s;
                                        '''
                param_select = {
                    'nickname': nickname,
                    'country_code': country_code}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()            
            if obj is None:
                self.logger.warning(
                    fmt(
                        'No found catalogs of nicknames and country code : ',
                        json={'country_code': country_code,
                              'nickname': nickname},
                    )
                )
                return 0
            else :
                self.logger.info('done call get_merchant_name')
                return obj

    def get_info_bacth_merchant_by_nickname(self, nicknames, country_code):

        self.logger.info('call get_info_bacth_merchant_by_nickname method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT nickname,
                            collective_nickname,
                            merchant_name,
                            description,
                            uid
                    FROM public.merchant
                    WHERE nickname = ANY (%s) AND
                        country_code = (%s);
                                        '''

                cur.execute(postgres_select_query, [nicknames, country_code])

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()  
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found catalogs of nicknames and country code : ',
                        json={'country_code': country_code,
                              'nickname': nicknames},
                    )
                )
                return 0
            else:
                self.logger.info('done call get_info_bacth_merchant_by_nickname')
                return obj

    def get_info_merchant_by_uid(self, merch_uid, country_code):

        self.logger.info('call get_merchant_name method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT  nickname,
                            collective_nickname,
                            merchant_name,
                            description
                    FROM public.merchant
                    WHERE uid = %(merch_uid)s AND
                        country_code = %(country_code)s;
                                        '''
                param_select = {
                    'merch_uid': merch_uid,
                    'country_code': country_code}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()  
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found merchant : ',
                        json={'country_code': country_code,
                              'merch_uid': merch_uid},
                    )
                )
                return 0
            else :
                self.logger.info('done call get_merchant_name')
                return obj

    def get_info_batch_merchant_by_uids(self, merch_uids=None, country_code='MX'):

        self.logger.info('call get_merchant_name method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT  uid,
                            nickname,
                            collective_nickname,
                            merchant_name,
                            description
                    FROM public.merchant
                    WHERE country_code = (%s)
                    AND uid = ANY (%s) ;
                                        '''

                cur.execute(postgres_select_query, [country_code, merch_uids])

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)
                
        finally:
            self.conn.close()  
            if obj is None:
                self.logger.info(
                    fmt(
                        'No found merchant : ',
                        json={'country_code': country_code,
                              'merch_uid': merch_uids},
                    )
                )
                return 0
            else :
                self.logger.info('done call get_info_merchant_by_uids')
                return obj

    def get_custom_category_by_userUID(self, user_uid):

        self.logger.info('call get_custom_category_by_userUID method')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                    SELECT  uid,
                            name,
                            category_uid,
                            keywords

                    FROM public.custom_category
                    WHERE user_uid = %(user_uid)s
                                        '''
                param_select = {'user_uid': user_uid}

                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchall()
        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()  
            if obj is None:
                self.logger.warning(
                    fmt('No found user_uid : ',
                        json={'user_uid': user_uid})
                )
                return 0
            else :
                self.logger.info('done call get_custom_category_by_userUID')
                return obj

    def insert_fact_table(self, list_items: list = None):
        self.logger.info('call insert_fact_table method')
        self.get_conection()
        try:
            with self.conn.cursor() as cur:
                for data in list_items:
                    postgres_insert_query = '''
                        INSERT INTO fact (
                            uid,
                            transaction_uid,
                            hash,
                            category_uid,
                            subcategory_uid,
                            custom_subcategory_uid,
                            lang_code,
                            country_code,
                            created_at,
                            updated_at,
                            valid_from,
                            valid_to,
                            user_uid,
                            description,
                            merchant_name,
                            stem,
                            bow,
                            collective_nickname,
                            nickname,
                            custom_nickname,
                            status
                            )
                        VALUES (
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s
                                )
                            '''
                    record_to_insert = (
                        generate(size=40),
                        data['transaction_uid'],
                        data['hash'],
                        data['category_uid'],
                        data['subcategory_uid'],
                        data['custom_subcategory_uid'],
                        data['lang_code'],
                        data['country_code'],
                        data['created_at'],
                        data['updated_at'],
                        data['valid_from'],
                        data['valid_to'],
                        data['user_uid'],
                        data['description'],
                        data['merchant_name'],
                        data['stem'],
                        data['bow'],
                        data['collective_nickname'],
                        data['nickname'],
                        data['custom_nickname'],
                        data['status'],
                    )
                    cur.execute(postgres_insert_query, record_to_insert)

        except BaseException as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(fmt('No insert transaction ', json={'data': list_items}))
            self.conn.rollback()
            return 0
        else:
            self.conn.commit()
        finally:
            self.conn.close()
            self.logger.info('done call insert_fact_table')
            return postgres_insert_query

    def insert_feature_store_table(self, list_items: list = None):
        '''
        '''
        self.logger.info('call insert_feature_store_table method')
        self.get_conection()
        try:
            with self.conn.cursor() as cur:
                for data in list_items:
                    postgres_insert_query = '''
                        INSERT INTO public.\
                                        feature_store
                                        (
                                            uid,
                                            description,
                                            hash,
                                            nickname,
                                            merchant_name,
                                            stem,
                                            bow,
                                            amount,
                                            category_uid,
                                            subcategory_uid,
                                            lang_code,
                                            country_code,
                                            single_cat,
                                            raw
                                        )
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                                        '''
                    record_to_insert = (
                        generate(size=40),
                        data['description'],
                        data['hash'],
                        data['nickname'],
                        data['merchant_name'],
                        data['stem'],
                        data['bow'],
                        data['amount'],
                        data['category_uid'],
                        data['subcategory_uid'],
                        data['lang_code'],
                        data['country_code'],
                        data['single_cat'],
                        data['raw'],
                    )
                    cur.execute(postgres_insert_query, record_to_insert)
            
        except BaseException as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(fmt('No insert features ', json={'data': list_items}))
            self.conn.rollback()
            return 0
        else:
            self.conn.commit()
        finally:
            self.conn.close()
            self.logger.info('done call insert_feature_store_table')
            return postgres_insert_query           

    def insert_custom_category(self, data: dict = None):
        '''
        '''
        self.logger.info('call insert_custom_category method')
        self.get_conection()
        try:
            with self.conn.cursor() as cur:
                postgres_insert_query = '''
                INSERT INTO public.custom_category(
                uid, 
                name, 
                keywords, 
                user_uid, 
                created_at, 
                updated_at, 
                deleted_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (uid) DO NOTHING
                                        '''

                record_to_insert = (
                    data['uid'],
                    data['name'],
                    data['keywords'],
                    data['user_uid'],
                    data['created_at'],
                    data['updated_at'],
                    data['deleted_at'])
                cur.execute(postgres_insert_query, record_to_insert)

        except BaseException as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(fmt('No insert new custom category ', json={'data': data}))
            self.conn.rollback()
            return 0
        else:
            self.conn.commit()
            return postgres_insert_query

        finally:
            self.conn.close()
            self.logger.info('done call insert_custom_category')
            
    def insert_custom_subcategory(self, data: dict = None):
        '''
        '''
        self.logger.info('call insert_custom_category method')
        self.get_conection()
        try:
            with self.conn.cursor() as cur:

                postgres_insert_query = '''
                INSERT INTO public.custom_subcategory(
                uid,
                category_uid,
                name,  
                keywords, 
                user_uid, 
                created_at, 
                updated_at, 
                deleted_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (uid) DO NOTHING
                                        '''

                record_to_insert = (
                    data['uid'],
                    data['parent_uid'],
                    data['name'],
                    data['keywords'],
                    data['user_uid'],
                    data['created_at'],
                    data['updated_at'],
                    data['deleted_at'])
                cur.execute(postgres_insert_query, record_to_insert)

        except BaseException as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(fmt('No insert new subcategory ', json={'data': data}))
            self.conn.rollback()
            return 0
        else:
            self.conn.commit()
            return postgres_insert_query

        finally:
            self.conn.close()
            self.logger.info('done call insert_custom_subcategory')
            
    def insert_custom_nickname(self, list_items: list = None):
        '''
        '''
        self.logger.info('call insert_custom_nickname method')
        self.get_conection()
        try:
            with self.conn.cursor() as cur:
                for data in list_items:

                    postgres_insert_query = '''
                    INSERT INTO public.custom_nickname(
                    uid, 
                    name, 
                    merchant_uid,
                    cuntry_code, 
                    keywords, 
                    user_uid, 
                    created_at, 
                    updated_at, 
                    deleted_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                            '''

                    record_to_insert = (
                        data['uid'],
                        data['name'],
                        data['merchant_uid'],
                        data['cuntry_code'],
                        data['keywords'],
                        data['user_uid'],
                        data['created_at'],
                        data['updated_at'],
                        data['deleted_at'])
                    cur.execute(postgres_insert_query, record_to_insert)

        except BaseException as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(fmt('No insert features ', json={'data': list_items}))
            self.conn.rollback()
            return 0
        else:
            self.conn.commit()
            return postgres_insert_query

        finally:
            self.conn.close()
            self.logger.info('done call insert_custom_nickname')

    def update_custom_category(self, data: dict = None):
        '''
        '''
        dt = datetime.now(timezone.utc).isoformat()

        data['created_at'] = dt
        data['updated_at'] = dt
        data['deleted_at'] = ''
        
        self.logger.info('call update_custom_category method')
        self.get_conection()
        try:
            with self.conn.cursor() as cur:
                postgres_insert_query = '''
                UPDATE public.custom_category SET 
                name=(%s),
                keywords=(%s),
                user_uid=(%s),
                created_at=(%s),
                updated_at=(%s),
                deleted_at=(%s)

                WHERE uid=(%s)
                
                        '''

                record_to_insert = (
                    data['name'],
                    data['keywords'],
                    data['user_uid'],
                    data['created_at'],
                    data['updated_at'],
                    data['deleted_at'],
                    data['uid'])
                cur.execute(postgres_insert_query, record_to_insert)

        except BaseException as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(fmt('No update custom category ', json={'data': data}))
            self.conn.rollback()
            return 0
        else:
            self.conn.commit()
            return postgres_insert_query

        finally:
            self.conn.close()
            self.logger.info('done call updated_custom_category')
    
    def update_custom_subcategory(self, data: dict = None):
        '''
        '''
        self.logger.info('call update_custom_subcategory method')
        self.get_conection()
        try:
            with self.conn.cursor() as cur:
                postgres_insert_query = '''
                UPDATE public.custom_subcategory SET 
                category_uid=(%s),
                name=(%s),
                icon_uid=(%s),
                color_uid=(%s),
                keywords=(%s),
                user_uid=(%s),
                created_at=(%s),
                updated_at=(%s),
                deleted_at=(%s)

                WHERE uid=(%s)
                
                '''
                
                record_to_insert = (
                    data['category_uid'],
                    data['name'],
                    data['icon_uid'],
                    data['color_uid'],
                    data['keywords'],
                    data['user_uid'],
                    data['created_at'],
                    data['updated_at'],
                    data['deleted_at'],
                    data['uid'])

                cur.execute(postgres_insert_query, record_to_insert)

        except BaseException as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(fmt('No update custom subcategory ', json={'data': data}))
            self.conn.rollback()
            return 0
        else:
            self.conn.commit()
            return postgres_insert_query

        finally:
            self.conn.close()
            self.logger.info('done call updated_custom_subcategory')

    def delete_custom_subcategory(self, custom_subcategory_uid: str = None) -> None:

        self.logger.info('call delete_custom_subcategory method ')

        self.get_conection()
        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                                        Delete from public.custom_subcategory where uid = (%s)
                                        '''

                record_to_insert = (custom_subcategory_uid,)
                cur.execute(postgres_select_query, record_to_insert)

        except Exception as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(
                    fmt('No found uid for custom subcategory: ',
                        json={'uid': custom_subcategory_uid})
                )
        else :
            self.conn.commit()
            self.logger.info('done call delete_custom_subcategory method ')

        finally:
            self.conn.close()
            
    def delete_custom_category(self, custom_category_uid: str = None) -> None:

        self.logger.info('call delete_custom_category method ')

        self.get_conection()
        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                                        Delete from public.custom_category where uid = (%s)
                                        '''
                record_to_insert = (custom_category_uid,)
                cur.execute(postgres_select_query, record_to_insert)

        except Exception as e:
            self.logger.exception(e, exc_info=True)
            self.logger.info(
                    fmt('No found uid for custom subcategory: ',
                        json={'uid': custom_category_uid})
                )
        else :
            self.conn.commit()
            self.logger.info('done call delete_custom_category method ')

        finally:
            self.conn.close()
     
    def get_custom_subcategory_info_by_uid(self, custom_subcategory_uid: str = None) -> None:

        self.logger.info('call get_custom_subcategory_uid_info_by_uid method ')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''

                            SELECT name,
                                    category_uid
                            FROM public.custom_subcategory
                            WHERE uid=%(custom_subcategory_uid)s;
                            '''

                param_select = {'custom_subcategory_uid': custom_subcategory_uid}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()
            # reveal_type(obj) would return 'Optional[Person]' here

            if obj is None:
                self.logger.warning(
                    fmt('No found uid for custom subcategory: ',
                        json={'custom_subcategory_uid': custom_subcategory_uid})
                )
                return 0

            else :
                self.logger.info('done call get_custom_subcategory_uid_info_by_uid method ')
                return obj

    def get_custom_subcategory_info_by_parent(self, uid: str = None) -> None:

        self.logger.info('call get_custom_subcategory_info_by_parent method ')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''

                            SELECT uid,
                                    name
                            FROM public.custom_subcategory
                            WHERE category_uid=%(uid)s;
                            '''

                param_select = {'category_uid': uid}
                cur.execute(postgres_select_query, param_select)

                obj = cur.fetchone()

        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()
            # reveal_type(obj) would return 'Optional[Person]' here

            if obj is None:
                self.logger.warning(
                    fmt('No found custom_category_uid(get_custom_subcategory_info_by_parent): ',
                        json={'custom_category_uid': uid})
                )
                return 0

            else :
                self.logger.info('done call get_custom_subcategory_info_by_parent method ')
                return obj

    def what_is(self,uid):
        '''
        Fix Refill comm
        '''
        flag_subcategory = None
        subcategory_name = None
        subcategory_uid = None
        category_uid = None
        category_custom_type = None
        subcategory_custom_type = None
        obj = None
        
        # [mapping_code,name,keywords,category_uid]
        obj = self.get_subcategory_info_by_uid(uid)

        if obj != 0 and obj != None:
            flag_subcategory = True
            subcategory_uid = uid
            category_uid = obj[3]
            subcategory_name = obj[1]
            category_custom_type = 'core'
            subcategory_custom_type = 'core'
            self.logger.info('Found core subcategory ')

        
        elif obj == 0:
            # ['name','parant_iud']
            obj = self.get_custom_subcategory_info_by_uid(uid)
            
            if obj != 0 :
                flag_subcategory = True
                category_uid = obj[1]
                subcategory_uid = uid
                subcategory_name = obj[0]
                category_custom_type = 'custom'
                subcategory_custom_type = 'custom'
                self.logger.info('Found custom subcategory')

            elif  obj == 0:
                # response :[(subcategory_uid, name_subcategory)]
                self.get_subcategory_info_by_parent(uid)
                if obj != 0 :
                    flag_subcategory = False
                    category_uid = uid
                    subcategory_uid = obj[0]
                    subcategory_name = obj[1]
                    category_custom_type = 'core'
                    subcategory_custom_type = 'core'

                    self.logger.info('Found core category by parent')

            else:
                # response :[(subcategory_uid, name_subcategory)]
                self.get_custom_subcategory_info_by_parent(uid)
                if obj != 0 :
                    flag_subcategory = False
                    category_uid = uid
                    subcategory_uid = obj[0]
                    subcategory_name = obj[1]
                    subcategory_custom_type = 'custom'
                    category_custom_type = 'custom'

                    self.logger.info('Found custom subcategory by parent')


        return [category_uid,subcategory_uid,subcategory_name,category_custom_type,subcategory_custom_type,flag_subcategory]
    
    def find_category_uid(self,subcategory_uid):
        type_ = None
        obj = None
        
        obj = self.get_subcategory_info_by_uid(subcategory_uid)
        if obj != 0:
            uid_category = obj[3]
        type_ = 'core'
        
        
        if obj == 0:
            obj = self.get_custom_subcategory_info_by_uid(subcategory_uid)
            type_ = 'custom'

            if obj != 0:
                uid_category = obj[2] 
        
        return [uid_category,type_]
        
    def get_custom_subcat_name_by_uid(self, uid: str = None) -> None:

        self.logger.info("call get_subcategory_name_by_uid method ")

        self.get_conection()
        obj = None  

        with self.conn.cursor() as cur:
            postgres_select_query = """

                        SELECT name
                        FROM public.custom_category
                        WHERE uid=%(uid)s;
                        """

            param_select = {"uid": uid}
            cur.execute(postgres_select_query, param_select)

            obj = cur.fetchone()

            # reveal_type(obj) would return 'Optional[Person]' here

            if obj is None:
                self.logger.warning(
                    fmt("No found custom subcategory_uid (get_custom_subcat_name_by_uid): ",
                        json={"custom_subcategory_uid": uid})
                )
                return 0

            self.logger.info(
                "done call get_subcategory_name_by_uid method ")

            return obj
            
    def get_categorys_names(self) -> None:

        self.logger.info('call get_categorys_name method ')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                        SELECT uid, name
                        FROM public.category
                                        '''
                cur.execute(postgres_select_query)

                obj = cur.fetchall()

        except Exception as e:
            self.logger.exception(e, exc_info=True)

        finally:
            self.conn.close()

            if obj is None:
                self.logger.warning('No table category')
                return 0
            else :
                self.logger.info('done call get_categorys_name method ')
                return obj

    def get_subcategorys_names(self) -> None:

        self.logger.info('call get_subcategorys_names method ')

        self.get_conection()
        obj = None  

        try :
            with self.conn.cursor() as cur:
                postgres_select_query = '''
                            SELECT uid,
                                    name
                            FROM public.subcategory
                            '''

                cur.execute(postgres_select_query)

                obj = cur.fetchall()

        except Exception as e:
            self.logger.exception(e, exc_info=True)
        finally:
            self.conn.close()
            if obj is None:
                self.logger.info('No table subcategory')
                return 0

            else :
                self.logger.info('done call get_subcategorys_names method ')
                return obj



if __name__ == '__main__':
    pass
    # Controller = ControllerPosgrestDB()
    # Controller.get_conection()
