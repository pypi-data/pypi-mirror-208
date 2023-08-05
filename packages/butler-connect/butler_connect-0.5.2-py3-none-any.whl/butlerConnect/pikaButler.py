
import pika, logging, time, os
from pika import frame
from pika.exchange_type import ExchangeType

from pika.exceptions import *

LOG = logging.getLogger(__name__)
import queue
import threading

import ssl

default_heartbeat = 600
default_blocked_connection_timeout = 300

class BasicPikaConnection(object):
    EXCHANGE_TYPE = ExchangeType.fanout
    def __init__(self,host,port,user,password,connectionName,callbackData,callbackControl,component,ssl_activate=False,ca_certificate=None,client_certificate=None,client_key=None,certificate_password='',virtual_host='/'):
        self.virtual_host = virtual_host
        self.ssl_activate = ssl_activate
        
        self.ca_certificate = ca_certificate
        self.certificate_password = certificate_password
        self.client_certificate = client_certificate
        self.client_key = client_key
        self.credentials = pika.PlainCredentials(user, password)
        self.host = host
        self.port = port
        self.component = component
        self.connectionName  = connectionName
        self.callbackData    = callbackData
        self.callbackControl = callbackControl

        self._connectionConsumer = None
        self._connectionPublisher = None
        
        self._channelConsumer = None
        self._channelPublish = None
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self.consumerRun = False
        self.publisherRun = False
        self.reconnectingTimeout = 10.0
        self.queSendData = queue.Queue()

    def bindExchangeConsumer(self,exchange,callback):
        queue_name =  f'{self.connectionName}_{exchange}'
        result = self._channelConsumer.queue_declare(queue=queue_name, exclusive=False)
        self._channelConsumer.exchange_declare(exchange=exchange,  exchange_type='fanout')
        self._channelConsumer.queue_bind(exchange=exchange, queue=queue_name)
        self._channelConsumer.basic_consume(queue=queue_name,
                            auto_ack=True,
                            on_message_callback=callback)
    
    def publish(self,topic,msg):
        LOG.info(f'{topic}=>{msg}')
        self.queSendData.put_nowait({topic:msg})
    
    def publishData(self,msg):
        topic = f'component.{self.component}.data.input'
        self.publish(topic=topic,msg=msg)

    def publishControl(self,msg):
        topic = f'component.{self.component}.control.input'
        self.publish(topic=topic,msg=msg)
            
            
    
    def startPublisher(self):
        # Bestimmte Fehlerbeahndlung not notwendig
        self.publisherRun = True
        while self.publisherRun :
            try:
                self.runPublisher()
            except (pika.exceptions.IncompatibleProtocolError, pika.exceptions.StreamLostError):
                desc = f'Loosing Connection from {self.host}:{self.port}'
                LOG.warning(desc)
            except Exception as e:
                if self.publisherRun:
                    desc = f'Exception Connection from {self.host}:{self.port} '
                    LOG.exception(desc)
                #self.publisherRun = False
            time.sleep(self.reconnectingTimeout )
            LOG.info(f'Try to reconnect!')
        
    def getSSLOptions(self):
        try:
            ca_certificate = os.path.abspath(self.ca_certificate)
            client_certificate = os.path.abspath(self.client_certificate)
            client_key = os.path.abspath(self.client_key)
            context = ssl.create_default_context(cafile=ca_certificate)
            context.load_default_certs()
            context.check_hostname = False
            context.load_cert_chain(certfile=client_certificate,keyfile=client_key,password=self.certificate_password)
            sslOpt = pika.SSLOptions(context, self.host)
            return sslOpt
        except:
            LOG.exception('Error while generating ssl-Options')
        return None
    
    def ConnectionParameters(self):
        if self.ssl_activate:
            return pika.ConnectionParameters(host=self.host,port=self.port,credentials=self.credentials,ssl_options=self.getSSLOptions(),heartbeat=default_heartbeat,blocked_connection_timeout=default_blocked_connection_timeout,virtual_host=self.virtual_host)
        else:
            return pika.ConnectionParameters(host=self.host,port=self.port,credentials=self.credentials,heartbeat=default_heartbeat,blocked_connection_timeout=default_blocked_connection_timeout,virtual_host=self.virtual_host)
    
    def runPublisher(self):
        LOG.info(f'Create pika Publish-Connection with: host={self.host}, post={self.port}')
        self._connectionPublisher = pika.BlockingConnection(self.ConnectionParameters())
        self._channelPublish = self._connectionPublisher.channel()
        self._channelPublish.confirm_delivery()
        
        while self.publisherRun :
            try:
                item = self.queSendData.get(block=True,timeout=default_heartbeat/2)
            except queue.Empty:
                item = {}
            if item != {}:
                try:
                    for topic in item.keys():
                        msg = item[topic]
                        LOG.info(f'publish data {topic}@{msg}')
                        try:
                            self._channelPublish .basic_publish(exchange=topic,
                                    routing_key='',
                                    body=msg,properties=pika.BasicProperties(content_type='text/plain',
                                                          delivery_mode=pika.DeliveryMode.Transient),
                                    mandatory=True)
                        except (pika.exceptions.UnroutableError, pika.exceptions.ChannelClosedByBroker) as e:
                            print(f'Error on publish {topic}=>{msg} ')
                            print(e)
                            self.que.put(item)
                        self.queSendData.task_done()
                except Exception as e:
                    self.que.put(item)
                    raise e
            # sending heartbeat
            else:
                # do a pika heartbeat
                self._connectionPublisher.process_data_events(time_limit=0.1) 
     
                
    def runConsumer(self):
        LOG.info(f'Create pika Consumer-Connection with: host={self.host}, post={self.port}')
        self._connectionConsumer = pika.BlockingConnection(self.ConnectionParameters())
        self._channelConsumer = self._connectionConsumer.channel()
        topicData = f'component.{self.component}.data.output'
        topicControl = f'component.{self.component}.control.output'
        self.bindExchangeConsumer(exchange=topicData,callback=self.callbackData)
        self.bindExchangeConsumer(exchange=topicControl,callback=self.callbackControl)
        LOG.info('self._channel.start_consuming()')
        self._channelConsumer.start_consuming()
        

    def startConsumer(self):
        self.consumerRun = True
        while self.consumerRun :
            try:
                self.runConsumer()
            except (pika.exceptions.IncompatibleProtocolError, pika.exceptions.StreamLostError):
                desc = f'Loosing Connection from {self.host}:{self.port}'
                LOG.warning(desc)
            except Exception as e:
                if self.consumerRun:
                    desc = f'Exception Connection from {self.host}:{self.port}'
                    LOG.exception(desc)
                #self.consumerRun = False
            time.sleep(self.reconnectingTimeout )
            LOG.info(f'Try to reconnect!')
        
        
    def stop(self):
        self.consumerRun = False
        self.publisherRun = False
        self._channelConsumer.stop_consuming()
        pass
        
        
