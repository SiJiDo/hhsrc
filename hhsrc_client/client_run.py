import os
import configparser
from time import time

cfg = configparser.ConfigParser()
cfg.read('config.ini')
FILEPATH = os.path.split(os.path.realpath(__file__))[0]

def run():
    #启动subfinder的celery
    if(cfg.get("WORKER_CONFIG", "subdomain_subfinder") == 'True'):
        os.chdir("{}/subdomain_scan/subfinder".format(FILEPATH))
        os.system("nohup celery -A subfinder worker -l info -Q subfinder -n subfinder_{} -c 1 &".format(time()))
    #启动amass的celery
    if(cfg.get("WORKER_CONFIG", "subdomain_amass") == 'True'):
        os.chdir("{}/subdomain_scan/amass".format(FILEPATH))
        os.system("nohup celery -A amass worker -l info -Q amass -n amass_{} -c 1 &".format(time()))
    #启动shuffledns的celery
    if(cfg.get("WORKER_CONFIG", "subdomain_shuffledns") == 'True'):
        os.chdir("{}/subdomain_scan/shuffledns".format(FILEPATH))
        os.system("nohup celery -A shuffledns worker -l info -Q shuffledns -n shuffledns_{} -c 1 &".format(time()))
    #启动domaininfo的celery
    if(cfg.get("WORKER_CONFIG", "subdomain_domaininfo") == 'True'):
        os.chdir("{}/subdomain_scan/domaininfo".format(FILEPATH))
        os.system("nohup celery -A domaininfo worker -l info -Q domaininfo -n domaininfo_{} -c 1 &".format(time()))
    #启动naabu的celery
    if(cfg.get("WORKER_CONFIG", "port_naabu") == 'True'):
        os.chdir("{}/port_scan/naabu".format(FILEPATH))
        os.system("nohup celery -A naabu worker -l info -Q naabu -n naabu_{} -c 1 &".format(time()))
    #启动httpx的celery
    if(cfg.get("WORKER_CONFIG", "http_httpx") == 'True'):
        os.chdir("{}/url_scan/httpx".format(FILEPATH))
        os.system("nohup celery -A httpx worker -l info -Q httpx -n httpx_{} -c 1 &".format(time()))
    #启动screenshot的celery
    if(cfg.get("WORKER_CONFIG", "http_screenshot") == 'True'):
        os.chdir("{}/url_scan/screenshot".format(FILEPATH))
        os.system("nohup celery -A screenshot worker -l info -Q screenshot -n screenshot_{} -c 1 &".format(time()))
    #启动fileleak的celery
    if(cfg.get("WORKER_CONFIG", "dirb_fileleak") == 'True'):
        os.chdir("{}/dirb_scan/fileleak".format(FILEPATH))
        os.system("nohup celery -A fileleak worker -l info -Q fileleak -n fileleak_{} -c 1 &".format(time()))
    #启动nuclei的celery
    if(cfg.get("WORKER_CONFIG", "dirb_nuclei") == 'True'):
        os.chdir("{}/dirb_scan/nuclei".format(FILEPATH))
        os.system("nohup celery -A nuclei worker -l info -Q nuclei -n nuclei_{} -c 1 &".format(time()))

if __name__ == '__main__':
    run()