# 导入loguru模块
from loguru import logger

# 定义一个Log类，封装loguru的功能
class LoguruHandler:
    # 初始化方法，设置日志文件的路径和格式
    def __init__(self, file_path, format, rotation=None, compression="zip"):
        # 使用logger.add方法添加一个日志处理器，指定文件路径和格式
        # 判断是否要日志滚动
        if  rotation is None:
            logger.add(file_path, format=format, compression="zip")
        else:
            logger.add(file_path, format=format, rotation=rotation, compression="zip")

    # 定义一个info方法，用于记录调试级别的日志
    def debug(self, message):
        # 使用logger.info方法输出信息级别的日志
        logger.debug(message)

    # 定义一个info方法，用于记录信息级别的日志
    def info(self, message):
        # 使用logger.info方法输出信息级别的日志
        logger.info(message)

    # 定义一个warning方法，用于记录警告级别的日志
    def warning(self, message):
        # 使用logger.error方法输出错误级别的日志
        logger.warning(message)

    # 定义一个error方法，用于记录错误级别的日志
    def error(self, message):
        # 使用logger.error方法输出错误级别的日志
        logger.error(message)

# # 创建一个Log对象，指定日志文件的路径和格式
# log = LoguruHandler("log.txt", "{time} - {level} - {message}")

# # 调用info方法，记录一条信息级别的日志
# log.info("This is an info message")

# # 调用error方法，记录一条错误级别的日志
# log.error("This is an error message")