import boto3
import time

def start_fargate_service():
    # Create clients for ECS and EC2 services
    ecs_client = boto3.client('ecs', region_name='us-east-1')
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    
    # Constants from your logs
    cluster_name = 'self-analyzation'
    service_name = 'self-analyzation-service'
    
    # Step 1: Update the service desired count to start the service
    print(f"Starting service {service_name} in cluster {cluster_name}...")
    response = ecs_client.update_service(
        cluster=cluster_name,
        service=service_name,
        desiredCount=1
    )
    
    # Step 2: Wait for the task to be running
    print("Waiting for task to start running...")
    waiter = ecs_client.get_waiter('services_stable')
    waiter.wait(
        cluster=cluster_name,
        services=[service_name],
        WaiterConfig={
            'Delay': 15,
            'MaxAttempts': 40
        }
    )
    
    # Step 3: Get the running task ARN
    tasks_response = ecs_client.list_tasks(
        cluster=cluster_name,
        serviceName=service_name
    )
    
    if not tasks_response['taskArns']:
        print("No tasks found. Service may not have started properly.")
        return
    
    task_arn = tasks_response['taskArns'][0]
    task_id = task_arn.split('/')[-1]
    print(f"Task running with ID: {task_id}")
    
    # Step 4: Get task details to find the network interface
    task_details = ecs_client.describe_tasks(
        cluster=cluster_name,
        tasks=[task_id]
    )
    
    if not task_details['tasks']:
        print("Task details not found.")
        return
    
    # Extract network interface ID from task details
    task = task_details['tasks'][0]
    eni_id = None
    
    for attachment in task['attachments']:
        if attachment['type'] == 'ElasticNetworkInterface':
            for detail in attachment['details']:
                if detail['name'] == 'networkInterfaceId':
                    eni_id = detail['value']
                    break
    
    if not eni_id:
        print("Network interface ID not found.")
        return
    
    print(f"Network interface ID: {eni_id}")
    
    # Step 5: Get the public IP for the network interface
    eni_details = ec2_client.describe_network_interfaces(
        NetworkInterfaceIds=[eni_id]
    )
    
    if not eni_details['NetworkInterfaces']:
        print("Network interface details not found.")
        return
    
    eni = eni_details['NetworkInterfaces'][0]
    if 'Association' in eni and 'PublicIp' in eni['Association']:
        public_ip = eni['Association']['PublicIp']
        public_dns = eni['Association']['PublicDnsName']
        print(f"Service is now accessible at:")
        print(f"Public IP: {public_ip}")
        print(f"Public DNS: {public_dns}")
    else:
        print("Public IP not found for the network interface.")
    
    # Print container details
    container = task['containers'][0]
    print(f"\nContainer details:")
    print(f"Name: {container['name']}")
    print(f"Image: {container['image']}")
    print(f"Status: {container['lastStatus']}")
    
    return task_id, eni_id

if __name__ == "__main__":
    start_fargate_service()