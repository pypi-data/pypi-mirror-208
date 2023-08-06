from core import ReconnectingConsumer

def main():

    callback = lambda x: print(x)
    example = ReconnectingConsumer('amqp://guest:guest@localhost:5672/%2F',"topic_logs","anonymous.info", callback)
    example.run()

if __name__ == '__main__':
    main()