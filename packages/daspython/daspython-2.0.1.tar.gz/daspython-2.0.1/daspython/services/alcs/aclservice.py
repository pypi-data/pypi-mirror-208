from daspython.common.api import ApiMethods, Token

class ChangeOwnershipRequest():
    attributeId: int
    entryId: str
    newOwnerId: int

class AclService(ApiMethods):

    def __init__(self, auth: Token):
        super().__init__(auth)

    def ChangeOwnership(self, request: ChangeOwnershipRequest) -> bool:
        api_url = '/api/services/app/Entry/UpdateEntryOwnership'       
        response = self.put_data(url=api_url, body=request)
        return response.get('success')