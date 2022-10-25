import json
import os
import requests


GH_ORGANIZATION_NAME = os.environ['GH_ORGANIZATION_NAME']
GH_PROJECT_NUMBER = int(os.environ['GH_PROJECT_NUMBER'])

GH_GRAPHQL_URL = 'https://api.github.com/graphql'
TOKEN = os.environ['GITHUB_TOKEN'] # add your PAT with read:org and write:org scope
if not TOKEN.startswith('ghp_'):
    print("WARNING: Github token does not start with 'ghp_'. If an error occurs, check that the token is configured properly.")


def get_json_result(query, variables=None):
    """Get JSON result of a GraphQL query or mutation."""

    # Manually create a session to disable the behavior of .netrc overriding
    # the Authorization header during local dev¹.
    # ¹https://github.com/psf/requests/issues/3929
    session = requests.Session()
    session.trust_env = False
    headers={'Authorization': f'token {TOKEN}'}
    r = session.post(GH_GRAPHQL_URL, json={'query': query, 'variables': variables}, headers=headers)

    if r.status_code != 200:
        raise Exception(f'[{r.status_code}] GitHub GraphQL API response: {r.text}')
    result = json.loads(r.text)
    if 'errors' in result:
        raise Exception(f'GitHub GraphQL API response has errors: {result["errors"]}')
    return result


def get_all_items(org_name, project_number):
    """Get items from a GitHub project."""
    query = """query($after: String, $login: String!, $projectNumber: Int!) {
        organization(login: $login) {
            projectNext(number: $projectNumber) {
                items(first: 100, after: $after) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        fieldValues(first:100) {
                            nodes {
                                projectField {
                                    id
                                    name
                                }
                                value
                            }
                        }
                    }
                }
            }
        }
    }
    """
    variables = {
        "login": org_name,
        "projectNumber": project_number
    }
    nodes = list()
    hasNextPage = True
    while hasNextPage:
        response = get_json_result(query, variables)
        hasNextPage = response["data"]["organization"]["projectNext"]["items"]["pageInfo"]["hasNextPage"]
        variables["after"] = response["data"]["organization"]["projectNext"]["items"]["pageInfo"]["endCursor"]
        nodes.extend(response["data"]["organization"]["projectNext"]["items"]["nodes"])
    return nodes


def update_project_item_field(project_id, item_id, field_id, value):
    """Update the field value of an item in a project."""
    mutation = """mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
        updateProjectNextItemField(input: { projectId: $projectId itemId: $itemId fieldId: $fieldId value: $value }) {
            projectNextItem {
                id
            }
        }
    }
    """
    variables = {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "value": str(value),
    }
    return get_json_result(mutation, variables)


def get_project_id(org_name, project_number):
    """Get the ID of a project."""
    query = """query($login: String!, $projectNumber: Int!) {
        organization(login: $login) {
            projectNext(number: $projectNumber) {
                id
            }
        }
    }
    """
    variables = {
        "login": org_name,
        "projectNumber": project_number
    }
    result = get_json_result(query, variables)
    return result['data']['organization']['projectNext']['id']


def get_project_fields_by_name(org_name, project_number):
    """Get a mapping of field names to a JSON object."""
    query = """query($login: String!, $projectNumber: Int!) {
        organization(login: $login) {
            projectNext(number: $projectNumber) {
                fields(first: 100) {
                    nodes {
                        id
                        name
                        settings
                    }
                }
            }
        }
    }
    """
    variables = {
        "login": org_name,
        "projectNumber": project_number
    }
    result = get_json_result(query, variables)
    return {
        item['name']: item
        for item in result['data']['organization']['projectNext']['fields']['nodes']
    }


def add_issue_to_project(issue_id, project_id):
    """Add an issue to a project."""
    mutation = """mutation($projectId: ID!, $issueId: ID!) {
        addProjectNextItem(input: { projectId: $projectId contentId: $issueId }) {
            projectNextItem {
                id
            }
        }
    }
    """
    variables = {
        "projectId": project_id,
        "issueId": issue_id
    }
    return get_json_result(mutation, variables)

def get_remaining_points():
    """Get the remaining GitHub API points for the access token defined at the global scope.

    More about the limit: https://docs.github.com/en/graphql/overview/resource-limitations#rate-limit
    """
    query = """query {
        rateLimit {
            remaining
        }
    }
    """
    result = get_json_result(query)
    return int(result["data"]["rateLimit"]["remaining"])
