import re
import splunk.Intersplunk as si


def mvfind(search_indexes, default_indexes):

    filters = [re.sub("\*","[^_].+",i) for i in search_indexes if re.search("\*",i)]
    # print filters
    if len(filters)>0:
        ind = []
        for di in default_indexes:
            for f in filters:
                if re.search("^"+f, di)>0:
                    ind.append(di)
                    break
        return ind
    else:
        return search_indexes

def megafind(search_indexes, data_pairs):
    if "*" in search_indexes and "_*" in search_indexes:
        return data_pairs
    elif "*" in search_indexes:
        pairs = [i for i in data_pairs if re.search("^[^_]",i)]
        for ind in search_indexes:
            if re.search("^_",ind):
                pairs.extend([dp for dp in data_pairs if re.search("^"+ind+"@",dp)])
    elif "_*" in search_indexes:
        pairs = [i for i in data_pairs if re.search("^_",i)]
        for ind in search_indexes:
            if re.search("^[^_]",ind):
                pairs.extend([dp for dp in data_pairs if re.search("^"+ind+"@",dp)])
    else:
        pairs = []
        if isinstance(search_indexes, basestring):
            pairs.extend([dp for dp in data_pairs if re.search("^"+search_indexes+"@",dp)])
        else:
            for ind in search_indexes:
                pairs.extend([dp for dp in data_pairs if re.search("^"+ind+"@",dp)]) 
    return pairs


def mvpairs(search_indexes, data_pairs):

    pairs = []
    if isinstance(search_indexes, basestring):
        filters = [re.sub("\*","[^_].+",search_indexes)]
    else:
        filters = [re.sub("\*","[^_].+",i) for i in search_indexes]
    for d in data_pairs:
        for f in filters:
            if re.search("^"+f+"@", d)>0:
                pairs.append(d)
                break
    return pairs


def mvmagic(indexes, sourcetypes, default_pairs, allowed_pairs):

    if len(indexes) == 0 and len(sourcetypes) == 0:
        return default_pairs.split("\n")
    if not sourcetypes: # len(sourcetypes) == 0:
        # pairs = mvpairs(indexes, allowed_pairs)
        return mvpairs(indexes, allowed_pairs.split("\n"))
    if not indexes:
        pairs = []
        if isinstance(sourcetypes, basestring):
            filters = [re.sub("\*","[^_].+",sourcetypes)]
        else:
            filters = [re.sub("\*","[^_].+",i) for i in sourcetypes]
        for d in default_pairs.split("\n"):
            for f in filters:
                if re.search("@"+f+"$", d)>0:
                    pairs.append(d)
                    break
        return pairs
    else:
        pairs = []
        if isinstance(sourcetypes, basestring):
            sourcetypes = [sourcetypes]
        st_filters = [re.sub("\*",".+",i) for i in sourcetypes]
        if isinstance(indexes, basestring):
            indexes = [indexes]
        index_filters = [re.sub("^\*","[^_].+",i) for i in indexes]
        index_filters = [re.sub("\*",".+",i) for i in index_filters]
        for d in allowed_pairs.split("\n"):
            for ifilter in index_filters:
                if re.search("^"+ifilter+"@", d)>0:
                    for sfilter in st_filters:
                        if re.search("@"+sfilter+"$", d)>0:
                            pairs.append(d)
                            break
        return pairs


# mvfind(search_indexes, default_indexes)

if __name__ == '__main__':
    try:
        keywords, options = si.getKeywordsAndOptions()
        examples    = options.get('pattern_field', None)
        match_list = options.get('list', None)
        output_field = options.get('output_field', None)
        mode = options.get('mode', None)
        index_field = options.get('index_field', None)
        st_field = options.get('st_field', None)
        defaults = options.get('defaults', None)
        allowed = options.get('allowed', None)
        dm = options.get('dm_field')
        if not examples:
            si.generateErrorResults('Requires pattern_field field.')
            exit(0)
        if not match_list and not st_field:
            si.generateErrorResults('Requires list field.')
            exit(0)
        if not output_field:
            output_field = "new_field"
        results, dummyresults, settings = si.getOrganizedResults()

        for result in results:
            if result.get(dm, None):
                continue
            if not mode:
                result[output_field] = mvfind(result[examples], result[match_list])
            elif mode == "x":
                result[output_field] = mvpairs(result[examples], result[match_list])
            elif mode == "y":
                result[output_field] = megafind(result[examples], result[st_field])
            else:
                result[output_field] = mvmagic(result.get(index_field, None), result.get(st_field, None), result[defaults], result[allowed])
        si.outputResults(results)
    except KeyError, e:
        si.generateErrorResults("Events are missing the '%s' field. Check to make sure the lookups are populated." % e)
    except Exception, e:
        import traceback
        stack = traceback.format_exc()
        si.generateErrorResults("Error '%s'. %s" % (e, stack))
