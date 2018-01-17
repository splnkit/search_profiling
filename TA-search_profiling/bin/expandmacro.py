import json
from urllib import urlencode
from splunk import entity
import splunk.Intersplunk as si

SEARCH_PARSER_PATH = 'search'

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
        owner      = "admin"
        
        for result in results:
            if result[macro_field] == "0":
                continue
            else:
                search = result.get(search_field,"")
                try:
                    output = entity.getEntity(SEARCH_PARSER_PATH, "parser", owner=owner, namespace=result["app"], sessionKey=sessionKey, q=search, parse_only="t", output_mode="json")
                    c = output.value
                    updated_search = " | ".join([command["command"]+" "+command["rawargs"] for command in json.loads(c).get("commands")])
                    if not updated_search.startswith("search"):
                        updated_search = "| %s" % updated_search
                    result[output_field] = str(updated_search)
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
