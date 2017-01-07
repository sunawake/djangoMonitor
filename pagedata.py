# -*- coding: utf-8 -*-
# in this version, we are using web-api to .... make things looked more modern. like this:
# http://suyang.me/analyse/webapi?region=101010100&section=1&chapter=1&uid=2014110298&type=timeline&stat=flat&length=10
# users must provice username,password to get uid ---- TA will get nothing without a correct uid.
# users will get what TA want by providing region,section,chapter,type,stat,length.

from diagram.models import Element
from diagram.models import Region
from diagram.models import Score
from diagram.models import User

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# def getUID(username,password)
def getUID():
    uid = "2014110298";
    return uid;

# see if region is legal
# region: 101-01-01-00, country-province-city-region
# region[0:3], region[3:5], region[5:7], region[7:9]

# see if input is legal
def verify(r,s,c,uid):
    # verify input
    try:
        region = int(r);
        section = int(s);
        chapter = int(c);
        uid = int(uid);
    except ValueError:
        section = 1;
        chapter = 1;
        region = 101000000;
        uid = 000000000;
    else:
        # verify section and chapter
        if len(Element.objects.values_list('page_id').filter(section_id=section, chapter_id=chapter))<1:
            s = 1;
            c = 1;
        # verify region by uid
        if len(User.objects.values_list('region_id').filter(uid=uid))<1:
            region = 101000000;
        else:
            region = User.objects.values_list('region_id',flat="True").filter(uid=uid).first();
    # get parent region
    region_UP = Region.objects.values_list('parent_id',flat="True").filter(region_id=region)[0];
    # get page, which is an list of page id.
    tmpList = Element.objects.values_list('page_id',flat="True").filter(section_id=section, chapter_id=chapter);
    page = [];
    for i in range(len(tmpList)):
        if int(tmpList[i])<1:
            continue;# prevent p=0
        page.append(str(tmpList[i]));
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "i" in locals():
        del i;
    page.sort();
    del tmpList;
    # return result
    return [region,region_UP,section,chapter,page];

def getPageContent(r,R,s,c):
    cn = "";
    cvs = [];
    # chaptername
    cn = Element.objects.values_list('name').filter(section_id=s, chapter_id=c, page_id="0")[0][0];
    cvs.append(int(Score.objects.values_list('value',flat='True').filter(region_id=r, section_id=s, chapter_id=c, page_id="0", stat="flat").order_by('time')[0]));
    cvs.append(int(Score.objects.values_list('value',flat='True').filter(region_id=r, section_id=s, chapter_id=c, page_id="0", stat="max").order_by('time')[0]));
    cvs.append(int(Score.objects.values_list('value',flat='True').filter(region_id=R, section_id=s, chapter_id=c, page_id="0", stat="mean").order_by('time')[0]));
    cvs.append(int(Score.objects.values_list('value',flat='True').filter(region_id=R, section_id=s, chapter_id=c, page_id="0", stat="max").order_by('time')[0]));
    return [cn,cvs];

# web-api

def getTimeLine(r,s,c,st,lg):
    # verify length
    try:
        lg = int(lg);
    except ValueError:
        lg = 12;
    dictionary = {};
    cname = Element.objects.values_list('name',flat='True').filter(section_id=s, chapter_id=c, page_id="0").first();
    tmpTuple = Score.objects.values_list('time','value').filter(region_id=r, section_id=s, chapter_id=c, page_id="0", stat=st).order_by('time')[0:lg];
    if st == "mean":
        name = cname + "平均值"; # decode('utf-8')
    elif st == "max":
        name = cname + "最大值"; # decode('utf-8')
    elif st == "min":
        name = cname + "最小值"; # decode('utf-8')
    else:
        name = cname;
    xl = [];
    yl = [];
    for i in range(len(tmpTuple)):
        xl.append(tmpTuple[i][0].strftime('%y/%m'));
        yl.append(int(tmpTuple[i][1]));
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "i" in locals():
        del i;
    del tmpTuple;
    dictionary["name"] = name;
    dictionary["xAxis"] = xl;
    dictionary["yAxis"] = yl;
    return dictionary;

