# -*- coding: utf-8 -*-
import json
import yaml
import socket
import inspect
import logging
import asyncio
import platform
import requests
import threading
import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver
import os, sys

sys.path.append(os.getcwd())
use_oop = True
try:
    # 如果 ./app/ 目录下存在 app_main.py 文件，则模型主程序使用非面向对象模式编程，忽略同目录下的 app_core.py 文件（如果存在）
    from app import app_main

    use_oop = False
except:
    # 如果 ./core/ 目录下存在 model_main.py 文件，则模型主程序使用面向对象模式编程
    from app.app_core import AppCore

    use_oop = True


class GlobalData:
    def __init__(self):
        self.app_core = None
        self.port = 80
        self.python_frontend_port = 7860

    def init_global_data(self):
        try:
            self.app_core = AppCore() if use_oop else app_main
            return True
        except Exception as e:
            logging.error(str(e))
            return False


g = GlobalData()


class DataApi(tornado.web.RequestHandler):

    async def post(self, *args, **kwargs):

        try:
            input = json.loads(str(self.request.body, encoding='utf-8'))
        except Exception as e:
            logging.error(str(e))
            result = {
                'status': 'err',
                'value': 'HTTP请求体错误：' + str(e)
            }
            self.write(result)
            return

        input['request_info'] = {}
        input['request_info']['http_request'] = self.request
        authorization = self.request.headers.get('Authorization')
        if authorization and authorization.lower().startswith('bearer'):
            input['request_info']['jwt'] = authorization[7:]  # 去除前缀“Bearer ”
        if authorization and authorization.lower().startswith('basic'):
            input['request_info']['auth_basic'] = authorization[6:]  # 去除前缀“Basic ”

        output = {
            'result': {},
            'finish': False
        }

        thread = threading.Thread(
            target=data_service,
            args=(input, output)
        )
        thread.setDaemon(True)
        thread.start()

        while not output['finish']:
            await asyncio.sleep(0.01)
        result = output['result']

        if self.request.headers.get('Origin'):
            self.set_header('Access-Control-Allow-Credentials', 'true')
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))

        if isinstance(result['value'], bytes):
            self.write(result['value'])
        else:
            self.write(result)

    async def options(self, *args, **kwargs):
        self.set_status(204)
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
        self.set_header('Access-Control-Allow-Headers', 'content-type')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')


def data_service(input, output):
    if not isinstance(input, dict):
        result = {
            'value': 'HTTP请求体不是JSON格式！',
            'status': 'err'
        }
        output['result'] = result
        output['finish'] = True
        return

    action = input.get('action')
    args = input.get('args')
    threading.current_thread().request_info = input.get('request_info')

    if action is None:
        result = {
            'value': 'HTTP请求体中未携带action！',
            'status': 'err'
        }
        output['result'] = result
        output['finish'] = True
        return

    if action == '__init__':
        result = {
            'value': '__init__禁止访问！',
            'status': 'err'
        }
        output['result'] = result
        output['finish'] = True
        return

    public_actions = getattr(g.app_core, 'public_actions', None)
    if public_actions is not None:
        if action not in public_actions:
            result = {
                'value': 'Action: {} 禁止访问！'.format(action),
                'status': 'err'
            }
            output['result'] = result
            output['finish'] = True
            return

    action_obj = getattr(g.app_core, action, None)
    if action_obj is None:
        result = {
            'value': 'Action: {} 未定义！'.format(action),
            'status': 'err'
        }
        output['result'] = result
        output['finish'] = True
        return

    result = {}
    try:
        result['value'] = action_obj(**args) if args else action_obj()  # kwargs为None或{}时，不带参数调用
        result['status'] = 'ok'
    except Exception as e:
        logging.error(str(e))
        result['value'] = str(e)
        result['status'] = 'err'

    output['result'] = result
    output['finish'] = True


