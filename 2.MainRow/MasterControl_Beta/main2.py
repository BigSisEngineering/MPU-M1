import threading
import os
import json
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time

# Assuming DIRECTORY is correctly set up as previously shown
DIRECTORY = os.path.join(os.path.dirname(__file__), 'src', 'frontEnd')
JSON_FILE_PATH = os.path.join(DIRECTORY, 'static', 'js', 'cage_status.json')

class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.path = '/template/index.html'
        if self.path == '/get_all_cages_status':
            self.handle_all_cages_status()
            return  # Important: Return after handling the request to prevent further processing
        # else:
        return SimpleHTTPRequestHandler.do_GET(self)

    def handle_all_cages_status(self):
        response = get_all_cages_status()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def get_all_cages_status():
    cage_addresses = [f"cage0x000{i}" for i in range(1, 10)] + [f"cage0x00{i}" for i in range(10, 16)]
    results = {}
    with threading.Lock():  # Locking to ensure thread safety for the shared 'results' dictionary
        threads = []
        for address in cage_addresses:
            thread = threading.Thread(target=request_cage_data, args=(address, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    # Save results to a JSON file
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(results, f)

    print(f"All cages status : {results}")
    # for address, data in results.items():
    #     print(f"{address}: {data}")

    return results


def request_cage_data(address, results):
    # print(f"Fetching data for {address}")  # Debugging line to ensure threads are running
    try:
        url = f"http://{address}:8080/BoardData"
        with urllib.request.urlopen(url, timeout=2) as response:  # 2-second timeout
            data = response.read()
            results[address] = json.loads(data)
            # print(f"Data for {address}: {results[address]}")  # Print fetched data
    except Exception as e:
        results[address] = str(e)
        # print(f"Error fetching data for {address}: {e}")  # Print errors



def fetch_data_periodically():
    while True:
        get_all_cages_status()
        time.sleep(3)  # Fetch data every 3 seconds, can be adjusted as needed

def run():
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHttpRequestHandler)
    
    # Start fetching data periodically in a daemon thread
    data_fetch_thread = threading.Thread(target=fetch_data_periodically)
    data_fetch_thread.daemon = True
    data_fetch_thread.start()

    print(f"Starting httpd server on {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()