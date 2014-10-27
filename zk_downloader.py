import http.client
import http.cookiejar
import urllib.parse
import os
import re

class ZKNodeData:
    """download data structure"""
    def __init__(self, nid, name, link, pid, pname, leaf):
        self.nid = nid
        self.name = name
        self.link = link
        self.pid  = pid
        self.leaf = leaf
        self.pname = pname

class ZKDownloader:
    """download course from zk site"""
    url = "http://jiaoshi.zhikang.org"
    course_url = None
    work_dir = "e:\\zk\\"
    def __init__(self, name, passwd, citycode, xx_url, zx_url, gz_url):
        self.name = name
        self.passwd = passwd
        self.citycode = citycode
        self.xx_url = self.url + xx_url
        self.zx_url = self.url + zx_url
        self.gz_url = self.url + gz_url
        if os.access(self.work_dir, os.F_OK) == False:
            os.mkdir(self.work_dir)
        os.chdir(self.work_dir)
    def login(self):
        """login use user and passwd. return navigate text"""
        params = urllib.parse.urlencode({'teaLoginArgsDto.userName' : self.name,
                                               'teaLoginArgsDto.password' : self.passwd,
                                               'teaLoginArgsDto.cityCode' : self.citycode,
                                               'modeType' : 0,
                                               't' : 0.56})
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        resp = self.opener.open("http://jiaoshi.zhikang.org/sixtteacher/login!login.action?%s" % params)
        resp_all = (resp.read().decode('utf-8'))
        nav_start_flag = "<nav class=\"nav clearfix\">"
        nav_stop_falg = "</nav>"
        start = resp_all.find(nav_start_flag)
        stop = resp_all.find(nav_stop_falg, start)
        if start == -1 or stop == -1 :
            print("login failure. please check the index page html format!")
            return None
        nav_txt = resp_all[start+len(nav_start_flag) : stop]
        return nav_txt

    def extract_course(self, text):
        data = []
        restart = 0
        course_text = text
        while True:
            course_text = course_text[restart:]
            #print("restart", restart, course_text)
            #extract div
            start_flag = "<div class=\"content_title\">"
            start = course_text.find(start_flag)
            if start == -1:
                break;
            stop = course_text.find("</div>", start)
            restart = stop
            item = course_text[start + len(start_flag) : stop]
            
            #extract link
            start_flag = "<a href=\""
            stop_flag = "\">"
            start = item .find(start_flag)
            if start == -1:
                break;
            stop = item.find(stop_flag, start)
            link = item[start + len (start_flag) : stop]
            link = ("%s%s" % (self.url, link))
            
            link = link.replace("course/course!detail.action", "lecture/lecture!listStandard.action")
            link = link.replace("curCourserId", "lectureReq.courseId")
            #extract link text
            start = item.find("</a>", stop)
            text = item[stop + len(stop_flag) : start]
            #save to node list
            node = ZKNodeData("", text, link, "", "", 0)
            data.append(node)
            #print(node.name, node.link)
            
        return data

    def extract_lecture(self, text):
        data = []
        stop = 0
        lecture_text = text
        while True:
            lecture_text = lecture_text[stop:]
            start_flag = "<a href=\""
            stop_flag = "\""
           
            start = lecture_text.find(start_flag)
            if start == -1:
                break
            stop = lecture_text.find(stop_flag, start + len(start_flag))
            link = lecture_text[start + len(start_flag) : stop]
            link = ("%s%s" % (self.url, link))
            link = link.replace("lecture!detail.action", "lecturedownload!downLecture.action")

            start = lecture_text.find("\">", stop)
            stop = lecture_text.find("</a>", start)
            text = lecture_text[start + len(stop_flag) + 1 : stop]
            node = ZKNodeData("", text, link, "", "", 0)
            data.append(node)
            #print(node.name, node.link)

        return data

    def goto_xx_page(self):
        """go to xiao xue page"""
        #create xx root dir
        xx_dir = "高中"
       
        if os.access(xx_dir, os.F_OK) == False:
            os.mkdir(xx_dir)

        data = dict()
        xx_resp = self.opener.open(self.xx_url)
        xx_str = xx_resp.read().decode('utf-8')
        #start flag
        nav_start_flag = "<aside class=\"content_nav\">"
        ul_start_flag = "<ul class=\"list_main\">"
        fn_start_flag = "onclick=\"directory("
        
        nav_start = xx_str.find(nav_start_flag)
        nav_stop = xx_str.find("</aside>", nav_start)
        if nav_start == -1 or nav_stop == -1:
            print("[xx]parse navigate content error, please check the html page format!")
            return None
        nav_text = xx_str[nav_start + len(nav_start_flag) : nav_stop]
        #parse navigate text and create navigate dir
        stop_div = 0
        while True:
            nav_text = nav_text[stop_div:]
            start_div = nav_text.find("<div")
            stop_div = nav_text.find("</div>", start_div)
            
            if start_div == -1 or stop_div == -1:
                break
            nav_item = nav_text[start_div : stop_div]

            #parse ul item
            start = nav_item.find(ul_start_flag)
            stop = nav_item.find("</ul>")
            if (start == -1 or stop == -1):
                continue
            ul_text = nav_item[start + len(ul_start_flag) : stop]
            stop = 0
            while True:
                ul_text = ul_text[stop:]
                li_text = ul_text[start : stop]
                #get li link
                start = ul_text.find(fn_start_flag);
                stop  = ul_text.find(")\"", start)
                if start == -1 or stop == -1:
                    break
                
                fn_text = ul_text[start  + len (fn_start_flag) : stop]
                args = fn_text.split(",")
                nid = args[0].replace('\'', '')
                pname = args[1].replace('\'', '')
                name = args[2].replace('\'', '')
                pid = args[3].replace('\'', '')
                params = urllib.parse.urlencode({"curTab" : 1,
                                                 "courseTypeChildId" : nid,
                                                 "curCourseTypeParentName" : pname,
                                                 "curCourseTypeChildName" : name,
                                                 "courseTypeParentId" : pid,
                                                 "t" : 0.34,
                                                 "modelTab" : 4,
                                                 "isSj" : 0})
                link = ("%s/sixtteacher/course/course!data.action?%s" % (self.url, params))
                #store parent
                if data.get(pid) == None:
                    node_parent = ZKNodeData(pid, pname, "", "", "", 0)
                    data[pid] = node_parent
                    #print(pid, pname)
                    dirname = xx_dir + "\\" + pname
                    if os.access(dirname, os.F_OK) == False:
                        os.mkdir(dirname)
                node_category = ZKNodeData(nid, name, link, pid, pname, 0)
                data[nid] = node_category
            
        #goto course link
        for k, v in data.items():
            if (v.link == ""):
                continue
            dirname = xx_dir + "\\" + v.pname + "\\" + v.name
            print("couse", dirname)
            if os.access(dirname, os.F_OK) == False:
                os.mkdir(dirname)
                        
            resp = self.opener.open(v.link)
            course_text = resp.read().decode('utf-8')
            pager_start_flag = "createPageNav("
            pager_start = course_text.find(pager_start_flag)
            if (pager_start == -1) :
                continue
            pager_stop = course_text.find(")", pager_start);
            fn_text = course_text[pager_start + len (pager_start_flag) : pager_stop]
            args = fn_text.split(",")
            curr_page = int(args[0])
            total_page = int(args[1])
            print(curr_page, total_page)
            course_list1 = self.extract_course(course_text)

            #request course details
            for c in course_list1:
                coursedir = dirname + "\\" + c.name
                if os.access(coursedir, os.F_OK) == False:
                    os.mkdir(coursedir)
                #reqeust file list
                resp = self.opener.open(c.link)
                detail_text = resp.read().decode('utf-8')
                lecture_list1 = self.extract_lecture(detail_text)

                #download lecture
                for l in lecture_list1:
                    #check file exist
                    file_name = coursedir + "\\" + l.name + ".doc"
                    #if os.access(file_name, os.F_OK) == True:
                    #    print("File %s already download into %s" % (file_name, coursedir))
                    #    continue
                    outf = open(file_name, "wb")
                    resp = self.opener.open(l.link)
                    print("Ready to download %s" % file_name)
                    while True:
                        s = resp.read(32*1024)
                        if (len(s) == 0):
                            outf.close()
                            break
                        outf.write(s)
                
            for i in range(curr_page+1, total_page+1):
                params=urllib.parse.urlencode({"curTab" : 1,
                                            "courseTypeChildId" : "",
                                            "curCourseTypeParentName" : "",
                                            "curCourseTypeChildName" : "",
                                            "courseTypeParentId" : "",
                                            "t" : 0.34,
                                            "modelTab" : 4,
                                            "isSj" : 0,
                                            "pageNo" : i,
                                            "filter" : ""})
                link = ("%s/sixtteacher/course/course!data.action?%s" % (self.url, params))
                resp = self.opener.open(link)
                course_text = resp.read().decode('utf-8')
                course_list2 = self.extract_course(course_text)

                for l in course_list2:
                    coursedir = dirname + "\\" + l.name
                    print("details", coursedir)
                    if os.access(coursedir, os.F_OK) == False:
                        os.mkdir(coursedir)
                #/sixtteacher/course/course!data.action?modelTab=4&isSj=0&pageNo=2&curTab=1&curGrade=xx&courseTypeChildId=&courseTypeParentId=&curCourseTypeChildName=&curCourseTypeParentName=&filter=
            
           

    def goto_zx_page(self):
        zx_resp = self.opener.open(self.zx_url)

    def goto_gz_page(self):
        zx_resp = self.opener.open(self.zx_url)
        
        

xx_url = "/sixtteacher/course/course!index.action?curGrade=xx&modelTab=4&isSj=0"
zx_url = "/sixtteacher/course/course!index.action?curGrade=cz&modelTab=4&isSj=0"
gz_url = "/sixtteacher/course/course!index.action?curGrade=gz&modelTab=4&isSj=0"
zkd = ZKDownloader("username ", "password", "020", gz_url, zx_url, gz_url)
nav_text = zkd.login()
if nav_text == None:
    print("login failure, please check the index page format")
print("Welcome to ZK Downloader")
ret = zkd.goto_xx_page()

