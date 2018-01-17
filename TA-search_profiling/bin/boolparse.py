import re

import splunk.Intersplunk as si

key_fields= ["index","sourcetype"]
bool_strings = ["AND","NOT","OR"]
bool_ops = [")","("]
bool_operations = ["AND","NOT","OR",")","("]


def wr(tokens):
    conditions = []
    for token in tokens:
        conditions.append(wildcard_replace(token))
    return conditions

def wildcard_replace(token):
    if token[0]=="*":
        token = re.sub("\*","[^_].+",token)
    else:
        token = re.sub("\*",".+", token)
    return token

def adjust_tokens(tokens):
    conditions = []
    i=0
    max=len(tokens)
    while i < max:
        if i+1<max and tokens[i+1]=="=":
            if tokens[i] in key_fields: 
                conditions.append(tokens[i])
                conditions.append(tokens[i+1])
                conditions.append(tokens[i+2])
                try:
                    if not tokens[i+3] in bool_operations:
                        conditions.append("AND")
                except:
                    pass
            i +=3
        elif tokens[i] in bool_operations:
            try:
                if tokens[i] == "(" and not conditions[-1] in bool_operations:

                    conditions.append("AND")
            except:
                pass
            conditions.append(tokens[i])
            try:
                if tokens[i] == ")" and not tokens[i+1] in bool_operations[0:3]:
                    conditions.append("AND")
            except:
                pass
            i+=1
        else:
            i+=1
    return conditions

def eliminate_tokens(tokens):
    conditions = []
    i=0
    max=len(tokens)
    while i < max:
        # print tokens[i]
        if i+1==max and tokens[i] in bool_strings:
            pass
        elif tokens[i] in bool_strings and tokens[i+1] in bool_strings:
            pass
        elif tokens[i] in bool_strings and tokens[i+1]==")":
            pass
        elif tokens[i] in bool_strings and tokens[i+1]=="(":
            if tokens[i+2]==")":
                i+=2
            elif tokens[i+2] in bool_strings:

                g = 2
                while i+g<max and tokens[i+g] in bool_strings:
                    if tokens[i+g+1] in key_fields:
                        g+=1
                        conditions.append(tokens[i])
                        conditions.append(tokens[i+1])
                        i+=g-1
                        break
                    elif tokens[i+g+1]==")":
                        i += g+1
                    else:
                        g+=1
                        
                #i+=2
            else:
                conditions.append(tokens[i])
        else:
            conditions.append(tokens[i])
        i+=1
    return conditions


class TokenType:
    NUM, STR, VAR, GT, GTE, LT, LTE, EQ, NEQ, LP, RP, AND, OR, NOT = range(14)


class TreeNode:
    tokenType = None
    value = None
    left = None
    right = None

    def __init__(self, tokenType):
        self.tokenType = tokenType


class Tokenizer:
    expression = None
    tokens = None
    tokenTypes = None
    i = 0

    def __init__(self, exp):
        self.expression = exp

    def next(self):
        self.i += 1
        return self.tokens[self.i-1]
    
    def peek(self):
        return self.tokens[self.i]

    def peek_ahead(self):
        return self.tokens[self.i+1]
    
    def hasNext(self):
        return self.i < len(self.tokens)

    def nextTokenType(self):
        return self.tokenTypes[self.i]
    
    def nextTokenTypeIsOperator(self):
        t = self.tokenTypes[self.i]
        return t == TokenType.GT or t == TokenType.GTE \
            or t == TokenType.LT or t == TokenType.LTE \
            or t == TokenType.EQ or t == TokenType.NEQ

    def tokenize(self):
        import re
        reg = re.compile(r'(\bAND\b|\bOR\b|\bNOT\b|!=|<=|>=|=|<|>|\(|\)|\s+)')
        self.tokens = reg.split(self.expression)
        self.tokens = [t.strip(" \"") for t in self.tokens if t.strip() != '']
        self.tokens = self.tokens[1:]
        self.tokenTypes = []
        self.tokens = adjust_tokens(self.tokens)
        self.tokens = eliminate_tokens(self.tokens)
        for t in self.tokens:
            if t == 'AND':
                self.tokenTypes.append(TokenType.AND)
            elif t == 'NOT':
                self.tokenTypes.append(TokenType.NOT)
            elif t == 'OR':
                self.tokenTypes.append(TokenType.OR)
            elif t == '(':
                self.tokenTypes.append(TokenType.LP)
            elif t == ')':
                self.tokenTypes.append(TokenType.RP)
            elif t == '<':
                self.tokenTypes.append(TokenType.LT)
            elif t == '<=':
                self.tokenTypes.append(TokenType.LTE)
            elif t == '>':
                self.tokenTypes.append(TokenType.GT)
            elif t == '>=':
                self.tokenTypes.append(TokenType.GTE)
            elif t == '=':
                self.tokenTypes.append(TokenType.EQ)
            elif t == '!=':
                self.tokenTypes.append(TokenType.NEQ)
            else:
                # number of string or variable
                if t[0] == '"' and t[-1] == '"':
                    self.tokenTypes.append(TokenType.STR)
                else:
                    try:
                        number = float(t)
                        self.tokenTypes.append(TokenType.NUM)
                    except:
                        if re.search('^[a-zA-Z_\*\:\-]+$', t):
                            if len(self.tokenTypes)>0 and self.tokenTypes[-1] == TokenType.EQ:
                                self.tokenTypes.append(TokenType.STR)
                            else:
                                self.tokenTypes.append(TokenType.VAR)
                        else:
                            self.tokenTypes.append(None)
        self.tokens = wr(self.tokens)
            
            
