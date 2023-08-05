#!python3
from threading import Thread
from eyes_soatra import eyes
import pandas
import json
import argparse

read_from = 'test/data/approve.csv'
records = pandas.read_csv(read_from).values
founds = []

def save_file(write_to):
    f = open(write_to, "w")
    
    try:
        json_data = json.dumps(founds, ensure_ascii=False, indent=4)
    except:
        json_data = None
        
    f.write(json_data if json_data else str(founds))
    f.close()
    
    print('\n--- done ---\n')
    print('length = ', len(founds))
    print('\n-------------\n')

def worker(start, end):
    for i in range(start, end):
        url = records[i][0]
        
        try:
            obj = eyes.view_page(url, show_header=True)
            
            if obj['active']:
                print(f'--- active {i} --- {url}')
                
            else:
                print(f'\n--- inactive {i} --- {url}\n')
                founds.append(obj)
                
        except:
            pass
        
def main(start_point, length, rows):
    length = (len(records) - start_point) if (start_point + length) > len(records) else length
    token = int(length / rows)
    write_to = f'test/checks/checked-{start_point}-{start_point + length} ({rows}).json'
    threads = []
    
    for i in range(0, rows):
        start = start_point + (i * token)
        
        if i == rows - 1:
            end = length
            thread = Thread(target=worker, kwargs={'start': start, 'end': end})
            threads.append(thread)
            
            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join()
                
            save_file(write_to)

        else:
            end = start + token
            thread = Thread(target=worker, kwargs={'start': start, 'end': end})
            threads.append(thread)
        
if __name__ == '__main__':
    defaults = {
        'start': 0,
        'length': 1000,
        'row': 500
    }
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", help="start point", default=defaults['start'])
    parser.add_argument("-l", "--length", help="length", default=defaults['length'])
    parser.add_argument("-r", "--row", help="row", default=defaults['row'])
    args = parser.parse_args()
    
    start_point = int(args.start)
    length = int(args.length)
    rows = int(args.row)

    main(start_point, length, rows)
