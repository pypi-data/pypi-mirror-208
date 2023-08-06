from core import Publisher
def main():
    # Connect to localhost:5672 as guest with the password guest and virtual host "/" (%2F)
    example = Publisher('amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat=3600',"topic_logs","anonymous.info")
    json_data = {
        "name": "John",
        "age": 30,
        "city": "New York",
        "arr": [1,2,3,4,5],
    }
    example.publish(json_data)


if __name__ == '__main__':
    main()