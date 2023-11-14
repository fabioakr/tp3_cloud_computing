import json, requests, threading
import time


def thread_requests(url, n, id):
    for i in range(n):
        response = requests.post(url, verify=False)
        print("Thread " + str(id) + " request " + str(i) + ": " + json.dumps(response.json()))
        #dictionary = json.dumps(response.json())
        #print_working_container(dictionary)

def print_working_container(dictionary):
    if 'container1' in dictionary:
        print('cont1')
    elif 'container2' in dictionary:
        print('cont2')
    elif 'container3' in dictionary:
        print('cont3')
    elif 'container4' in dictionary:
        print('cont4')
    elif 'container5' in dictionary:
        print('cont5')
    elif 'container6' in dictionary:
        print('cont6')
    elif 'container7' in dictionary:
        print('cont7')
    elif 'container8' in dictionary:
        print('cont8')
    else:
        print('no container')


def run_workloads(orchestrator_ip, n_threads, n_requests):

    # waiting till all the workers containers are running
    time.sleep(5*60)

    url = "http://" + orchestrator_ip + ":80/orchestrator"
    all_threads = []

    # initiating thread_count threads, which will all run thread_requests function
    for i in range(1, n_threads + 1):
        all_threads.append(threading.Thread(target=thread_requests, args=[url, n_requests, i]))

    # starting all the threads
    for i in range(0, n_threads):
        all_threads[i].start()

    # joining all the threads
    for i in range(0, n_threads):
        all_threads[i].join()


if __name__ == '__main__':
    pass
