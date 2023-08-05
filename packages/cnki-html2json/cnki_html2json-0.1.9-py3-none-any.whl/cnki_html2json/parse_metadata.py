from lxml import html
import re

class Parse:
    
    def __init__(self,detail_html:str):
        """
        解析论文详情页的元数据
        detail_html:论文详情页html
        """
        self.content = detail_html
        self.tree = html.fromstring(self.content)

    def _parse(self,xpath_expression:str):

        parse_result = [i.strip() for i in self.tree.xpath(xpath_expression) if i.strip()!='']
        parse_result_length = len(parse_result)
    
        if parse_result_length == 0:
            return None
        elif parse_result_length == 1:
            return parse_result[0]
        else:
            return parse_result

    def extract_metadata(self)->dict:
        """提取论文元数据"""
        metadata = {}
        metadata['title'] = self._parse('//h1/text()')
        metadata['authors'] = self._parse('//h3[@id="authorpart"]/span/a/text()')
        
        orgs = []
        orgs_xpath_list = ['//h3/a[@class="author"]/text()','//h3[@id="authorpart"]/following-sibling::h3[1]/span[1]/a[@class="author"]/text()','//h3[@id="authorpart"]/following-sibling::h3[1]/span/text()']
        for org_xpath in orgs_xpath_list:
            orgs = self._parse(org_xpath)
            if orgs:
                break
        metadata['orgs'] = orgs
        
        try:
            funds = re.sub(r'\s','',self._parse('//p[@class="funds"]//text()')) # type: ignore
        except:
            funds = self._parse('//p[@class="funds"]//text()')
        
        metadata['abstract'] = self._parse('//span[@id="ChDivSummary"]/text()')
        metadata['keywords'] = self._parse('//p[@class="keywords"]/a[@name="keyword"]/text()')
        metadata['funds'] = funds
        metadata['class_num'] = self._parse('//span[text()="分类号："]/following-sibling::p[1]/text()')
        metadata['source'] = self._parse('//div[@class="top-tip"]/span[1]/a[1][contains(@href,"journal")]/text()')
        metadata['issue'] = self._parse('//div[@class="top-tip"]/span[1]/a[2][contains(@href,"journal")]/text()')
        
        return {'metadata':metadata}