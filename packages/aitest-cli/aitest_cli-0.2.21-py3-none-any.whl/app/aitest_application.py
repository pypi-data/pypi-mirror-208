from datetime import *
import click
import os
import requests
import json
from sys import *
import base64
from prettytable import PrettyTable
import time

# lOGGING MODULE
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

# Command Group
@click.group(name='configure')
def configure():
    pass


def get_access_token(profile, client_id, client_secret_id):
    if profile == 'dev':
        access_token_api = "https://login-marxeed-dev.auth.us-east-1.amazoncognito.com/oauth2/token"
    else:
        access_token_api = "https://login.aaic.cc/oauth2/token"

    str_to_encode = client_id + ":" + client_secret_id
    encoded_str = base64.b64encode(str_to_encode.encode('utf-8'))
    encoded_value = encoded_str.decode('utf-8')
    data = {'grant_type': 'client_credentials', 'scope': 'aitestpublic/runtest'}
    access_token_api_headers = {"Authorization": f"Basic {encoded_value}",
                                "content-type": "application/x-www-form-urlencoded"}
    token = requests.post(access_token_api, headers=access_token_api_headers, data=data)
    if token.status_code == 400:
        click.echo('\n"error" : "Please add your valid Client ID and Client Secret ID ."\n')
        exit()
    else:
        token_data = token.json()

    access_token = token_data["access_token"]
    return access_token

# Logging module
def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_logger(logger_name, debug):
   logger = logging.getLogger(logger_name)
   if debug:
       logger.setLevel(logging.DEBUG); # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   return logger

# Creating command
@configure.command(name='configure')
@click.option('--env', '-e', required=False)
@click.option('-debug', '--debug', is_flag=True, help='Enables debug mode')
def configure(env, debug):
    """If this command is run with no arguments, you will be prompted for configuration values such as your User ID, Client ID and Client Secret ID.If your configure file does not  exist
       (the default location is ~/.aitest/prod/configure), the aitest CLI will create it for you.To keep an existing value, hit enter when prompted for the value.
        Default Environment is PROD
       To save the configurations , you can run below command:\n
       aitest configure -e [aitest enviornment (dev/prod)]
       To save the configurations and see output in debug mode, you can run below command:\n
       aitest configure -e [aitest enviornment (dev/prod)] -debug/--debug [debug mode]

    """
    # Enabling Logger
    logger = get_logger("configure", debug)
    logger.debug("Configuring user id, client id and client secret id for ai-test cli \n")

    user_id = input('Enter aiTest User Identifier :')
    client_id = input('Enter Client ID :')
    client_secret_id = input('Enter Client Secret ID :')

    if env and env == 'dev':
        profile = 'dev'
        logger.debug("Profile set to dev environment \n")
    else:
        profile = 'prod'
        logger.debug("Profile set to prod environment \n")

    folder_path = os.path.join(os.path.expanduser('~'), (".aitest/{}".format(profile)))
    logger.debug("Folder path is set to \n", folder_path)
    folder_exist = os.path.exists(folder_path)
    if not folder_exist:
        logger.debug("Folder " + folder_path +" is not exist")
        os.mkdir(folder_path)
        logger.debug("Created folder with path ", folder_path)
        fd = open(os.path.join(folder_path, "configure"), 'w')
        logger.debug("Opened folder " + folder_path + " in write mode\n")

        if user_id:
            fd.write("user_id = " + user_id + "\n")
            logger.debug("User entered user id , writing it")
        else:
            fd.write("user_id = " + " " + "\n")
            logger.debug("User did not entered user id , writing blank user id \n")

        if client_id:
            fd.write("client_id = " + client_id + "\n")
            logger.debug("User entered client id , writing it \n")
        else:
            fd.write("client_id = " + " " + "\n")
            logger.debug("User did not entered client id , writing blank client id \n")

        if client_secret_id:
            fd.write("client_secret_id = " + client_secret_id + "\n")
            logger.debug("User entered client secret id , writing it \n")
        else:
            fd.write("client_secret_id = " + " " + "\n")
            logger.debug("User did not entered client secret id , writing blank client secret id \n")
        fd.close()
        logger.debug("Closed opened file \n")
    else:
        logger.debug("Folder " + folder_path +" is exist")
        file_path = os.path.join(os.path.expanduser('~'), (".aitest/{}".format(profile)), "configure")
        file = open(file_path, "r")
        logger.debug("Opened file " + file_path + " in read mode \n")
        logger.debug("Saving existing content of file as ex conetent \n")
        content = file.read()
        data = content.split("\n")
        ex_user_id = data[0].split(" = ")[1]
        ex_client_id = data[1].split(" = ")[1]
        ex_client_secret_id = data[2].split(" = ")[1]

        fd = open(os.path.join(folder_path, "configure"), 'w')
        logger.debug("Opened file " + file_path + " in write mode \n")
        if user_id:
            fd.write("user_id = " + user_id + "\n")
            logger.debug("User entered user id , writing it to "+ folder_path +" \n")
        else:
            fd.write("user_id = " + ex_user_id + "\n")
            logger.debug("User did not entered any user id , using ex value of user id \n")

        if client_id:
            fd.write("client_id = " + client_id + "\n")
            logger.debug("User entered client id , writing it to "+ folder_path +" \n")
        else:
            fd.write("client_id = " + ex_client_id + "\n")
            logger.debug("User did not entered any client id , using ex value of client id \n")

        if client_secret_id:
            fd.write("client_secret_id = " + client_secret_id + "\n")
            logger.debug("User entered client secret id , writing it to "+ folder_path +" \n")
        else:
            fd.write("client_secret_id = " + ex_client_secret_id + "\n")
            logger.debug("User did not entered any client secret id , using ex value of client secret id \n")
        fd.close()
        logger.debug("Closed opened " + folder_path + " file \n")


