from pyPhasesRecordloaderSHHS.recordLoaders.RecordLoaderSHHS import RecordLoaderSHHS

class RecordLoaderMESA(RecordLoaderSHHS):
    def getFilePathSignal(self, recordId):
        return f"{self.filePath}/polysomnography/edfs/{recordId}.edf"

    def getFilePathAnnotation(self, recordId):
        return f"{self.filePath}/polysomnography/annotations-events-nsrr/{recordId}-nsrr.xml"