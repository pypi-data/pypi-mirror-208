from Scrapinger.Library.scrapingerGlobals import scrapingerGlobal
from RolexReserver.Library.rolexReserverConfig import rolexReserverConfig

class rolexReserverGlobal(scrapingerGlobal):
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ呼び出し
        super().__init__()

        self.rolexReserverConfig:rolexReserverConfig = None
        """ RolexReserver共通設定 """

# インスタンス生成(import時に実行される)
gv = rolexReserverGlobal()
