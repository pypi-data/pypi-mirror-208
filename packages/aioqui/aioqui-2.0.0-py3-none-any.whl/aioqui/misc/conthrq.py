from uuid import uuid4, UUID
from threading import Thread


class ConditionalThreadQueue:
    class ConditionalThread(Thread):
        to_complete: bool = True

        def kill(self) -> None:
            self.to_complete = False

    def __init__(self):
        self.__threads: dict[UUID, ConditionalThreadQueue.ConditionalThread] = {}

    def new(self, pre: callable, post: callable) -> UUID:
        if self.__threads:  # kill prev thread if exists
            key = list(self.__threads.keys())[-1]
            self.__threads[key].kill()

        def target(thread_uuid: UUID):  # create target for the new thread
            pre()
            thread = self.__threads[thread_uuid]
            if thread.to_complete:  # call post() if thread was not killed
                post()
            self.__threads.pop(thread_uuid)

        uuid = uuid4()
        thread = ConditionalThreadQueue.ConditionalThread(target=target, args=(uuid, ))
        self.__threads[uuid] = thread
        thread.start()
        return uuid

    def __getitem__(self, uuid: UUID):
        return self.__threads[uuid]
