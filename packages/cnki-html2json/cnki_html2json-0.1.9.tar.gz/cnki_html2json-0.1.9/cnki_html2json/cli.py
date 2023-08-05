import argparse
from cnki_html2json.crawl import start_crawl

def main():
    parser = argparse.ArgumentParser(description='CNKI crawler. Convert the html format of papers to json format.')
    parser.add_argument('-s','--start_paper_index',type=int,default=1,help='start index, default is 1')
    parser.add_argument('-e','--end_paper_index',type=int,default=None,help='end index, default is None, which means download to the end')
    parser.add_argument('-m','--mode',type=str,default='raw',choices=['raw','structure','plain'])
    parser.add_argument('-b','--browser_type',type=str,default='Chrome',choices=['Chrome','Edge','Firefox'])
    parser.add_argument('-save','--save_path',type=str,default='dataset',help='save path, default is <dataset> folder in the current directory')
    parser.add_argument('-wait','--wait_time',type=int,default=120,help='waiting time for search, default is 120 seconds')
    parser.add_argument('-l','--log',action='store_true',help="whether to save log, specify this parameter to save log, no need to pass value")
    args = parser.parse_args()
    start_crawl(start_paper_index = args.start_paper_index,
                end_paper_index = args.end_paper_index,
                mode = args.mode,
                save_path = args.save_path,
                log = args.log,
                wait_time = args.wait_time,
                browser_type = args.browser_type,
                )