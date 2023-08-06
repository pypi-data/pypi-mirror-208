
from utils.system import decorate_exception_result
from test_framework.state import UpgradeType
from test_framework.firmware_engine.oakgate.nvme_download import NVMeDownload
from test_framework.firmware_engine.oakgate.two_step_download import OakgateTwoStepDownload


class OakgateDownloader(object):

    def __init__(self):
        pass

    @decorate_exception_result
    def run(self, parameters):
        download_type = int(parameters.get("upgrade_type", 1))
        dl_engine = OakgateTwoStepDownload() if download_type == UpgradeType.TwoStepDownload[0] else NVMeDownload()
        ret, logs = dl_engine.run(parameters)
        return ret, logs
