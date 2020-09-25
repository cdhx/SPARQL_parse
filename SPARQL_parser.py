# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 21:42:48 2020

@author: 黄祥
"""
#不标准的情况：
#WHERE,SELECT,ASK没有大写
#代求变量多于实际数量，不写代求变量
#完整链接的生成，应该严格按照前缀，简写形式的生成，才需要字典，确认一下
import re

import json
import socket
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

class RegexDict(dict):
    import re
    def __init__(self, *args, **kwds):
        self.update(*args, **kwds)

    def __getitem__(self, required):
        for key in dict.__iter__(self):
            if self.re.match(key, required):
                return dict.__getitem__(self, key)

#{}前后空格，末尾没有.，变量统一，去前缀，
class SPARQL(object):
    def __init__(self, raw_sparql):        
        self.raw_sparql=raw_sparql
        self.pre_map={
         'prop': '<http://dbpedia.org/property/>',
         'owl': '<http://www.w3.org/2002/07/owl#>',
         'dbp': '<http://dbpedia.org/property/>',
         'dct': '<http://purl.org/dc/terms/>',
         'res': '<http://dbpedia.org/resource/>',
         'dbo': '<http://dbpedia.org/ontology/>',
         'skos': '<http://www.w3.org/2004/02/skos/core#>',
         'db': '<http://dbpedia.org/>',
         'yago': '<http://dbpedia.org/class/yago/>',
         'onto': '<http://dbpedia.org/ontology/>',
         #'xsd': '<http://www.w3.org/2001/XMLSchema#>',#注释掉它，比较特殊,#可能导致了还原出错，另外former中只有两个链接可能出现，泛化没有意义
         'rdfs': '<http://www.w3.org/2000/01/rdf-schema#>',
         'foaf': '<http://xmlns.com/foaf/0.1/>',
         'dbr': '<http://dbpedia.org/resource/>',
         'dbc': '<http://dbpedia.org/resource/Category:>',
         'dbpedia2': '<http://dbpedia.org/property/>'
        }
        
        self.map_pre = RegexDict({
        '<http://dbpedia.org/>':'db',
        '<http://dbpedia.org/class/yago/.*?>':'yago',
        '<http://dbpedia.org/ontology/.*?>':'dbo',
        '<http://dbpedia.org/property/.*?>':'dbp',
        '<http://dbpedia.org/resource/.*?>':'dbr',
        '<http://dbpedia.org/resource/Category:>':'dbc',
        '<http://purl.org/dc/terms/.*?>':'dct',
        '<http://www.w3.org/1999/02/22-rdf-syntax-ns#>':'rdf',
        '<http://www.w3.org/2000/01/rdf-schema#>':'rdfs',
        #'<http://www.w3.org/2001/XMLSchema#>':'xsd',
        '<http://www.w3.org/2002/07/owl#>':'owl',
        '<http://xmlns.com/foaf/0.1/>':'foaf',
        '<http://www.w3.org/2004/02/skos/core#>':'skos'
         })
        self.normalize()
        self.set_sparql()
        self.set_former()
        self.set_abbr_sparql()
        self.set_constrain()
        self.set_former()
        self.set_intent()
        self.set_link()
        self.set_sparql()
        self.set_vars()
        self.set_where()
        self.set_triple_num()
        self.set_host_ip()
        self.set_template()
        self.set_former_template()
        self.set_where_template()
        
        
    def normalize(self):
            
        #去连续空格，前后空格，{}旁边的空格
        self.sparql=' '.join(self.raw_sparql.split())#去连续空格
        self.sparql=self.sparql.replace('. }','}')#去掉最后一句的句号
        self.sparql=self.sparql.replace(' }','}')#去掉}前的空格        
        self.sparql=self.sparql.replace('{ ','{')#去掉{后的空格        
        self.sparql=' '.join(self.sparql.split())#去连续空格
        self.sparql=self.sparql.strip()#去前后空格
  

    def draw(self):
        from graphviz import Digraph
        dot = Digraph(format='jpg')
    
        dot.attr(label=question[0])
        #SPARQL标准化
        sparql_query=get_simple_query_string(sparql_query)
        where=sparql_query[sparql_query.find('{')+1:sparql_query.find('}')].strip(' ') 
    
        for node in edg['nodes']:
            dot.node('node'+str(node['nodeID']),desc,shape='box')
                
        for edge in edg['edges']:
            dot.edge('node'+str(edge['from']),'node'+str(edge['to']),edgeTypeMap[str(edge['edgeType'])])
    
        filename=edg['qid']
        dot.render(filename,'SPARQL_plot/',format='jpg',cleanup=True)
    def set_sparql(self):
        string=self.sparql
        query_start=0
        #有前缀
        if string.find('PREFIX')!=-1:#有前缀的格式
            pattern_pre=re.compile(r'PREFIX .+?>')
            pre_list=pattern_pre.findall(string) #所有前缀
            #query正文开始（前缀后面） 
            #最后一个前缀
            last_pre=pre_list[[string.find(p) for p in pre_list].index(max([string.find(p) for p in pre_list]))]
            #正文
            query_start=string.find(last_pre)+len(last_pre)+1                
            
            #简写对照表for pre in self.pre_map.keys():
            #dbo:content content_index是：后面一个位置
            for pre in self.pre_map.keys():
                while string.find(pre+':',query_start)!=-1:
                    content_index=string.find(pre+':',query_start)+len(pre)+1 
                    #dbo:content content 就是content
                    content=string[content_index:string.find(' ',max(query_start,content_index))]
                    #前缀形式的部分         
                    pre_format=string[content_index-len(pre)-1:string.find(' ',content_index)]
                    #完整格式
                    new_format=self.pre_map[pre][:-1]+content+'>'
                    #替换
                    string=string.replace(pre_format,new_format)                
        self.sparql=string[query_start:]      
    
    def set_intent(self):
        if 'ASK' in self.former:self.intent='ASK'
        elif 'COUNT' in self.former:self.intent='COUNT'
        else: self.intent='SELECT'
        
    def set_where(self):
        self.where=self.sparql[self.sparql.find('WHERE'):].strip()
    def set_triple_num(self):
        self.triple_num=len(self.where.split('.'))
    def set_constrain(self):#不完善，可能在WHERE里面
        self.constrain=self.sparql[self.sparql.find('}')+1:]
    def set_former(self):
        self.former=self.sparql[:self.sparql.find('WHERE')].strip()
    def set_link(self):
        pattern=re.compile('<.+?>')
        result=re.findall(pattern,self.sparql)
        if 'xsd:data' in self.sparql:
            result.append('xsd:data')
        if 'a' in self.sparql or 'ref:type' in self.sparql:
            result.append('rdf:type')
        self.link=result
    def set_template(self):
        self.template=re.sub('<.+?>','<E/R>',self.sparql)
    def set_former_template(self):
        self.former_template=self.template[:self.template.find('WHERE')].strip()
    def set_where_template(self):
        self.where_template=self.template[self.template.find('WHERE'):].strip()
    def set_abbr_sparql(self):
        string=self.sparql
        if string.find('PREFIX')!=-1:#有前缀的格式,只留正文
            pattern_pre=re.compile(r'PREFIX .+?>')
            pre_list=pattern_pre.findall(string) #所有前缀
            #最后一个prefix
            last_pre=pre_list[[string.find(p) for p in pre_list].index(max([string.find(p) for p in pre_list]))]
            query_start=string.find(last_pre)+len(last_pre)+1  #正文开始的     索引
            string=string[query_start:]   #取query正文
            
        #有些有前缀和没有前缀混合的，还有只有有前缀形式的，把有前缀的转换掉
        pattern=re.compile(r'<.+?>')
        full_format=pattern.findall(string)#所有完整的uri
        for x in full_format:
            content=x[max(x.rfind('/'),x.rfind('#'))+1:-1]#获取内容
            full_uri=x
            pre_uri=self.map_pre[x[:max(x.rfind('/'),x.rfind('#'))+1]+'>']+':'+content
            string=string.replace(full_uri,pre_uri)           
            
        #检查不标准的缩写 onto,res
        for pre in self.pre_map.keys():
            if pre not in self.map_pre.values():#不标准，如果标准的也处理会陷入死循环
                while string.find(pre+':')!=-1:#有这种缩写
                    abr_start=string.find(pre+':')
                    abr_stop=abr_start+len(pre)
                    ill_form=string[abr_start:abr_stop]#现在的格式#
                    standard_form=self.map_pre[self.pre_map[ill_form]]
                    #替换
                    string=string.replace(ill_form,standard_form)         
        self.abbr_sparql=string

    def set_vars(self):        
        all_var=[]
        def find_variable(substr):
            end_index=999
            if substr.find(' ')!=-1:
                end_index=min(end_index,substr.find(' '))
            if substr.find(')')!=-1:
                end_index=min(end_index,substr.find(')'))
            if substr.find('}')!=-1:
                end_index=min(end_index,substr.find('}'))
            if substr.find(';')!=-1:
                end_index=min(end_index,substr.find(';'))
            if substr.find(',')!=-1:
                end_index=min(end_index,substr.find(','))
            if substr.find('.')!=-1:
                end_index=min(end_index,substr.find('.'))
            return end_index
        end_index=0
        start_inde=0
        sparql_query=self.sparql
        while sparql_query.find('?',end_index)!=-1:
            start_index=sparql_query.find('?',end_index)
            end_index=find_variable(sparql_query[start_index:])
            all_var.append(sparql_query[start_index:end_index+start_index])
            end_index+=start_index
        
        self.firstVar=all_var[0]
        self.all_var=list(set(all_var))
    def set_host_ip(self):
        """查询本机ip地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        self.ip_address=ip
    def query8890(self):
        sparql = SPARQLWrapper('http://'+self.ip_address+':8890/sparql')
        #sparql = SPARQLWrapper('http://192.168.43.129:8890/sparql')
        sparql.setQuery(self.raw_sparql)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()#json,type为dict
        self.answer=self.answer_convert(results)
        return self.answer
    def answer_convert(self,item_answer):
        if 'boolean' in item_answer.keys():
            at='boolean'
        else:
            at= item_answer['head']['vars'][0]
        answer=[]
        if at=='boolean':
            answer.append(item_answer['boolean'])        
        else:
            for cand in item_answer['results']['bindings']:
                if at=='date':
                    answer.append(cand['date']['value'])
                elif at=='number':
                    answer.append(cand['c']['value'])                
                elif at=='resource' or at=='uri':
                    answer.append(cand['uri']['value'])
                elif at=='string':
                    answer.append(cand['string']['value'])
                elif at=='callret-0':
                    answer.append(cand['callret-0']['value'])
                else:#貌似都是这个套路，不知道还有什么类型
                    answer.append(cand[at]['value'])
        return answer