from os import getenv
from pykafka import KafkaClient
from pykafka.common import OffsetType
import math
from itertools import islice
import json

null=None; true=True; false=False

from kafka import KafkaProducer
from json import dumps as dumps_


class Producer:
    def __init__(
                self, 
                topic = None,
                kafka_brokers = None,
                acks = None,
                api_version = None,
                client_id = None
                 ):
        self.kafka_api_version = api_version
        self.topic = topic
        self.acks = acks
        self.client_id = client_id
        self.kafka_brokers = kafka_brokers
        

    def init_producer(self) -> None:

        self.producer = KafkaProducer(
            acks = self.acks,
            api_version=self.kafka_api_version,
            bootstrap_servers = self.kafka_brokers,
            value_serializer = lambda x: dumps_(x).encode('utf-8'),
        )

    def send_message(self, data: dict) -> None:
        self.producer.send(self.topic, value=data)
        # block until all async messages are sent
        self.producer.flush()


            
def get_offset_latest(topics,kafka_brokers):
    
    latest_offsets = {k: 0 for k in topics}
    earliest_available_offsets = {k: 0 for k in topics}
    
    
    for topic_ in topics:
        client = KafkaClient(hosts=kafka_brokers)
        topic = client.topics[topic_]

        consumer = topic.get_simple_consumer(auto_offset_reset=OffsetType.LATEST,reset_offset_on_start=True)

        earliest_available_offsets[topic_] = topic.earliest_available_offsets()[0][0][0]
        latest_offsets[topic_] = topic.latest_available_offsets()[0][0][0]
    
    return earliest_available_offsets,latest_offsets





def get_send_messages(topic_,last_num_messages,kafka_brokers):
    list_type_messages = []
    list_content_messages = []
    client = KafkaClient(hosts=kafka_brokers)
    
    topic = client.topics[topic_]
    

    consumer = topic.get_simple_consumer(auto_offset_reset=OffsetType.LATEST,reset_offset_on_start=True)


    # how many messages should we get from the end of each partition?
    MAX_PARTITION_REWIND = int(math.ceil(last_num_messages / len(consumer._partitions)))

    # find the beginning of the range we care about for each partition
    offsets = [(p, op.last_offset_consumed - MAX_PARTITION_REWIND) for p, op in consumer._partitions.items()]

    print(offsets)

    # if we want to rewind before the beginning of the partition, limit to beginning
    offsets = [(p, (o if o > -1 else -2)) for p, o in offsets]

    # reset the consumer's offsets
    consumer.reset_offsets(offsets)

    message_count = 0
    message_categorized_count = 0
    for message in islice(consumer, last_num_messages):
        print("offset: ",message.offset)
        current_offset = message.offset
        message = json.loads(message.value)
        if message['type'] ==  'transaction-categorized':
            message_categorized_count += 1
            for transaction in message['data']['transactions']:
                pass
                # list_content_messages.append({'uid':transaction['uid'],'kw_group':transaction['categorization']['kw_group']})

        message_count += 1
        list_type_messages.append(message["type"])
        
        if message_count == last_num_messages :
            break

    print("message_count: ", message_count)
    print("message_categorized_count: ", message_categorized_count) 

        
    return list_type_messages,list_content_messages



if __name__ == '__main__':
    
    confluence_library= False
    port_current = '9094'
    port_new = '9092'
    default_kafka_host = 'localhost:9092'
    enable_port_replace = True


    if getenv('KAFKA_BROKERS'):
        if len(getenv('KAFKA_BROKERS')) != 0:
            kafka_brokers = getenv('KAFKA_BROKERS')


    elif getenv('KAFKA_HOST') and getenv('KAFKA_PORT'):
        kafka_brokers = getenv('KAFKA_HOST') + ':' + getenv('KAFKA_PORT')
    else :
        kafka_brokers = default_kafka_host

    kafka_brokers = kafka_brokers.replace(port_current,port_new)

    print("kafka_brokers: ", kafka_brokers)
    
   



    acks = 'all'
    api_version = (2,6,1)
    group_id  = 'categorization-'
    topic_set = 'transaction'

    topics_get = ['transaction']
    message_type = 'transaction-update-kw-group'
    earliest_available_offsets,latest_offsets = get_offset_latest(topics_get,kafka_brokers)




    print(earliest_available_offsets )
    print(latest_offsets)

    
    for topic in topics_get :
        print("topic: ", topic)
        last_num_messages = latest_offsets[topic] - earliest_available_offsets[topic]
        print("last_num_messages: ", last_num_messages)
        list_type_messages,list_content_messages = get_send_messages(topic,last_num_messages,kafka_brokers)

        
        print("list_type_messages: ",list_type_messages)

    """ 
        # d_unique = pd.DataFrame(d).drop_duplicates().to_dict('records')
        set_of_jsons = {json.dumps(d, sort_keys=True) for d in list_content_messages}
        list_content_messages = [json.loads(t) for t in set_of_jsons]
        
        print("Remover duplicados... \nNúmero de transacciones: ",len(list_content_messages))
        
        message_struct['data']['transactions'] = list_content_messages
        
        if confluence_library :
            if enable_port_replace:
                kafka_brokers = kafka_brokers.replace(port_current,port_new)
        else :
            if enable_port_replace:
                kafka_brokers = kafka_brokers.replace(port_current,port_new).split(',')


        print("kafka_brokers: ", kafka_brokers)
        
        acks = 'all'
        api_version = (2,6,1)
        group_id  = 'categorization-update-kw-group'
        client_id = None
        ProdTrans = Producer('transaction', kafka_brokers, acks, api_version , client_id)
        ProdTrans.init_producer()
        ProdTrans.send_message(message_struct)
        print(message_struct)
    """