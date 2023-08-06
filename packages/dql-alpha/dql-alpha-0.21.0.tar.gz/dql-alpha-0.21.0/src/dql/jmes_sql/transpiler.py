import jmespath
from jmespath.visitor import Options, TreeInterpreter

from dql.jmes_sql.field_ops import FieldOps
from dql.jmes_sql.functions_sql import FunctionsSql


class Transpiler(TreeInterpreter):
    COMPARATOR_FUNC = {
        "eq": FieldOps.equals,
        "ne": FieldOps.not_equals,
        "lt": FieldOps.op_lt,
        "gt": FieldOps.op_gt,
        "lte": FieldOps.op_le,
        "gte": FieldOps.op_ge,
    }

    def __init__(self, table, json_column, all_columns):
        self.original_table = table
        self.json_column = json_column
        self.all_columns = all_columns

        super().__init__(options=Options(custom_functions=FunctionsSql(self)))

        self._views = []
        self._views_counter = 0
        self._last_view_name = json_column

    @staticmethod
    def execute_query(con, query, table, json_column, all_columns):
        sql = Transpiler.build_sql(query, table, json_column, all_columns)
        return con.executescript(sql)

    @staticmethod
    def build_sql(query, table, json_column, all_columns):
        ts = Transpiler(table, json_column, all_columns)
        sql, view_name = ts.translate(query)
        q = f"""
            {sql}

            SELECT *
            FROM {view_name}
        """
        return q

    def default_visit(self, node, *args, **kwargs):
        raise NotImplementedError("default_visit")

    @property
    def all_columns_in_sql(self):
        return ", ".join(self.all_columns)

    def _append_condition_view(self, condition):
        new_view_name = f"V{self._views_counter}"
        self._views.append(
            f"""
            CREATE TEMP VIEW {new_view_name} AS
            SELECT * FROM '{self._last_view_name}'
            {'WHERE ' + condition if condition else ''};
        """
        )

        self._last_view_name = new_view_name
        self._views_counter += 1

    def _append_initial_view(self):
        new_view_name = f"V{self._views_counter}"
        self._views.append(
            f"""
            CREATE TEMP VIEW {new_view_name} AS
            SELECT {self.all_columns_in_sql},
                   {self.json_column} AS {FieldOps.CUST_FIELD}
            FROM '{self.original_table}'
        """
        )

        self._views.append("""DROP MACRO IF EXISTS PROJECT""")
        self._views.append(
            """
            CREATE MACRO PROJECT(arr, field) AS
                list_transform(from_json(arr, '["json"]'),
                               x -> json_extract_string(json(x), field))
        """
        )

        self._last_view_name = new_view_name
        self._views_counter += 1

    def _append_cust_field_view(self, cust_field):
        new_view_name = f"V{self._views_counter}"
        self._views.append(
            f"""
            CREATE TEMP VIEW {new_view_name} AS
            SELECT {self.all_columns_in_sql},
                   {cust_field} AS {FieldOps.CUST_FIELD}
            FROM '{self._last_view_name}'
        """
        )

        self._last_view_name = new_view_name
        self._views_counter += 1

    def _append_final_view(self):
        new_view_name = f"V{self._views_counter}"
        self._views.append(
            f"""
            CREATE TEMP VIEW {new_view_name} AS
            SELECT {self.all_columns_in_sql}
            FROM '{self._last_view_name}'
            WHERE {FieldOps.CUST_FIELD}
        """
        )

        self._last_view_name = new_view_name
        self._views_counter += 1

    def translate(self, query):
        self._append_initial_view()

        tree = jmespath.compile(query).parsed
        result = self.visit(tree, "")

        self._append_cust_field_view(result)
        self._append_final_view()

        prepare_views = ";".join(self._views) + ";"

        return prepare_views, self._last_view_name

    def visit_field(self, node, value):
        try:
            node_value = node["value"]

            field = FieldOps.get_field_name(value)
            if field:
                return f"{value}->>'{node_value}'"

            return FieldOps.str_to_filed(node_value)
        except AttributeError:
            return None

    def visit_function_expression(self, node, value):
        resolved_args = []
        for child in node["children"]:
            current = self.visit(child, value)
            resolved_args.append(current)
        return self._functions.call_function(node["value"], resolved_args)

    def visit_index(self, node, value):
        return value + "->>" + str(node["value"])

    def visit_projection(self, node, value):
        base = self.visit(node["children"][0], value)
        field = FieldOps.resolve_filed(base)
        if not field:
            return TreeInterpreter.visit_projection(self, node, value)

        curr = self.visit(node["children"][1], "")
        curr_field_name = FieldOps.get_field_name(curr)

        return f"{FieldOps.CMD_PREFIX}PROJECT({field}, {curr_field_name})"
