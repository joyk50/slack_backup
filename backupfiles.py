import os
import fnmatch
import json
import wget
from tqdm.auto import tqdm
import traceback

includes = ['*.json']

def getMessages(subdir='.', includes=includes):
    msg_list = []
    files = os.listdir(subdir)
    for pat in includes:
        for f in fnmatch.filter(files, pat):
            json_file = os.path.join(subdir, f)
            msg_list.append(json_file)
    return msg_list

def extractUrls(msg_list, debug=False):
    urls = dict()
    cnt = 1
    for msg in msg_list:
        with open(msg, 'r') as f:
            contents = json.load(f)
        # print(msg, type(contents))

        for message in contents:
            # print(type(message), message)
            try:
                for file in message.get('files'):
                    fn = file.get('name')
                    if fn in urls:
                        base, ext = os.path.splitext(fn)
                        fn = f"{base}_{cnt}{ext}"
                        cnt += 1
                    urls[fn] = file.get('url_private_download')
            except TypeError:
                # raise
                continue

    if debug: print(urls)
    return urls

def downloadUrls(urls, out_path='.', includes=includes):
    bck_dir = os.path.join(subdir, 'files')
    if not os.path.exists(bck_dir):
        os.makedirs(bck_dir, exist_ok=True)

    for fn, url in tqdm(urls.items(), total=len(urls), desc=bck_dir):
        try:
            write_fn = os.path.join(bck_dir, fn)
        
            if not os.path.exists(write_fn):
                wget.download(url, out=write_fn)
        except TypeError:
            print(f"Error: {bck_dir}/{fn}")

if __name__=='__main__':
    
    # transform glob patterns to regular expressions
    # includes = r'|'.join([fnmatch.translate(x) for x in includes])
    # print(includes)

    for root, dirs, _ in os.walk('./'):
        for dir in dirs:
            subdir = os.path.join(root, dir)
            msg_list = getMessages(subdir)
            urls = extractUrls(msg_list)
            print(f"{subdir} - 다운로드 파일 수: {len(urls)}")
            if len(urls) > 0:
                downloadUrls(urls, out_path=subdir, includes=includes)
