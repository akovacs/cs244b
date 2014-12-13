#!/usr/bin/env python

import requests
import json
from subprocess import call

# Simple python script to repeatedly upload the specified file as multipart form post

NUM_TRIALS=100

url = 'http://localhost:8080/api/shard'

replicas=[ #requirements.txt ba5d991290ca46c5249f03334f1870b0a595e985afdcd65aea677746bc8cab98  
           [('cs244b-1','data-10240bb1-8080'),('cs244b-2','replica-ae5b8562-8082'),('cs244b-7','replica-c570e5d7-8092')],
           #perf.txt         420b2a7f7539361849be70c925d26b010563818c9276c5bda61370ce340d509b
           [('cs244b-1','data-10240bb1-8080'),('cs244b-11','replica-3e4ecc9b-8100'),('cs244b-3','replica-4c92ff13-8084')]]

files = [
    {'file': open('scripts/testdata/requirements.txt', 'rb').read()}, # 16 B
    {'file': open('scripts/testdata/perf.txt', 'rb').read()}, # 2 KB
    #{'file': open('scripts/testdata/Chord.pdf', 'rb').read()} #, # 195 KB
    #{'file': open('scripts/testdata/gondola.jpg', 'rb').read()} #, # 1.2 MB
    #{'file': open('scripts/testdata/lake.jpg', 'rb').read()} # 12.2 MB
]

def postFile(fileToPost):
    # POST the file once
    file_id = None
    response = requests.post(url, files=fileToPost)
    responseJson = json.loads(response.text)
    if 'id' in responseJson:
        file_id = responseJson['id']
    return file_id


def getLatencies(file_id, index, numReplicasToRemove):
    ## Test GET requests
    for iteration in range(NUM_TRIALS):
        #print 'GET',iteration,'/',NUM_TRIALS
        result = requests.get(url+'/'+file_id)

    # Extract latency numbers from DropWizard
    latencies = requests.get('http://localhost:8080/admin/metrics')
    timers = json.loads(latencies.text)['timers']
    with (open('getperf/'+str(index)+'-'+str(numReplicasToRemove)+'.txt', 'w')) as outfile:
        outfile.write(json.dumps(timers['edu.stanford.cs244b.Shard.getItem']))
    print 'Get median latency for file ' + str(index) + ': ' + str(timers['edu.stanford.cs244b.Shard.getItem']['p50'])


for index, current_file in enumerate(files):
    for numReplicasToRemove in range(len(replicas[index])-1):
        #call(['vagrant', 'provision'])
        
        print 'Starting test on file ' + str(index)

        # upload file to the shard, replicate it
        file_id = postFile(current_file)

        # remove specified copies
        for (replicaHost, replicaFolder) in replicas[index][0:numReplicasToRemove]:
            print ' '.join(['vagrant', 'ssh', replicaHost, '-c', "'sudo rm "+replicaFolder+"/*'"])
            call(['vagrant', 'ssh', replicaHost, '-c', "'sudo rm "+replicaFolder+"/*'"])
            
        # get latencies 
        getLatencies(file_id, index, numReplicasToRemove)


