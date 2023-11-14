"""
    File operating the cleaning of any instances generated
    previously in the AWS account, to avoid running out of
    balance. 
"""

def main(client):

    # Terminates all instances
    response = client.describe_instances()
    #print(len(response['Reservations']))
    instance_ids = []
    for i in range(len(response['Reservations'])):
        instance_ids.append(response['Reservations'][i]['Instances'][0]['InstanceId'])
    client.terminate_instances(InstanceIds = instance_ids)

if __name__ == '__main__':
    pass
