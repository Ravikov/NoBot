# 主函数入口
# v0.2.0

# 执行前检查
from check import check
check()

import time
import threading
import sys
import io
import shutil
from src.common import config
from debug.log import log
from src.touch_llm import *
from src.reply import reply
from src.start_ways import *
from src.guide import set_config

# 设置编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==========<测试函数部分>==========
def test(api,url=None,key=None,model=None):
    if api == 0:
        re = connect(key,url,model,[{'role':'user','content':'Just Answer 1'}])
    else:
        re =  connect(config[api]['key'],config[api]['url'],config[api]['name'],[{'role':'user','content':'Just Answer 1'}])
    if re != 1:
        log('测试返回'+re.text)
        re = re.json()
        if re["choices"][0]["message"]["content"] == '1':
            log('模型测试通过')
        else:
            log('测试未通过','warn')
    else:
        log('出错,请检查状态码','error')


# ==========<程序启动部分>==========
# 启动函数
def run_bot():
    if __name__ == '__main__':
        log('程序启动')
        if config['non_setup']:
            log('首次启动,编辑配置文件...')
            start_way = 'set'
        else:
            print("""请选择启动方式:
                save-备份配置文件
                load-恢复上一次备份
                set-设置配置文件
                0-测试模型联通(一般会消耗 10 tokens左右)
                1-webhook启动(未维护,不建议使用)
                2-命令行启动
                3-微信启动(不可用)
                4-微信clawbot启动
            """)
            print('在下方输入选择编号并回车,程序运行途中,您可以随时按 CTRL+C 退出,包括现在')
            try:
                start_way = input()
            except KeyboardInterrupt:
                log('选择中断')
                return 0
        
        match start_way:
            case '0':
                answer = input(
                    '请输入要测试的模型...\n'
                    '当前可选模型列表:\n'
                    f"1-主模型: {config['API']['name']} , url地址: {config['API']['url']}\n"
                    f"2-辅助模型: {config['secAPI']['name']} , url地址: {config['secAPI']['url']}\n"
                    f"3-联网模型: {config['searchAPI']['name']} , url地址: {config['searchAPI']['url']}\n"
                    '4-亦可键入url,key,modle进行测试\n'
                )
                if answer == '1':
                    test('API')
                elif answer == '2':
                    test('secAPI')
                elif answer == '3':
                    test('searchAPI')
                elif answer == '4':
                    url = input('请输入模型url地址: ')
                    key = input('请输入对应url的API key: ')
                    model = input('请输入模型名: ')
                    test(0,url,key,model)
            case '1':
                # 子线程
                # 1.创建子线程flask启动函数
                def start_flask():
                    log(f'flask子线程开始运行,按Ctrl+C退出程序,线程ID: {flask_work.ident}')
                    log('3秒后启动flask进程...')
                    time.sleep(3)
                    # 启动flask app
                    log('Bot成功唤醒')
                    app.run(host='0.0.0.0',port=5000)
                # 2.创建子进程以规避app.run对日志的阻塞
                flask_work = threading.Thread(target=start_flask,daemon=True)
                flask_work.start()

            case '2':
                log('命令行启动...')
                # 发起请求
                question = input("请输入问题：")
                result,ms = reply(question)
                print(f'\n请求成功, 返回结果：\n\n{result}\n\n延迟{ms}s')
            case '3':
                log('微信启动...')
                threading.Thread(target=wechat_bot,daemon=True).start()
            case '4':
                log('Wechat Claw Bot启动...')
                threading.Thread(target=wechat_claw,daemon=True).start()

            case 'set':
                threading.Thread(target=set_config,daemon=True).start()
            case 'save':
                shutil.copy('config/config.json','config/config.json.bak')
                log('备份配置文件成功!')
            case 'load':
                shutil.copy('config/config.json.bak','config/config.json')
                log('加载配置文件成功!')

            case _:
                log('输入有误')

        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            log('收到终止指令...')
            log("程序优雅退出~")
    
    return 0

ender = run_bot()
log(f'程序结束,结束码: {ender}')