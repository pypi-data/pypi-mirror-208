#!/usr/bin/env python
import json
#import adal
#import azure.common.credentials as credentials
#import azure.batch._batch_service_client as batch
#import azure.batch.batch_auth as batchauth
#import azure.batch.models as batchmodels
#from azure.servicebus import SubscriptionClient, ServiceBusClient, TopicClient, QueueClient, Message
from azure.servicebus import ServiceBusReceiver, ServiceBusReceiveMode, ServiceBusClient
#from typing_extensions import Required
from dhi.platform.args import ClientArgs
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("-c", "--connectionstring", help="Service bus connection string", required=True)
    parser.add_argument("-x", "--executionid", default=ClientArgs.GetDefault("DHIEXECUTIONID"), help="Execution run id (topic name)")
    parser.add_argument("-s", "--subscription", default="engine", help="Subscription name")
    parser.add_argument("-t", "--timeout", default=10, help="Timeout [seconds]", type=int)

def main():
    args = ClientArgs.ParseBasic(description="Show engine messages", init=initParser)

    #topicClient = TopicClient.from_connection_string(connectionString, topicName)
    #client = ServiceBusClient.from_connection_string(connectionString)
    #subscription = client.get_subscription(topicName, subscriptionName)
    #subscription = SubscriptionClient.from_connection_string(args.connectionstring, args.subscription, topic=args.executionid)
    #for msg in subscription.get_receiver(idle_timeout=args.timeout):
    #    print(msg)
    #    msg.complete
    #receiver = ServiceBusReceiver._from_connection_string(conn_str=args.connectionstring, topic_name=args.executionid, #subscription_name=args.subscription, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, max_wait_time=args.timeout)
    #if receiver:
    #    for msg in receiver:
    #        Format.DumpPlain(vars(msg))

    client = ServiceBusClient.from_connection_string(conn_str=args.connectionstring)
    with client:
        receiver = client.get_subscription_receiver(topic_name=args.executionid, subscription_name=args.subscription, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, max_wait_time=args.timeout) #, prefetch_count=20)
        with receiver:
            for msg in receiver:
                print(f"### {msg.message_id}")
                #print(f"  {type(msg.message)}")
                #print(f"  {msg.message}")
                #obj = json.loads(f"{msg}")
                obj = json.loads(str(msg))
                Format.DumpPlain(obj)

if __name__ == '__main__':
    main()
