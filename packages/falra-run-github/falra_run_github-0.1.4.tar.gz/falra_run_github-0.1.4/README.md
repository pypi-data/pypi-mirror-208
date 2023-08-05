# falra_run_github


## Ussage(pip install falra_run_github=0.0.2)

### Download and execute python code from github
python3 -m falra_run_github --action=start --repo_url=https://github.com/user-account/user-repo --access_token=user_access_token --repo_name=user-repo --py_name=main.py --argument="['arg_1', 'arg_2']"

### Show the executing results in falra_output.txt
python3 -m falra_run_github --action=output --repo_name=user-repo

### Delete source codes downloaded from github
python3 -m falra_run_github --action=clean 


## Ussage(original main.py)

### Download and execute python code from github
python3 main.py --action=start --repo_url=https://github.com/user-account/user-repo --access_token=user_access_token --repo_name=user-repo --py_name=main.py --argument="['arg_1', 'arg_2']"

### Show the executing results in falra_output.txt
python3 main.py --action=output --repo_name=user-repo

### Delete source codes downloaded from github
python3 main.py --action=clean 

