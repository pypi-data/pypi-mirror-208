"""
Generic Views
"""
from flask.views import MethodView
from ms_utils import ViewGeneralMethods


class GenericItemCrud(MethodView):
    """
    Generic Crud Class
    """
    init_every_request = False
    db = None
    model = None
    validator = None
    schema = None

    def __init__(self, db, model, validator, schema):
        self.db = db
        self.model = model
        self.validator = validator
        self.schema = schema
        ViewGeneralMethods.db = db

    def get(self, object_id):
        """
        Component Type details
        :param object_id:
        :return:
        """
        return ViewGeneralMethods().generic_details(self.model, self.schema, object_id)

    def patch(self, object_id):
        """
        Component Type update
        :param object_id:
        :return:
        """
        return ViewGeneralMethods().generic_update_or_create(self.model, self.validator, object_id)

    def delete(self, object_id):
        """
        Component Type update
        :param object_id:
        :return:
        """
        return ViewGeneralMethods().generic_delete(self.model, object_id)


class GenericGroupCrud(MethodView):
    """
    Generic Crud Class
    """
    init_every_request = False
    model = None
    validator = None
    schema = None

    def __init__(self, db, model, validator, schema):
        self.db = db
        self.model = model
        self.validator = validator
        self.schema = schema
        ViewGeneralMethods.db = db

    vmg = ViewGeneralMethods()

    # Component Type
    def get(self):
        """
        Component type list
        :return: jsonify
        """
        return ViewGeneralMethods().generic_list(self.model, self.schema)

    def post(self):
        """
        Create component type
        :return: jsonfy
        """
        return ViewGeneralMethods().generic_update_or_create(self.model, self.validator)


def register_api(app, db, model, name, schema, post_validator, path_validator):
    """
    Register API method
    :param schema:
    :param post_validator:
    :param path_validator:
    :param app:
    :param db:
    :param model:
    :param name:
    :return:
    """
    item = GenericItemCrud.as_view(f"{name}-item", db, model, path_validator, schema)
    group = GenericGroupCrud.as_view(f"{name}-group", db, model, post_validator, schema)
    app.add_url_rule(f"/{name}/<int:object_id>", view_func=item)
    app.add_url_rule(f"/{name}/", view_func=group)