def getSubRegion(r,s,c,st,lg):
    # currently we use lg to specify if the chart is bar or pie.
    dictionary = {};
    name = "";
    cname = Element.objects.filter(section_id=s, chapter_id=c, page_id="0").values_list('name',flat='True').first();
    if st == "mean":
        name = cname + "平均值"; # decode('utf-8')
    elif st == "max":
        name = cname + "最大值"; # decode('utf-8')
    elif st == "min":
        name = cname + "最小值"; # decode('utf-8')
    else:
        name = cname;
    sub_regions = Region.objects.filter(parent_id=r).values_list('region_id',flat='True');
    xl = [];
    yl = [];
    # whether the diagram is bar or pie
    try:
        lg = int(lg);
    except ValueError:
        lg = 0;
    if lg>1:
        lg = 1;
    for i in range(len(sub_regions)):
        xv = Region.objects.filter(region_id=sub_regions[i]).values_list('name',flat='True')[0];
        xl.append(xv);
        if lg<1:
            yl.append(int(Score.objects.filter(region_id=sub_regions[i], section_id=s, chapter_id=c, page_id="0", stat=st).order_by('time').values_list('value',flat="True")[0]));
        else:
            tmpDict = {};
            tmpDict["name"] = xv;
            tmpDict["value"] = int(Score.objects.filter(region_id=sub_regions[i], section_id=s, chapter_id=c, page_id="0", stat=st).order_by('time').values_list('value',flat="True")[0]);
            yl.append(tmpDict);
            del tmpDict;
            del xv;
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "i" in locals():
        del i;
    dictionary["name"] = name;
    dictionary["xAxis"] = xl;
    dictionary["yAxis"] = yl;
    return dictionary;

def getSubElement(r,s,c,p,st,lg):
    # currently we ignore param "lg".
    dictionary = {};
    name = "";
    cname = Element.objects.filter(section_id=s, chapter_id=c, page_id="0").values_list('name',flat='True').first();
    if st == "mean":
        name = cname + "平均值"; # decode('utf-8')
    elif st == "max":
        name = cname + "最大值"; # decode('utf-8')
    elif st == "min":
        name = cname + "最小值"; # decode('utf-8')
    else:
        name = cname;
    xl = [];
    yl = [];
    # whether the diagram is bar or pie
    try:
        lg = int(lg);
    except ValueError:
        lg = 0;
    for i in range(len(p)):
        xl.append(Element.objects.filter(section_id=s,chapter_id=c,page_id=p[i]).values_list('name',flat='True')[0]);
        if lg == 0:
            yl.append(int(Score.objects.values_list('value',flat="True").filter(region_id=r,section_id=s,chapter_id=c,page_id=p[i],stat=st).order_by('time')[0]));
        if lg == 1:
            tmpDict = {};
            tmpDict["name"] = Element.objects.filter(section_id=s,chapter_id=c,page_id=p[i]).values_list('name',flat='True')[0];
            tmpDict["value"] = int(Score.objects.values_list('value',flat="True").filter(region_id=r,section_id=s,chapter_id=c,page_id=p[i],stat=st).order_by('time')[0]);
            yl.append(tmpDict);
            del tmpDict;
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "i" in locals():
        del i;
    dictionary["name"] = name;
    dictionary["xAxis"] = xl;
    dictionary["yAxis"] = yl;
    return dictionary;

# conclusion of data.

