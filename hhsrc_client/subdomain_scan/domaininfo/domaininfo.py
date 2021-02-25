#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
import os
from time import time
import json
from threading import *
import queue
import dns.resolver

FILEPATH = os.path.split(os.path.realpath(__file__))[0]

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'redis://127.0.0.1:6379/0'
    backend = 'redis://127.0.0.1:6379/2'

app = Celery('hhsrc.domaininfo', broker=broker, backend=backend, )
app.config_from_object('config')
result = []

@app.task
def run(domain_list):
    thread_count = 64
    domain_queue = queue.Queue()
    for domain in domain_list:
        domain_queue.put(domain)

    # 使用多线程
    threads = []
    for i in range(0, thread_count):
        thread = domaininfo(domain_queue)
        thread.start()
        threads.append(thread)

    for j in threads:
        j.join()
    print(result)
    return {'tool': 'domaininfo', 'result': result}

#使用多线程
class domaininfo(Thread):
    def __init__(self, domain_queue):
        Thread.__init__(self)
        self.queue = domain_queue

    ### func:get_ip and func:get_cname
    def get_ip(self, domain, log_flag = True):
        domain = domain.strip()
        ips = []
        try:
            answers = dns.resolver.resolve(domain, 'A')
            for rdata in answers:
                ips.append(rdata.address)
        except dns.resolver.NXDOMAIN as e:
            if log_flag:
                print("{} {}".format(domain, e))

        except Exception as e:
            if log_flag:
                print("{} {}".format(domain, e))
        return ips

    def get_cname(self, domain, log_flag = True):
        cnames = []
        try:
            answers = dns.resolver.resolve(domain, 'CNAME')
            for rdata in answers:
                cnames.append(str(rdata.target).strip(".").lower())
        except dns.resolver.NoAnswer as e:
            if log_flag:
                print(e)
        except Exception as e:
            if log_flag:
                print("{} {}".format(domain, e))
        return cnames

    def run(self):
        queue = self.queue
        while not queue.empty():
            try:
                domain = queue.get()
                ips = self.get_ip(domain)
                if not ips:
                    result.append({})
                cnames = self.get_cname(domain, False)
                info = {
                    "domain": domain,
                    "type": "A",
                    "record": ips,
                    "ips": ips
                }
                if cnames:
                    info["type"] = 'CNAME'
                    info["record"] = cnames
                result.append(info)
            except:
                pass
                #print("[-]host unknow")

        return


if __name__ == '__main__':
    list = [
        "asia-news-abroad.vivo.com",
"asia-exstatic.vivo.com",
"visionplus.vivo.com",
"sg-exstpay.vivo.com",
"es.vivo.com",
"sdp.vivo.com",
"tech.vivo.com",
"in-ali-browserproxy-cname.vivo.com",
"internetgratis.vivo.com",
"shgj.vivo.com",
"vivo.com",
"browserproxy.vivo.com",
"homepage.vivo.com",
"cloud.vivo.com",
"shop.vivo.com",
"hr.vivo.com",
"360.vivo.com",
"ru.vivo.com",
"www.vivo.com",
"easyshare.vivo.com",
"go.vivo.com",
"issue.dev.vivo.com",
"p2pw9w4irnb.ohzzwfdhop.vivo.com",
"hybrid.vivo.com",
"icampusbrasil.vivo.com",
"www2.vivo.com",
"www.ru.vivo.com",
"browsercloud.vivo.com",
"www.portal.vivo.com",
"in-exstatic-vivofs.vivo.com",
"ddivulga.vivo.com",
"institutocem.static.vivo.com",
"vivo360.vivo.com",
"slb-exvivoportal-web.vivo.com",
"bs.vivo.com",
"as.vivo.com",
"passport.vivo.com",
"asia-ali-cname-www.vivo.com",
"mms.vivo.com",
"daleto.vivo.com",
"findphone.vivo.com",
"browsercore.vivo.com",
"in-ali-cname-www.vivo.com",
"e.vivo.com",
"zhushou.vivo.com",
"asia-exstatic-vivofs.vivo.com",
"portalrecarga.vivo.com",
"portaldeinformacoes.vivo.com",
"vds.vivo.com",
"bhwkju.vivo.com",
"webcloud.vivo.com",
"www.pelis.vivo.com",
"global.vivo.com",
"mshop.vivo.com",
"portal.vivo.com",
"tianma-prd-in.vivo.com",
"err.up.vivo.com",
"zhaopin.vivo.com",
"zap.vivo.com",
"medialive.vivo.com",
"homepagestatic.vivo.com",
"zs.vivo.com",
    ]
    run(list)
