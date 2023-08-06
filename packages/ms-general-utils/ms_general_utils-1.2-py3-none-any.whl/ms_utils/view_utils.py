"""
View Utils
"""
from flask_marshmallow import Marshmallow

from ms_utils import prepare_json_response, PaginationSchema
from flask import current_app, request

from .model_utils import generic_get_serialize_data
from .validation_utils import validate_generic_form


class ViewGeneralMethods:
    """
    View generic Methods
    """
    ma = Marshmallow()
    db = None

    def __int__(self, ma, app, db):
        self.db = db
        self.ma = ma
        self.ma.init_app(app)

    def generic_list(self, model, schema, **kwargs):
        """
        Generic list
        :return: jsonify
        """
        page = int(request.args.get('page')) if request.args.get('page') else 1
        per_page = int(request.args.get('per_page')) if request.args.get('per_page') else 10

        query = model.query.filter_by(**kwargs) \
            .paginate(page=page, per_page=per_page) if request.args.get(
            'q') else model.query.paginate(page=page, per_page=per_page)
        query.items = generic_get_serialize_data(schema(many=True), query.items)
        data = generic_get_serialize_data(
            PaginationSchema(self.ma, current_app, schema(many=True)).pagination_sub_class, query)

        return prepare_json_response(f'{model.__name__} get successfully', data=data)

    def generic_update_or_create(self, model, validation_class, object_id=None):
        """
        Generic method for create or update provider
        :param validation_class:
        :param model:
        :param object_id:
        :return: jsonify
        """
        errors = validate_generic_form(validation_class)
        if errors is not None:
            return errors
        action_text = 'created'
        try:
            data = request.json
            if object_id is None:
                self.generic_create(model, data)
            else:
                action_text = 'updated'
                model_object = model.query.get_or_404(object_id)
                self.generic_update(model_object, data)
            self.db.session.commit()
        except ValueError:
            self.db.session.rollback()
            return prepare_json_response(f'{model.__name__} can not be {action_text} successfully', False, code=400)
        return prepare_json_response(f'{model.__name__} {action_text} successfully')

    def generic_create(self, model, data):
        """
        Generic Create method
        :param model:
        :param data:
        :return:
        """
        model_object = model(**data)
        self.db.session.add(model_object)

    @staticmethod
    def generic_update(model_object, data):
        """
        Generic Update method
        :param data:
        :param model_object:
        :return:
        """
        model_object.query.filter_by(id=model_object.id).update(data)

    def generic_details(self, model, schema, object_id):
        """
        Generic details method
        :param schema:
        :param model:
        :param object_id:
        :return:
        """
        model_object = self.db.get_or_404(model, object_id)
        return prepare_json_response(f'{model.__name__} get successfully',
                                     data=generic_get_serialize_data(schema(), model_object))

    def generic_delete(self, model, object_id):
        """
        Generic delete method
        :param model:
        :param object_id:
        :return:
        """
        model_object = self.db.get_or_404(model, object_id)
        model_object.delete()
        return prepare_json_response(f'{model.__name__} deleted successfully!')

    def generic_change_boolean(self, model, object_id, field):
        """
        Generic change boolean method
        :param model:
        :param object_id:
        :param field:
        :return:
        """
        model_object = self.db.get_or_404(model, object_id)
        model.query.filter_by(id=object_id).update({field: not getattr(model_object, field)})
        self.db.session.commit()
        return prepare_json_response(
            f'{model.__name__} field {field} updated to {getattr(model_object, field)} successfully!')
