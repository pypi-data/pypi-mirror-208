import os,sys,time,datetime
from trendingbot.scrape import scrape_site

class SITE:
    def __init__(self,name,url,locate):
        self.name=name
        self.url=url
        self.locate=locate

class TRENDING_Assistant(object):
    NAME="Assistant"
    DESC="assistant of autoprocess"
    def __init__(self,name=NAME,desc=DESC,archive_path="",clock_h=12,clock_m=0):
        self.dir=""
        assert archive_path!=""
        assert os.path.exists(archive_path)
        assert clock_h<24 and clock_h>=0 and clock_m<60 and clock_m>=0
        self.hour=clock_h
        self.minute=clock_m

        self.dir=archive_path
        self.log=self.dir+f"/{name}.log"

        # if not os.path.exists(archive_path):
        #     self.f=open(self.log,"w",encoding="utf8")
        # else:
        #     self.f=open(self.log,"a",encoding="utf8")
        # sys.stdout=self.f
        # sys.stderr=self.f
        self.run()

    def log_msg(self,content,type='INFO'):
        with open(self.log,'at',encoding='utf8') as fp:
            t=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fp.write(f'[{type}] {t}'+'\t')
            fp.write(content+'\n')
    def get_web(self):
        return [
            SITE("知乎", 'https://tophub.today/n/mproPpoq6O', "HOT"),
            SITE("微博", 'https://tophub.today/n/KqndgxeLl9', "HOT"),
            SITE("百度", 'https://tophub.today/n/Jb0vmloB1G', "HOT"),

            SITE("天猫", 'https://tophub.today/n/7Gdab3peQy', "COMSUME"),
            SITE("京东", 'https://tophub.today/n/YqoXzV6dOD', "COMSUME"),
            SITE("36氪", 'https://tophub.today/n/Q1Vd5Ko85R', "COMSUME"),
            SITE("今日热卖", 'https://tophub.today/n/x9ozqX7eXb', "COMSUME"),
            SITE("pdd", 'https://tophub.today/n/ARe1QZ2e7n', "COMSUME"),


            SITE("微信", 'https://tophub.today/n/WnBe01o371', "COMMUNITE"),
            SITE("少数派", 'https://tophub.today/n/Y2KeDGQdNP', "COMMUNITE"),
            SITE("虎嗅", 'https://tophub.today/n/5VaobgvAj1', "COMMUNITE"),
            SITE("baidubar", 'https://tophub.today/n/Om4ejxvxEN', "COMMUNITE"),
            SITE("天涯", 'https://tophub.today/n/Jb0vmmlvB1', "COMMUNITE"),
            SITE("水木社区", 'https://tophub.today/n/rDgeyqeZqJ', "COMMUNITE"),
            SITE("虎扑", 'https://tophub.today/n/G47o8weMmN', "COMMUNITE"),
            SITE("澎湃", 'https://tophub.today/n/wWmoO5Rd4E', "COMMUNITE"),
            SITE("宽带山", 'https://tophub.today/n/Jb0vml8oB1', "COMMUNITE"),

            SITE("acfun", 'https://tophub.today/n/qENeYpdY49', "ENTERTAINMENT"),
            SITE("bili", 'https://tophub.today/n/74KvxwokxM', "ENTERTAINMENT"),
            SITE("tiktok", 'https://tophub.today/n/DpQvNABoNE', "ENTERTAINMENT"),

            SITE("知乎日报", 'https://tophub.today/n/KMZd7VOvrO', "DAILY"),
            SITE("历史上的今天", 'https://tophub.today/n/KMZd7X3erO', "DAILY"),
            SITE("todayheadline", 'https://tophub.today/n/x9ozB4KoXb', "DAILY"),

            SITE("起点", 'https://tophub.today/n/VaobmGneAj', "FICTION"),

            SITE("taptap", 'https://tophub.today/n/6ARe1k2v7n', "GAME"),
            SITE("3dm", 'https://tophub.today/n/YqoXQR0vOD', "GAME"),
            SITE("游研社", 'https://tophub.today/n/Om4ej8mvxE', "GAME"),

            SITE("新浪体育", 'https://tophub.today/n/wWmoOqYd4E', "SOPRTS"),
            SITE("知乎体育", 'https://tophub.today/n/2KeDwVYdNP', "SOPRTS"),
            SITE("虎扑社区", 'https://tophub.today/n/6ARe1YLe7n', "SOPRTS"),
            SITE("懂球帝", 'https://tophub.today/n/n3moBE1eN5', "SOPRTS"),

            SITE("人人都是经理", 'https://tophub.today/n/20MdKx4ew1', "WORK"),
            SITE("咖啡日报", 'https://tophub.today/n/9Jndklye3V', "WORK"),
            SITE("产品100", 'https://tophub.today/n/K7GdalYvQy', "WORK"),
            SITE("Product Hunt", 'https://tophub.today/n/LBwdG0jePx', "WORK"),



            SITE("appstore", 'https://tophub.today/n/4anopWBelZ', "MOBILE"),
            SITE("aifanxiu", 'https://tophub.today/n/Jndkp4ye3V', "MOBILE"),
            SITE("最美应用", 'https://tophub.today/n/zQ0or05d8B', "MOBILE"),
            SITE("汽车之家", 'https://tophub.today/n/YqoXQGXvOD', "CAR"),
            SITE("老司机", 'https://tophub.today/n/1yjvQN6dbg', "CAR"),
            SITE("易车网", 'https://tophub.today/n/ENeYLZqdY4', "CAR"),

            # SITE("", 'https://tophub.today', "CN"),

            SITE("新浪财经", 'https://tophub.today/n/rx9ozj7oXb', "ECONOMY"),
            SITE("wallstreet",'https://tophub.today/n/G2me3ndwjq',"ECONOMY"),
            SITE("第一财经",'https://tophub.today/n/0MdKam4ow1',"ECONOMY"),
            SITE("snowball",'https://tophub.today/n/X12owXzvNV',"ECONOMY"),
            SITE("财经",'https://tophub.today/n/3QeLGVPd7k',"ECONOMY"),
            SITE("stockbar",'https://tophub.today/n/rx9ozQbeXb',"ECONOMY"),
            SITE("Buffett",'https://tophub.today/n/yjvQDXPobg',"ECONOMY"),
            SITE("ilovecrack",'https://tophub.today/n/NKGoRAzel6',"ECONOMY"),

            SITE("github",'https://tophub.today/n/rYqoXQ8vOD',"TECH"),
            SITE("nuggets",'https://tophub.today/n/QaqeEaVe9R',"TECH"),
            SITE("csdn",'https://tophub.today/n/K7GdajgeQy',"TECH"),
            SITE("IT之家", 'https://tophub.today/n/74Kvx59dkx', "TECH"),
            SITE("开发者头条", 'https://tophub.today/n/5VaobmGeAj', "TECH"),

            SITE("看雪论坛", 'https://tophub.today/n/Kqndg1xoLl', "NETSECURITY"),
            SITE("安全客", 'https://tophub.today/n/qYwv4MNdPa', "NETSECURITY"),
            SITE("FreeBuf", 'https://tophub.today/n/WYKd6pzoaP', "NETSECURITY"),
            SITE("安全脉搏 ", 'https://tophub.today/n/NRrvWG1v5z', "NETSECURITY"),
        ]

    def take_rest(self,now,year,month,day,hour,minute):
        today = datetime.datetime(year=year, month=month, day=day,hour=hour,minute=minute)
        next_day = today + datetime.timedelta(days=1)
        if self.rest:
            sleept = (next_day - now).seconds
            print(sleept)
            if sleept < 300:
                self.rest = False
            # time.sleep(max(sleept-100,200))
            time.sleep(1)
    def reset_rest(self):
        self.rest=True

    def run(self):
        step=0
        self.rest=True
        self.websites=self.get_web()
        while self.websites:
            now=datetime.datetime.now()
            year,month,day=now.year,now.month,now.day
            # sleep
            print('rest')
            self.take_rest(now,year,month,day,self.hour,self.minute)
            print('invoke')
            sign=self.scrape_web(year,month,day)
            if sign:
                self.log_msg('update complete with some wrong','WARN')
            else:
                self.log_msg('update complete successfully','INFO')
            self.reset_rest()
            step+=1
    def scrape_web(self,year,month,day):
        sign=0
        for i,site in enumerate(self.websites):
            try:
                output=scrape_site(site)
                self.save_archive(year,month,day,site.name,output)
            except:
                sign=1
                self.log_msg(f'{site.name} crawl error','ERROR')
                # self.websites.pop(i)
                self.log_msg(f'drop website:{site.name}', 'WARN')
        return sign
    def save_archive(self,year,month,day,site,output):
        dir_y=self.dir+f"/{year}"
        dir_m=dir_y+f"/{month}"
        dir_d=dir_m+f"/{day}"
        path_site=dir_d+f"/{site}"
        if not os.path.exists(dir_y):
            os.mkdir(dir_y)
        if not os.path.exists(dir_m):
            os.mkdir(dir_m)
        if not os.path.exists(dir_d):
            os.mkdir(dir_d)
        # if not os.path.exists(path_site):
        with open(path_site+'.txt',mode="wt",encoding="utf8") as fp:
            for ht in output['trending_list']:
                fp.write(f'{ht.topic}\t')
                fp.write(f'{ht.type}\t')
                fp.write(f'{ht.content}\n')

# TRENDING_Assistant(archive_path="../archive",clock_h=10,clock_m=0)




