# Command Group
@click.group(name='run')
def run():
    pass


# Creating command
@run.command(name='run')
@click.option('--testrun_id', '-id', required=True)
@click.option('--wait_time', '-w', required=False)
@click.option('--git_pass', '-p', required=False)
@click.option('--branch', '-b', required=False)
@click.option('--testrun_name', '-n', required=False)
@click.option('--env', '-e', required=False)
@click.option('-debug', '--debug', is_flag=True, help='Enables debug mode')
def run(testrun_id, git_pass, wait_time, branch, testrun_name, env, debug):
    """If this command is run with testrun id as an argument, aitest CLI will create new test for you with same configuration of provided testrun id.Enter git password with -p only if you used git url of the automation code for creating the test otherwise no need to enter git password.
       Enter the waiting time in minutes with -w as an argument, To wait for looking the testrun status in given time.\n
       Default Environment is PROD
       Enter branch name with -w as an [optional] argument to run aiTest CLI on specific branch
       Enter testrun name with -n as an [optional] argument to rename the testrun
       To re-run the test, you can run below command:\n
       aitest run -id [testrun id] -p [git password] -w [wait_time] -b [branch_name] -n [testrun_name] -e [aitest enviornment (dev/prod)]
       To re-run the test in debug mode, you can run below command:\n
       aitest run -id [testrun id] -p [git password] -w [wait_time] -b [branch_name] -n [testrun_name] -e [aitest enviornment (dev/prod)] -debug/--debug

    """
    # Enabling Logger
    logger = get_logger("run", debug)
    logger.debug("Creating new test with given testrun id " + testrun_id +" \n")

    if env and env == 'dev':
        profile = 'dev'
        logger.debug("Profile set to dev environment \n")
    else:
        profile = 'prod'
        logger.debug("Profile set to prod environment \n")
    try:
        if "USER_ID" in os.environ and "CLIENT_ID" in os.environ and "CLIENT_SECRET_ID" in os.environ:
            logger.debug("Found user id, client id and client secret id from enviornment \n")
            logger.debug("Using enviornment values for user id, client id and client secret id \n")
            user_id = os.environ["USER_ID"]
            client_id = os.environ["CLIENT_ID"]
            client_secret_id = os.environ["CLIENT_SECRET_ID"]
        else:
            file_path = os.path.join(os.path.expanduser('~'), (".aitest/{}".format(profile)), "configure")
            logger.debug("Using "+ file_path +" values for user id, client id and client secret id \n")
            file = open(file_path, "r")
            content = file.read()
            data = content.split("\n")
            user_id = data[0].split(" = ")[1]
            client_id = data[1].split(" = ")[1]
            client_secret_id = data[2].split(" = ")[1]
    except:
        logger.debug("user id, client id and client secret id neither present in enviornment nor in configure file. \n")
        click.echo('\n"error" : "Please add your valid USER_ID, CLIENT_ID and CLIENT_SECRET_ID in configure file."\n')
        exit()

    logger.debug("Getting access token for "+ profile +" using given client and client secret id \n")
    access_token = get_access_token(profile, client_id, client_secret_id)
    logger.debug("Successfully got access token \n")

    headers = {"Authorization": f"Bearer {access_token}", "aiTest-User-Identifier": user_id}
    logger.debug("Created headers for further api calls \n" + json.dumps(headers) + " \n")
    if profile == 'dev':
        base_url = "https://api.aitest.dev.appliedaiconsulting.com/public/v1/testrun/load_test"
        logger.debug("Using "+ base_url + " for further api calls \n")
    else:
        base_url = "https://api.aitest.appliedaiconsulting.com/public/v1/testrun/load_test"
        logger.debug("Using "+ base_url + " for further api calls \n")

    dd = {"testrun_id": testrun_id, "git_password": git_pass, "git_branch": branch, "testrun_name": testrun_name}
    logger.debug("User eneterd data for testrun is " + json.dumps(dd) + " \n")
    payload = json.dumps(dd)
    logger.debug("Dumped user entered data in json " + payload + " \n")

    logger.debug("Calling post api with given payload \n "+ payload + " \n and headers \n " + json.dumps(headers) + "\n") 
    res2 = requests.post(base_url, data=payload, headers=headers)
    logger.debug("Got "+ str(res2.status_code) + " response from post api ("+base_url+") call with body \n " + json.dumps(res2.json()))
    if res2.status_code == 401:
        logger.debug("Got "+ str(res2.status_code) + " response , User ID is not valid for this request \n ") 
        click.echo('\n"error" : "Please add your valid User ID."\n')
        exit()
    
    if res2.status_code == 400:
        err_response = res2.json()
        logger.debug("Got "+ str(res2.status_code) + f" response , {err_response['body']} \n ") 
        click.echo(f'\n"error" : {err_response["body"]} \n')
        exit()
    if res2.status_code == 200:
        logger.debug("Got "+ str(res2.status_code) + " resposne from post api request \n ") 
        res_body = res2.json()
        try:
            logger.debug("Loading resposne body in json object \n")
            test_data = json.loads(res_body['body'])
        except:
            logger.debug("Got exception while loading response body in json data \n" + json.dumps(res_body))
            click.echo(res_body)
            exit(-1)
        project_id = test_data['load_test_details']['project_id']
        test_type = test_data['load_test_details']['test_type']
        testrun_id_new = test_data['load_test_details']['testrun_id']
        if test_type == 'functional_test':
            sub_link = 'multi-browser-test'
        elif test_type == 'load_test':
            sub_link = 'performance-test'
        else:
            sub_link = 'url-test'
        if profile == 'dev':
            aitest_ui = "https://app.aitest.dev.appliedaiconsulting.com/"
            logger.debug("Using "+ aitest_ui + " for further ui calls \n")
        else:
            aitest_ui = "https://app.aitest.appliedaiconsulting.com/"
            logger.debug("Using "+ aitest_ui + " for further ui calls \n")

        testrun_link = aitest_ui + sub_link + "?testrun_id=" + testrun_id_new + "&project_id=" + project_id
        logger.debug("Created testrun link as  "+ testrun_link + " \n")
        logger.debug("Testrun created successfully \n Testrun Name : " + test_data['load_test_details']['testrun_name'] + " \nTestrun ID : " + test_data['load_test_details']['testrun_id'] +" \n")
        click.echo(
            f"\nTestrun created successfully\nTestrun Name : {test_data['load_test_details']['testrun_name']}\nTestrun ID : {test_data['load_test_details']['testrun_id']}\n")
        click.echo(f"\nTestrun Link: {testrun_link}\n")
        if wait_time:
            click.echo("Testrun is in progress, result will be displayed once it get completed.")
            logger.debug("\n Testrun is in progress, result will be displayed once it get completed. \n")
            new_time = datetime.now() + timedelta(minutes=int(wait_time))
            test_status = ""
            
            # while test_status != "completed":
            # sleep time before making status API call
            sleep_time_to_poll_status = 300
            logger.debug("Before making an api call, sleep time to poll status is set to 300 \n")
            wait_time = int((int(wait_time) * 60) / 10)
            logger.debug("Wait time is " + str(wait_time) + "\n")
            if wait_time < 300:
                sleep_time_to_poll_status = wait_time
                logger.debug("Sleep time value is set to the wait time value \n")
                
            while True:
                # get access token for every status call to avoid token expiration
                logger.debug("Getting access token for every status call to avoid token expiration  \n")
                access_token = get_access_token(profile=profile, client_id=client_id, client_secret_id=client_secret_id)
                headers = {"Authorization": f"Bearer {access_token}", "aiTest-User-Identifier": user_id}

                if (datetime.now().strftime("%H:%M:%S")) >= (new_time.strftime("%H:%M:%S")):
                    logger.debug("\n The request is timed out. The testrun is still in progress. To see the status of the testrun, please run command : [ aitest status "+ test_data['load_test_details']['testrun_id'] +"]")
                    click.echo(
                        f"The request is timed out. The testrun is still in progress. To see the status of the testrun, please run command : [ aitest status {test_data['load_test_details']['testrun_id']} ].")
                    exit()
                if profile == 'dev':
                    base_url = f"https://api.aitest.dev.appliedaiconsulting.com/public/v1/testrun_result/status/{test_data['load_test_details']['testrun_id']}"
                    logger.debug("Using "+ base_url + " to get testrun_result \n")
                else:
                    base_url = f"https://api.aitest.appliedaiconsulting.com/public/v1/testrun_result/status/{test_data['load_test_details']['testrun_id']}"
                    logger.debug("Using "+ base_url + " to get testrun_result \n")

                logger.debug("Calling get api to get testrun_result \n")
                status_res = requests.get(base_url, headers=headers)
                logger.debug("Got " + str(status_res ) + " response from testrun_result get call with body \n " + json.dumps(status_res.json())+  " \n") 
                status_test_data = status_res.json()
                if status_test_data.get("statusCode") and status_test_data['statusCode'] == 200:
                    body = json.loads(status_test_data['body'])
                    test_status = body['testrun_status']
                    # click.echo(f"Test status is: {test_status}\n")
                else:
                    test_status = ""
                if test_status == "completed":
                    logger.debug("Test completed successfully with status " + test_status +  " \n") 
                    break
                # if test_status == "completed":
                #     testrun_status_details = body['testrun_status_details']
                #     table = PrettyTable(
                #         ["browser_name", "browser_version", "test run result id", "status", "time taken"])
                #     click.echo(f"\ntest status : {test_status}\n")
                #     fail_count = 0
                #     for i in testrun_status_details:
                #         if i['testrun_result_status'] == "fail":
                #             fail_count += 1
                #         table.add_row([i['browser_name'], i['browser_version'], i['testrun_result_id'],
                #                        i['testrun_result_status'], i['time_taken']])
                #     click.echo(table)
                #     if fail_count == 0:
                #         click.echo(
                #             "All test cases from this testrun have passed. Please refer above table for more details.")
                #         exit()
                #     else:
                #         click.echo(
                #             f"{fail_count} test cases from this testrun have failed. Please refer above table for more details.")
                #         exit(1)
                # adding a wait time so that we don't make continuous CALLS to status API.
                click.echo(f"Testrun in Progress waiting for {sleep_time_to_poll_status} seconds to perform next status call..")
                time.sleep(sleep_time_to_poll_status)
                # wait_time = int((int(wait_time) * 60) / 10)
                # if wait_time > 300:
                #     click.echo(f"Testrun in Progress waiting for {wait_time} seconds to perform next status call..")
                #     time.sleep(300)
                # time.sleep(wait_time)
                # click.echo(f"Testrun in Progress waiting for {wait_time} seconds to perform next status call..")

            if test_status == "completed":
                logger.debug("Testrun is completed ...\n ")
                logger.debug("Adding details in table for completed testrun ...")
                testrun_status_details = body.get('testrun_status_details', [])
                table = PrettyTable(
                    ["browser_name", "browser_version", "test run result id", "status", "time taken"])
                click.echo(f"\ntest status : {test_status}\n")
                click.echo(f"\nTestrun Link: {testrun_link}\n")
                fail_count = 0
                for i in testrun_status_details:
                    if i['testrun_result_status'] == "fail":
                        fail_count += 1
                    logger.debug("Adding row entry in table for data " + str(i) + "\n")
                    table.add_row([i['browser_name'], i['browser_version'], i['testrun_result_id'],
                                    i['testrun_result_status'], i['time_taken']])
                
                click.echo(table)
                logger.debug("Added table is \n " + str(table))
                if fail_count == 0:
                    logger.debug("\nAll test cases from this testrun have passed. Please refer above table for more details.")
                    click.echo(
                        "All test cases from this testrun have passed. Please refer above table for more details.")
                    exit()
                else:
                    logger.debug( str(fail_count) +" Test cases from this testrun have failed. Please refer above table for more details.")
                    click.echo(
                        f" Some test cases from this testrun have failed. Please refer above table for more details.")
                    exit(1)

    else:
        logger.debug("\n Testrun result is " + json.dumps(res2.json()))
        click.echo(res2.json())
        exit()


