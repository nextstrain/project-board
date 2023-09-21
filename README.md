# Nextstrain GitHub Project

The Nextstrain team previously used [a GitHub project](https://github.com/orgs/nextstrain/projects/11) to plan and track development work across repositories. It is no longer maintained, but the scripts used to automate populating the board with items is kept in this repository for archival purposes.

### Status

1. **New** - all new items to be triaged
2. **Prioritized** - prioritized and ready for work
3. **In Progress** - work in progress
4. **In Review** - work is mostly done, blocked on final discussions
5. **Backlog** - de-prioritized
6. **Done** - all work done, though changes may need to be bundled in a release to take affect

### Automation

New items are added automatically every day using [this GitHub Actions workflow](https://github.com/nextstrain/planning/actions/workflows/update_github_project.yml).

GitHub projects has limited automation. You can see what is enabled [here](https://github.com/orgs/nextstrain/projects/11/workflows):

- The status is set to **New** when:
    - An issue/PR is added to the project.
    - An issue/PR is reopened.
- The status is set to **Done** when:
    - A PR is merged or closed.
    - An issue is closed.
- The item is **archived** when its status is set to Done. See the workflow for the exact query.

### Local development

These environment variables are required for the scripts to function properly.

```sh
export GH_ORGANIZATION_NAME='nextstrain'
export GH_PROJECT_NUMBER='11'
export GITHUB_TOKEN='' # This should be a GitHub token with read:project and project scope
```
