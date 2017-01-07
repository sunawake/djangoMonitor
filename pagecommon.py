# coding=UTF-8
# return global variables for every page.
from diagram.models import Element

def sidebar(request):
    # just for select
    sectionAnchors = ["s0","s1","s2","s3","s4","s5","s6","s7","s8","s9"];
    chapterAnchors = ["c0","c1","c2","c3","c4","c5","c6","c7","c8","c9"];
    SIDEBAR = {};
    # new section branch
    tmpSecTuple = Element.objects.filter(chapter_id="0",page_id="0").values_list("section_id","name").order_by("section_id");
    for i in range(len(tmpSecTuple)):
        tmpSecID = int(tmpSecTuple[i][0]); # list indices must be integers, not unicode
        if tmpSecID < 1:
            continue;
        tmpSecName = tmpSecTuple[i][1];
        tmpSecAnchor = sectionAnchors[tmpSecID];
        SIDEBAR[tmpSecAnchor] = {};
        SIDEBAR[tmpSecAnchor]["name"] = tmpSecName;
        SIDEBAR[tmpSecAnchor]["chapter"] = {};
        # new chapter branch
        tmpChaTuple = Element.objects.filter(section_id=tmpSecID, page_id="0").values_list("chapter_id","name").order_by("chapter_id");
        for j in range(len(tmpChaTuple)):
            tmpChaID = int(tmpChaTuple[j][0]); # list indices must be integers, not unicode
            if tmpChaID < 1:
                continue;
            tmpChaName = tmpChaTuple[j][1];
            tmpChaAnchor = chapterAnchors[tmpChaID];
            SIDEBAR[tmpSecAnchor]["chapter"][tmpChaAnchor] = {};
            SIDEBAR[tmpSecAnchor]["chapter"][tmpChaAnchor]["name"] = tmpChaName;
    return {'SIDEBAR':SIDEBAR};
