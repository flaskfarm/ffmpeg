from email import header

from support import SupportSubprocess
from support.expand.ffmpeg import SupportFfmpeg
from support.expand.ffprobe import SupportFfprobe

from .setup import *

name = 'download'

class ModuleDownload(PluginModuleBase):
    db_default = {
        f'ffmpeg_path': 'ffmpeg',
        f'ffprobe_path': 'ffprobe',
        f'max_pf_count': '0',
        f'save_path': "download",
        f'timeout_minute': '60',

        f'download_url': '',
        f'download_curl': '',
    }


    def __init__(self, P):
        super(ModuleDownload, self).__init__(P, 'list')
        self.name = name
        default_route_socketio_module(self, attach='/list')


    def process_menu(self, page_name, req):
        arg = P.ModelSetting.to_dict()
        try:
            arg['path_data'] = F.config['path_data']
            if page_name == 'request':
                arg['temp_filename'] = f"{str(time.time()).split('.')[0]}.mp4"

            return render_template(f'{P.package_name}_{name}_{page_name}.html', arg=arg)
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            return render_template('sample.html', title=f"{P.package_name}/{name}/{page_name}")

    
    
    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'ffmpeg_version':
            ffmpeg_path = P.ModelSetting.get('ffmpeg_path')
            if os.path.exists(ffmpeg_path) == False:
                ret['ret'] = 'danger'
                ret['msg'] = "파일이 없습니다."
            else:
                cmd = [ffmpeg_path, '-version']
                result = SupportSubprocess.execute_command_return(cmd)
                P.logger.info(result)
                ret['modal'] = result['log']
                ret['title'] = 'ffmpeg 버전'
        elif command == 'ffprobe_version':
            ffmpeg_path = P.ModelSetting.get('ffprobe_path')
            if os.path.exists(ffmpeg_path) == False:
                ret['ret'] = 'danger'
                ret['msg'] = "파일이 없습니다."
            else:
                cmd = [ffmpeg_path, '-version']
                result = SupportSubprocess.execute_command_return(cmd)
                P.logger.info(result)
                ret['modal'] = result['log']
                ret['title'] = 'ffprobe 버전'
              
        elif command == 'download':
            filename = arg1
            url = arg2
            P.ModelSetting.set('download_url', arg2)
            ffmpeg = SupportFfmpeg(url, filename, 
                #callback_id=f"{P.package_name}_{time.time()}",
                callback_function=self.callback_function,
                max_pf_count = P.ModelSetting.get('max_pf_count'),
                save_path = os.path.join(F.config['path_data'], P.ModelSetting.get('save_path')),
                timeout_minute = P.ModelSetting.get('timeout_minute'),
            )
            ret['json'] = ffmpeg.start()
            #logger.warning(d(ret))
            return jsonify(ret)
        elif command == 'download_curl':
            filename = arg1
            curl = arg2
            P.ModelSetting.set('download_curl', curl)
            lines = curl.split('\n')

            logger.warning(d(lines))
            headers = {}
            for line in lines:
                line = line.replace('--compressed', '')
                line = line.strip(' \\')
                logger.debug(line)
                if line.startswith('curl'):
                    url = line.replace('curl ', '').strip("'")
                    logger.error(url)
                elif line.startswith('-H'):
                    tmp = line.replace('-H ', '').strip("'").split(': ')
                    if tmp[0].startswith('sec-'):
                        continue
                    if tmp[0] in ['if-none-match']:
                        continue
                    headers[tmp[0].strip()] = tmp[1].strip()
            
            #logger.warning(d(headers))

            ffmpeg = SupportFfmpeg(url, filename, 
                #callback_id=f"{P.package_name}_{time.time()}",
                callback_function=self.callback_function,
                max_pf_count = P.ModelSetting.get('max_pf_count'),
                save_path = ToolUtil.make_path(P.ModelSetting.get('save_path')),
                timeout_minute = P.ModelSetting.get('timeout_minute'),
                headers=headers,
            )
            ret['json'] = ffmpeg.start()
            
            #logger.warning(d(ret))
            return jsonify(ret)
        elif command == 'list':
            ret = []
            for ins in SupportFfmpeg.get_list():
                ret.append(ins.get_data())
        elif command == 'stop':
            P.logger.error(arg1)
            ffmpeg = SupportFfmpeg.get_instance_by_idx(arg1)
            P.logger.error(ffmpeg)
            ffmpeg.stop()
            ret['data'] = ffmpeg.get_data()
        return jsonify(ret)

    # TODO: 동작 확인 필요
    def process_api(self, sub, req):
        ret = {'ret':'success'}
        try: 
            if sub == 'download':
                url = request.args.get('url')
                filename = request.args.get('filename')
                callback_id = request.args.get('id')
                save_path = request.args.get('save_path')
                if save_path is None:
                    save_path = ToolUtil.make_path(P.ModelSetting.get('save_path'))
                if not os.path.exists(save_path):
                    os.makedirs(save_path)    
                ffmpeg = SupportFfmpeg(url, filename, 
                    callback_id = callback_id,
                    max_pf_count = P.ModelSetting.get('max_pf_count'),
                    save_path = save_path,
                    timeout_minute = P.ModelSetting.get('timeout_minute'),
                )
                ffmpeg.start()
                ret['data'] = ffmpeg.get_data()
            elif sub == 'stop':
                callback_id = request.args.get('id')
                ffmpeg = SupportFfmpeg.get_instance_by_callback_id(callback_id)
                ffmpeg.stop()
                ret['data'] = ffmpeg.get_data()
            elif sub == 'status':
                ret = {}
                callback_id = request.args.get('id')
                ffmpeg = SupportFfmpeg.get_instance_by_callback_id(callback_id)
                ret['data'] = ffmpeg.get_data()
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
            ret['ret'] = 'exception'
            ret['log'] = traceback.format_exc()    
        return jsonify(ret)
    

    def plugin_load(self):
        self.support_init()

    def plugin_load_celery(self):    
        self.support_init()


    def plugin_unload(self):
        SupportFfmpeg.all_stop()
        

    def setting_save_after(self, change_list):
        self.support_init()
                
    
    def support_init(self):
        SupportFfmpeg.initialize(P.ModelSetting.get('ffmpeg_path'), os.path.join(F.config['path_data'], 'tmp'), self.callback_function, P.ModelSetting.get_int('max_pf_count'))
        SupportFfprobe.initialize(P.ModelSetting.get('ffprobe_path'))

    def callback_function(self, **args):
        refresh_type = None
        if args['type'] == 'status_change':
            if args['status'] == SupportFfmpeg.Status.DOWNLOADING:
                refresh_type = 'status_change'
            elif args['status'] == SupportFfmpeg.Status.COMPLETED:
                refresh_type = 'status_change'
            elif args['status'] == SupportFfmpeg.Status.READY:
                data = {'type':'info', 'msg' : '다운로드중 Duration(%s)' % args['data']['duration_str'] + '<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                refresh_type = 'add'    
        elif args['type'] == 'last':
            if args['status'] == SupportFfmpeg.Status.WRONG_URL:
                data = {'type':'warning', 'msg' : '잘못된 URL입니다'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                refresh_type = 'add'
            elif args['status'] == SupportFfmpeg.Status.WRONG_DIRECTORY:
                data = {'type':'warning', 'msg' : '잘못된 디렉토리입니다.<br>' + args['data']['save_fullpath']}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                refresh_type = 'add'
            elif args['status'] == SupportFfmpeg.Status.ERROR or args['status'] == SupportFfmpeg.Status.EXCEPTION:
                data = {'type':'warning', 'msg' : '다운로드 시작 실패.<br>' + args['data']['save_fullpath']}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)
                refresh_type = 'add'
            elif args['status'] == SupportFfmpeg.Status.USER_STOP:
                data = {'type':'warning', 'msg' : '다운로드가 중지 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.COMPLETED:
                data = {'type':'success', 'msg' : '다운로드가 완료 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.TIME_OVER:
                data = {'type':'warning', 'msg' : '시간초과로 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.PF_STOP:
                data = {'type':'warning', 'msg' : 'PF초과로 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
            elif args['status'] == SupportFfmpeg.Status.FORCE_STOP:
                data = {'type':'warning', 'msg' : '강제 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'   
            elif args['status'] == SupportFfmpeg.Status.HTTP_FORBIDDEN:
                data = {'type':'warning', 'msg' : '403에러로 중단 되었습니다.<br>' + args['data']['save_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'   
            elif args['status'] == SupportFfmpeg.Status.ALREADY_DOWNLOADING:
                data = {'type':'warning', 'msg' : '임시파일폴더에 파일이 있습니다.<br>' + args['data']['temp_fullpath'], 'url':'/ffmpeg/download/list'}
                socketio.emit("notify", data, namespace='/framework', broadcast=True)        
                refresh_type = 'last'
        elif args['type'] == 'normal':
            if args['status'] == SupportFfmpeg.Status.DOWNLOADING:
                refresh_type = 'status'
        #P.logger.info(refresh_type)
        self.socketio_callback(refresh_type, args['data'])
