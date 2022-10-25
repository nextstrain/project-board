import json
from helpers import (
    GH_ORGANIZATION_NAME,
    GH_PROJECT_NUMBER,
    get_all_items,
    print_usage,
    update_project_item_field,
    get_project_id,
    get_project_fields_by_name,
)


# adapted from https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad
class PainScoreCalculator():
    def __init__(self):
        self.org_name = GH_ORGANIZATION_NAME
        self.project_number = GH_PROJECT_NUMBER

    @print_usage
    def run(self):
        print('getting project fields...')
        fields_by_name = get_project_fields_by_name(self.org_name, self.project_number)
        field_option_rank = self.get_field_option_rank(fields_by_name)
        print('getting items...')
        items = get_all_items(self.org_name, self.project_number)
        print('calculating pain scores...')
        item_pain_scores = self.get_item_pain_scores(items, field_option_rank)
        pain_score_field_id = fields_by_name["User Pain Score"]["id"]
        print('updating project items with pain scores...')
        self.write_item_pain_scores(item_pain_scores, pain_score_field_id)
        print('done.')

    def get_field_option_rank(self, fields_by_name):
        """Get a mapping of pain score column field ID to options.

        Options are represented as a mapping of option ID to integer value.

        Returns
        -------
        {
            field_id :
            {
                option_id : value (int)
            }
        }

        Representation:

        {
            id(Type) :
                {
                    id(Type=1) : 1
                    id(Type=2) : 2
                    ...
                }
            id(Priority) :
                {
                    id(Priority=1) : 1
                    id(Priority=2) : 2
                    ...
                }
            ...
        }
        """
        field_option_rank = dict()
        for name in fields_by_name:
            if name in {'Type', 'Priority', 'Likelihood'}:
                field = fields_by_name[name]
                settings = json.loads(field['settings'])
                # cast first character of option name to integer
                option_id_to_int_rank = {option['id']: int(option['name'][0]) for option in settings['options']}
                field_option_rank[field['id']] = option_id_to_int_rank
        return field_option_rank

    def get_item_pain_scores(self, items, field_option_rank):
        """Get a mapping of item IDs to calculated pain scores."""
        item_pain_scores = dict()
        for item in items:
            pain_score = None
            for field in item['fieldValues']['nodes']:
                field_id = field['projectField']['id']
                if field_id in field_option_rank.keys():
                    if not pain_score:
                        pain_score = 1
                    option_id = field['value']
                    field_value_int = field_option_rank[field_id][option_id]
                    pain_score *= field_value_int
            if pain_score:
                item_pain_scores[item['id']] = pain_score
        return item_pain_scores

    def write_item_pain_scores(self, item_pain_scores, pain_score_field_id):
        """Update the project with pain scores for each item."""
        project_id = get_project_id(self.org_name, self.project_number)
        for i, (item_id, score) in enumerate(item_pain_scores.items()):
            print(f'updating pain score for issue {i + 1}/{len(item_pain_scores)}')
            update_project_item_field(project_id, item_id, pain_score_field_id, score)


if __name__ == '__main__':
    PainScoreCalculator().run()
