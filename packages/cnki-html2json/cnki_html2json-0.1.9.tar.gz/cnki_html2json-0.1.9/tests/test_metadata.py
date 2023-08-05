from cnki_html2json import parse_metadata

def test_metadata():
    with open('tests/metadata.html','r') as f:
        content = f.read()
    result = parse_metadata.Parse(content).extract_metadata()

    assert result['metadata']['title'] == "ChatGPT对文献情报工作的影响"
    