def basicConsumerCallback(ch, method, properties, body):
        pass
      
    
class basicConnection(object):
    EXCHANGE_TYPE = ExchangeType.fanout
    def __init__(self,connectionName,topic="",callback=None,connectionParameter:pika.ConnectionParameters=None) -> None:
        self.connectionName = connectionName
        self.topic = topic
        self.callback:basicConsumerCallback = callback
        self.connection:pika.BlockingConnection = None
        self.channel:pika.BlockingChannel = None
        self.connectionParameter:pika.ConnectionParameters = connectionParameter
        self.reconnectingTimeout = 10.0
        self.isRunning = False
        self.threadObj = None
    
    def start(self):
        self.isRunning = True
        self.threadObj = threading.Thread(target=self.thread)
        self.threadObj .start()
    
    def stop(self):
        self.isRunning = False
    
    def thread(self):
        while self.isRunning :
            try:
                self.run()
            except (ConnectionResetError, StreamLostError ) as e:
                LOG.warning(f'Loosing connection. Do a reset!')
            except Exception as e:
                if self.isRunning:
                    desc = f'Exception Connection from {self.topic}@{self.connectionParameter}'
                    LOG.exception(desc)
            if self.isRunning:
                time.sleep(self.reconnectingTimeout )
                LOG.info(f'Try to reconnect!')
    
    def run(self):
        pass

