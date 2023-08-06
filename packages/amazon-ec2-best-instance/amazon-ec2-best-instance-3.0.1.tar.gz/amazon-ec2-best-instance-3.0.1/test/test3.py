from amazon_ec2_best_instance import Ec2BestInstance

ec2_best_instance = Ec2BestInstance()

response = ec2_best_instance.get_best_instance_types({
    'vcpu': 10,
    'memory_gb': 16
})

print(response) # ['m5a.16xlarge', ... ,'r5n.metal']

