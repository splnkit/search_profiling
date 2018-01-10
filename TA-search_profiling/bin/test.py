import re

si = "_audit"
prs = ["_audit@audittrail","main@access_combined","main@linux_secure"]

def mvpairs(search_indexes, data_pairs):

    pairs = []
    if isinstance(search_indexes, basestring):
        filters = [re.sub("\*","[^_].+",search_indexes)]
    else:
        filters = [re.sub("\*","[^_].+",i) for i in search_indexes]
    print filters
    for d in data_pairs:
        for f in filters:
            if re.search("^"+f+"@", d)>0:
                pairs.append(d)
                break
    return pairs

print mvpairs(si, prs)