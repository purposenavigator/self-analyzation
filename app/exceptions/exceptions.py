class InvalidTopicException(Exception):
    def __init__(self, topic: str):
        self.topic = topic
        self.message = f"Invalid topic: {topic}"
        super().__init__(self.message)
