import json
from urllib import urlencode
from splunk.rest import simpleRequest
import splunk.Intersplunk as si

# mvfind(search_indexes, default_indexes)

if __name__ == '__main__':
    try:
        keywords,options = si.getKeywordsAndOptions()
        macro_field      = options.get('macro_field', None)
        search_field     = options.get('search_field', None)
        output_field     = options.get('output_field', "new_field")

        if not macro_field:
            si.generateErrorResults('Requires macro_field field.')
            exit(0)
        if not search_field:
            si.generateErrorResults('Requires search_field field.')
            exit(0)
        results,dummyresults,settings = si.getOrganizedResults()

        sessionKey = settings.get("sessionKey", None)
        owner      = settings.get("owner", None)
        namespace  = settings.get("namespace", None)
        
        for result in results:
            if result[macro_field] == "0":
                continue
            else:
                search = result.get(search_field,"Frooty Tooty")
                args = {'output_mode': 'json',
                        'parse_only': 't',
                        'q': search}
                # si.generateErrorResults("Error '%s'. %s" % (search, search_field))
                try:
                    r, c = simpleRequest('/search/parser', getargs=args, sessionKey=settings["sessionKey"], raiseAllErrors=True)
#                    si.generateErrorResults("Error '%r'. %s" % (c, r))
                    updated_search = json.loads(c).get("normalizedSearch")
                    result[output_field] = updated_search
                except Exception, e:
                    import traceback
                    stack =  traceback.format_exc()
                    # si.generateErrorResults("Error '%s'. %s" % (e, stack))
                    result[output_field] = search
        si.outputResults(results)
    except Exception, e:
        import traceback
        stack =  traceback.format_exc()
        si.generateErrorResults("Error '%s'. %s" % (e, stack))