class StreamApi(tornado.web.RequestHandler):

    async def post(self, path, *args, **kwargs):

        if '/' in path:
            i = path.find('/')
            action = path[:i]
            path_args = path[i + 1:]
        else:
            action = path
            path_args = None

        input = {
            'action': action,
            'bytestream': self.request.body,
            'request_info': {},
        }
        input['request_info']['http_request'] = self.request
        if path_args:
            input['request_info']['path_args'] = path_args
        authorization = self.request.headers.get('Authorization')
        if authorization and authorization.lower().startswith('bearer'):
            input['request_info']['jwt'] = authorization[7:]  # 去除前缀“Bearer ”
        if authorization and authorization.lower().startswith('basic'):
            input['request_info']['auth_basic'] = authorization[6:]  # 去除前缀“Basic ”

        output = {
            'result': {},
            'finish': False
        }

        thread = threading.Thread(
            target=stream_service,
            args=(input, output)
        )
        thread.setDaemon(True)
        thread.start()

        while not output['finish']:
            await asyncio.sleep(0.01)
        result = output['result']

        if self.request.headers.get('Origin'):
            self.set_header('Access-Control-Allow-Credentials', 'true')
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))

        if isinstance(result['value'], bytes):
            self.write(result['value'])
        else:
            self.write(result)

    async def options(self, *args, **kwargs):
        self.set_status(204)
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
        self.set_header('Access-Control-Allow-Headers', 'content-type')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')


def stream_service(input, output):
    action = input.get('action')
    bytestream = input.get('bytestream')
    threading.current_thread().request_info = input.get('request_info')

    if action == '__init__':
        result = {
            'value': '__init__禁止访问！',
            'status': 'err'
        }
        output['result'] = result
        output['finish'] = True
        return

    public_actions = getattr(g.app_core, 'public_actions', None)
    if public_actions is not None:
        if action not in public_actions:
            result = {
                'value': 'Action: {} 禁止访问！'.format(action),
                'status': 'err'
            }
            output['result'] = result
            output['finish'] = True
            return

    action_obj = getattr(g.app_core, action, None)
    if action_obj is None:
        result = {
            'value': 'Action: {} 未定义！'.format(action),
            'status': 'err'
        }
        output['result'] = result
        output['finish'] = True
        return

    result = {}
    try:
        result['value'] = action_obj(bytestream)
        result['status'] = 'ok'
    except Exception as e:
        logging.error(str(e))
        result['value'] = str(e)
        result['status'] = 'err'

    output['result'] = result
    output['finish'] = True


class FileApi(tornado.web.RequestHandler):

    async def post(self, path, *args, **kwargs):

        if '/' in path:
            i = path.find('/')
            action = path[:i]
            path_args = path[i + 1:]
        else:
            action = path
            path_args = None

        try:
            file_obj = self.request.files.get(action)[0]
            file_body = file_obj.body
            filename = file_obj.filename
        except Exception as e:
            logging.error(str(e))
            result = {
                'status': 'err',
                'value': 'HTTP文件上传请求体错误：' + str(e)
            }
            self.write(result)
            return

        input = {
            'action': action,
            'bytestream': file_body,
            'request_info': {},
        }
        input['request_info']['http_request'] = self.request
        input['request_info']['filename'] = filename
        if path_args:
            input['request_info']['path_args'] = path_args
        authorization = self.request.headers.get('Authorization')
        if authorization and authorization.lower().startswith('bearer'):
            input['request_info']['jwt'] = authorization[7:]  # 去除前缀“Bearer ”
        if authorization and authorization.lower().startswith('basic'):
            input['request_info']['auth_basic'] = authorization[6:]  # 去除前缀“Basic ”

        output = {
            'result': {},
            'finish': False
        }
        thread = threading.Thread(
            target=stream_service,
            args=(input, output)
        )
        thread.setDaemon(True)
        thread.start()

        while not output['finish']:
            await asyncio.sleep(0.01)
        result = output['result']

        if self.request.headers.get('Origin'):
            self.set_header('Access-Control-Allow-Credentials', 'true')
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))

        if isinstance(result['value'], bytes):
            self.write(result['value'])
        else:
            self.write(result)

    async def options(self, *args, **kwargs):
        self.set_status(204)
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
        self.set_header('Access-Control-Allow-Headers', 'content-type')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')