# Command Group
@click.group(name='status')
def status():
    """ status command is use to display the status of particular test.  """
    pass


# Creating command
@status.command(name='status')
@click.option('--testrun_id', '-id', required=True)
@click.option('--env', '-e', required=False)
@click.option('-debug', '--debug', is_flag=True, help='Enables debug mode')
def status(testrun_id, env, debug):
    """ If this command is run with testrun id as an argument, aitest CLI will display the test details .\n  
        Default Environment is PROD
        To see the status of test , you can run below command:\n
        aitest status -id [testrun_id] -e [aitest enviornment (dev/prod)]
        To see the status of test in debug mode , you can run below command:\n
        aitest status -id [testrun_id] -e [aitest enviornment (dev/prod)] -debug/--debug 
    """
    # Enabling Logger
    logger = get_logger("status", debug)
    logger.debug("Checking status for \n " +  testrun_id)

    if env and env == 'dev':
        profile = 'dev'
        logger.debug("Profile set to dev environment \n")
    else:
        profile = 'prod'
        logger.debug("Profile set to prod environment \n")
    try:
        if "USER_ID" in os.environ and "CLIENT_ID" in os.environ and "CLIENT_SECRET_ID" in os.environ:
            logger.debug("Found user id, client id and client secret id from enviornment \n")
            logger.debug("Using enviornment values for user id, client id and client secret id \n")
            user_id = os.environ["USER_ID"]
            client_id = os.environ["CLIENT_ID"]
            client_secret_id = os.environ["CLIENT_SECRET_ID"]
        else:
            file_path = os.path.join(os.path.expanduser('~'), (".aitest/{}".format(profile)), "configure")
            logger.debug("Using "+ file_path +" values for user id, client id and client secret id \n")
            file = open(file_path, "r")
            content = file.read()
            data = content.split("\n")
            user_id = data[0].split(" = ")[1]
            client_id = data[1].split(" = ")[1]
            client_secret_id = data[2].split(" = ")[1]
    except:
        logger.debug("user id, client id and client secret id neither present in enviornment nor in configure file. \n")
        click.echo('\n"error" : "Please add your valid USER_ID, CLIENT_ID and CLIENT_SECRET_ID in configure file."\n')
        exit()

    logger.debug("Getting access token for "+ profile +" using given client and client secret id \n")
    access_token = get_access_token(profile=profile, client_id=client_id, client_secret_id=client_secret_id)
    logger.debug("Successfully got access token \n")

    headers = {"Authorization": f"Bearer {access_token}", "aiTest-User-Identifier": user_id}
    logger.debug("Created headers for further api calls \n" + json.dumps(headers) + " \n")

    if profile == 'dev':
        base_url = f"https://api.aitest.dev.appliedaiconsulting.com/public/v1/testrun_result/status/{testrun_id}"
        logger.debug("Using "+ base_url + " for further api calls \n")
    else:
        base_url = f"https://api.aitest.appliedaiconsulting.com/public/v1/testrun_result/status/{testrun_id}"
        logger.debug("Using "+ base_url + " for further api calls \n")

    logger.debug("Calling get api to get status of  payload \n " + testrun_id + "\n")
    status_res = requests.get(base_url, headers=headers)
    logger.debug("Get api response for "+ base_url + "is \n " + json.dumps(status_res.json()) + "\n") 
    if status_res.status_code == 401:
        logger.debug("User ID is not valid for this request got status code as \n "+ str(status_res.status_code))
        click.echo('\n"error" : "Please add your valid User ID."\n')
        exit()
    status_test_data = status_res.json()

    body = json.loads(status_test_data['body'])

    test_status = body['testrun_status']

    testrun_status_details = body['testrun_status_details']
    logger.debug("Testrun status details are \n "+ json.dumps(testrun_status_details))
    table = PrettyTable(["browser_name", "browser_version", "test run result id", "status", "time taken"])
    logger.debug("\n Testrun status is " + test_status)

    click.echo(f"\nTestrun Status : {test_status}\n")
    fail_count = 0
    logger.debug("\n Adding testrun status details in table \n ")
    for i in testrun_status_details:
        if i['testrun_result_status'] == "fail":
            fail_count += 1
        logger.debug("Adding row entry in table for data " + str(i) + "\n")
        table.add_row([i['browser_name'], i['browser_version'], i['testrun_result_id'], i['testrun_result_status'],
                       i['time_taken']])
    logger.debug("Added table is \n " + str(table))
    click.echo(table)
    if fail_count == 0:
        logger.debug("\n All test cases from this testrun have passed. Please refer above table for more details. \n")
        click.echo("All test cases from this testrun have passed. Please refer above table for more details.")
        exit()
    else:
        logger.debug(str(fail_count) + " test cases from this testrun have failed. Please refer above table for more details. \n")
        click.echo(f"{fail_count} test cases from this testrun have failed. Please refer above table for more details.")
        exit(1)
