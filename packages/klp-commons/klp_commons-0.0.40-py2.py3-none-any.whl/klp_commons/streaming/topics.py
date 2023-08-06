
import time
from math import ceil

from numpy import unique
from os import getenv
from datetime import datetime
from itertools import islice

from pykafka import KafkaClient
from pykafka.common import OffsetType
from klp_commons.log.log import Log
from klp_commons.log.structuredMessage import StructuredMessage
from klp_commons.controllers.controller_mongodb import ControllerMongoDB

from traceback import  format_exc
from sys import exc_info, exit

null=None; true=True; false=False
fmt = StructuredMessage

from kafka import KafkaProducer
from json import dumps as dumps_ 
from json import  loads as loads_


class Topics():

    def __init__(self,topics,
                level: str = None, # logging levels
                 event_level: str = None, # event logging levels  for sentry
                 filename_log: str = None, # file
                 is_local_env: bool = False # enable Sentry 
                 ): 
        self.topics = topics
        self.kafka_brokers = None
        self.earliest_available_offsets = None
        self.latest_offsets = None
        self.list_type_messages = []
        self.list_content_messages = []
        self.others_types_messages_list = ['machine-learning-asset-created',
                                'machine-learning-asset-deleted',
                                'machine-learning-asset-updated',
                                'machine-learning-business-created',
                                'machine-learning-business-deleted',
                                'machine-learning-business-updated',
                                'machine-learning-person-created',
                                'machine-learning-person-deleted',
                                'machine-learning-person-updated',
                                'machine-learning-special-moment-created',
                                'machine-learning-special-moment-deleted',
                                'machine-learning-special-moment-updated',
                                'machine-learning-expense-created',
                                'machine-learning-expense-updated',
                                'machine-learning-expense-deleted',
                                'machine-learning-income-created',
                                'machine-learning-income-updated',
                                'custom-category-created',
                                'custom-category-updated',
                                ]
        self.MongoDB = ControllerMongoDB()

        
        if filename_log is None:
            filename_log = 'Topics.log'
        
        confluence_library= False
        port_current = '9094'
        port_new = '9092'
        default_kafka_host = 'localhost:9092'
        enable_port_replace = True
        
        if getenv('KAFKA_BROKERS'):
            if len(getenv('KAFKA_BROKERS')) != 0:
                self.kafka_brokers = getenv('KAFKA_BROKERS')


        elif getenv('KAFKA_HOST') and getenv('KAFKA_PORT'):
            self.kafka_brokers = getenv('KAFKA_HOST') + ':' + getenv('KAFKA_PORT')
        else :
            self.kafka_brokers = default_kafka_host

        self.kafka_brokers = self.kafka_brokers.replace(port_current,port_new)

        if enable_port_replace:
            self.client = KafkaClient(hosts=self.kafka_brokers)

        
        self.Logger = Log(
            path_file = filename_log,
            level = level,
            event_level = event_level,
            is_local_env = is_local_env)

        self.Logger.startlogging()

        # module_name.TopicKafka_name
        self.logger = self.Logger.get_log('Topics')
        self.logger.info("Constructor Topics()")    
    
    def extract_offset_index(self):
        """
        Obtener el offset más antiguo disponible (earliest) y el 
        offset más reciente (latest) de la lista de tópicos
        almacenada en la variable topics
        """
        self.logger.info("Call get_offset_index()")

        self.latest_offsets = {k: 0 for k in self.topics}
        self.earliest_available_offsets = {k: 0 for k in self.topics}

        for topic_ in self.topics:
            self.logger.info(fmt('Get index for: ', json={"topic":topic_}))

            topic = self.client.topics[topic_]
            self.earliest_available_offsets[topic_] = topic.earliest_available_offsets()[0][0][0]
            self.latest_offsets[topic_] = topic.latest_available_offsets()[0][0][0]

        self.logger.info("Done call get_offset_index()")
        
    def get_offsets(self):
        return self.earliest_available_offsets, self.latest_offsets  
    
    def extract_messages(self,topic_,last_num_messages,flag_content = False, flag_send= False):
    
    
        topic = self.client.topics[topic_]


        consumer = topic.get_simple_consumer(auto_offset_reset=OffsetType.LATEST,reset_offset_on_start=True)


        # how many messages should we get from the end of each partition?
        MAX_PARTITION_REWIND = int(ceil(last_num_messages / len(consumer._partitions)))

        # find the beginning of the range we care about for each partition
        offsets = [(p, op.last_offset_consumed - MAX_PARTITION_REWIND) for p, op in consumer._partitions.items()]

        # if we want to rewind before the beginning of the partition, limit to beginning
        offsets = [(p, (o if o > -1 else -2)) for p, o in offsets]

        # reset the consumer's offsets
        consumer.reset_offsets(offsets)

        message_count = 0
        message_categorized_count = 0
        for message in islice(consumer, last_num_messages):
            self.logger.info(fmt('Processing ... current offset ', json={"offset":message.offset}))

            # same time of all variables crete_at/update value 

            self.dt =  datetime.utcnow().isoformat()
            # self.dt = datetime.now(timezone.utc).strftime(self.format_inter)
            self.offset = message.offset



            self.logger.info("message processing ... ")
            
            # encrypted = Crypto.encrypt(data)

            current_offset = self.offset
            message = loads_(message.value)
            
            self.logger.info(fmt("message type and offset incoming", json={'type':message['type'],"offset":self.offset}))
            print("type:", message['type'], "  offset: ", self.offset)
            
            
            message['offset_'] = self.offset
            message['datetime_reporting'] = self.dt
            message_count += 1

            self.list_type_messages.append(message["type"])

            if flag_content:
                self.list_content_messages.append(message)
            if flag_send:
                self.send_message(message)

            if message_count == last_num_messages :
                self.logger.info("message_count == last_num_messages -> True")
                self.logger.info("Break Loop")
                consumer.stop()
                time.sleep(0.1)
                break

    def get_messages(self):
        return self.list_type_messages, self.list_content_messages,
                
    def value_count_type_message(self):

        values, counts = unique(self.list_type_messages, return_counts=True)

        return values, counts

    def save_messages_to_mongodb(self):

        for topic in self.topics :
            print("topic: ", topic)
            last_num_messages = latest_offsets[topic] - earliest_available_offsets[topic]

            self.extract_messages(topic,last_num_messages,flag_send= True)
            
    def value_counts_types(self):
        
        dict_value_counts = dict()
        
        for topic in self.topics :
            print("topic: ", topic)
            last_num_messages = latest_offsets[topic] - earliest_available_offsets[topic]

            self.extract_messages(topic,last_num_messages)

            values, counts = unique(self.list_type_messages, return_counts=True)
            dict_value_counts[topic] = zip(values, counts)
        
        return dict_value_counts
            
    def send_message(self,message):

        try :
            if message['type'] == 'transaction-homologated':
                self.logger.info("Call save transaction-homologated ")

                message['_id'] = self.offset
                self.MongoDB.get_con_collect(collection_name='transaction-homologated')
                self.MongoDB.set_document(message)
                # fix insert many 
                self.MongoDB.insert_one_collection()
                self.MongoDB.close_con()
                self.logger.info("Don call save transaction-homologated ")
            elif message['type'] in self.others_types_messages_list :
                
                self.logger.info("Call save into " + message['type'] + " colecction mongodb ")

                if message['type'] == 'machine-learning-asset-created':
                    for msj in message['data']['assetsCreated']:
                        msj['_id'] = msj['uid']
                        del msj['uid']

                        self.MongoDB.get_con_collect(collection_name=message['type'].split("machine-learning-")[1])
                        self.MongoDB.set_document(msj)
                        # fix insert many 
                        self.MongoDB.insert_one_collection()
                        self.MongoDB.close_con()

                elif isinstance(message['data'] , list) :
                    for msj in message['data']:

                        msj['_id'] = msj['uid']
                        del msj['uid']

                        self.MongoDB.get_con_collect(collection_name=message['type'].split("machine-learning-")[1])
                        self.MongoDB.set_document(msj)
                        # fix insert many 
                        self.MongoDB.insert_one_collection()
                        self.MongoDB.close_con()


                else :

                    message['_id'] = message['data']['uid']
                    del message['data']['uid']
                    self.MongoDB.get_con_collect(collection_name=message['type'].split("machine-learning-")[1])

                    self.MongoDB.set_document(message)
                    self.MongoDB.insert_one_collection()
                    self.MongoDB.close_con()

        except ValueError as e:
            exit
            traceback_info = format_exc()
            type_ , value , _ = exc_info()
            
            json_ = {
                    'type': message['type'],
                    'error_type':str(type_.__name__),
                    'error_value':str(value),
                    'traceback_info': traceback_info
                    }
            
            self.logger.error(fmt('Exception for processing message. Save message traceback info, details error:', json = json_))
        
        
        
        self.logger.info("Done save into " + message['type'] + " colecction mongodb ")




if __name__ == "__main__":

    list_topics = ['transaction','machine-learning'] 
    level_default = 'info'
    event_level_default = 'error'
    fn = 'topics.log'
    save_db = True

    topics = Topics(list_topics,
                    level=level_default,
                    event_level=event_level_default,
                    filename_log=fn,
                    is_local_env=False
                   )

    topics.extract_offset_index()


    earliest_available_offsets, latest_offsets = topics.get_offsets()
    
    print(earliest_available_offsets, "\n _:_ \n" ,latest_offsets)


    if save_db:
        topics.save_messages_to_mongodb()


    print(topics.value_count_type_message())

    print("Finish script OK ")
