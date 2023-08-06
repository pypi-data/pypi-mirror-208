from amazon_ec2_best_instance import Ec2BestInstance

ec2_best_instance = Ec2BestInstance()

response1 = ec2_best_instance.get_best_instance_types({
    'vcpu': 16,
    'memory_gb': 10
})

print(response1)

response2 = ec2_best_instance.get_best_instance_types({
    'vcpu': 1,
    'memory_gb': 2
})

print(response2)

#

response3 = ec2_best_instance.get_best_instance_types({
    'vcpu': 1,
    'memory_gb': 2,
    'burstable': False
})

is_a1 = False

for instance_type in response3:
    if 'a1' in instance_type:
        is_a1 = True
        break

#assert is_a1, "test"

print(response3)

#

ec2_best_instance = Ec2BestInstance({
    'region': 'us-east-1'
})

response4 = ec2_best_instance.get_best_instance_types({
    'vcpu': 1,
    'memory_gb': 2,
    'burstable': False,
    'is_best_price': True,
    'usage_class': 'spot',
    'is_current_generation': True
})

print('response4', str(response4))

#




