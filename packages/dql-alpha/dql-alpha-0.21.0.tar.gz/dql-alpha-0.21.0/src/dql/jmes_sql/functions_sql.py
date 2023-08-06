from jmespath import exceptions
from jmespath.functions import Functions, signature

from dql.jmes_sql.field_ops import FieldOps


class FunctionsSql(Functions):
    def __init__(self, transpiler):
        super().__init__()
        self.transpiler = transpiler

    def call_function(self, function_name, resolved_args):
        try:
            spec = self.FUNCTION_TABLE[function_name]
        except KeyError:
            raise exceptions.UnknownFunctionError(
                "Unknown function: %s()" % function_name
            )
        function = spec["function"]
        self._validate_arguments(
            resolved_args,
            spec["signature"],
            function_name,
        )
        return function(self, *resolved_args)

    @signature({"types": ["array", "string"]}, {"types": []})
    def _func_contains(self, subject, search):
        if not subject:
            return f"list_contains({FieldOps.CUST_FIELD}, '{search}')"

        cmd = FieldOps.get_cmd(subject)
        if cmd:
            value = FieldOps.get_cmd(search)
            if not value:
                value = f"'{search}'"
            return f"list_contains({cmd}, {value})"

        field = FieldOps.resolve_filed(subject)
        if field:
            return field + f" LIKE '%{search}%'"

        return f"'{subject}' LIKE '%{search}%'"
