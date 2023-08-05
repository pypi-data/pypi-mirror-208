from pathlib import Path
from pyPhases import PluginAdapter
from pyPhasesRecordloader import RecordLoader


class Plugin(PluginAdapter):
    def initPlugin(self):
        RecordLoader.registerRecordLoader("RecordLoaderMESA", "pyPhasesRecordloaderMESA.recordLoaders")
        RecordLoader.registerRecordLoader("MESAAnnotationLoader", "pyPhasesRecordloaderMESA.recordLoaders")
        mesaPath = Path(self.getConfig("mesa-path"))

        self.project.setConfig("loader.mesa.filePath", mesaPath.as_posix())
        self.project.setConfig("loader.mesa.dataset.downloader.basePath", mesaPath.as_posix())
        self.project.setConfig(
            "loader.mesa.dataset.downloader.basePathExtensionwise",
            [
                (mesaPath / "polysomnography/edfs/").as_posix(),
                (mesaPath / "polysomnography/annotations-events-nsrr/").as_posix(),
            ],
        )
