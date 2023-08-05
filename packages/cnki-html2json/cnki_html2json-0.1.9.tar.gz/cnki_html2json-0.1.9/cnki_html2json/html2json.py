# -*- coding: utf-8 -*-
import re
import json
import os
from lxml import html

class ExtractContent:

    def __init__(self,html_str:str) -> None:
        self.html_str = html_str
        self.error = False

    def _process_html(self):
        """处理原始html"""
        html_str = re.sub(r'<script.*?>.*?</script>','',self.html_str,flags=re.S)
        html_str = re.sub(r'<style.*?>.*?</style>','',html_str,flags=re.S)

        # remove image
        html_str = re.sub(r'<div class="area_img".*?</div>','',html_str,flags=re.S)
        try:
            html_tree = html.fromstring(self.html_str)
        except:
            self.error = True
        else:
            start_node = html_tree.xpath('//div[@class="main"]')[0]
            body_str = html.tostring(start_node,encoding='unicode').strip()
            self.body_tree = html.fromstring(body_str)

    def _extract_node(self):
        level1_chapters = self.body_tree.xpath('//dd[@class="guide" or @class="guide noico"]/p/a/text()')
        level1_chapters_href = self.body_tree.xpath('//dd[@class="guide" or @class="guide noico"]/p/a/@href')
        level1_chapters_href = [i for i in level1_chapters_href if i != '#']
        
        try:
            del level1_chapters[level1_chapters_href.index('#a_bibliography')]
        
        # 如果没有参考文献字段，不再进行解析
        except ValueError:
            self.error = True
        
        else:
            level1_chapters_href.remove('#a_bibliography')
            level1_chapters_id = []
            for href in level1_chapters_href:
                try:
                    level1_chapters_id.append(int(href.replace('#','')))
                except ValueError:
                    del level1_chapters[level1_chapters_href.index(href)]
                    level1_chapters_href.remove(href)

            level1_id_chapter_dict = dict(zip(level1_chapters_id,level1_chapters))
       
            # level2_chapters = self.body_tree.xpath('//ul[@class="contentbox"]/li/a/text()')
            level2_chapters = self.body_tree.xpath('//p/a[@href != "#"]/../following-sibling::ul[@class="contentbox"]/li/a/text()')
            level2_chapters_href = self.body_tree.xpath('//ul[@class="contentbox"]/li/a/@href')
            level2_chapters_href = [i for i in level2_chapters_href if i != '#']
            level2_chapters_id = [int(href.replace('#','')) for href in level2_chapters_href]
            level2_id_chapter_dict = level2_id_chapter_dict = dict(zip(level2_chapters_id,level2_chapters))

            self.id_chapter_dict = level1_id_chapter_dict|level2_id_chapter_dict

            # 一二级章节id映射
            level1_map_level2 = {}
            for href in level1_chapters_href:
                level2_href_list = self.body_tree.xpath(f'//p/a[@href="{href}"]/../following-sibling::ul[@class="contentbox"]/li/a/@href')
                level2_href_list = [i for i in level2_href_list if i != '#']
                level2_id_list = [int(href.replace('#','')) for href in level2_href_list]
                level1_map_level2[int(href.replace('#',''))] = level2_id_list
            self.level1_map_level2 = level1_map_level2
            # print('level1_map_level2',self.level1_map_level2)
            
            # 章节节点包含的内容节点
            node_id_list = sorted(self.id_chapter_dict.keys())
            last_content_node_id = int(self.body_tree.xpath('//div[@class="p1"][last()]/p/@id')[0])

            node_content_id_list = []
            for idx,node_id in enumerate(node_id_list[:-1]):
                node_content_id_list.append(list(range(node_id+1,node_id_list[idx+1])))
            node_content_id_list.append(list(range(node_id_list[-1]+1,last_content_node_id+1)))
            self.node_id_dict = dict(zip(node_id_list,node_content_id_list))

    def _obtain_node_content(self,node_list:list,raw_mode=False)->tuple:
        """获取节点包含的内容"""
        
        # 获取节点所在段落的文本
        # text_xpath_expression = '//p[' + ' or '.join([f'@id="{id}"' for id in node_list]) + ']/text()'
        # text_xpath_content = self.body_tree.xpath(text_xpath_expression)
        # text_xpath_content = ''.join(text_xpath_content).strip()
        
        text_content = ''
        for id in node_list:
            try:
                node = self.body_tree.xpath(f'//p[@id="{id}"]')[0]
            except IndexError:
                pass
            else:
                node_str = str(html.tostring(node,encoding='unicode'))
                node_content_list = [i for i in re.findall(r'>(.*?)<', node_str) if i != '']

                # 将正文中包含的[]转换为(),防止参考文献索引识别错误
                node_content_list = [re.sub(r'\[(\d+(,\s*\d+)*)\]',r'(\1)',node) for node in node_content_list]
                text_content += ''.join(node_content_list).strip()+'\n'

        # 获取参考文献索引  
        nested_ref_index = [eval(i) for i in re.findall(r'\[[\d,]+\]',text_content)]
        flat_ref_index = sorted(set([j for i in nested_ref_index for j in i]))

        # 获取节点所在段落的参考文献索引
        # ref_index_xpath_expression = '//p[' + ' or '.join([f'@id="{id}"' for id in node_list]) + ']/citation//a[@class="sup"]/text()'
        # ref_index_xpath_content = self.body_tree.xpath(ref_index_xpath_expression)
        # ref_index_xpath_content = [int(i) for i in ref_index_xpath_content]

        if not raw_mode:
            text_content = re.sub(r'\[[\d,]+\]','',text_content)
            text_content = re.sub(r'\n','',text_content)
        return flat_ref_index,text_content
    
    def _extract_structure_content(self,raw_mode=False)->dict:
        """提取结构化内容"""
        body_text = {}
        other = {}
        for level1_id,level2_id_list in self.level1_map_level2.items():
            level1_chapter = self.id_chapter_dict[level1_id]
            
            # 如果不存在二级标题
            if not level2_id_list:
                if re.match(r'作者贡献声明|利益冲突声明|注释',level1_chapter):
                    other[level1_chapter] = self._obtain_node_content(self.node_id_dict[level1_id])[1]
                else:
                    body_text[level1_chapter] = dict(zip(['reference_index','text'],self._obtain_node_content(self.node_id_dict[level1_id],raw_mode)))
            else:
                body_text[level1_chapter] = {}
                if self.node_id_dict[level1_id]:
                    untitled_chapter = dict(zip(['reference_index','text'],self._obtain_node_content(self.node_id_dict[level1_id],raw_mode)))
                    body_text[level1_chapter]['untitled'] = untitled_chapter
                
                for level2_id in level2_id_list:
                    level2_chapter = self.id_chapter_dict[level2_id]
                    level2_id_content = dict(zip(['reference_index','text'],self._obtain_node_content(self.node_id_dict[level2_id],raw_mode)))
                    body_text[level1_chapter][level2_chapter]=level2_id_content
        
        return {'body_text':body_text,'other':other}

    def _extract_plain_content(self)->dict:
        """提取纯文本内容"""
        body_text = ''
        other = {}
        for node_id,map_id_list in self.node_id_dict.items():
            node_name = self.id_chapter_dict[node_id]
            if re.match(r'作者贡献声明|利益冲突声明|注释',node_name):
                other[node_name] = self._obtain_node_content(self.node_id_dict[node_id])[1]
            else:
                body_text += self._obtain_node_content(map_id_list)[1]
        return {'body_text':body_text,'other':other}
    
    def _extract_reference(self):
        """提取参考文献"""
        reference = [doc.strip() for doc in self.body_tree.xpath('//div[@id="a_bibliography"]/p/a/text()') if doc.strip()!='']
        reference = [f'[{idx}] '+re.sub(r'^[\.]+','',doc).strip() for idx,doc in enumerate(reference,1)]
        self.reference = reference

    @staticmethod
    def _export_json(text,json_path):
        """导出json文件"""
        folder_path = os.path.dirname(json_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(json_path,'w',encoding='utf-8') as f:
            json.dump(text,f,ensure_ascii=False,indent=4)

    def extract(self,mode:str='raw',export_path=None):
        """
        将论文的html字符串转换为字典\n
        mode: 模式，structure|plain|raw，默认为raw\n
        export_path: 导出json文件的路径，默认为None，如果导出json文件，该参数必须指定
        """
        
        self._process_html()
        if self.error:
            return {'body_text':None,'other':None}
        self._extract_node()
        if self.error:
            return {'body_text':None,'other':None}
        self._extract_reference()

        if mode == 'structure':
            body_content = self._extract_structure_content()
        elif mode == 'plain':
            body_content = self._extract_plain_content()
        elif mode == 'raw':
            body_content = self._extract_structure_content(raw_mode=True)
        else:
            raise ValueError('mode参数只能为structure|plain|raw')

        body_content['other']['参考文献'] = self.reference
        if not export_path:
            return body_content
        else:
           self._export_json(body_content,export_path)