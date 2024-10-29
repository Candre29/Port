# Dependencies to install:
# $ python -m pip install requests

# The following script updates the "Number of EOL packages" property of the "Service" blueprint entities, according to the relation with the "Frameworks" blueprint. 

import requests

## First we need to make a post request to generate auth token for subsequent API requests
CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'

API_URL = 'https://api.getport.io/v1'


credentials = {'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET}

token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)

access_token = token_response.json()['accessToken']

if access_token:
    print("successfully retrieved access token")
# You can now use the value in access_token when making further requests

### retrieving the framework entities 
print("Retrieving frameworks information")
headers = {'Authorization': f'Bearer {access_token}'}

blueprint_id = 'framework'
framework_entities_response = requests.get(f'{API_URL}/blueprints/{blueprint_id}/entities', headers=headers)

framework_entities= framework_entities_response.json()['entities']


only_entity_state = {}
for entity in framework_entities:
    only_entity_state[entity['identifier']] = entity['properties']['state']

print(f'Successfully retrieved frameworks and states  \n payload:{only_entity_state}')

### Service entities information
print( '\n Retrieving service entities information')
blueprint_service_id = 'service'

service_entities_response = requests.get(f'{API_URL}/blueprints/{blueprint_service_id}/entities', headers=headers)

service_entities = service_entities_response.json()['entities']
only_identifier_used_frameworks = []

for entity in service_entities:
    only_identifier_used_frameworks.append(
        {'identifier': entity['identifier'],
         'used_frameworks': entity['relations']['used_frameworks']}
    )
    
print(f'Successfully retrieved used frameworks for each service \n payload:{only_identifier_used_frameworks}')

#Now we have 1 list an 1 dictionary. Dictionary "only_entity_state" contains the states of the frameworks listed on our framework Blueprint in Port. List "only_identifier_used_frameworks" contains the used frameworks for each service under our service Blueprint.

#Finding the number of EOL packages 
number_of_EOL_by_service = []

for entities in only_identifier_used_frameworks:
    number_EOL = 0
    for frameworks in entities['used_frameworks']:
        if only_entity_state[frameworks] == 'EOL':
            number_EOL=number_EOL+1
    number_of_EOL_by_service.append({
        'service_identifier': entities['identifier'],
        'number_EOL': number_EOL
    })
    
print(f'\n\n Number of EOL by service {number_of_EOL_by_service}')

##Updating port by making a patch request

print('\n Making patch request to update number of EOL packages for each service entity')

for service in number_of_EOL_by_service:
    service_id = service['service_identifier']
    body= service['number_EOL']
    data = {
        "properties":{
            "number_of_eol_packages": body
        }
    }
    print(f'Making patch request to service entity {service_id}, adding value of EOL : {body} \n {data}')
    print(f'url {API_URL}/blueprints/{blueprint_service_id}/entities/{service_id}')
    
    requests.patch(f'{API_URL}/blueprints/{blueprint_service_id}/entities/{service_id}', headers=headers, json=data )
    
print("\n\n Number of EOL packages successfully updated")