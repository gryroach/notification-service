from .base import BaseWorker, BaseWorkerSettings, WorkerContext


class FormerWorkerSettings(BaseWorkerSettings):
    worker_type = "former"


class FormerWorker(BaseWorker):
    @staticmethod
    async def process_template(ctx: WorkerContext) -> None:
        pass
