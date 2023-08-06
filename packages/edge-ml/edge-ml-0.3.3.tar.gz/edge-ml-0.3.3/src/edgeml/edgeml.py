import requests as req
from edgeml.consts import getProjectEndpoint, initDatasetIncrement, addDatasetIncrement
from edgeml.Dataset import Dataset
import time

class DatasetReceiver:

    def __init__(self, backendURL, readKey=None, writeKey=None):
        self.backendURL = backendURL
        self._readKey=readKey
        self._writeKey=writeKey
        res = req.get(backendURL + getProjectEndpoint + readKey)
        if res.status_code == 403:
            raise RuntimeError("Invalid key")
        elif res.status_code >= 300:
            raise RuntimeError(res.reason)
        self.datasets = []
        res_data = res.json()
        datasets = res_data["datasets"]
        self.labeligns = res_data["labelings"]
        for d in datasets:
            tmp_dataset = Dataset(backendURL, self._readKey, self._writeKey)
            tmp_dataset.parse(d, self.labeligns)
            self.datasets.append(tmp_dataset)

    def loadData(self):
        for d in self.datasets:
            d.loadData()

    @property
    def data(self):
        return [x.data for x in self.datasets]

    def __str__(self) -> str:
        return "\n".join([str(x) for x in self.datasets])

URLS = {
    "uploadDataset": "/api/deviceapi/uploadDataset",
    "initDatasetIncrement": "/ds/api/dataset/init/",
    "addDatasetIncrement": "/ds/api/dataset/append/",
    "getDatasetsInProject": "/ds/api/datasets/"
}

UPLOAD_INTERVAL = 5 * 1000

class DatasetCollector:
    def __init__(
        self, url, apiKey, name, useDeviceTime, timeSeries, metaData, datasetLabel=None
    ):
        self.url = url
        self.apiKey = apiKey
        self.name = name
        self.useDeviceTime = useDeviceTime
        self.timeSeries = timeSeries
        self.metaData = metaData
        self.datasetLabel = datasetLabel
        self.error = None
        self.uploadComplete = False
        self.labeling = None
        self.lastChecked = time.time() * 1000

        if self.useDeviceTime:
            self.addDataPoint = self._addDataPoint_DeviceTime
        else:
            self.addDataPoint = self._addDataPoint_OwnTimeStamps


        if self.datasetLabel:
            labeling_name, label_name = self.datasetLabel.split("_")
            self.labeling = {"labelingName": labeling_name, "labelName": label_name}

        self.error = None

        res = req.post(
            url + initDatasetIncrement + apiKey,
            json={
                "name": self.name,
                "metaData": self.metaData,
                "timeSeries": self.timeSeries,
                "labeling": self.labeling,
            },
        )

        if res.status_code != 200:
            raise RuntimeError(res.text.split(':')[1][1:-2])

        res_data = res.json()
        if not res_data or not res_data["id"]:
            raise RuntimeError("Could not generate DatasetCollector")
        self.datasetKey = res_data["id"]
        self.dataStore = {x: [] for x in self.timeSeries}
    
    async def _addDataPoint_DeviceTime(self, name, value):
        timestamp = int(time.time() * 1000)
        await self._addDataPoint_OwnTimeStamps(timestamp, name, value)

    async def _addDataPoint_OwnTimeStamps(self, timestamp, name, value):
        if name not in self.timeSeries:
            raise ValueError("invalid time-series name")

        if not isinstance(value, (int, float)):
            raise ValueError("Datapoint is not a number")

        if not isinstance(timestamp, (int)):
            raise ValueError("Provide a valid timestamp")
        self.dataStore[name].append([timestamp, value])

        if time.time() * 1000 - self.lastChecked > UPLOAD_INTERVAL:
            self.upload(self.labeling)
            self.lastChecked = time.time() * 1000


    async def upload(self, uploadLabel):
        tmp_dataStore = self.dataStore.copy()
        tmp_dataStore = [{"name": k, "data": tmp_dataStore[k]} for k in tmp_dataStore.keys()]
        response = req.post(
            self.url
            + addDatasetIncrement
            + self.apiKey
            + "/"
            + self.datasetKey,
            json={"data": tmp_dataStore, "labeling": None},
        )
        self.dataStore = {x: [] for x in self.timeSeries}
        if response.status_code != 200:
            raise RuntimeError("Upload failed")

    # Synchronizes the server with the data when you have added all data
    def onComplete(self):
        if self.uploadComplete:
            raise RuntimeError("Dataset is already uploaded")
        tmp_dataStore = self.dataStore.copy()
        tmp_dataStore = [{"name": k, "data": tmp_dataStore[k]} for k in tmp_dataStore.keys()]
        response = req.post(
            self.url
            + addDatasetIncrement
            + self.apiKey
            + "/"
            + self.datasetKey,
            json={"data": tmp_dataStore, "labeling": self.labeling},
        )
        if response.status_code != 200:
            raise RuntimeError("Upload failed")
        if self.error:
            raise RuntimeError(self.error)
        self.uploadComplete = True
        self.dataStore = {x: [] for x in self.timeSeries}
        return True