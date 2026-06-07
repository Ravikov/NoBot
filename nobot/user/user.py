import pathlib
import json
import shutil
import pathlib
import time
from debug.log import *

root = pathlib.Path(__file__).parent.parent
listfile = pathlib.Path(__file__).parent / 'userlist.json'

class User:

    def __init__(self, name='main', mode='choose'):
        self.name = name
        self.mode = mode

def load_usrjson():
    with open(listfile, 'r', encoding='utf-8') as f:
        return json.load(f)
def save_usrlist(usrlist):
    userjson = load_usrjson()
    with open(listfile, 'w', encoding='utf-8') as f:
        userjson['user'] = usrlist
        json.dump(userjson,f,ensure_ascii=False,indent=2)

def run():
    global usrobj
    # 检查是否首次启动
    try:
        with open(root/'config'/'main'/'config.json','r',encoding='utf-8') as f:
            main_config = json.load(f)
            if main_config['non_setup']:
                log('配置文件未经设置,进入main用户')
                usrobj=User(name='main')
                return
            else:
                pass
    except:
        log('首次启动,直接进入main用户')
        usrobj=User(name='main')
        return

    # 检查与创建userlist
    try:
        load_usrjson()
        debug_log(f'{listfile}存在')
    except:
        debug_log(f'{listfile}不存在,尝试创建')
        with open(listfile, 'w', encoding='utf-8') as f:
            userjson = {
                "user": [
                    {
                    "name":"main",
                    "creat_time": time.strftime('%Y-%m-%d %H:%M',time.localtime())
                    }
                ]
            }
            json.dump(userjson,f,ensure_ascii=False,indent=2)
        debug_log('创建完毕')

    userlist = load_usrjson()['user']
    def get_namelist():
        global userlist
        userlist = load_usrjson()['user']
        user_namelist = []
        for usr in userlist:
            user_namelist.append(usr['name'])
        return user_namelist
    user_namelist = get_namelist()

    def choose():
        global usrobj
        while 1:
            print('当前有如下用户:')
            for usr in userlist:
                print(f"名称: {usr['name']},创建时间: {usr['creat_time']}")
                
            print('请输入启动用户的名称,或输入delete来删除一个用户,输入creat来创建一个用户')
            start_user = input('>>>')

            if start_user in get_namelist():
                break
            else:
                match start_user:
                    case 'delete':
                        return User(mode='delete')
                    case 'creat':
                        return User(mode='creat')
                    case _:
                        log('选择有误,请重新选择!')

        log(f"选定用户{start_user}")
        usrobj = User(name=start_user)
        return usrobj

    def get_usrconfig(name):
        return [
            root/'config'/name,
            root/'memory'/name,
            root.parent/'IMchat'/'clawbot'/'config'/name
        ]

    while 1:
        usrobj = choose()
        match usrobj.mode:
            case 'delete':
                print('\n请输入要删除的用户名称')
                del_name = input('delete/>>>')
                if del_name in get_namelist() and del_name != 'main':
                    
                    agree = input(f'最后确定,要删除用户{del_name}吗?此操作不可逆! [Yes/n]')
                    if agree in ['Yes','yes']:
                        log(f'删除用户{del_name}')
                        usr_config = get_usrconfig(del_name)
                        for f in usr_config:
                            debug_log(f"删除目录{f}")
                            shutil.rmtree(f)
                        del_dict = [d for d in userlist if d['name'] == del_name][0]
                        debug_log(f"删除用户字典{del_dict}")
                        userlist = load_usrjson()['user']
                        userlist.remove(del_dict)
                        save_usrlist(userlist)
                        log(f"删除用户 {del_name} 成功")
                    else:
                        print('取消删除操作')
                        continue
                else:
                    if del_name == 'main':
                        print('主用户无法删除!')
                    else:
                        print('输入的用户名不存在! 程序将重新运行')
            case 'creat':
                while 1:
                    print('\n请输入要创建的用户名称(建议为英文,如果中文报错就重新用英文创建,不要有"_"以外的字符),输入/choose返回入口')
                    creat_name = input('creat/>>>')
                    if creat_name == '/choose':
                        break
                    if creat_name in get_namelist():
                        print('新创建的用户名不能和已有的相同! ')
                    else:
                        break

                if creat_name == '/choose':
                    print('\n')
                    continue

                usr_config = get_usrconfig(creat_name)
                for f in usr_config:
                    debug_log(f"创建目录{f}")
                    pathlib.Path(f).mkdir(parents=True)
                userlist = load_usrjson()['user']
                new_usrdict = {'name':creat_name,'creat_time':time.strftime('%Y-%m-%d %H:%M',time.localtime())}
                userlist.append(new_usrdict)
                debug_log(f"添加用户字典{new_usrdict}")
                save_usrlist(userlist)
                log(f'创建用户 {creat_name} 成功')
            case 'choose':
                break

run()