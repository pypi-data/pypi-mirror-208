from starkcore.utils.resource import Resource
from ..utils import rest


class IssuingBalance(Resource):
    """# IssuingBalance object
    The IssuingBalance object displays the current issuing balance of the Workspace,
    which is the result of the sum of all transactions within this
    Workspace. The balance is never generated by the user, but it
    can be retrieved to see the available information.
    ## Attributes (return-only):
    - id [string]: unique id returned when IssuingBalance is created. ex: "5656565656565656"
    - amount [integer]: current balance amount of the Workspace in cents. ex: 200 (= R$ 2.00)
    - currency [string]: currency of the current Workspace. Expect others to be added eventually. ex: "BRL"
    - updated [datetime.datetime]: latest update datetime for the IssuingBalance. ex: datetime.datetime(2020, 3, 10, 10, 30, 0, 0)
    """

    def __init__(self, id, amount, currency, updated):
        Resource.__init__(self, id=id)

        self.amount = amount
        self.currency = currency
        self.updated = updated


_resource = {"class": IssuingBalance, "name": "IssuingBalance"}


def get(user=None):
    """# Retrieve the IssuingBalance object
    Receive the IssuingBalance object linked to your Workspace in the Stark Infra API
    ## Parameters (optional):
    - user [Organization/Project object, default None]: Organization or Project object. Not necessary if starkinfra.user was set before function call.
    ## Return:
    - IssuingBalance object with updated attributes
    """
    return next(rest.get_stream(resource=_resource, user=user))