class basicConsumer(basicConnection):
    def __init__(self,connectionName,topic,callback,connectionParameter:pika.ConnectionParameters=None,createExchangeIfNotExists=False,exclusive=False,createExchangeType:ExchangeType=ExchangeType.fanout,routing_key=None,reconnectingCallback=None) -> None:
        super().__init__(connectionName=connectionName,topic=topic,callback=callback,connectionParameter=connectionParameter)
        self.createExchangeIfNotExists = createExchangeIfNotExists
        self.createExchangeType = createExchangeType
        self.exclusive = exclusive
        self.routing_key = routing_key
        self.reconnectingCallback = reconnectingCallback
    
    def run(self):
        LOG.info(f'Create pika Consumer-Connection for {self.topic} with: {self.connectionParameter}')
        self.connection = pika.BlockingConnection(self.connectionParameter)
        self.channel = self.connection.channel()
        
        queue_name =  f'{self.connectionName}' #_consume_{self.topic}'
        result = self.channel.queue_declare(queue=queue_name, exclusive=self.exclusive)
        if self.createExchangeIfNotExists:
            self.channel.exchange_declare(exchange=self.topic, exchange_type=self.createExchangeType)
        self.channel.queue_bind(exchange=self.topic, queue=queue_name,routing_key=self.routing_key )
        self.channel.basic_consume(queue=queue_name,
                            auto_ack=True,
                            on_message_callback=self.callback)

        try:
            if self.reconnectingCallback != None: self.reconnectingCallback()
        except: LOG.exception("Error on calling reconnectingCallback-Fkt")
        self.channel.start_consuming()
    def bindExchange(self,topic):
        connection = pika.BlockingConnection(self.connectionParameter)
        channel = connection.channel()
        channel.exchange_bind(self.topic,topic)
        connection.close()
    def stop(self):
        super().stop()   
        self.channel.stop_consuming()
        #self.channel.close()
        #time.sleep(0.25)
        #self.connection.close()
         
class basicPublisher(basicConnection):
    def __init__(self,connectionName,connectionParameter:pika.ConnectionParameters=None) -> None:
        super().__init__(connectionName=connectionName,connectionParameter=connectionParameter)
        self.que = queue.Queue()
        self.connection = None
        self.channel = None
    def run(self):
        LOG.info(f'Create pika Publish-Connection with: {self.connectionParameter}')
        self.connection = pika.BlockingConnection(self.connectionParameter)
        self.channel:pika.adapters.blocking_connection.BlockingChannel = self.connection.channel()
        self.channel.confirm_delivery()
        
        while self.isRunning :
            try:
                item = self.que.get(block=True,timeout=default_heartbeat/4)
            except:
                item = {}      
            if item != {}:
                try:
                    for topic in item.keys():
                        d = item[topic]
                        msg = d.get('msg')
                        routing_key = d.get('routing_key',None)
                        if routing_key == None: routing_key = ''
                        LOG.info(f'publish data {topic}@{msg}')
                        try:
                            self.channel.basic_publish(exchange=topic,
                                routing_key=routing_key,
                                body=msg,properties=pika.BasicProperties(content_type='text/plain',
                                                          delivery_mode=pika.DeliveryMode.Transient),
                          mandatory=True)
                        except (pika.exceptions.UnroutableError, pika.exceptions.ChannelClosedByBroker) as e:
                            print(f'Error on publish {topic}=>{msg} with routing_key={routing_key}')
                            print(e)
                            self.que.put(item)
                except Exception as e:
                    self.que.put(item)
                    raise e
            else:
                # do a pika heartbeat
                self.connection.process_data_events(time_limit=0.1) 

            
    def publish(self,topic,msg,routing_key=None):
        LOG.info(f'publish {topic}=>{msg} with routing_key={routing_key}')
        self.que.put_nowait({topic:{'msg':msg,'routing_key':routing_key}})
    def stop(self):
        super().stop()   
        self.que.put({})
        #self.channel.close()
        #self.connection.close()
    
