

from numpy import sum as sum_, array, floor
from pandas import Series,concat,DataFrame, to_datetime
from datetime import datetime,timedelta
from klp_commons.controllers.controller_mongodb import ControllerMongoDB
from klp_commons.controllers.controller_postgresdb import ControllerPostgresDB

class Summary:
    """
    """

    # Variables de clase

    def __init__(self,from_date_str = None, num_days= 30):
        self.CMongo = ControllerMongoDB()
        self.CMongo.get_con_db('klopp')
        
        self.CPDB = ControllerPostgresDB()

        self.category_names = self.CPDB.get_categorys_names()
        self.subcategory_names = self.CPDB.get_subcategorys_names()
        
        self.dict_names = {k:v for k,v in self.category_names}

        self.rename_cols_ = [
                    'user_id', 
                    'id',
                    'description',
                    'clean_description',
                    'original_created_at',
                    'validated',
                    'bank',
                    'subcategory_precategorized',
                    'subcagegory_custom',
                    'category_precategorized',
                    'category_custom',
                    'nickname_suggested',
                    'nickname_custom',
                    'change_nickname',
                    'change_category',
                    'change_subcategory',
                    'updated_num',
                    'classification_date',
                    'classification_time',
                    'created_at_date',
                    'created_at_time',
                    'updated_at_date',
                    'updated_at_time'
                            ]
        self.rename_cols = [
                    'user_id', 
                    'id',
                    'description',
                    'clean_description',
                    'classified_at',
                    'original_created_at',
                    'created_at',
                    'updated_at',
                    'validated',
                    'bank',
                    'subcategory_precategorized',
                    'subcagegory_custom',
                    'category_precategorized',
                    'category_custom',
                    'nickname_suggested',
                    'nickname_custom',
                    'change_nickname',
                    'change_category',
                    'change_subcategory',
                    'updated_num'
                    ]
        self.num_days = num_days
        self.last_period = None
        self.from_date = from_date_str
        self.to_date = None
        self.set_date_range()
        
    def set_date_range(self):
        self.from_date = datetime.strptime(self.from_date , '%Y-%m-%d')
        self.to_date = self.from_date + timedelta(days=self.num_days)
        self.last_period = self.from_date - timedelta(days=self.num_days)

    def agg_master(self):
        self.query_summary_category = [
            # { "$unwind": "$history-track" },
            {
            "$match": {
                "$or":[
                    {"created_at": {'$gte':self.from_date,'$lt': self.to_date}},
                    {"history-track.updated_at": {'$gte':self.from_date,'$lt': self.to_date}}
                        ]
                    }
            },
        {'$group': 
                 {'_id': {
                        'user_id': "$user_uid",
                        'id':'$_id',
                        'original_created_at': "$original_created_at",
                        'classified_at': "$history-track.classified_at",
                        'created_at': "$created_at" ,
                        'transaction_type': "$type" ,
                        'updated_at': "$history-track.updated_at",
                        'description':'$source_description',
                        'clean_description':'$history-track.clean_description',
                        'category_id': "$history-track.category_uid",
                        'nickname': '$history-track.nickname',
                        'type': "$history-track.type",
                        'bank': "$account_institution_name",
                        'change_nickname': '$history-track.change_nickname',
                        'change_subcategory': '$history-track.change_subcat',
                        'change_category': '$history-track.change_cat',
                        'validated': '$history-track.validated',
                       },
                'count': {"$sum": 1}
                }

             
            }
            
        ]

        
        
        self.agg_result = self.CMongo.con_db.fact.aggregate(self.query_summary_category) 

        df_list= list()
        
        for i in self.agg_result: 
            df_tmp = DataFrame(i)
            count = df_tmp['count'] 
            del df_tmp['count']
            df_tmp.loc['count', :] = [count.values]
            df_list.append(DataFrame(df_tmp).transpose()) 

        self.df_agg_master = concat(df_list) 
        self.df_agg_master.reset_index(inplace = True, drop = True)
        self.df_agg_master['count'] = self.df_agg_master['count'].apply(Series)[1]
        
        del self.df_agg_master['count']
        
        self.df_agg_master['updated_at'].fillna(False,inplace = True)
        #self.df_agg_master['validated'] = self.df_agg_master['validated'].fillna(False)
    def summary_master(self):
        
        self.agg_master()
        df_summ = self.df_agg_master 
        df_summ.reset_index(inplace = True)
        df_summ['category_name'] = self.map_names(df_summ.category_id.values.tolist())

        # error , se elimino subcategoryname de el flujo de trabajo de categorization
        # ya no se almacena; es necesario hacer un cruce con el subcategoyr uid
        tmp1 = df_summ['subcategory_name'].apply(Series).add_prefix('SUBCATEGORY_NAME_LEVEL_')[['SUBCATEGORY_NAME_LEVEL_0','SUBCATEGORY_NAME_LEVEL_1']]
        
        tmp2 = df_summ['category_name'].apply(Series).add_prefix('CATEGORY_NAME_LEVEL_')[['CATEGORY_NAME_LEVEL_0','CATEGORY_NAME_LEVEL_1']]
        
        tmp3 =df_summ['nickname'].apply(Series).add_prefix('NICKNAME_LEVEL_')[['NICKNAME_LEVEL_0','NICKNAME_LEVEL_1']]

        tmp4 = df_summ['change_nickname'].apply(Series,dtype=object).add_prefix('change_nickname_LEVEL_')[['change_nickname_LEVEL_0']]
        tmp5 = df_summ['change_subcategory'].apply(Series,dtype=object).add_prefix('change_subcategory_LEVEL_')[['change_subcategory_LEVEL_0']]
        tmp6 =df_summ['change_category'].apply(Series,dtype=object).add_prefix('change_category_LEVEL_')[['change_category_LEVEL_0']]
        
        
        df_summ['validated'] = df_summ['validated'].apply(Series,dtype=object).add_prefix('validated_LEVEL_')[['validated_LEVEL_0']]
        
        df_summ['updated_at'] = df_summ['updated_at'].apply(Series,dtype=object).add_prefix('updated_at_LEVEL_')[['updated_at_LEVEL_1']]
        
        df_tmp = df_summ['clean_description'].apply(Series,dtype=object)
        
        if df_tmp.empty :
            df_summ['clean_description'] = df_summ['description'].apply(Series,dtype=object)
        else : 
            df_summ['clean_description'] = df_summ['clean_description'].apply(Series,dtype=object)
            
        df_tmp = df_summ['classified_at'].apply(Series,dtype=object)
        
        if df_tmp.empty : 
            df_summ['classified_at'] =  df_summ['updated_at']
        else :
            df_summ['classified_at'] = df_summ['classified_at'].apply(Series,dtype=object)

        df_expand = df_summ['type'].apply(Series)
        df_expand = df_expand.apply(Series.value_counts, axis=1)

        if 'report-expense-updated' in df_expand.columns :
            df_expand = df_expand[['transaction-categorized','report-expense-created','report-expense-updated']]
            df_expand.columns = ['pre-categorized','validate_','updated']
            df_expand = df_expand['updated']
        else :
            
            df_expand['updated'] = 0
            del df_expand['transaction-categorized']
            del df_expand['report-expense-created']
            
            
            
        del  df_summ['type']
        
        cols = ['user_id',
                'id',
                'description',
                'clean_description',
                'classified_at',
                'original_created_at',
                'created_at',
                'updated_at',
                'validated',
                'bank',
               'transaction_type']
        
        
        frames = [df_summ[cols],tmp1,tmp2,tmp3,tmp4,tmp6,tmp5,df_expand]

        df_final = concat(frames, axis=1)
        df_final.fillna(False,inplace=True)
        
        df_final['bank'] = df_final.bank.str.split(pat = '_', expand = True)[0]
        
        self.df_master = df_final

    def trasform_datetime(self):
        
        self.df_master['classification_date'] = to_datetime(s.df_master.classified_at).dt.date
        self.df_master['classification_time'] = to_datetime(s.df_master.classified_at).dt.time
        
        self.df_master['created_at_date'] = to_datetime(s.df_master.classified_at).dt.date
        self.df_master['created_at_time'] = to_datetime(s.df_master.classified_at).dt.time
        
        
        self.df_master['updated_at_date'] = to_datetime(s.df_master.classified_at).dt.date
        self.df_master['updated_at_time'] = to_datetime(s.df_master.classified_at).dt.time     
        
    def remove_conflicts(self):
        ids_list = self.df_master[self.df_master.created_at<self.from_date].id.values.tolist()
        
        self.CMongo.con_db.AggMaster.cube.delete_many({"ID": { "$in": ids_list}})
        self.CMongo.con_db.FacMaster.cube.delete_many({"ID": { "$in": ids_list}}) 
        
        #del self.df_master['classified_at']
        #del self.df_master['created_at']
        #del self.df_master['updated_at']
        self.df_master.columns = self.rename_cols
   
    def add_new_data(self):
        self.df_agg_master['updated_at'].fillna(False,inplace = True)
        self.CMongo.con_db.AggMaster.cube.insert_many(self.df_agg_master.to_dict(orient='records'))
        self.CMongo.con_db.FacMaster.cube.insert_many(self.df_master.to_dict(orient='records'))

    def map_names(self,list_nested_uids):
        list_final = list ()
        for l in list_nested_uids:
            list_nested =list()
            for item in l:
                item = self.dict_names.get(item,item)
                list_nested.append(item)
            
            list_final.append(list_nested)
        return DataFrame(array(list_final,dtype=object))
      
    def summary_category_lv1 (self):
        columns_cat_level_1 = ['Category',
                               'Users (With this category used)',
                               'Classified transactions',
                               'Transaction per review']
        
        grouped = self.df_master .groupby(['category_precategorized'])
        
        summary_gruped = grouped.agg({'user_id': Series.nunique,
                             'id': Series.nunique,
                             'validated': Series.sum})
        
        summary_gruped.reset_index(inplace = True)
        summary_gruped['validated'] = summary_gruped['id'] - summary_gruped['validated'] 
        summary_gruped.columns = columns_cat_level_1
        
        return summary_gruped
        
    def summary_nickname_lv1(self):
        
        columns_nickname_level_1 = [
                            'Precategorized',
                            'Nicknames suggesteds',
                            'Number of changes nicknames',
                            'Percentage of changes nicknames',
                            'Nickname accuracy percentage']  
        
        #self.df_master['nickname_detected'] = self.df_master['nickname_suggested'] != ''
        
        grouped = self.df_master .groupby(['category_precategorized'])
        summary_gruped = grouped.agg({
                'nickname_suggested': Series.count,
                 'change_nickname': Series.sum,

        })
        
        summary_gruped.reset_index(inplace = True)
        
        summary_gruped['Percentage of changes'] = (summary_gruped['change_nickname'] *100/ 
              summary_gruped['nickname_suggested']).apply(floor)
        tmp  =summary_gruped['nickname_suggested']-summary_gruped['change_nickname']
        
        summary_gruped['Nickname accuracy percentage'] = (tmp/summary_gruped['nickname_suggested']*100).apply(floor)
        

        summary_gruped.columns = columns_nickname_level_1
        
        del summary_gruped['Precategorized']
        return summary_gruped
    
    def summary_subcategory_lv1(self):
        columns_subcat_level_1 = ['category_precategorized',
        'Subcategory suggested',
        'Number of changes subcategory',
        'Percentage of changes subcategory',
        'Subcategory accuracy percent'
                          ]

    
        grouped = self.df_master .groupby(['category_precategorized'])
        
        summary_gruped = grouped.agg({'subcategory_precategorized': Series.count,
             'change_subcategory': Series.sum})
        summary_gruped.reset_index(inplace = True)
        
        summary_gruped['Percentage of changes'] = (summary_gruped['change_subcategory'] *100/ 
          summary_gruped['subcategory_precategorized']).apply(floor)
        tmp  =summary_gruped['subcategory_precategorized']-summary_gruped['change_subcategory']
        summary_gruped['Subcategory accuracy percentage'] = (tmp/summary_gruped['subcategory_precategorized']*100).apply(floor)
        summary_gruped.columns = columns_subcat_level_1
        
        del summary_gruped['category_precategorized']
        return summary_gruped
    
    def summary_category_lv2(self):

        columns_cat_level_2 = [
                'Category',
                'Subcategory',
                'Classified transactions',
                'Users (With this subcategory used)',
                'Unclassified transactions'
                ]
        
        self.df_master['classified'] = self.df_master['subcategory_precategorized'] != 'Without Classification'
        self.df_master['unclassified'] = self.df_master['subcategory_precategorized'] == 'Without Classification'

        grouped = self.df_master .groupby(['category_precategorized','subcategory_precategorized'])
        summary_gruped = grouped.agg({
             'classified': Series.sum,
             'user_id': Series.nunique,
            'unclassified':Series.sum})

        summary_gruped.reset_index(inplace = True)
        summary_gruped.columns = columns_cat_level_2
        del summary_gruped['Category']
        
        return summary_gruped

    def summary_nickname_lv2(self):

        columns_nickname_level_2 = [
                    'Category',
                    'Subcategory',
                    'Nicknames suggesteds',
                    'Number of changes nicknames',
                    'Percentage of changes nicknames',
                    'Nickname accuracy percent'
                          ]
        
        sub_cols = [
                'Nicknames suggesteds',
                'Number of changes nicknames',
                'Percentage of changes nicknames',
                'Nickname accuracy percent'
                ]
        
        #self.df_master['nickname_detected'] = self.df_master['nickname_suggested'] != ''
        
        grouped = self.df_master .groupby(['category_precategorized','subcategory_precategorized'])
        
        summary_gruped = grouped.agg({'nickname_suggested': Series.count,
             'change_nickname': Series.sum})


        summary_gruped.reset_index(inplace = True)
        summary_gruped['Percentage of changes'] = (summary_gruped['change_nickname'] *100/ summary_gruped['nickname_suggested']).apply(floor)
        tmp  =summary_gruped['nickname_suggested']-summary_gruped['change_nickname']
        summary_gruped['Nickname accuracy percentage'] = (tmp/summary_gruped['nickname_suggested']*100).apply(floor)
        summary_gruped.columns = columns_nickname_level_2
                
        return summary_gruped[sub_cols]
        
    def summary_subcategory_lv2(self):
    
        columns_subcat_level_2 = [
            'Category',
            'Subcategory',
            'Subcategory suggested',
            'Number of changes subcategory',
            'Percentage of changes subcategory',
            'Subcategory accuracy percent'
                          ]
        grouped = self.df_master.groupby(['category_precategorized','subcategory_precategorized'])
        summary_gruped = grouped.agg({'id': Series.count,
             'change_subcategory': Series.sum})

        summary_gruped.reset_index(inplace = True)
        
        summary_gruped['Percentage of changes'] = (summary_gruped['change_subcategory'] *100/ 
          summary_gruped['id']).apply(floor)
        tmp  =summary_gruped['id']-summary_gruped['change_subcategory']
        summary_gruped['Subcategory accuracy percentage'] = (tmp/summary_gruped['id']*100).apply(floor)
        summary_gruped.columns = columns_subcat_level_2
        
        del summary_gruped['Category']
        del summary_gruped['Subcategory']

        return summary_gruped
    
    def summary_description_lv3(self):
        columns_description_level_3 = [
                            'Concept (Clean)',
                            'Classified transactions',
                            'Users (With this classified transaction)',
                            'Unclassified transactions',
                            'Frecuency (User)'
                          ]
        
        columns_red = [
                    'Concept (Clean)',
                    'Classified transactions',
                    'Users (With this classified transaction)',
                    'Frecuency (User)',
                    'Unclassified transactions',
                  ]
        
        self.df_master['classified'] = self.df_master['subcategory_precategorized'] != 'Without Classification'
        #self.df_master['unclassified'] = self.df_master['subcategory_precategorized'] == 'Without Classification'
        
        grouped = self.df_master.groupby(['clean_description','nickname_suggested','category_precategorized','subcategory_precategorized'])
        summary_gruped = grouped.agg(
            transactions=('id', Series.count),
            users=('user_id', Series.nunique),
            classified=('classified', sum))
        
        summary_gruped['frec'] = summary_gruped['transactions']/summary_gruped['users']
        summary_gruped.reset_index(inplace = True)

        del summary_gruped['nickname_suggested']
        del summary_gruped['category_precategorized']
        del summary_gruped['subcategory_precategorized']
        
        summary_gruped.columns = columns_description_level_3
        
        return summary_gruped[columns_red]

    def summary_nickname_lv3(self):
        
        cols_nickname_lv3 = ['Description clean',
                             'Nickname suggested',
                             'Number of changes nickname',
                             'Percentage of changes nickname',
                             'Nickname accuracy percent']
        
        self.df_master['classified'] = self.df_master['subcategory_precategorized'] != 'Without Classification'

        grouped = self.df_master.groupby(['clean_description','nickname_suggested','category_precategorized','subcategory_precategorized'])
        summary_gruped = grouped.agg(change_nickname=('change_nickname', Series.sum),
                                    count_=('nickname_suggested', Series.count))
        summary_gruped.reset_index(inplace = True)

        summary_gruped['Percentage of changes'] = (summary_gruped['change_nickname'] *100/ summary_gruped['count_']).apply(floor)
        tmp  =summary_gruped['count_']-summary_gruped['change_nickname']
        summary_gruped['Nickname accuracy percentage'] = (tmp/summary_gruped['count_']*100).apply(floor)
        del summary_gruped['count_']
        del summary_gruped['category_precategorized']
        del summary_gruped['subcategory_precategorized']
        
        summary_gruped.columns = cols_nickname_lv3
        
        del summary_gruped['Description clean']
        return summary_gruped
        
    def summary_subcategory_lv3(self):
        
        cols_subcat_lv3 = [
                        'Description clean',
                        'Category suggested',
                        'Subcategory suggested',
                        'Number of changes subcategory',
                        'Percentage of changes subcategory',
                        'Subcategory accuracy percent'
                        ]

        grouped = self.df_master.groupby(['clean_description','nickname_suggested','category_precategorized','subcategory_precategorized'])
        summary_gruped = grouped.agg(change_subcategory=('change_subcategory', Series.sum),
                count_=('subcategory_precategorized', Series.count))
        summary_gruped.reset_index(inplace = True)

        summary_gruped['Percentage of changes'] = (summary_gruped['change_subcategory'] *100/ 
        summary_gruped['count_']).apply(floor)
        tmp = summary_gruped['count_']-summary_gruped['change_subcategory']
        summary_gruped['Subcategory accuracy percentage'] = (tmp/summary_gruped['count_']*100)

        del summary_gruped['count_']
        del summary_gruped['nickname_suggested']
        summary_gruped.columns = cols_subcat_lv3
        del summary_gruped['Description clean']
        return summary_gruped
    
    def summary_user_lv4(self):
        cols = ['ID User',
                'Concept (Clean)',
                'Classified transactions',
                'Frecuency (User)',
                'Unclassified transactions']

        self.df_master['classified'] = self.df_master['subcategory_precategorized'] != 'Without Classification'
        self.df_master['unclassified'] = self.df_master['subcategory_precategorized'] == 'Without Classification'

        grouped = self.df_master.groupby(['user_id','clean_description','category_precategorized','subcategory_precategorized','nickname_suggested'])
        summary_gruped = grouped.agg(
                                transactions=('classified', Series.sum),
                                frecuency=('user_id', Series.nunique),
                                count_=('unclassified', Series.sum)
                                    )
        summary_gruped.reset_index(inplace = True)
        del summary_gruped['category_precategorized']
        del summary_gruped['subcategory_precategorized']
        del summary_gruped['nickname_suggested']
        summary_gruped.columns = cols

        return summary_gruped

    def summary_nickname_lv4(self):
          
        cols = ['user_id',
                'clean_description',
                'Nickname suggested',
                'Number of changes nickname',
                'Percentage of changes nickname',
                'Nickname accuracy percent'
               ]

        grouped = self.df_master.groupby(['user_id','clean_description','category_precategorized','subcategory_precategorized','nickname_suggested'])
        summary_gruped = grouped.agg(
                                change_nickname=('change_nickname', Series.sum),
                                 count_=('nickname_suggested', Series.count))

        summary_gruped.reset_index(inplace = True)

        summary_gruped['Percentage of changes'] = (summary_gruped['change_nickname'] *100/ summary_gruped['count_']).apply(floor)
        tmp  =summary_gruped['count_']-summary_gruped['change_nickname']
        
        summary_gruped['Nickname accuracy percentage'] = (tmp/summary_gruped['count_']*100).apply(floor)
        
        del summary_gruped['count_']

        
        
        del summary_gruped['category_precategorized']
        del summary_gruped['subcategory_precategorized']
        
        summary_gruped.columns = cols

        del summary_gruped['user_id']
        del summary_gruped['clean_description']
        return summary_gruped

    def summary_subcategory_lv4(self):
    
      
        cols = [
            'User ID',
            'clean_description',
            'Category suggested',
            'Subcategory suggested',
            'Number of changes subcategory',
            'Percentage of changes subcategory',
            'Subcategory accuracy percent'
            ]

        grouped = self.df_master.groupby(['user_id','clean_description','category_precategorized','subcategory_precategorized','nickname_suggested'])
        summary_gruped = grouped.agg(
                                change_nickname=('change_subcategory', Series.sum),
                                 count_=('subcategory_precategorized', Series.count))

        summary_gruped.reset_index(inplace = True)

        summary_gruped['Percentage of changes'] = (summary_gruped['change_nickname'] *100/ summary_gruped['count_']).apply(floor)
        tmp  =summary_gruped['count_']-summary_gruped['change_nickname']
        summary_gruped['Nickname accuracy percentage'] = (tmp/summary_gruped['count_']*100).apply(floor)
        del summary_gruped['count_']
        del summary_gruped['nickname_suggested']
        summary_gruped.columns = cols

        del summary_gruped['User ID']
        del summary_gruped['clean_description']

        
        return summary_gruped
    
    def summary_user_lv5(self):
        
        cols = ['ID User',
        'Nickname',
        'Transactions with this alias',
        'Percentage of transactions with this alias']
        
        grouped = self.df_master.groupby(['user_id','nickname_suggested'])
        summary_gruped = grouped.agg(
                                 count_=('subcategory_precategorized', Series.count),
                                #porcent=("id", lambda x: (max(x) - min(x)).days)    
        )

        summary_gruped.reset_index(inplace = True)
        summary_gruped['Percent of transactions with this alias'] = (summary_gruped['count_'] *100/ summary_gruped['count_'].sum()).apply(floor)
        summary_gruped.columns = cols
        
        return summary_gruped

    def summary_user_lv6(self):
        
        cols = [
            'ID User',
            'ID Transaction',
            'Full concept',
            'Clean concept',
            'Day (Of classification)',
            'Hr (Classification)'
            'Bank',
            'Nickname suggested',
            'Change',
            'User alias'
            ]

        cols = ['user_id',
                'id',
                'description',
                'clean_description',
                'bank',
                'classified_at',
                'nickname_suggested',
                'change_nickname',
                'nickname_custom'
               ]
        
        sub_cols =['user_id',
                'id',
                'description',
                'clean_description',
                'bank']
        sub_cols_ = ['nickname_suggested',
                'change_nickname',
                'nickname_custom']
        
        df_final = self.df_master[cols]


        
        cols = ['Day (Of classification)','Hr (Classification)']        

        #df_final['classified_at']= df_final['classified_at'].apply(lambda x: str(x))
        
        df_final['classified_at'] = self.df_master['updated_at']
        
        df_final['classified_at'] = df_final['classified_at'].apply(lambda x: str(x))


        df_tmp = df_final.classified_at.str.split(pat = ' ', expand = True)

        df_tmp.columns = cols
        
        del df_final['classified_at']
        
        
        
        return  pd.concat([df_final[sub_cols], df_tmp, df_final[sub_cols_]], axis=1)
    
    def generate_cubes(self):
        #-------------------------------------------------<Level One>
        df_ =  concat([self.summary_category_lv1(),
                       self.summary_nickname_lv1(),
                       self.summary_subcategory_lv1()]
                      , axis=1)
        df_['from_date'] = self.from_date
        df_['to_date'] = self.to_date
        df_.reset_index(drop=True, inplace=True)
        self.CMongo.con_db["LevelOne."+ self.from_date.strftime("%b") +".cube"].insert_many(df_.to_dict(orient='records'))
        #-------------------------------------------------<Level Two>
        df_ =  concat([self.summary_category_lv2(),
                       self.summary_nickname_lv2(),
                       self.summary_subcategory_lv2()],
                      axis = 1)
        df_['from_date'] = self.from_date
        df_['to_date'] = self.to_date
        
        df_.reset_index(drop=True, inplace=True)
        self.CMongo.con_db["LevelTwo."+ self.from_date.strftime("%b") +".cube"].insert_many(df_.to_dict(orient='records'))
        #-------------------------------------------------<Level Three>
        df_ = concat([self.summary_description_lv3(),
                      self.summary_nickname_lv3(),
                      self.summary_subcategory_lv3()],
                     axis = 1)
        df_['from_date'] = self.from_date
        df_['to_date'] = self.to_date
        df_.reset_index(drop=True, inplace=True)
        self.CMongo.con_db["LevelThree."+ self.from_date.strftime("%b") +".cube"].insert_many(df_.to_dict(orient='records'))
        #-------------------------------------------------<Level Four>
        df_ =  concat([self.summary_user_lv4(),
                       self.summary_nickname_lv4(),
                       self.summary_subcategory_lv4()],
                      axis = 1)
        df_['from_date'] = self.from_date
        df_['to_date'] = self.to_date
        df_.reset_index(drop=True, inplace=True)
        self.CMongo.con_db["LevelFour."+ self.from_date.strftime("%b") +".cube"].insert_many(df_.to_dict(orient='records'))
        #-------------------------------------------------<Level Five>
        df_ = self.summary_user_lv5()
        df_['from_date'] = self.from_date
        df_['to_date'] = self.to_date
        df_.reset_index(drop=True, inplace=True)
        self.CMongo.con_db["LevelFive."+ self.from_date.strftime("%b") +".cube"].insert_many(df_.to_dict(orient='records'))
        #-------------------------------------------------<Level Six>
        df_ = self.summary_user_lv6()
        df_['from_date'] = self.from_date
        df_['to_date'] = self.to_date
        df_.reset_index(drop=True, inplace=True)
        self.CMongo.con_db["LevelSix."+ self.from_date.strftime("%b") +".cube"].insert_many(df_.to_dict(orient='records'))

    def run(self):
        self.summary_master()
        #self.trasform_datetime()
        self.remove_conflicts()
        self.add_new_data()
        self.generate_cubes()
        self.CMongo.close_con()
