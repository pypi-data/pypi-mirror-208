from json import loads as loads_
from confluent_kafka import Consumer as Consumer_
from kafka import KafkaConsumer as KafkaConsumer_
from kafka import TopicPartition

class Consumer:
    '''
    Schema (or event type):transaction-homologated
    topic (string): 'transaction'
    key (string): undefined
    value (string):



    '''
     
    def __init__(self, topics_list = None,
                         kafka_brokers = None,
                          group_id = None, 
                          api_version = None,
                          client_id = None,
                          heartbeat_interval_ms = None,
                          session_timeout_ms = None,
                          auto_offset_reset = None
                          ):


        self.auto_offset_reset = auto_offset_reset
        self.session_timeout_ms = session_timeout_ms
        self.heartbeat_interval_ms = heartbeat_interval_ms
        self.topics_list = topics_list
        self.group_id = group_id
        self.kafka_brokers = kafka_brokers
        self.kafka_api_version = api_version
        self._consumer = None
        self.client_id = client_id
        self.data = []
        

    def init_consumer(self):

        self._consumer = KafkaConsumer_(
            api_version= self.kafka_api_version,
            auto_offset_reset=self.auto_offset_reset,
            session_timeout_ms = self.session_timeout_ms,
            heartbeat_interval_ms = self.heartbeat_interval_ms,
            enable_auto_commit=True,
            bootstrap_servers = self.kafka_brokers,
            group_id = self.group_id,
            value_deserializer = lambda x: loads_(x.decode('utf-8')),
        )
        self._consumer.subscribe(self.topics_list)

    @property
    def consumer(self):
        return self._consumer

    @consumer.setter
    def consumer(self, value):
        if isinstance(value, KafkaConsumer_):
            self._consumer = value

    def star_read(self):
        self.receive_message()

    

    def commit_check(self,partition,KAFKA_TOPIC_NAME):
        # message.partition
        # Optionally, To check if everything went good
        return self._consumer.committed(TopicPartition(KAFKA_TOPIC_NAME,partition ))


class KafkaConsumer:
    '''
    Schema (or event type):transaction-homologated
    topic (string): 'transaction'
    key (string): undefined
    value (string):

    '''

    def __init__(self, topics_list = None,
                         kafka_brokers = None,
                          group_id = None, 
                          api_version = None,
                          heartbeat_interval_ms = None,
                          session_timeout_ms = None,
                          auto_offset_reset = None
                          ):
        
        self.heartbeat_interval_ms = heartbeat_interval_ms
        self.session_timeout_ms = session_timeout_ms
        self.auto_offset_reset = auto_offset_reset
        self.topics_list = topics_list
        self.group_id = group_id
        self.kafka_brokers = kafka_brokers
        self.kafka_api_version = api_version
        self._consumer = None
        self.client_id = None
        

    def init_consumer(self):
        
        conf = {'bootstrap.servers': self.kafka_brokers,
                'group.id': self.group_id,
                'enable.auto.commit': True,
                'auto.offset.reset': 'smallest'}
                    
        self._consumer = Consumer_(conf)

        self._consumer.subscribe(self.topics_list)

    @property
    def consumer(self):
        return self._consumer

    @consumer.setter
    def consumer(self, value):
        if isinstance(value, Consumer_):
            self._consumer = value


if __name__ == '__main__':
    pass
