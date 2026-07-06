from queue import Queue
import threading

class TaskQueue:
    def __init__(self, workers, handler):
        self.q = Queue()
        self.handler = handler

        for _ in range(workers):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()

    def worker(self):
        while True:
            task = self.q.get()
            try:
                self.handler(*task)
            except Exception as e:
                print("worker error:", e)
            self.q.task_done()

    def add(self, task):
        self.q.put(task)
