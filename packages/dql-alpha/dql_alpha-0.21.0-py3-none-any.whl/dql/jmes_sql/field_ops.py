from jmespath.visitor import TreeInterpreter

COMPARATOR_FUNC = TreeInterpreter.COMPARATOR_FUNC


class FieldOps:
    CUST_FIELD = "_cust"
    FIELD_PREFIX = "::"
    CMD_PREFIX = "##"

    @staticmethod
    def resolve_filed(name):
        field = FieldOps.get_field_name(name)
        if not field:
            return None
        return FieldOps.CUST_FIELD + "->>" + field

    @staticmethod
    def _gen_op(x, y, op, op_not_sql):
        x_field = FieldOps.resolve_filed(x)
        y_field = FieldOps.resolve_filed(y)

        if not x_field and not y_field:
            return op_not_sql(x, y)

        left = FieldOps.json_to_sql(x_field) if x_field else FieldOps.constant_to_sql(x)
        right = (
            FieldOps.json_to_sql(y_field) if y_field else FieldOps.constant_to_sql(y)
        )

        return f"({left}) {op} ({right})"

    @staticmethod
    def constant_to_sql(x):
        return "'" + x + "'" if isinstance(x, str) else x

    @staticmethod
    def equals(x, y):
        return FieldOps._gen_op(x, y, "==", COMPARATOR_FUNC["eq"])

    @staticmethod
    def not_equals(x, y):
        return FieldOps._gen_op(x, y, "!=", COMPARATOR_FUNC["ne"])

    @staticmethod
    def op_lt(x, y):
        return FieldOps._gen_op(x, y, "<", COMPARATOR_FUNC["lt"])

    @staticmethod
    def op_le(x, y):
        return FieldOps._gen_op(x, y, "<=", COMPARATOR_FUNC["le"])

    @staticmethod
    def op_gt(x, y):
        return FieldOps._gen_op(x, y, ">", COMPARATOR_FUNC["gt"])

    @staticmethod
    def op_ge(x, y):
        return FieldOps._gen_op(x, y, ">=", COMPARATOR_FUNC["ge"])

    @staticmethod
    def get_field_name(value):
        if type(value) in (int, float):
            return None
        if not value.startswith(FieldOps.FIELD_PREFIX):
            return None
        return value[len(FieldOps.FIELD_PREFIX) :]

    @staticmethod
    def get_cmd(value):
        if not value.startswith(FieldOps.CMD_PREFIX):
            return None
        return value[len(FieldOps.CMD_PREFIX) :]

    @staticmethod
    def str_to_filed(value):
        return FieldOps.FIELD_PREFIX + "'" + value + "'"

    @staticmethod
    def json_to_sql(x_field):
        head, tail = x_field.rsplit("->>", 1)
        return "->>".join([head, tail])
