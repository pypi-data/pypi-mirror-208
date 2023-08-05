import mlflow


"""
Sidetrek mlflow wrapper.
"""


class MlflowLogger:
    __TRACKING_URI = "https://mlflow.sidetrek.com/p"

    def __set_tracking_uri(self, url: str):
        # from self.__mflow import set_tracking_uri
        # self.__mflow.set_registry_uri
        if url != self.__TRACKING_URI:
            raise Exception("Tracking uri can't be changed to " + url)

    def __init__(self):
        self.mlflow = mlflow
        self.mlflow.set_tracking_uri(self.__TRACKING_URI)

        # User should not change the tracking uri
        self.mlflow.set_tracking_uri = self.__set_tracking_uri


mlflow_logger = MlflowLogger()
logger = mlflow_logger.mlflow