class BasicBrokerThreadingConnection(object):
    def __init__(self,host,port,user,password,connectionName,ssl_activate=False,ca_certificate=None,client_certificate=None,client_key=None,certificate_password='',virtual_host='/'):
        self.ssl_activate = ssl_activate
        self.ca_certificate = ca_certificate
        self.certificate_password = certificate_password
        self.client_certificate = client_certificate
        self.client_key = client_key
        self.credentials = pika.PlainCredentials(user, password)
        self.host = host
        self.port = port
        self.connectionName  = connectionName
        #self.consumer:basicConsumer = None
        self.virtual_host = virtual_host
        self.publisher:basicPublisher = None
        self.consumerMap = {} # map of basicConsumer
    def getConnectionName(self):
        return self.connectionName
    def testConnection(self):
        # Test the connection and return True if is connectabel. 
        # Return an exception if not connectable
        connection = pika.BlockingConnection(self.ConnectionParameters('butler-building-agents_connection-test'))
        channel = connection.channel()
        connection.close()
        return True
    
    def publish(self,topic,msg,routing_key=None):
        if self.publisher != None:
            self.publisher.publish(topic=topic,msg=msg,routing_key=routing_key)
        else:
            LOG.error("Publisher was not created!")
    
    def createPublisher(self):
        name = f'{self.connectionName}_publisher'
        self.publisher = basicPublisher(name,connectionParameter=self.ConnectionParameters(name))    
        self.publisher.start()

    def createConsumer(self,topic,callback,createExchangeIfNotExists,createExchangeType:ExchangeType=ExchangeType.fanout,routing_key=None,reconnectingCallback=None):
        connectionName = f'{self.connectionName}_consumer_{topic}'
        consumer = basicConsumer(connectionName=connectionName, topic=topic,callback=callback,connectionParameter=self.ConnectionParameters(connectionName),createExchangeIfNotExists=createExchangeIfNotExists,createExchangeType=createExchangeType,routing_key=routing_key,reconnectingCallback=reconnectingCallback)
        consumer.start()
        self.consumerMap.update({
            topic:consumer
        })
    def stopAllConnections(self):
        if self.publisher != None:
            self.publisher.stop()
        for topic,consumer in self.consumerMap.items():
            consumer.stop()
            
    def getSSLOptions(self):
        try:
            ca_certificate = os.path.abspath(self.ca_certificate)
            client_certificate = os.path.abspath(self.client_certificate)
            client_key = os.path.abspath(self.client_key)
            context = ssl.create_default_context(cafile=ca_certificate)
            context.load_default_certs()
            context.load_cert_chain(certfile=client_certificate,keyfile=client_key,password=self.certificate_password)
            sslOpt = pika.SSLOptions(context, self.host)
            return sslOpt
        except:
            LOG.exception('Error while generating ssl-Options')
        return None
    
    def ConnectionParameters(self,connectionName):
        props = { 'connection_name' : connectionName }
        if self.ssl_activate:
            return pika.ConnectionParameters(host=self.host,port=self.port,credentials=self.credentials,ssl_options=self.getSSLOptions(),client_properties=props,heartbeat=default_heartbeat,blocked_connection_timeout=default_blocked_connection_timeout,virtual_host=self.virtual_host)
        else:
            return pika.ConnectionParameters(host=self.host,port=self.port,credentials=self.credentials,client_properties=props,heartbeat=default_heartbeat,blocked_connection_timeout=default_blocked_connection_timeout,virtual_host=self.virtual_host)
        
    def bindExchangeOnConsumer(self,destTopic,srcTopic):
        if destTopic in self.consumerMap:
            self.consumerMap[destTopic].bindExchange(topic = srcTopic)