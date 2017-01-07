from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import json
import pagedata

def analyse(request):
    return HttpResponseRedirect("/monitor/analyse/s1c1");

def diagram(request, s, c):
    # uid = pagedata.getUID(request.GET("username"), request.GET("password"));
    uid = pagedata.getUID();
    # veriy inputs
    if "region" in request.GET:
        region = request.GET['region'];
    else:
        region = "101010100";
    [region,REGION,s,c,p] = pagedata.verify(region,s,c,uid);
    [cn,cvs] = pagedata.getPageContent(region,REGION,s,c);
    con = pagedata.getConclusion(region,s,c,p);
    tbv = pagedata.getTable(region,s,c,p);
    return render(request, "analyse.html", {"region":region, "REGION":REGION, "section":s, "chapter":c, "uid":uid, "cn":cn, "cvs":cvs, "con":con, "tbv":tbv}, context_instance=RequestContext(request));

def webapi(request):
    # http://national.me:8080/monitor/analyse/webapi?region=101010100&section=1&chapter=1&uid=2014110298&type=timeline&stat=flat&length=10
    request.encoding='utf-8';
    # initialize inputs
    region = "1010000000000";
    section = "1";
    chapter = "1";
    uid = "0000000000";
    type = "timeline";
    stat = "flat";
    length = 0;
    if "region" in request.GET:
        region = request.GET["region"];
    if "section" in request.GET:
        section = request.GET["section"];
    if "chapter" in request.GET:
        chapter = request.GET["chapter"];
    if  "uid" in request.GET:
        uid = request.GET["uid"];
    if "type" in request.GET:
        type = request.GET["type"];
    if "stat" in request.GET:
        stat = request.GET["stat"];
    if "length" in request.GET:
        length = request.GET["length"];
    # do some verification
    [region,region_UP,section,chapter,page] = pagedata.verify(region,section,chapter,uid);
    if stat not in ["flat","mean","max","min","tongbi","huanbi"]:
        stat = "flat";
    # final result initialization
    dictionary = {};
    # let's rock!
    if "timeline" == type:
        dictionary = pagedata.getTimeLine(region,section,chapter,stat,length);
    elif "subregion" == type:
        dictionary = pagedata.getSubRegion(region,section,chapter,stat,length);
    elif "subelement" == type:
        dictionary = pagedata.getSubElement(region,section,chapter,page,stat,length);
    else:
        dictionary["url"] = "http://www.bupt.edu.cn/";
    return HttpResponse(json.dumps(dictionary), content_type='application/json');
