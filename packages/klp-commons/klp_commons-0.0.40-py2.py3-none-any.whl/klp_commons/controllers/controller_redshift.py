
from logging import getLogger
import traceback
from os import getenv
from botocore.exceptions import ClientError
import sqlalchemy as sa
from sqlalchemy.engine.url import URL
from sqlalchemy import orm as sa_orm
from math import ceil
from nanoid import generate
import sqlalchemy as sa
from sqlalchemy.engine.url import URL
from klp_commons.log.structuredMessage import StructuredMessage
from sqlalchemy import orm as sa_orm
from datetime import datetime
from pandas import read_sql_query
from sqlalchemy import text
from datetime import datetime,timedelta
from pandas import DataFrame
from pandas import concat  
#import uuid
#import random

fmt = StructuredMessage
message = 'redshiftController'


class ControllerRedShift:
    def __init__(self):

        self.error = False
        self.url_string= None
        self.metadata = None
        self.session = None
        self.engine = None
        self.region_name = None
        self.driver = 'redshift+redshift_connector'
        self.REDSHIFT_DATABASE = getenv("REDSHIFT_DATABASE")
        self.REDSHIFT_USER = getenv("REDSHIFT_USER")
        self.REDSHIFT_PASSWORD = getenv("REDSHIFT_PASSWORD")
        self.REDSHIFT_HOST = getenv("REDSHIFT_HOST")
        self.REDSHIFT_PORT = getenv("REDSHIFT_PORT")
        self.prefix = getenv("NODE_ENV") + '_'
        self.date_format= '%Y-%m-%dT%H:%M:%S'

        # set self.url_string
        self.get_url()

        # module_name.TopicKafka_name
        self.logger = getLogger(message)

        # Init ()
        self.logger.info("donde init method of ControllerRedShift ")

        """
        engine = sa.create_engine(url)
        Session = sa_orm.sessionmaker()
        Session.configure(bind=engine)
        session = Session()

        # Define Session-based Metadata
        metadata = sa.MetaData(bind=session.bind)

        # table_name
        # metadata
        # engine
        """
          
    def get_url(self):
        
        # build the sqlalchemy URL
        self.url_string = URL.create(
        drivername=self.driver,
        host=self.REDSHIFT_HOST,# Amazon Redshift host
        port=self.REDSHIFT_PORT, # Amazon Redshift port
        database=self.REDSHIFT_DATABASE, # Amazon Redshift database
        username=self.REDSHIFT_USER, # Amazon Redshift username
        password=self.REDSHIFT_PASSWORD # Amazon Redshift password
        )

    def get_conection(self) -> None:

        self.logger.info("call get_conection() method of ControllerRedShift ")

        try:
                
                self.engine = sa.create_engine(self.url_string)
                Session = sa_orm.sessionmaker()
                Session.configure(bind=self.engine)
                self.session = Session()
                # Define Session-based Metadata
                self.metadata = sa.MetaData(bind=self.session.bind)
                
        except ClientError as err:
            self.logger.error('error  get_conection RedShift')
            raise TypeError('error  get_conection RedShift')

        self.logger.info(" Done get_conection() method of RedShift")

    def close_conection(self):          
        self.session.close() 
        self.engine.dispose()

    def execute_query(self,query=None):        

        return read_sql_query(text(query),self.engine)    

    def insert_dim_user(self,dict_values):
        with self.engine.connect() as cur:
            redshift_insert_query = '''
                        INSERT INTO dim_user (user_uid,postcode)
                        VALUES (%s,%s)
                                    '''
            record_to_insert = (
                        dict_values['user_uid'],
                        dict_values['postcode']
                                )
            cur.execute(redshift_insert_query, record_to_insert)
            
    def insert_dim_account(self,dict_values):
        with self.engine.connect() as cur:
            redshift_insert_query = '''
                        INSERT INTO dim_account (account_uid,
                                                    bank_name,
                                                    account_type,
                                                    bank_type)
                        VALUES (%s,%s,%s,%s)
                                    '''
            record_to_insert = (
                        dict_values['account_uid'],
                        dict_values['bank_name'],
                        dict_values['account_type'],
                        dict_values['bank_type']
                                )
            cur.execute(redshift_insert_query, record_to_insert)      
            
    def insert_dim_dates(self,dict_values):
        with self.engine.connect() as cur:
            redshift_insert_query = '''
                        INSERT INTO dim_dates (
                                                transaction_date,
                                                day_of_month,
                                                month_of_year,
                                                month_name,
                                                year,
                                                week_of_month,
                                                quarter_of_year
                                                )
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                                    '''
            record_to_insert = (
                        dict_values['transaction_date'],
                        dict_values['day_of_month'],
                        dict_values['month_of_year'],
                        dict_values['month_name'],
                        dict_values['year'],
                        dict_values['week_of_month'],
                        dict_values['quarter_of_year']
                                )
            cur.execute(redshift_insert_query, record_to_insert)
            
    def date_descomposition(self,transaction_date):
        
        transaction_date = datetime.strptime(transaction_date, self.date_format).date()
        year = transaction_date.year
        month = transaction_date.month
        month_name = transaction_date.strftime('%b')
        day = transaction_date.day
        week_of_month = self.week_of_month(transaction_date)
        quarter_of_year = self.quarter_of_year(transaction_date)
        
        result = {
        'transaction_date':transaction_date,
        'day_of_month':day,
        'month_of_year':month,
        'month_name':month_name,
        'year':year,
        'week_of_month':week_of_month,
        'quarter_of_year':quarter_of_year
        }

        return result 
        
        # transaction_date.dt.weekday
        #transaction_date.dt.weekday_name

    def test(self):

        sql = "SELECT * FROM staging;"
        print(read_sql_query(text(sql),self.engine))
        
    def select_is_essential(self, start='2023-03-07 00:00:00', end = '2023-03-07 23:59:59'):        

        sql = f"""SELECT
                    dim_transactions.transaction_uid,
                    dim_transactions.nickname_recommended,
                    dim_transactions.is_essential_collective,
                    dim_transactions.is_essential_custom,
                    dim_transactions.is_essential_recommended
                FROM 
                    fact_transactions, dim_transactions
                WHERE 
                    fact_transactions.updated_at 
                        BETWEEN '{start}' and '{end}';"""
        return read_sql_query(text(sql),self.engine)
    
    def select_is_membership(self, start='2023-03-07 00:00:00', end = '2023-03-07 23:59:59'):        

        sql = f"""SELECT
                    dim_transactions.transaction_uid,
                    dim_transactions.nickname_recommended,
                    dim_transactions.is_membership_collective,
                    dim_transactions.is_membership_custom,
                    dim_transactions.is_membership_recommended
                FROM 
                    fact_transactions, dim_transactions
                WHERE 
                    fact_transactions.updated_at 
                        BETWEEN '{start}' and '{end}';"""
        return read_sql_query(text(sql),self.engine)
    
    def exists_user(self,user_uid):

        sql = f"""
                SELECT EXISTS (select 1 FROM dim_user
                WHERE dim_user.user_uid = '{user_uid}');
                """
        return read_sql_query(text(sql),self.engine)
      
    def select_nickname(self, start='2023-03-07 00:00:00', end = '2023-03-07 23:59:59'):        

        sql = f"""SELECT
                    dim_transactions.transaction_uid,
                    dim_transactions.clean_description,
                    dim_transactions.nickname_collective,
                    dim_transactions.nickname_custom,
                    dim_transactions.nickname_recommended
                FROM 
                    fact_transactions, dim_transactions
                WHERE 
                    fact_transactions.updated_at 
                        BETWEEN '{start}' and '{end}';"""
        return read_sql_query(text(sql),self.engine)
    
    def select_subcategory(self, start='2023-03-07 00:00:00', end = '2023-03-07 23:59:59'):        

        sql = f"""SELECT
                    dim_transactions.transaction_uid,
                    dim_transactions.nickname_recommended,
                    dim_transactions.subcategory_uid_collective,
                    dim_transactions.subcategory_uid_custom,
                    dim_transactions.subcategory_uid_recommended
                FROM 
                    fact_transactions, dim_transactions
                WHERE 
                    fact_transactions.updated_at 
                        BETWEEN '{start}' and '{end}';"""
        return read_sql_query(text(sql),self.engine)
    
    def exists(self, table_name,column_name ,value ):

        sql = "SELECT "+ column_name +" FROM " + table_name + " WHERE " + column_name + " = '"+ value +"';"
        
        if read_sql_query(text(sql),self.engine).shape[0] != 0:
            return True
        else : return False

    def week_of_month(self,dt):
        """ Returns the week of the month for the specified date.
        """

        first_day = dt.replace(day=1)

        dom = dt.day
        adjusted_dom = dom + first_day.weekday()

        return int(ceil(adjusted_dom/7.0))

    def quarter_of_year(self,dt):

        return ceil(dt.month/3.)

    def mapping_dict_(self,dict_values):
        return {
            'approved_asset' : dict_values['approved_asset'],
            'approved_business' : dict_values['approved_business'],
            'approved_category' : dict_values['approved_category'],
            'approved_frequency' : dict_values['approved_frequency'],
            'approved_income_source' : dict_values['approved_income_source'],
            'approved_is_essential' : dict_values['approved_is_essential'],
            'approved_is_loan_received' : dict_values['approved_is_loan_received'],
            'approved_is_loan_requested' : dict_values['approved_is_loan_requested'],
            'approved_is_membership' : dict_values['approved_is_membership'],
            'approved_nickname' : dict_values['approved_nickname'],
            'approved_person' : dict_values['approved_person'],
            'approved_special_moment' : dict_values['approved_special_moment'],
            'approved_subcategory' : dict_values['approved_subcategory'],
            'asset_uid_collective' : dict_values['asset_uid_def_collect'],
            'asset_uid_custom' : dict_values['asset_uid_def_usr'],
            'asset_uid_recommended' : dict_values['asset_uid_def_algo'],
            'business_uid_collective' : dict_values['business_uid_def_collect'],
            'business_uid_custom' : dict_values['business_uid_def_usr'],
            'business_uid_recommended' : dict_values['business_uid_def_algo'],
            'category_custom_type' : dict_values['category_custom_type'],
            'category_uid_collective' : dict_values['category_uid_def_collect'],
            'category_uid_custom' : dict_values['category_uid_def_usr'],
            'category_uid_recommended' : dict_values['category_uid_def_algo'],
            'classified_date' : dict_values['classified_date'],
            'clean_description' : dict_values['clean_description'],
            'country_code' : dict_values['country_code'],
            'created_homologation_date' : dict_values['created_homologation_date'],
            'flow_type' : dict_values['flow_type'],
            'frequency_uid_collective' : dict_values['frequency_uid_def_collect'],
            'frequency_uid_custom' : dict_values['frequency_uid_def_usr'],
            'frequency_uid_recommended' : dict_values['frequency_uid_def_algo'],
            'income_source_uid_collective' : dict_values['income_source_uid_def_collect'],
            'income_source_uid_custom' : dict_values['income_source_uid_def_usr'],
            'income_source_uid_recommended' : dict_values['income_source_uid_def_algo'],
            'is_essential_collective' : dict_values['is_essential_def_collect'],
            'is_essential_custom' : dict_values['is_essential_def_usr'],
            'is_essential_recommended' : dict_values['is_essential_def_algo'],
            'is_loan_received_collective' : dict_values['is_loan_received_def_collect'],
            'is_loan_received_custom' : dict_values['is_loan_received_def_usr'],
            'is_loan_received_recommended' : dict_values['is_loan_received_def_algo'],
            'is_loan_requested_collective' : dict_values['is_loan_requested_def_collect'],
            'is_loan_requested_custom' : dict_values['is_loan_requested_def_usr'],
            'is_loan_requested_recommended' : dict_values['is_loan_requested_def_algo'],
            'is_membership_collective' : dict_values['is_membership_def_collect'],
            'is_membership_custom' : dict_values['is_membership_def_usr'],
            'is_membership_recommended' : dict_values['is_membership_def_algo'],
            'language_code' : dict_values['language_code'],
            'message_type' : dict_values['message_type'],
            'model_classification_version' : dict_values['model_classification_version'],
            'model_collective_version' : dict_values['model_collective_version'],
            'model_nickname_version' : dict_values['model_nickname_version'],
            'model_nlp_version' : dict_values['model_nlp_version'],
            'nickname_collective' : dict_values['nickname_collect'],
            'nickname_custom' : dict_values['nickname_usr'],
            'nickname_recommended' : dict_values['nickname_algo'],
            'original_created_date' : dict_values['original_created_date'],
            'person_uid_collective' : dict_values['person_uid_def_collect'],
            'person_uid_custom' : dict_values['person_uid_def_usr'],
            'person_uid_recommended' : dict_values['person_uid_def_algo'],
            'source_description' : dict_values['source_description'],
            'special_moment_uid_collective' : dict_values['special_moment_uid_def_collect'],
            'special_moment_uid_custom' : dict_values['special_moment_uid_def_usr'],
            'special_moment_uid_recommended' : dict_values['special_moment_uid_def_algo'],
            'subcategory_custom_type' : dict_values['subcategory_custom_type'],
            'subcategory_uid_collective' : dict_values['subcategory_uid_def_collect'],
            'subcategory_uid_custom' : dict_values['subcategory_uid_def_usr'],
            'subcategory_uid_recommended' : dict_values['subcategory_uid_def_algo'],
            'transaction_uid' : dict_values['transaction_uid'],
            'updated_date' : dict_values['updated_at'],
            'validated' : dict_values['validated'],
            'validated_date' : dict_values['creted_at']                    
        }

    def insert_dim_transaction(self,dict_values):
        with self.engine.connect() as cur:
            redshift_insert_query = '''
                        INSERT INTO dim_transactions (
                        approved_asset,
                        approved_business,
                        approved_category,
                        approved_frequency,
                        approved_income_source,
                        approved_is_essential,
                        approved_is_loan_received,
                        approved_is_loan_requested,
                        approved_is_membership,
                        approved_nickname,
                        approved_person,
                        approved_special_moment,
                        approved_subcategory,
                        asset_uid_collective,
                        asset_uid_custom,
                        asset_uid_recommended,
                        business_uid_collective,
                        business_uid_custom,
                        business_uid_recommended,
                        category_custom_type,
                        category_uid_collective,
                        category_uid_custom,
                        category_uid_recommended,
                        classified_date,
                        clean_description,
                        country_code,
                        created_homologation_date,
                        flow_type,
                        frequency_uid_collective,
                        frequency_uid_custom,
                        frequency_uid_recommended,
                        income_source_uid_collective,
                        income_source_uid_custom,
                        income_source_uid_recommended,
                        is_autocategorized,
                        is_essential_collective,
                        is_essential_custom,
                        is_essential_recommended,
                        is_loan_received_collective,
                        is_loan_received_custom,
                        is_loan_received_recommended,
                        is_loan_requested_collective,
                        is_loan_requested_custom,
                        is_loan_requested_recommended,
                        is_membership_collective,
                        is_membership_custom,
                        is_membership_recommended,
                        language_code,
                        message_type,
                        model_classification_version,
                        model_collective_version,
                        model_nickname_version,
                        model_nlp_version,
                        nickname_collective,
                        nickname_custom,
                        nickname_recommended,
                        original_created_date,
                        person_uid_collective,
                        person_uid_custom,
                        person_uid_recommended,
                        source_description,
                        special_moment_uid_collective,
                        special_moment_uid_custom,
                        special_moment_uid_recommended,
                        subcategory_custom_type,
                        subcategory_uid_collective,
                        subcategory_uid_custom,
                        subcategory_uid_recommended,
                        transaction_uid,
                        updated_date,
                        validated,
                        validated_date
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
                                 dict_values['approved_asset'],
                                dict_values['approved_business'],
                                dict_values['approved_category'],
                                dict_values['approved_frequency'],
                                dict_values['approved_income_source'],
                                dict_values['approved_is_essential'],
                                dict_values['approved_is_loan_received'],
                                dict_values['approved_is_loan_requested'],
                                dict_values['approved_is_membership'],
                                dict_values['approved_nickname'],
                                dict_values['approved_person'],
                                dict_values['approved_special_moment'],
                                dict_values['approved_subcategory'],
                                dict_values['asset_uid_def_collect'],
                                dict_values['asset_uid_def_usr'],
                                dict_values['asset_uid_def_algo'],
                                dict_values['business_uid_def_collect'],
                                dict_values['business_uid_def_usr'],
                                dict_values['business_uid_def_algo'],
                                dict_values['category_custom_type'],
                                dict_values['cat_uid_def_collect'],
                                dict_values['cat_uid_def_usr'],
                                dict_values['cat_uid_def_algo'],
                                dict_values['classified_at'],
                                dict_values['clean_description'],
                                dict_values['country_code'],
                                dict_values['created_at_homologation'],
                                dict_values['flow_type'],
                                dict_values['frequency_uid_def_collect'],
                                dict_values['frequency_uid_def_usr'],
                                dict_values['frequency_uid_def_algo'],
                                dict_values['income_source_uid_def_collect'],
                                dict_values['income_source_uid_def_usr'],
                                dict_values['income_source_uid_def_algo'],
                                dict_values['is_autocategorized'],
                                dict_values['is_essential_def_collect'],
                                dict_values['is_essential_def_usr'],
                                dict_values['is_essential_def_algo'],
                                dict_values['is_loan_received_def_collect'],
                                dict_values['is_loan_received_def_usr'],
                                dict_values['is_loan_received_def_algo'],
                                dict_values['is_loan_requested_def_collect'],
                                dict_values['is_loan_requested_def_usr'],
                                dict_values['is_loan_requested_def_algo'],
                                dict_values['is_membership_def_collect'],
                                dict_values['is_membership_def_usr'],
                                dict_values['is_membership_def_algo'],
                                dict_values['language_code'],
                                dict_values['message_type'],
                                dict_values['model_classification_version'],
                                dict_values['model_collective_version'],
                                dict_values['model_nickname_version'],
                                dict_values['model_nlp_version'],
                                dict_values['nickname_collect'],
                                dict_values['nickname_usr'],
                                dict_values['nickname_algo'],
                                dict_values['original_created_date'],
                                dict_values['person_uid_def_collect'],
                                dict_values['person_uid_def_usr'],
                                dict_values['person_uid_def_algo'],
                                dict_values['source_description'],
                                dict_values['special_moment_uid_def_collect'],
                                dict_values['special_moment_uid_def_usr'],
                                dict_values['special_moment_uid_def_algo'],
                                dict_values['subcategory_custom_type'],
                                dict_values['subcat_uid_def_collect'],
                                dict_values['subcat_uid_def_usr'],
                                dict_values['subcat_uid_def_algo'],
                                dict_values['transaction_uid'],
                                dict_values['updated_at'],
                                dict_values['validated'],
                                dict_values['created_at']                               
                                                       )
            cur.execute(redshift_insert_query, record_to_insert)

    def insert_dim_visualization(self,dict_values):
        with self.engine.connect() as cur:
            redshift_insert_query = '''
                        INSERT INTO dim_visualization (
                                asset_uid,
                                business_uid,
                                category_uid,
                                classified_date,
                                clean_description,
                                country_code,
                                created_homologation_date,
                                description,
                                flow_type,
                                frequency_uid,
                                is_autocategorized,
                                income_source_uid,
                                is_essential,
                                is_loan_received,
                                is_loan_requested,
                                is_membership,
                                language_code,
                                message_type,
                                original_created_date,
                                person_uid,
                                source_description,
                                special_moment_uid,
                                subcategory_uid,
                                transaction_uid,
                                updated_date,
                                validated,
                                validated_date
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
                        dict_values['asset_uid'],
                        dict_values['business_uid'],
                        dict_values['category_uid'],
                        dict_values['classified_at'],
                        dict_values['clean_description'],
                        dict_values['country_code'],
                        dict_values['created_at_homologation'],
                        dict_values['description'],
                        dict_values['flow_type'],
                        dict_values['frequency_uid'],
                        dict_values['is_autocategorized'],
                        dict_values['income_source_uid'],
                        dict_values['is_essential'],
                        dict_values['is_loan_received'],
                        dict_values['is_loan_requested'],
                        dict_values['is_membership'],
                        dict_values['language_code'],
                        dict_values['message_type'],
                        dict_values['original_created_date'],
                        dict_values['person_uid'],
                        dict_values['source_description'],
                        dict_values['special_moment_uid'],
                        dict_values['subcategory_uid'],
                        dict_values['transaction_uid'],
                        dict_values['updated_at'],
                        dict_values['validated'],
                        dict_values['created_at']

                            )
            cur.execute(redshift_insert_query, record_to_insert)

    def insert_fact_transactions(self,dict_values):
        with self.engine.connect() as cur:
            redshift_insert_query = '''
                        INSERT INTO fact_transactions (
                                                transaction_date,
                                                transaction_uid,
                                                user_uid,
                                                account_uid,
                                                amount,
                                                currency
                                                )
                        VALUES (%s,%s,%s,%s,%s,%s)
                                    '''
            record_to_insert = (
                        dict_values['transaction_date'],
                        dict_values['transaction_uid'],
                        dict_values['user_uid'],
                        dict_values['account_uid'],
                        dict_values['amount'],
                        dict_values['currency']
                                )
            cur.execute(redshift_insert_query, record_to_insert)

    def insert_fact_visualization(self,dict_values):
        with self.engine.connect() as cur:
            redshift_insert_query = '''
                        INSERT INTO fact_visualization (
                                                transaction_date,
                                                transaction_uid,
                                                user_uid,
                                                account_uid,
                                                amount,
                                                currency
                                                )
                        VALUES (%s,%s,%s,%s,%s,%s)
                                    '''
            record_to_insert = (
                        dict_values['transaction_date'],
                        dict_values['transaction_uid'],
                        dict_values['user_uid'],
                        dict_values['account_uid'],
                        dict_values['amount'],
                        dict_values['currency']
                                )
            cur.execute(redshift_insert_query, record_to_insert)
            
    def insert_(self):
        """
        INSERT INTO target
        SELECT * FROM temp
        WHERE temp.primary_key NOT IN (SELECT DISTINCT primary_key FROM target)
        """

    def creted_table(self,table_name = 'staging'):
        
        RedshiftDBTable = sa.Table(
                                table_name,
                                self.metadata,
                                sa.Column('session_id', sa.VARCHAR(80)),
                                sa.Column('click_region', sa.VARCHAR(100)),
                                sa.Column('product_id', sa.VARCHAR(40)),
                                redshift_diststyle='KEY',
                                redshift_distkey='session_id',
                                redshift_sortkey='product_id'
                                    )

        # Drop the table if it already exists
        if sa.inspect(self.engine).has_table(table_name):
            RedshiftDBTable.drop(bind=self.engine)

        # Create the table (execute the "CREATE TABLE" SQL statement for "")
        RedshiftDBTable.create(bind=self.engine)
        self.session.commit()
        
    def get_date_range(self,num_days = 30):
        # today 
        to_date = datetime.utcnow()
        from_date = to_date  - timedelta(days=num_days)

        return from_date, to_date

    def get_collective_is_essential(self):

        [from_date, to_date ]= self.get_date_range()

        self.get_conection()
        df_is_essential = self.select_is_essential(start = from_date, end = to_date).dropna(subset=['nickname_recommended'])

        df_is_essential = df_is_essential[df_is_essential.nickname_recommended != "No Suggestion"]
        cols = [
                'is_essential_collective',
                'is_essential_custom',
                'is_essential_recommended'
                ]

        list_cols = []

        for col in cols :
            df_tmp = df_is_essential[['transaction_uid','nickname_recommended', col]]
            df_tmp.rename(columns={col: "is_essential"},inplace=True)
            list_cols.append(df_tmp)

        result = concat(list_cols,axis=0)
        result.dropna(inplace = True)
        result.drop_duplicates(subset=['transaction_uid'], keep='last',inplace = True)
        result= DataFrame(result.groupby(['nickname_recommended','is_essential']).count()['transaction_uid'] \
                                   .groupby(['nickname_recommended','is_essential']).agg('max'))

        return result.reset_index().drop_duplicates(subset='nickname_recommended', keep='first').set_index('nickname_recommended')['is_essential'].to_dict()

    def get_collective_is_membership(self):

        [from_date, to_date ]= self.get_date_range()

        self.get_conection()
        df_is_membership = self.select_is_membership(start = from_date, end = to_date).dropna(subset=['nickname_recommended'])

        df_is_membership = df_is_membership[df_is_membership.nickname_recommended != "No Suggestion"]
        cols = [
                'is_membership_collective',
                'is_membership_custom',
                'is_membership_recommended'
                ]

        list_cols = []

        for col in cols :
            df_tmp = df_is_membership[['transaction_uid','nickname_recommended', col]]
            df_tmp.rename(columns={col: "is_membership"},inplace=True)
            list_cols.append(df_tmp)

        result = concat(list_cols,axis=0)
        result.dropna(inplace = True)
        result.drop_duplicates(subset=['transaction_uid'], keep='last',inplace = True)
        result= DataFrame(result.groupby(['nickname_recommended','is_membership']).count()['transaction_uid'] \
                                   .groupby(['nickname_recommended','is_membership']).agg('max'))

        return result.reset_index().drop_duplicates(subset='nickname_recommended', keep='first').set_index('nickname_recommended')['is_membership'].to_dict()

    def get_collective_nickname(self):

        [from_date, to_date ]= self.get_date_range()

        self.get_conection()
        df_nickname = self.select_nickname(start = from_date, end = to_date).dropna(subset=['clean_description'])

        df_nickname = df_nickname[df_nickname.nickname_recommended != "No Suggestion"]
        
        cols = [
                'nickname_collective',
                'nickname_custom',
                'nickname_recommended'
                ]

        list_cols = []

        for col in cols :
            df_tmp = df_nickname[['transaction_uid','clean_description', col]]
            df_tmp.rename(columns={col: "nickname"},inplace=True)
            list_cols.append(df_tmp)

        result = concat(list_cols,axis=0)
        result.dropna(inplace = True)
        result.drop_duplicates(subset=['transaction_uid'], keep='last',inplace = True)
        result= DataFrame(result.groupby(['clean_description','nickname']).count()['transaction_uid'] \
                                   .groupby(['clean_description','nickname']).agg('max'))

        return result.reset_index().drop_duplicates(subset='clean_description', keep='first').set_index('clean_description')['nickname'].to_dict()

    def get_collective_subcategory(self):

        [from_date, to_date ]= self.get_date_range()

        self.get_conection()
        df_subcategory = self.select_subcategory(start = from_date, end = to_date).dropna(subset=['nickname_recommended'])

        df_subcategory = df_subcategory[df_subcategory.nickname_recommended != "No Suggestion"]
        
        cols = [
            'subcategory_uid_collective',
            'subcategory_uid_custom',
            'subcategory_uid_recommended'
                ]

        list_cols = []

        for col in cols :
            df_tmp = df_subcategory[['transaction_uid','nickname_recommended', col]]
            df_tmp.rename(columns={col: "subcategory_uid"},inplace=True)
            list_cols.append(df_tmp)

        result = concat(list_cols,axis=0)
        result.dropna(inplace = True)
        result.drop_duplicates(subset=['transaction_uid'], keep='last',inplace = True)
        result= DataFrame(result.groupby(['nickname_recommended','subcategory_uid']).count()['transaction_uid'] \
                                   .groupby(['nickname_recommended','subcategory_uid']).agg('max'))

        return result.reset_index().drop_duplicates(subset='nickname_recommended', keep='first').set_index('nickname_recommended')['subcategory_uid'].to_dict()