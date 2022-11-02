from datetime import date, timedelta
from typing import List
from helpers import (
    GH_ORGANIZATION_NAME,
    GH_PROJECT_NUMBER,
    get_json_result,
    get_project_id,
    add_issue_to_project,
    print_usage,
)


def get_recent_open_issue_ids(org_name:str, min_date:date, exclude_authors:List[str]=[]):
    """Get recent open issues under an organization."""
    query = """query($after: String, $query: String!) {
        search(first: 100, after: $after, type: ISSUE, query: $query) {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                ... on Issue {
                        id
                    }
                ... on PullRequest {
                        id
                    }
            }
        }
    }
    """
    min_date = min_date.strftime(r'%Y-%m-%d')
    query_exclude_authors = ' '.join([f'-author:{author}' for author in exclude_authors])
    variables = {
        "query": f"org:{org_name} state:open updated:>={min_date} {query_exclude_authors}"
    }
    nodes = list()
    hasNextPage = True
    while hasNextPage:
        response = get_json_result(query, variables)
        hasNextPage = response["data"]["search"]["pageInfo"]["hasNextPage"]
        variables["after"] = response["data"]["search"]["pageInfo"]["endCursor"]
        nodes.extend(response["data"]["search"]["nodes"])
    return [node['id'] for node in nodes]


@print_usage
def main():
    """
    Find all issues/PRs that are:
    1. under the nextstrain organization
    2. open
    3. active within the last 2 weeks
    4. not authored by bots

    and add them to the planning project.
    """
    project_id = get_project_id(org_name=GH_ORGANIZATION_NAME, project_number=GH_PROJECT_NUMBER)
    min_date = date.today() - timedelta(days=14)
    exclude_authors = ['app/dependabot', 'nextstrain-bot']
    print('getting issues...')
    issue_ids = get_recent_open_issue_ids('nextstrain', min_date, exclude_authors)
    print(f'found {len(issue_ids)} recent issues.')
    print('adding issues (nothing happens if already added)...')
    for i, issue_id in enumerate(issue_ids):
        print(f'adding issue {i + 1}/{len(issue_ids)}')
        add_issue_to_project(issue_id, project_id)
    print('done')
    # TODO: update non-draft PRs to "In Review" state


if __name__ == '__main__':
    main()
