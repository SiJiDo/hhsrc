#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
import os
from time import time
import json

from process import SubProcessSrc
from urllib.parse import urlparse

FILEPATH = os.path.split(os.path.realpath(__file__))[0]

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'redis://127.0.0.1:6379/0'
    backend = 'redis://127.0.0.1:6379/2'

app = Celery('hhsrc.gau', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(target):

    work_dir = FILEPATH + '/tools'
    out_file_name = 'gau_{}.txt'.format(time())
    tmp_file_name = 'tmp_{}.txt'.format(time())
    out_file_name2 = 'httpx_{}.txt'.format(time())

    # 执行命令 ./gau -o 1.txt -random-agent -b jpg,png,gif www.jd.com
    if DEBUG == 'True':
        command = ['./gau_mac', '-o', out_file_name, '-random-agent', '-b', 'jpg,png,gif,html', target]
        command1 = ['sort', '-u', out_file_name, '-o', tmp_file_name]
        command2 = ['./httpx_mac', '-l', tmp_file_name, '-status-code', '-no-color', '-o', out_file_name2]
    else:
        command = ['./gau', '-o', out_file_name, '-random-agent', '-b', 'jpg,png,gif,html', target]
        command1 = ['sort', '-u', out_file_name, '-o', tmp_file_name]
        command2 = ['./httpx_mac', '-l', tmp_file_name, '-status-code', '-no-color', '-o', out_file_name2]
    result = []
    tmp = []
    tmp2 = []
    try:
        sb = SubProcessSrc(command, cwd=work_dir).run()
        if sb['status'] == 0:
            gau_result = [] 
            # 运行成功，读取数据
            with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                gau_result.append(f.readlines())
            sb = SubProcessSrc(command1, cwd=work_dir).run()
            if sb['status'] == 0:
                with open('{}/{}'.format(work_dir, tmp_file_name), 'r') as f:
                    tmp = f.readlines()
                for t in tmp:
                    t = t.split('\n')[0]
                    t2 = t.split('?')[0]
                    if(t2 not in tmp2):
                        tmp2.append(t)
                os.system('rm -rf {}/{}'.format(work_dir, tmp_file_name))
            file = open(FILEPATH + '/tools/' + tmp_file_name, 'w');
            for tag in tmp2:
                file.write(tag + '\n')
            file.close()

            sb = SubProcessSrc(command2, cwd=work_dir).run()
            if sb['status'] == 0:
                print("-------------开始存储------------")
                with open('{}/{}'.format(work_dir, out_file_name2), 'r') as f:
                    dic = {}
                    re = f.readlines()
                    print(type(re))
                    print(re)
                    if('[200]' in re and re not in tmp):
                        url = re.split(' [')[0]
                        urlres = urlparse(url)
                        dic["host"] =  urlres.scheme + "://" + urlres.netloc
                        dic["scheme"] = urlres.scheme 
                        dic["path"] = urlres.netloc + urlres.path
                        dic["param"] = urlres.params       
                        result.append(dic)

    except Exception as e:
        print(e)

    try:
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
        os.system('rm -rf {}/{}'.format(work_dir, tmp_file_name))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name2))
    except:
        pass
    return {'tool': 'gau', 'result': result}

if __name__ == '__main__':
    target = 'www.jd.com'
    print(run(target))