def getConclusion(r,s,c,p):
    conclusion = {};
    tmpTuple = Element.objects.values_list('name','timesinfo').filter(section_id=s, chapter_id=c, page_id="0");
    chaptername = tmpTuple[0][0].decode('utf-8');
    timeinfo = tmpTuple[0][1];
    del tmpTuple;
    if "day" == timeinfo:
        period = 365;
    elif "month" == timeinfo:
        period = 12;
    elif "season" == timeinfo:
        period = 4;
    else:
        period = 1;
    # current time
    time = Score.objects.values_list('time',flat="True").filter(region_id=r, section_id=s, chapter_id=c, page_id="0", stat="flat").order_by('time')[0].strftime('%Y年%m月');
    # tongbi huanbi
    ch_tongbi = int(Score.objects.values_list('value',flat="True").filter(region_id=r, section_id=s, chapter_id=c, page_id="0", stat="tongbi").order_by('time')[0]);
    ch_huanbi = int(Score.objects.values_list('value',flat="True").filter(region_id=r, section_id=s, chapter_id=c, page_id="0", stat="huanbi").order_by('time')[0]);
    # for c0101
    sentence = "{0}{1}数据显示，{2}环比{3}{4}%，同比{5}{6}%。".decode('utf-8');
    if ch_huanbi<0:
        str3 = "下降"; # decode('utf-8')
    else:
        str3 = "增长"; # decode('utf-8')
    str4 = str(abs(ch_huanbi));
    if ch_tongbi<0:
        str5 = "下降"; # decode('utf-8')
    else:
        str5 = "增长"; # decode('utf-8')
    str6 = str(abs(ch_tongbi));
    conclusion["c0101"] = sentence.format(time,chaptername,chaptername,str3,str4,str5,str6);
    del str3,str4,str5,str6,sentence;
    # for c0201
    conclusion["c0201"] = "根据数据显示，本月各地得分体现出明显的差异。";
    # for c0301
    num = len(p);
    huanbiname = [];
    huanbilist = [];
    tongbiname = [];
    tongbilist = [];
    name0 = Element.objects.values_list('name',flat="True").filter(section_id=s,chapter_id=c,page_id=p[0])[0];
    huanbi0 = int(Score.objects.values_list('value',flat="True").filter(region_id=r, section_id=s, chapter_id=c, page_id=p[0], stat="huanbi").order_by('time')[0]);
    tongbi0 = int(Score.objects.values_list('value',flat="True").filter(region_id=r, section_id=s, chapter_id=c, page_id=p[0], stat="tongbi").order_by('time')[0]);
    huanbiname.append(name0.decode('utf-8'));
    huanbilist.append(huanbi0);
    tongbiname.append(name0.decode('utf-8'));
    tongbilist.append(tongbi0);
    del name0,huanbi0,tongbi0;
    for i in range(1,num):
        name = Element.objects.values_list('name',flat="True").filter(section_id=s,chapter_id=c,page_id=p[i])[0];
        huanbi = int(Score.objects.values_list('value',flat="True").filter(region_id=r, section_id=s, chapter_id=c, page_id=p[i], stat="huanbi").order_by('time')[0]);
        tongbi = int(Score.objects.values_list('value',flat="True").filter(region_id=r, section_id=s, chapter_id=c, page_id=p[i], stat="tongbi").order_by('time')[0]);
        # sorted huanbi list and tongbi list
        # at the next version i will use other insert method which is more efficient.
        if huanbi <= huanbilist[0]:
            huanbiname.insert(0,name.decode('utf-8'));
            huanbilist.insert(0,huanbi);
        elif huanbi >= huanbilist[-1]:
            huanbiname.append(name.decode('utf-8'));
            huanbilist.append(huanbi);
        else: 
            for j in range(1,len(huanbilist)):
                if ((huanbi >= huanbilist[j-1]) and (huanbi <= huanbilist[j])):
                    huanbiname.insert(j,name.decode('utf-8'));
                    huanbilist.insert(j,huanbi);
                    break;
            # I accidently find it that if I don't delete i, Index may Out Of Range.
            if "j" in locals():
                del j;
        if tongbi <= tongbilist[0]:
            tongbiname.insert(0,name.decode('utf-8'));
            tongbilist.insert(0,tongbi);
        elif tongbi >= tongbilist[-1]:
            tongbiname.append(name.decode('utf-8'));
            tongbilist.append(tongbi);
        else: 
            for j in range(1,len(tongbilist)):
                if ((tongbi >= tongbilist[j-1]) and (tongbi <= tongbilist[j])):
                    tongbiname.insert(j,name.decode('utf-8'));
                    tongbilist.insert(j,tongbi);
                    break;
            # I accidently find it that if I don't delete i, Index may Out Of Range.
            if "j" in locals():
                del j;
        del name,huanbi,tongbi;
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "i" in locals():
        del i;
    if ch_huanbi<0:
        str2 = "下降"; # decode('utf-8')
    else:
        str2 = "增长"; # decode('utf-8')
    str3 = str(ch_huanbi);
    tmpnamelist = [];
    tmpvaluelist = [];
    tmpvaluestrlist = [];
    if ch_huanbi<0:
        for i in range(len(huanbilist)):
            if huanbilist[i]<0:
                tmpnamelist.append(huanbiname[i]);
                tmpvaluelist.append(abs(huanbilist[i]));
                tmpvaluestrlist.append(str(abs(huanbilist[i])));
        # I accidently find it that if I don't delete i, Index may Out Of Range.
        if "i" in locals():
            del i;
    else:
        for i in range(len(huanbilist)):
            if huanbilist[i]>=0:
                tmpnamelist.append(huanbiname[i]);
                tmpvaluelist.append(abs(huanbilist[i]));
                tmpvaluestrlist.append(str(abs(huanbilist[i])));
        # I accidently find it that if I don't delete i, Index may Out Of Range.
        if "i" in locals():
            del i;
    if len(tmpnamelist)<1:
        str4 = huanbiname[0];
        tmp = [];
        for i in huanbilist:
            tmp.append(str(i));
        # I accidently find it that if I don't delete i, Index may Out Of Range.
        if "i" in locals():
            del i;
        str5 = "、".join(huanbiname);
        del tmp;
        str6 = str2;
        str7 = "、".join(tmp);
        str10 = "100";
    else:
        str4 = "、".join(tmpnamelist);
        str5 = "、".join(tmpnamelist);
        str6 = str2;
        str7 = "、".join(tmpvaluestrlist);
        summ = 0;
        for i in huanbilist:
            summ = summ + abs(i);
        # I accidently find it that if I don't delete i, Index may Out Of Range.
        if "i" in locals():
            del i;
        str10 = str(sum(tmpvaluelist)/summ*100);
        del summ;
    del tmpnamelist,tmpvaluelist;
    str9 = str2;
    if ch_tongbi<0:
        str12 = "下降"; # decode('utf-8')
        str13 = "降幅"; # decode('utf-8')
    else:
        str12 = "增长"; # decode('utf-8')
        str13 = "涨幅"; # decode('utf-8')
    str15 = "、".join(tongbiname);
    tmp = [];
    for i in tongbilist:
        tmp.append(str(i));
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "i" in locals():
        del i;
    str16 = "、".join(tmp);
    del tmp;
    del tongbilist,tongbiname,huanbilist,huanbiname;
    sentence = "从环比看，{0}{1}环比{2}{3}%，主要是受{4}的影响。{5}环比分别{6}{7}个百分点，合计影响{8}环比{9}约{10}个百分点。从同比看，总的来讲{11}同比呈现{12}态势，部分分类{13}较高。{14}{15}同比分别上涨{16}个百分点。";
    conclusion["c0301"] = sentence.format(time,chaptername,str2,str3,str4,str5,str6,str7,chaptername,str9,str10,chaptername,str12,str13,time,str15,str16);
    del sentence,ch_tongbi,ch_huanbi,time,chaptername,str2,str3,str4,str5,str6,str7,str9,str10,str12,str13,str15,str16;
    return conclusion;