class SpecialApi(tornado.web.RequestHandler):

    async def get(self, *args, **kwargs):

        input = {
            'request_info': {},
        }
        input['request_info']['http_request'] = self.request
        authorization = self.request.headers.get('Authorization')
        if authorization and authorization.lower().startswith('bearer'):
            input['request_info']['jwt'] = authorization[7:]  # 去除前缀“Bearer ”
        if authorization and authorization.lower().startswith('basic'):
            input['request_info']['auth_basic'] = authorization[6:]  # 去除前缀“Basic ”

        output = {
            'result': {},
            'finish': False
        }

        thread = threading.Thread(
            target=special_service,
            args=(input, output)
        )
        thread.setDaemon(True)
        thread.start()

        while not output['finish']:
            await asyncio.sleep(0.01)
        result = output['result']

        if result['status'] == 'ok':
            if self.request.headers.get('Origin'):
                self.set_header('Access-Control-Allow-Credentials', 'true')
                self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
            self.write(result['value'])
        else:
            self.set_status(400)
            self.write(result['value'])

    async def post(self, *args, **kwargs):

        input = {
            'request_info': {},
        }
        input['request_info']['http_request'] = self.request
        authorization = self.request.headers.get('Authorization')
        if authorization and authorization.lower().startswith('bearer'):
            input['request_info']['jwt'] = authorization[7:]  # 去除前缀“Bearer ”
        if authorization and authorization.lower().startswith('basic'):
            input['request_info']['auth_basic'] = authorization[6:]  # 去除前缀“Basic ”

        output = {
            'result': {},
            'finish': False
        }

        thread = threading.Thread(
            target=special_service,
            args=(input, output)
        )
        thread.setDaemon(True)
        thread.start()

        while not output['finish']:
            await asyncio.sleep(0.01)
        result = output['result']

        if result['status'] == 'ok':
            if self.request.headers.get('Origin'):
                self.set_header('Access-Control-Allow-Credentials', 'true')
                self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
            self.write(result['value'])
        else:
            self.set_status(400)
            self.write(result['value'])

    async def put(self, *args, **kwargs):

        input = {
            'request_info': {},
        }
        input['request_info']['http_request'] = self.request
        authorization = self.request.headers.get('Authorization')
        if authorization and authorization.lower().startswith('bearer'):
            input['request_info']['jwt'] = authorization[7:]  # 去除前缀“Bearer ”
        if authorization and authorization.lower().startswith('basic'):
            input['request_info']['auth_basic'] = authorization[6:]  # 去除前缀“Basic ”

        output = {
            'result': {},
            'finish': False
        }

        thread = threading.Thread(
            target=special_service,
            args=(input, output)
        )
        thread.setDaemon(True)
        thread.start()

        while not output['finish']:
            await asyncio.sleep(0.01)
        result = output['result']

        if result['status'] == 'ok':
            if self.request.headers.get('Origin'):
                self.set_header('Access-Control-Allow-Credentials', 'true')
                self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
            self.write(result['value'])
        else:
            self.set_status(400)
            self.write(result['value'])

    async def delete(self, *args, **kwargs):

        input = {
            'request_info': {},
        }
        input['request_info']['http_request'] = self.request
        authorization = self.request.headers.get('Authorization')
        if authorization and authorization.lower().startswith('bearer'):
            input['request_info']['jwt'] = authorization[7:]  # 去除前缀“Bearer ”
        if authorization and authorization.lower().startswith('basic'):
            input['request_info']['auth_basic'] = authorization[6:]  # 去除前缀“Basic ”

        output = {
            'result': {},
            'finish': False
        }

        thread = threading.Thread(
            target=special_service,
            args=(input, output)
        )
        thread.setDaemon(True)
        thread.start()

        while not output['finish']:
            await asyncio.sleep(0.01)
        result = output['result']

        if result['status'] == 'ok':
            if self.request.headers.get('Origin'):
                self.set_header('Access-Control-Allow-Credentials', 'true')
                self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
            self.write(result['value'])
        else:
            self.set_status(400)
            self.write(result['value'])

    async def options(self, *args, **kwargs):
        # 允许跨域
        self.set_status(204)
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin'))
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')


