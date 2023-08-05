from cnki_html2json import html2json

def test_fulltext():
    with open('tests/fulltext.html','r') as f:
        content = f.read()

def test_fulltext_crawl():
    with open('tests/fulltext_crawl.html','r') as f:
        content = f.read()

    text_structure = html2json.ExtractContent(content).extract('structure')
    assert text_structure['body_text']['1 引言']['text'][:14] == '近年来，以Chat GPT(' # type:ignore
    assert text_structure['body_text']['1 引言']['reference_index'][0]==1 # type:ignore

    text_raw = html2json.ExtractContent(content).extract('raw') # type:ignore
    assert '[1]' in text_raw['body_text']['1 引言']['text'] # type:ignore