def getTable(region,s,c,p):
    table = {};
    region_UP = Region.objects.values_list('parent_id',flat="True").filter(region_id=region)[0];
    # I trust that every data i need is here.
    # for c0101
    # get recent 12 tips. at this version i will consider using "reverse" instead of get the whole table out!
    timelist = Score.objects.values_list('time',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id="0", stat="flat").order_by('time')[0:12].reverse();
    datalist = Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id="0", stat="flat").order_by('time')[0:12].reverse();
    tongbilist = Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id="0", stat="tongbi").order_by('time')[0:12].reverse();
    huanbilist = Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id="0", stat="huanbi").order_by('time')[0:12].reverse();
    hisbestlist = Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id="0", stat="max").order_by('time')[0:12].reverse();
    regmeanlist = Score.objects.values_list('value',flat="True").filter(region_id=region_UP, section_id=s, chapter_id=c, page_id="0", stat="mean").order_by('time')[0:12].reverse();
    regbestlist = Score.objects.values_list('value',flat="True").filter(region_id=region_UP, section_id=s, chapter_id=c, page_id="0", stat="max").order_by('time')[0:12].reverse();
    tmpDict = [];
    for i in range(12):
        tmp = []; # every line
        tmp.append(timelist[i].strftime("%Y年%m月%d日"));
        tmp.append(datalist[i]);
        tmp.append(tongbilist[i]);
        tmp.append(huanbilist[i]);
        tmp.append(hisbestlist[i]);
        tmp.append(regmeanlist[i]);
        tmp.append(regbestlist[i]);
        tmpDict.append(tmp);
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "i" in locals():
        del i;
    table["c0101"] = tmpDict;
    del tmpDict,tmp;
    # for c0201
    # get sub regions
    sub_regions = Region.objects.values_list('region_id',flat='True').filter(parent_id=region);
    tmpDict = [];
    for reg in sub_regions:
        tmp = [];
        # name
        tmp.append(Region.objects.values_list('name',flat='True').filter(region_id=reg)[0]);
        # data
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=reg, section_id=s, chapter_id=c, page_id="0", stat="flat").order_by('time')[0]));
        # tongbi
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=reg, section_id=s, chapter_id=c, page_id="0", stat="tongbi").order_by('time')[0]));
        # huanbi
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=reg, section_id=s, chapter_id=c, page_id="0", stat="huanbi").order_by('time')[0]));
        # historical best
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=reg, section_id=s, chapter_id=c, page_id="0", stat="max").order_by('time')[0]));
        # region mean
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id="0", stat="mean").order_by('time')[0]));
        # region best
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id="0", stat="max").order_by('time')[0]));
        tmpDict.append(tmp);
    # I accidently find it that if I don't delete i, Index may Out Of Range.
    if "reg" in locals():
        del reg;
    table["c0201"] = tmpDict;
    del tmp,tmpDict;
    # for c0301
    # get sub elements
    tmpDict = [];
    for page in p:
        tmp = [];
        # name
        tmp.append(Element.objects.values_list('name',flat="True").filter(section_id=s, chapter_id=c, page_id=page)[0]);
        # data
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id=page, stat="flat").order_by('time')[0]));
        # tongbi
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id=page, stat="tongbi").order_by('time')[0]));
        # huanbi
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id=page, stat="huanbi").order_by('time')[0]));
        # historical best
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region, section_id=s, chapter_id=c, page_id=page, stat="max").order_by('time')[0]));
        # region mean
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region_UP, section_id=s, chapter_id=c, page_id=page, stat="mean").order_by('time')[0]));
        # region best
        tmp.append(int(Score.objects.values_list('value',flat="True").filter(region_id=region_UP, section_id=s, chapter_id=c, page_id=page, stat="max").order_by('time')[0]));
        tmpDict.append(tmp);
    # del page;
    table["c0301"] = tmpDict;
    del tmp,tmpDict;
    return table;
