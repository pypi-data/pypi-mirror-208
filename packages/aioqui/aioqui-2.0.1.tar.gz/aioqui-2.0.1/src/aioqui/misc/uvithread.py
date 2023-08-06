import contextlib
import threading
import uvicorn
import asyncio
import time
from uvicorn import Config  # to import while using `Server`


class Server(uvicorn.Server):
    def install_signal_handlers(self):  # overriding to disable
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.stop()
        return self

    def stop(self):
        self.should_exit = True
        self.thread.join()
        asyncio.get_event_loop().stop()