def special_service(input, output):
    threading.current_thread().request_info = input.get('request_info')
    result = {}
    try:
        result['value'] = g.app_core.special_api()
        result['status'] = 'ok'
    except Exception as e:
        logging.error(str(e))
        result['value'] = str(e)
        result['status'] = 'err'

    output['result'] = result
    output['finish'] = True


class WebSocketServer(tornado.websocket.WebSocketHandler):

    def open(self):
        pass

    def on_message(self, message):
        try:
            msg = json.loads(message, encoding='utf-8')
        except Exception as e:
            logging.error(str(e))
            logging.error('WebSocket消息必须采用JSON格式！')
            return

        thread = threading.Thread(
            target=websocket_message_runner,
            args=(asyncio.get_event_loop(), self, msg)
        )
        thread.setDaemon(True)
        thread.start()

    def on_close(self):
        logging.critical('websocket closed')

    def check_origin(self, origin):
        return True


def websocket_message_runner(event_loop, websocket, msg):
    asyncio.set_event_loop(event_loop)
    try:
        g.app_core.process_websocket_message(websocket, msg)
    except Exception as e:
        logging.error(str(e))


class HealthChecker(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('{"description": "ServiceBoot", "status": "UP"}')


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def start_python_frontend():
    try:
        from app.python_frontend import PythonFrontend
        python_frontend = PythonFrontend()
        logging.critical('##################################################')
        logging.critical(f'    Python frontend started ...')
        logging.critical(f'    Web access: http://{get_local_ip()}:{g.python_frontend_port}/')
        logging.critical('##################################################')
        thread = threading.Thread(target=python_frontend_thread, args=(asyncio.get_event_loop(), python_frontend))
        thread.setDaemon(True)
        thread.start()
    except Exception as e:
        logging.error('Python前端启动失败：' + str(e))


def python_frontend_thread(event_loop, python_frontend):
    asyncio.set_event_loop(event_loop)
    kwargs = {
        'server_name': '0.0.0.0',
        'server_port': g.python_frontend_port,
        'show_api': False,
    }
    python_frontend.launch(**kwargs)


def serviceboot_client(action, **args):
    url = f'http://127.0.0.1:{g.port}/api/data'
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': '*/*',
    }
    body = {
        'action': action,
        'args': args,
    }

    try:
        res = requests.post(url=url, json=body, headers=headers)
    except Exception as e:
        return {
            'status': 'err',
            'value': '网络或服务器故障：' + str(e)
        }

    if res.status_code != 200:
        return {
            'status': 'err',
            'value': res.text
        }

    try:
        # JSON数据，转化成JSON对象
        result = json.loads(res.text, encoding='utf-8')
    except:
        # 非JSON数据（二进制字节流），直接返回
        result = res.content

    return result


def gen_api_docs(*api_functions):
    api_md_text = '## [ServiceBoot](https://openi.pcl.ac.cn/cubepy/serviceboot) APIs\n\n'
    for function in api_functions:
        name = function.__name__
        args = inspect.signature(function).parameters

        api_md_text += f'### {name}\n\n'
        api_md_text += '- HTTP方法： POST\n\n'
        api_md_text += '- API端点： /api/data\n\n'
        api_md_text += '- HTTP请求体：\n'
        api_md_text += '```\n'
        api_md_text += '{\n'
        api_md_text += f'    "action": "{name}",\n'
        api_md_text += '    "args": {\n'
        for arg in args:
            api_md_text += f'        "{arg}": <{arg}的值>,\n'
        api_md_text += '    }\n'
        api_md_text += '}\n'
        api_md_text += '```\n\n'
        api_md_text += '- HTTP响应体：\n'
        api_md_text += '```\n'
        api_md_text += '{\n'
        api_md_text += '    "status": "ok" | "err",\n'
        api_md_text += '    "value": <服务端计算返回值> | <错误描述>,\n'
        api_md_text += '}\n'
        api_md_text += '```\n\n'
    api_md_text += '\n\n'

    return api_md_text


def start():
    app_profile = os.environ.get('APP_PROFILE', 'dev').lower()
    log_level = logging.DEBUG if app_profile == 'dev' else logging.ERROR
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        with open('./application.yml', 'rb') as f:
            yml = yaml.load(f, Loader=yaml.SafeLoader)
    except:
        logging.error('服务配置文件application.yml不存在！')
        return

    try:
        ename = yml['serviceboot']['ename']
    except:
        logging.error('未指定服务英文名！请在application.yml文件中编辑修改...')
        return

    try:
        cname = yml['serviceboot']['cname']
    except:
        cname = ename.upper()

    if app_profile == 'dev':
        try:
            port = yml['serviceboot']['port']['dev']
        except:
            logging.error('未指定服务端口号！缺省使用80端口。')
            port = 80
    else:
        try:
            port = yml['serviceboot']['port']['prod']
        except:
            logging.error('未指定服务端口号！缺省使用80端口。')
            port = 80
    g.port = port

    if not g.init_global_data():
        logging.error('微服务： {}/{} 初始化失败！'.format(cname, ename))
        return

    try:
        use_python_frontend = yml['serviceboot']['use_python_frontend']
    except:
        use_python_frontend = False
    # 启动Python前端服务
    if use_python_frontend:
        try:
            g.python_frontend_port = yml['serviceboot']['python_frontend_port']
        except:
            g.python_frontend_port = 7860
        start_python_frontend()

    handlers = [
        (r'/management/health', HealthChecker),
        (r'/special/(.*)', SpecialApi),
        (r'/api/data', DataApi),
        (r'/api/stream/(.*)', StreamApi),
        (r'/api/file/(.*)', FileApi),
        (r'/websocket', WebSocketServer),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': 'webapp/www', 'default_filename': 'index.html'}),
    ]

    debug = 'dev' == app_profile  # 开发模式缺省启动debug
    try:
        process_number = yml['serviceboot']['process_num']  # 如果yml配置文件中指定了进程数，则强制使用
        if debug:
            debug = 1 == process_number  # 开发模式模式下，如果yml配置文件中指定了进程数不为1，则强制关闭debug
    except:
        process_number = 1  # 如果yml配置文件中未指定进程数，则设定进程数=1

    if platform.system() != 'Linux':  # 非Linux环境中一律设定进程数=1
        process_number = 1

    app = tornado.web.Application(
        handlers=handlers,
        debug=debug
    )
    http_server = tornado.httpserver.HTTPServer(app, max_buffer_size=1000 * 1024 * 1024)
    http_server.bind(port)
    http_server.start(num_processes=process_number)

    try:
        has_web = yml['serviceboot']['has_web']  # 如果yml配置文件中指定了进程数，则强制使用
    except:
        has_web = False

    logging.critical('##################################################')
    logging.critical('    ServiceBoot微服务： {}/{} started ...'.format(cname, ename))
    logging.critical('    Listening at: {}:{}'.format(get_local_ip(), port))
    if has_web:
        logging.critical('    Web access: http://{}:{}/'.format(get_local_ip(), port))
    logging.critical('    App profile: {}'.format(app_profile))
    logging.critical('##################################################')
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    start()
