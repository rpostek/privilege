import json
import yaml

role_descriptions = {'USER_FILLING': 'Zatwierdzający', 'USER': 'Sporządzający'}

if __name__ == "__main__":
    output = {'roles': []}
    roles = set()
    users = []
    users_roles = []
    with open('users.json', encoding='utf-8') as f:
        data = json.load(f)
        for user in data:
            if user['activated']:
                users.append({'login': user['login'], 'first_name': user['firstName'].strip(), 'last_name': user['lastName'].strip()})
                for role in user['roles']:
                    roles.add(role['name'])
                    users_roles.append((user['login'], role['name']))
    for role in roles:
        role_dict = {'role': role, 'description': role_descriptions.get(role, '')}
        user_logins = [x for x in users_roles if x[1] == role]
        user_dict_list = [u for u in users if u['login'] in [x[0] for x in user_logins]]
        role_dict['users'] = user_dict_list
        output['roles'].append(role_dict)
    yaml.dump(output, default_flow_style=False, sort_keys=False, indent=2, width=1000, allow_unicode=True, stream=open('rorum.yaml', 'w',encoding='utf-8'))


