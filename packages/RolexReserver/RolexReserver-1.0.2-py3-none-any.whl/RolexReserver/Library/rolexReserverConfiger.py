import LibHanger.Library.uwLogger as Logger
from LibHanger.Library.uwGlobals import configer
from LibHanger.Library.uwGlobals import *
from RolexReserver.Library.rolexReserverGlobals import *

class rolexReserverConfiger(configer):
    
    """
    RolexReserver共通設定クラス
    """
    
    def __init__(self, _tgv:rolexReserverGlobal, _file, _configFolderName):
        
        """
        コンストラクタ
        """
        
        # RolexReserver.ini
        da = rolexReserverConfig()
        da.getConfig(_file, _configFolderName)

        # gvセット
        _tgv.rolexReserverConfig = da
        
        # ロガー設定
        Logger.setting(da)
