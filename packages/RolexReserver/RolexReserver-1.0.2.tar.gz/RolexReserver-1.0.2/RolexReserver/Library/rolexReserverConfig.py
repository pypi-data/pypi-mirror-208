from Scrapinger.Library.scrapingConfig import scrapingConfig

class rolexReserverConfig(scrapingConfig):
    
    """
    RolexReserver共通設定クラス(RolexReserverConfig)
    """ 
    
    class settingValueStruct(scrapingConfig.settingValueStruct):

        """
        設定値構造体
        """ 

        class MailConfig(scrapingConfig.settingValueStruct.MailConfig):
            
            """
            MailConfig
            """
            
            mail_from = ''
            mail_to = ''
            
            def __init__(self):
                
                """
                コンストラクタ
                """
                
                super().__init__()
                
                self.mail_from = ''
                """ 送信元メールアドレス """
            
                self.mail_to = ''
                """ 送信先メールアドレス """

    def __init__(self):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__()

        self.rolexReserverMailConfig = self.settingValueStruct.MailConfig()
        """ RolexReserver Mail Config """

        self.rolexReserverMailConfig.mail_from = ''
        """ RolexReserver Mail Config - mail_from """

        self.rolexReserverMailConfig.mail_to = ''
        """ RolexReserver Mail Config - mail_to """
        
        self.processAbortFile = 'stopper.txt'
        """ process abort file """

        self.LimitsScrapingCount = 0
        """ Limits Scraping Count """

        self.rolexUrl = 'https://airrsv.net/rxbt-jnt/calendar'
        """ Rolex予約サイトURL """
        
        self.menuExistsMsgString = '選択可能な予約メニューがありません。'
        """ 予約可能メニューの存在有無を示す文字列(予約可能メニューが無い場合に生成されるメッセージ) """

        self.menuExistsCheckLogFormat = "(RMEC-LOG)"
        """ 予約可能メニュー存在チェックログプレフィックス """

        self.menuExistsCheckLogNoData = "NO DATA"
        """ 予約可能メニュー存在チェックログ(データ無し) """

        self.menuExistsCheckLogExistsData = "EXISTS DATA"
        """ 予約可能メニュー存在チェックログ(データ有り) """
        
        # 設定ファイル名追加
        self.setConfigFileName('RolexReserver.ini')
        
    def getConfig(self, _scriptFilePath: str, configFileDir: str = ''):
        
        """ 
        設定ファイルを読み込む 
        
        Parameters
        ----------
        _scriptFilePath : str
            スクリプトファイルパス
        configFileDir : str
            設定ファイルの格納場所となるディレクトリ
        """

        # 基底側のiniファイル読込
        super().getConfig(_scriptFilePath, configFileDir)
        
    def setInstanceMemberValues(self):
        
        """ 
        インスタンス変数に読み取った設定値をセットする
        """
        
        # 基底側実行
        super().setInstanceMemberValues()
        
        # Rolex予約サイトURL
        self.setConfigValue('rolexUrl',self.config_ini,'SITE','ROLEX_URL',str)

        # RolexReserver MailConfig - mail_from
        self.setConfigValue('rolexReserverMailConfig.mail_from',self.config_ini,'MAIL_CONFIG','MAIL_FROM',str)

        # RolexReserver MailConfig - mail_to
        self.setConfigValue('rolexReserverMailConfig.mail_to',self.config_ini,'MAIL_CONFIG','MAIL_TO',str)

        # RolexReserver Limits Scraping Count
        self.setConfigValue('LimitsScrapingCount',self.config_ini,'SITE','LIMITS_SCRAPING_COUNT_ONEDAY',int)

        # process abort file
        self.setConfigValue('processAbortFile',self.config_ini,'ABORT','PROCESS_ABORT_FILE',str)
        
        # menuExistsMsgString
        self.setConfigValue('menuExistsMsgString',self.config_ini,'SITE','MENU_EXISTS_MESSAGE',str)

        # menuExistsCheckLogFormat
        self.setConfigValue('menuExistsCheckLogFormat',self.config_ini,'SITE','MENU_EXISTS_CHECK_LOG_FORMAT',str)

        # menuExistsCheckLogNoData
        self.setConfigValue('menuExistsCheckLogNoData',self.config_ini,'SITE','MENU_EXISTS_CHECK_LOG_NODATA',str)

        # menuExistsCheckLogExistsData
        self.setConfigValue('menuExistsCheckLogExistsData',self.config_ini,'SITE','MENU_EXISTS_CHECK_LOG_EXISTSDATA',str)