class BooleanParser:
    tokenizer = None
    root = None

    def __init__(self, exp):
        self.tokenizer = Tokenizer(exp)
        self.tokenizer.tokenize()
        self.parse()

    def parse(self):
        self.root = self.parseExpression()

    def parseExpression(self):
        andTerm1 = self.parseAndTerm()
        while self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.OR:
            self.tokenizer.next()
            andTermX = self.parseAndTerm()
            andTerm = TreeNode(TokenType.OR)
            andTerm.left = andTerm1
            andTerm.right = andTermX
            andTerm1 = andTerm
        return andTerm1

    def parseAndTerm(self):
        condition1 = self.parseCondition()
        while self.tokenizer.hasNext() and (self.tokenizer.nextTokenType() == TokenType.AND or self.tokenizer.nextTokenType() == TokenType.NOT):
            tt = self.tokenizer.nextTokenType()
            self.tokenizer.next()
            conditionX = self.parseCondition()
            condition = TreeNode(tt)
            condition.left = condition1
            condition.right = conditionX
            condition1 = condition
        return condition1

    def parseCondition(self):
        if self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.LP:
            self.tokenizer.next()
            expression = self.parseExpression()
            if self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.RP:
                self.tokenizer.next()
                return expression
            else:
                raise Exception("Closing ) expected, but got " + self.tokenizer.next())

        terminal1 = self.parseTerminal()
        if self.tokenizer.hasNext() and self.tokenizer.nextTokenTypeIsOperator():
            condition = TreeNode(self.tokenizer.nextTokenType())
            self.tokenizer.next()
            terminal2 = self.parseTerminal()
            condition.left = terminal1
            condition.right = terminal2
            return condition
        else:
            raise Exception('Operator expected, but got ' + self.tokenizer.next())
    
    def parseTerminal(self):
        if self.tokenizer.hasNext():
            tokenType = self.tokenizer.nextTokenType()
            if tokenType == TokenType.NUM:
                n = TreeNode(tokenType)
                n.value = float(self.tokenizer.next())
                return n
            elif tokenType == TokenType.STR or tokenType == TokenType.VAR:
                n = TreeNode(tokenType)
                n.value = self.tokenizer.next()
                return n
            else:
                raise Exception('NUM, STR, or VAR expected, but got ' + self.tokenizer.next())
        
        else:
            raise Exception('NUM, STR, or VAR expected, but got ' + self.tokenizer.next())
    
    def evaluate(self, variable_dict):
        return self.evaluateRecursive(self.root, variable_dict)
    
    def evaluateRecursive(self, treeNode, variable_dict):
        if treeNode.tokenType == TokenType.NUM or treeNode.tokenType == TokenType.STR:
            return treeNode.value
        if treeNode.tokenType == TokenType.VAR:
            return variable_dict.get(treeNode.value)
        
        left = self.evaluateRecursive(treeNode.left, variable_dict)
        right = self.evaluateRecursive(treeNode.right, variable_dict)
        if treeNode.tokenType == TokenType.GT:
            return left > right
        elif treeNode.tokenType == TokenType.GTE:
            return left >= right
        elif treeNode.tokenType == TokenType.LT:
            return left < right
        elif treeNode.tokenType == TokenType.LTE:
            return left <= right
        elif treeNode.tokenType == TokenType.EQ:
#            return left == right
            return bool(re.match(right,left))
        elif treeNode.tokenType == TokenType.NEQ:
            return left != right
        elif treeNode.tokenType == TokenType.AND:
            return left and right
        elif treeNode.tokenType == TokenType.OR:
            return left or right
        elif treeNode.tokenType == TokenType.NOT:
            return left and not right
        else:
            raise Exception('Unexpected type ' + str(treeNode.tokenType))

if __name__ == '__main__':
    try:
        keywords, options = si.getKeywordsAndOptions()
        base_search       = options.get('search_field', None)
        match_list = options.get('list', None)
        output_field = options.get('output_field', None)
        bool_field = options.get('bool_field', None)
        if not base_search:
            si.generateErrorResults('Requires pattern_field field.')
            exit(0)
        if not match_list:
            si.generateErrorResults('Requires list field.')
            exit(0)
        if not output_field:
            output_field = "new_field"
        results,dummyresults,settings = si.getOrganizedResults()

        for result in results:
            if result[bool_field] == "1":
                matching_data = []
                orig_match = result[match_list]
                try:
                    parsed_search = BooleanParser(result[base_search])
                    if isinstance(result[match_list], list):
                        idx_st_list = (pair for pair in result[match_list])
                    else:
                        idx_st_list = [result[match_list],]
                    for idx_st_pair in idx_st_list:
                        idx, sourcetype = idx_st_pair.split("@")
                        if parsed_search.evaluate({"index": idx, "sourcetype": sourcetype}):
                            matching_data.append(idx_st_pair)
                    result[output_field] = matching_data
                except Exception, e:
                    # import traceback
                    # stack =  traceback.format_exc()
                    # si.generateErrorResults("Error '%s'. %s %s" % (e, stack, result[base_search]))
                    # si.outputResults(results)
                    result[output_field] = result[match_list]
        si.outputResults(results)
    except Exception, e:
        import traceback
        stack =  traceback.format_exc()
        si.generateErrorResults("Error '%s'. %s" % (e, stack))
