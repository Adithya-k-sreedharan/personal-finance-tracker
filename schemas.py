from marshmallow import Schema, fields, validate

class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    date = fields.Date(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=255))
    created_at = fields.DateTime(dump_only=True)

class MonthlyLimitSchema(Schema):
    id = fields.Int(dump_only=True)
    limit_amount = fields.Float(required=True, validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# Schema instances
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
monthly_limit_schema = MonthlyLimitSchema()
monthly_limits_schema = MonthlyLimitSchema(many=True)
