import argparse
import json
import os
import requests

# You need the 'requests' library and python > 3.6
# install using pip install requests
# Create an access token under My Profile -> Access Token

jira_base_url = "https://issues.apache.org/jira"
jira_rest_base_url = "https://issues.apache.org/jira/rest/api/2"
tp_base_url = "https://dataartisans.tpondemand.com"
tp_rest_base_url = "https://dataartisans.tpondemand.com/api/v1"

default_tp_project_name = "Apache Flink"

def get_entity_id(entity_type, entity_name, tp_access_token):
    tp_entity_url = f"{tp_rest_base_url}/{entity_type}?access_token={tp_access_token}&format=json&where=(Name eq '{entity_name}')"
    tp_response = requests.get(tp_entity_url)

    tp_response.raise_for_status()

    if len(tp_response.json()['Items']) > 0:
        tp_id = tp_response.json()['Items'][0]['Id']
    else:
        raise Exception(f"Could not find entity {entity_name} in {entity_type}")
    return tp_id

def main():
    tp_access_token = os.environ.get('TP_ACCESS_TOKEN')

    if tp_access_token is None:
        raise Exception("Need to have TP access token in TP_ACCESS_TOKEN env variable")

    parser = argparse.ArgumentParser(description='Import a Jira Issue into Target Process and link to the original issue.')
    parser.add_argument('jira_id', metavar='ID', type=str,
                        help='id of the Jira Issue to import, for example FLINK-1337')

    parser.add_argument('--tp-feature-id', type=str, dest='tp_feature_id',
                        help='parent feature id')

    parser.add_argument('--tp-project', type=str, dest='tp_project', default=default_tp_project_name,
                        help='project to which to add the user story, for example "Apache Flink"')

    parser.add_argument('--tp-team', type=str, dest='tp_team', required=True,
                        help='team to assign, for example "Dream Team"')

    parser.add_argument('--tags', type=str, dest='tags', required=False,
                        help='tags to assign')

    parser.add_argument('--issue-type', type=str, dest='issue_type', required=False, default="user-story",
                        help='issue type, can be one of "user-story" or "bug"')

    args = parser.parse_args()

    jira_id = args.jira_id

    jira_url = f'{jira_rest_base_url}/issue/{jira_id}'
    jira_response = requests.get(jira_url)

    # throw an exception in case of failure
    jira_response.raise_for_status()

    tp_project_id = get_entity_id("projects", args.tp_project, tp_access_token)
    tp_team_id = get_entity_id("teams", args.tp_team, tp_access_token)

    jira_summary = jira_response.json()['fields']['summary']
    jira_description = jira_base_url + "/browse/" + jira_id
    tp_us_name = f"[{jira_id}] {jira_summary}"
    data = {
            'Project': {'Id': tp_project_id},
            'Team': {'Id': tp_team_id},
            'Name': tp_us_name,
            'Description': jira_description}
    if args.tp_feature_id != None:
        data['Feature'] = {'Id': args.tp_feature_id}
    if args.tags != None:
        data['Tags'] = args.tags
    if (args.issue_type == "user-story"):
        tp_add_user_story_url = f"{tp_rest_base_url}/UserStories?access_token={tp_access_token}&format=json"
        tp_response = requests.post(tp_add_user_story_url, json = data, headers = {'Content-type': 'application/json'})
    elif (args.issue_type == "bug"):
        tp_add_bug_url = f"{tp_rest_base_url}/Bugs?access_token={tp_access_token}&format=json"
        tp_response = requests.post(tp_add_bug_url, json = data, headers = {'Content-type': 'application/json'})
    else:
        raise f"Unknown issue type {args.issue_type}."

    tp_response.raise_for_status()
    tp_id = tp_response.json()['Id']
    tp_url = f"{tp_base_url}/entity/{tp_id}"
    print(f"Added issue: {tp_url}")

if __name__ == "__main__":
    main()