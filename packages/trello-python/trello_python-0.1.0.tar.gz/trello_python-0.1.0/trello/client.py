from urllib.parse import urlencode

import requests

from trello.exceptions import UnauthorizedError, WrongFormatInputError, ContactsLimitExceededError


class Client(object):
    URL = "https://api.trello.com/1/"
    AUTH_URL = "https://trello.com/1/authorize?"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, api_key, token=None):
        self.key = api_key
        self.token = token

    def authorization_url(self, return_url, state=None):
        if state:
            return_url = f"{return_url}?state={state}"
        params = {
            "expiration": "never",
            "return_url": return_url,
            "name": "NewToken",
            "scope": "read,write,account",
            "response_type": "token",
            "key": self.key,
        }
        return self.AUTH_URL + urlencode(params)

    def set_token(self, token):
        self.token = token
        return True

    def get_current_user(self):
        """
        Use this function to get user's id, you will need it to access some other endpoints.
        """
        return self.get("members/me/")

    def get_workspaces(self, member_id, filter: str = None, fields: str = None, paid_account: bool = None):
        """
        filter = One of: all, members, none, public (Note: members filters to only private Workspaces) \n
        fields = all or a comma-separated list of organization fields \n
        paid_accounts = Whether or not to include paid account information in the returned workspace object
        """
        args = locals()
        params = self.set_request_params(args)
        return self.get(f"members/{member_id}/organizations", params=params)

    def get_members(self, organization_id):
        return self.get(f"organizations/{organization_id}/members")

    def get_boards(self, workspace_id, filter: str = None, fields: str = None):
        """
        filter = One of: all, members, none, public (Note: members filters to only private Workspaces) \n
        fields = all or a comma-separated list of organization fields \n
        """
        args = locals()
        params = self.set_request_params(args)
        return self.get(f"organizations/{workspace_id}/boards", params=params)

    def get_board(self, board_id, fields="all", lists=None):
        args = locals()
        params = self.set_request_params(args)
        return self.get(f"boards/{board_id}", params=params)

    def get_board_lists(self, board_id, cards: str = None, filter: str = None, fields: str = None):
        """
        cards = Valid values: all, closed, none, open \n
        filter = Valid values: all, closed, none, open \n
        fields = all or a comma-separated list of list fields
        """
        args = locals()
        params = self.set_request_params(args)
        return self.get(f"boards/{board_id}/lists", params=params)

    def get_board_labels(self, board_id, limit: int = None):
        """
        limit = default: 50, maximum: 1000
        """
        args = locals()
        params = self.set_request_params(args)
        return self.get(f"boards/{board_id}/labels", params=params)

    def get_cards(self, board_id, limit=None):
        params = {}
        if limit:
            params.update(limit=limit)
        return self.get(f"boards/{board_id}/cards", params=params)

    def create_card(
        self,
        idList,
        name: str = None,
        desc: str = None,
        pos: str = None,
        due: str = None,
        start: str = None,
        dueComplete: bool = None,
        idMembers: str = None,
        idLabels: str = None,
        urlSource: str = None,
    ):
        """
        due, start: these params accept only isoformat dates.
        idMembers, idLabels: string with a list of ids separated by commas.
        """
        args = locals()
        params = self.set_request_params(args)
        return self.post("cards", params=params)

    def add_label_to_card(self, card_id, label_id):
        params = {"value": label_id}
        return self.post(f"cards/{card_id}/idLabels", params=params)

    def add_comment_to_card(self, card_id, comment: str):
        params = {"text": comment}
        return self.post(f"cards/{card_id}/actions/comments", params=params)

    def get_card_customfields(self, card_id):
        return self.get(f"cards/{card_id}/customFieldItems")

    def get_card_actions(self, card_id, action_type: str = None, page: int = None):
        """
        filter = A comma-separated list of action types. Default: commentCard
        """
        params = {}
        if action_type:
            params.update({"filter": action_type})
        if page:
            params.update({"page": page})
        return self.get(f"cards/{card_id}/actions", params=params)

    def get_card_checklists(self, card_id, fields: str = None):
        """
        fields = all or a comma-separated list of: idBoard,idCard,name,pos
        """
        params = {}
        if fields:
            params.update({"fields": fields})
        return self.get(f"cards/{card_id}/checklists", params=params)

    def add_item_to_checklist(
        self,
        checklist_id,
        name: str,
        pos: str = None,
        checked: bool = None,
        due: str = None,
        dueReminder: str = None,
        idMember: str = None,
    ):
        args = locals()
        params = self.set_request_params(args)
        return self.post(f"checklists/{checklist_id}/checkItems", params=params)

    def create_label(self, board_id, name, color: str = None):
        params = {"idBoard": board_id, "name": name}
        if color:
            params.update(color=color)
        return self.post("labels/", params=params)

    def get_token_webhooks(self):
        return self.get(f"tokens/{self.token}/webhooks")

    def create_webhook(self, idModel: str, callbackURL: str, description: str = None, active: bool = True):
        args = locals()
        params = self.set_request_params(args)
        return self.post(f"webhooks/", params=params)

    def delete_webhook(self, webhook_id):
        return self.delete(f"webhooks/{webhook_id}")

    def search(self, query, modelTypes: str = None, partial=None):
        args = locals()
        params = self.set_request_params(args)
        return self.get(f"search/", params=params)

    def get_customfield(self, customfield_id):
        return self.get(f"customFields/{customfield_id}")

    def get(self, endpoint, **kwargs):
        response = self.request("GET", endpoint, **kwargs)
        return self.parse(response)

    def post(self, endpoint, **kwargs):
        response = self.request("POST", endpoint, **kwargs)
        return self.parse(response)

    def delete(self, endpoint, **kwargs):
        response = self.request("DELETE", endpoint, **kwargs)
        return self.parse(response)

    def put(self, endpoint, **kwargs):
        response = self.request("PUT", endpoint, **kwargs)
        return self.parse(response)

    def patch(self, endpoint, **kwargs):
        response = self.request("PATCH", endpoint, **kwargs)
        return self.parse(response)

    def request(self, method, endpoint, headers=None, params=None, **kwargs):
        if headers:
            self.headers.update(headers)
        self.params = {"key": self.key, "token": self.token}
        if params:
            self.params.update(params)
        return requests.request(method, self.URL + endpoint, headers=self.headers, params=self.params, **kwargs)

    def parse(self, response):
        status_code = response.status_code
        if "Content-Type" in response.headers and "application/json" in response.headers["Content-Type"]:
            try:
                r = response.json()
            except ValueError:
                r = response.text
        else:
            r = response.text
        if status_code == 200:
            return r
        if status_code == 204:
            return None
        if status_code == 400:
            raise WrongFormatInputError(r)
        if status_code == 401:
            raise UnauthorizedError(r)
        if status_code == 406:
            raise ContactsLimitExceededError(r)
        if status_code == 500:
            raise Exception
        return r

    def set_request_params(self, args):
        params = {}
        for arg in args:
            if args[arg] is not None and arg != "self":
                params.update({f"{arg}": args[arg]})
        return params
