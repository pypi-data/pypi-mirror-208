from amazon_ec2_best_instance import Ec2BestInstance

ec2_best_instance = Ec2BestInstance()

response = ec2_best_instance.get_best_instance_types({
    # Required. Float
    'vcpu': 31.2,
    # Required. Float
    'memory_gb': 100.5,
    # Optional. String. Default: 'on-demand'. Values: 'spot'|'on-demand'
    'usage_class': 'spot',
    # Optional. Boolean.
    # If this parameter is set to True, the method will return the instance type with the best price.
    'is_best_price': True,
    # Optional. Boolean.
    # If this parameter is set to True, the method will return the instance type with the instance storage.
    'is_instance_storage_supported': True,
    # Optional. Integer. Max spot instance frequency interruption in percent.
    # Note: If you specify >=21, then the '>20%' rate is applied
    # It is used only if 'usage_class' == 'spot' and 'is_best_price' == True
    'max_interruption_frequency': 30
})

print(response)
'''
[
    {
        'instance_type': 'r5ad.8xlarge',
        'price': '0.570000',
        'interruption_frequency': {
            'min': 6,
            'max': 10,
            'rate': '5-10%'
        }
    }
]
'''
