class ExitComponent:
    def __init__(self, backend_id, component_id):
        self.backend_id = backend_id
        self.component_id = component_id

    def __str__(self):
        return str(self.component_id)


class ExitForeignAppComponent:
    def __init__(self, backend_id, foreign_app_id):
        self.backend_id = backend_id
        self.foreign_app_id = foreign_app_id

    def __str__(self):
        return f"A{self.foreign_app_id}"


class ExitFederatedAppComponent:
    def __init__(self, backend_id, federated_app_id, federated_account_guid):
        self.backend_id = backend_id
        self.federated_app_id = federated_app_id
        self.federated_account_guid = federated_account_guid

    def __str__(self):
        return f"Ex{self.federated_account_guid}:{self.federated_app_id}"


class UnresolvedExitComponent:
    def __init__(self, backend_id):
        self.backend_id = backend_id

    def __str__(self):
        return f"{{[UNRESOLVED][{self.backend_id}]}}"
