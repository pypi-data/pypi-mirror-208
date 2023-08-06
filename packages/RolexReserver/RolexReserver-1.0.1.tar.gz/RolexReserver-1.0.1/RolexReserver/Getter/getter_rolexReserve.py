#import datetime
#import pandas as pd
#import numpy as np
import LibHanger.Library.uwLogger as Logger
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame
#from enum import Enum
#from decimal import Decimal
#from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from RolexReserver.Library.rolexReserverConfig import rolexReserverConfig
from RolexReserver.Library.rolexReserverGlobals import *
from RolexReserver.Library.rolexReserverException import getterError
#from RolexReserver.Library.rolexReserverException import gettingValueError
from RolexReserver.Getter.Base.baseGetter import baseGetter

class getter_rolexReserve(baseGetter):
    
    """
    予約サイト巡回
    """
    
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        super().__init__()

        # レコードセット初期化
        self.init_recset()

        # スクレイピング準備
        self.wdc.settingScrape()
            
    def init_recset(self):
        """
        レコードセット初期化
        """

        pass

    @Logger.loggerDecorator("getData")
    def getData(self, *args, **kwargs):
        
        """
        予約状況取得
        
        Parameters
        ----------
        None
        
        """
        
        result = None
        try:
            kwargs['getter'] = self
            
            # 予約状況取得
            self.getRolexReserveDataToDataFrame(**kwargs)
            
        except Exception as e: # その他例外
            Logger.logging.error(str(e))
            raise getterError
        
        return result
    
    def cbCheckMem():
        pass
    
    @Logger.loggerDecorator("getStockDataToDataFrame")
    def getRolexReserveDataToDataFrame(self, *args, **kwargs):

        """
        予約状況取得
        
        Parameters
        ----------
        None
        
        """
        
        # 検索url(ルート)
        rootUrl = gv.rolexReserverConfig.rolexUrl

        # ウィンドウサイズを1200x1000にする
        self.wdc.browserCtl.changeBrowserSize('1200', '1000')
        
        # ページロード
        self.wdc.browserCtl.loadPage(rootUrl)
        
        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

    class chrome(browserContainer.chrome):
        
        """
        ブラウザコンテナ:chrome
        """

        def __init__(self, _config: rolexReserverConfig):
            
            """
            コンストラクタ
            
            Parameters
            ----------
                _config : rolexReserverConfig
                    共通設定
            """
            
            super().__init__(_config)

            self.config = _config
            self.cbCreateSearchResultDataFrameByWebDriver = self.createSearchResultDataFrameByWebDriver

        def createSearchResultDataFrameByWebDriver(self, element, *args, **kwargs) -> DataFrame:
            
            """
            予約状況をDataFrameで返す(By Selenium)
            """
            
            return self.getReserveData(element, *args, **kwargs)

        def getReserveData(self, element, *args, **kwargs):
            
            """
            予約状況をDataFrameで返す(By Selenium)
            
            Parameters
            ----------
            kwargs : getter_rolexReserve
                @getter
                    Getterクラス
            """
            
            # getterインスタンス取得
            bc:getter_rolexReserve = kwargs.get('getter')

            # 次週ボタンをクリックする
            
            # html解析
            html = element.parent.page_source
            bsSrc = BeautifulSoup(html, 'lxml')
            
            # スクレイピング結果から改行ｺｰﾄﾞを除去
            [tag.extract() for tag in bsSrc(string='\n')]

            # 予約状況テーブル取得
            reservedTables = bsSrc.contents[0].contents[1].find_all(class_="ly-mainMsg")[0]
                        
            if reservedTables:
                
                # 選択可能なメニューがあるかどうか判別
                if reservedTables.contents[0].text:
                    # 選択可能な予約メニューの存在チェック
                    # '選択可能な予約メニューがありません。'が含まれるかどうか
                    menuExistsMsg = reservedTables.contents[0].text
                    if self.config.menuExistsMsgString in menuExistsMsg:
                        Logger.logging.info(self.config.menuExistsCheckLogFormat.format(self.config.menuExistsCheckLogNoData))
                    else:
                        Logger.logging.info(self.config.menuExistsCheckLogFormat.format(self.config.menuExistsCheckLogExistsData))
                    
                return None
            else:
                Logger.logging.info(self.config.menuExistsCheckLogFormat.format('Data Not Exists.'))

    class beautifulSoup(browserContainer.beautifulSoup):
        
        """
        ブラウザコンテナ:beautifulSoup
        """

        def __init__(self, _config: rolexReserverConfig):
            
            """
            コンストラクタ
            
            Parameters
            ----------
                _config : rolexReserverConfig
                    共通設定
            """

            super().__init__(_config)
            
            self.config = _config
            self.cbCreateSearchResultDataFrameByBeutifulSoup = self.createSearchResultDataFrameByBeutifulSoup
            