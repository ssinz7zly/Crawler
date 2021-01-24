# -*- coding: UTF-8 -*-
'''
@File ：豆瓣电影.py
@IDE ：PyCharm
@Author ：zly
@Date ：2021/1/23 15:12
'''
from bs4 import BeautifulSoup  #网页解析，获取数据
import re   #正则表达式，进行文字匹配
import urllib.request,urllib.error  #制定url，获取网页数据
import xlwt #进行excel操作
import sqlite3  #进行数据库操作

def main():
    baseurl="https://movie.douban.com/top250?start="
    datalist=getData(baseurl)
    savepath="D://爬虫//豆瓣电影Top250.xls"
    saveData(datalist,savepath)

#正则提取
findLink=re.compile(r'<a href="(.*?)">')
findImgsrc=re.compile(r'<img.*src="(.*?)"',re.S) #re.S让换行符包括在字符中
findTitle=re.compile(r'<span class="title">(.*)</span>')
findRating=re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findJudge=re.compile(r'<span>(\d*)人评价</span>')
findInq=re.compile(r'<span class="inq">(.*)</span>')
findBd=re.compile(r'<p class="">(.*?)</p>',re.S)

#爬取网页
def getData(baseurl):
    datalist=[]
    for i in range(0,10):  #一页有25个，要获取250页故要做循环
        url=baseurl+str(i*25)
        html=askURL(url)   #保存获取到的网页源码
        #逐一解析数据
        soup =BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):     #查找符合要求的字符串形成列表(div 中class属性是item)
            data=[]  #保存一部电影的所有信息
            item=str(item)
            link=re.findall(findLink,item)[0]   #找到的第一个就可以了
            data.append(link)
            Imgsrc=re.findall(findImgsrc,item)[0]
            data.append(Imgsrc)
            Title=re.findall(findTitle,item)   #片名有好几个
            if len(Title)==2:
                ctitle=Title[0]     #只加中文title
                data.append(ctitle)
                otitle=Title[1].replace("/","")  #去掉无关符号
                data.append(otitle)
            else:
                data.append(Title[0])
                data.append(" ")   #没有外国title就留空(不然保存到excel等地方会错位)
            Rating=re.findall(findRating,item)[0]
            data.append(Rating)
            JudgeNumber = re.findall(findJudge, item)[0]
            data.append(JudgeNumber)
            Inq = re.findall(findInq, item)
            if len(Inq) !=0:
                Inq=Inq[0].replace("。","")
                data.append(Inq)
            else:
                data.append(" ")  #还是防止错位
            Bd = re.findall(findBd, item)[0]
            Bd=re.sub("<br(\s+)?/>(\s+)?"," ",Bd)   #因为有一个或多个<br>标签，所以要替换
            Bd=re.sub("/"," ",Bd)
            data.append(Bd.strip())
            datalist.append(data)
    return datalist

#得到指定一个URL的网页内容
def askURL(url):
    head={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75"
    }  #身份伪装
    request=urllib.request.Request(url,headers=head)  #封装成一个对象
    html=""
    try:
        response=urllib.request.urlopen(request)
        html=response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):   #判断e这个对象里卖弄是否包含code属性
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html

#保存数据
def saveData(datalist,savepath):
    book=xlwt.Workbook(encoding="utf-8",style_compression=0)
    sheet=book.add_sheet("豆瓣电影Top250",cell_overwrite_ok=True)
    col=("电影详情链接","图片链接","影片中文名","影片外文名","评分","评价数","概况","相关信息")
    for i in range(8):
        sheet.write(0,i,col[i])  #写列名,0,i代表第1行第i+1列
    for i in range(0,250):
        print("第%d条"%(i+1))
        data=datalist[i]
        for j in range(8):
            sheet.write(i+1,j,data[j])
    book.save(savepath)

if __name__=="__main__":   #程序入口
     main()
     print("爬取完毕")
