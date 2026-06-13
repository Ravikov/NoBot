from debug.log import log

# retry装饰器
def retry(obj,trytime=3):
    def wrapper(*args,**kwargs):
        for i in range(trytime):
            try:
                return obj(*args,**kwargs)
            except Exception as e:
                log(f'执行{obj.__name__}发生错误: {e}, 正在重试...({i+1}/{trytime})','Error')
        log(f'执行{obj.__name__}失败: 已达最大重试次数 {trytime}', 'Error')
    return wrapper