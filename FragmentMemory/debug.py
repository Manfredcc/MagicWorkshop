import logging
import os

class Logger:
    def __init__(self, logFile='fragMem.log', log_level=logging.DEBUG):
        # 使用单例模式，确保整个应用只有一个Logger实例存在
        _instance = None

        def __new__(cls, *args, **kwargs):
            if not cls._instance:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance.__init__(*args, **kwargs)
            return cls._instance
        # 初始化log对象：
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

        # 创建文件处理器，将日志写入文件
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # 创建控制台处理器，将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # 创建格式器，将其添加到处理器中
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将处理器添加到log对象
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def pDebug(self, msg):
        self.logger.debug(msg)

    def pInfo(self, msg):
        self.logger.info(msg)

    def pWarn(self, msg):
        self.logger.warning(msg)

    def pError(self, msg):
        self.logger.error(msg)
