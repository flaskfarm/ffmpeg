setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': 'list',
    'menu': {
        'uri': __package__,
        'name': 'FFMPEG',
        'list': [
            {
                'uri': 'download',
                'name': '다운로드',
                'list': [
                    {
                        'uri': 'setting',
                        'name': '설정',
                    },
                    {
                        'uri': 'request',
                        'name': '다운로드 요청',
                    },
                    {
                        'uri': 'list',
                        'name': '다운로드 목록',
                    },
                    
                ]
            },
            {
                'uri': 'manual',
                'name': '매뉴얼',
                'list': [
                    {
                        'uri': 'README.md',
                        'name': 'README',
                    },
                ]
            },
            {
                'uri': 'log',
                'name': '로그',
            },
        ]
    },
    'default_route': 'normal',
}

from plugin import *

P = create_plugin_instance(setting)
try:
    from .mod_download import ModuleDownload
    P.set_module_list([ModuleDownload])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

