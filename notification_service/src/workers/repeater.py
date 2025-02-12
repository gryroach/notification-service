from .base import BaseWorker, BaseWorkerSettings, WorkerContext


class RepeaterWorkerSettings(BaseWorkerSettings):
    worker_type = "repeater"


class RepeaterWorker(BaseWorker):
    @staticmethod
    async def handle_dlq(ctx: WorkerContext) -> None:
        pass
