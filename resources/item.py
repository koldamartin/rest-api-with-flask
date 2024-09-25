
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

from db import db
from schemas import PlainItemSchema, ItemUpdateSchema, ItemSchema
from models import ItemModel

blp = Blueprint("Items", __name__, description="Operations on items")


class Item(MethodView):
    @blp.route("/item", methods=["GET"])
    @blp.response(200, ItemSchema(many=True))
    def get_all_items(self):
        return ItemModel.query.all()

    @jwt_required()
    @blp.route("/item/<int:item_id>", methods=["GET"])
    @blp.response(200, ItemSchema)
    def get_item(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required(fresh=True)  # Use fresh tokens for important operations, other operations could use non-fresh tokens
    @blp.route("/item", methods=["POST"])
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def create_item(self, item_data):

        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item")
        return item

    @blp.route("/item/<int:item_id>", methods=["PUT"])
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def update_item(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(item_id, **item_data)
        db.add(item)
        db.session.commit()
        raise NotImplementedError("Updating an item is not implemented/")

    @jwt_required()
    @blp.route("/item/<int:item_id>", methods=["DELETE"])
    def delete_item(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        raise {"message": "Item deleted"}
