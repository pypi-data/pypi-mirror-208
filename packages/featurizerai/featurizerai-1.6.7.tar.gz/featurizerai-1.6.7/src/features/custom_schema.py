from pyspark.sql.types import *


class custom_schema:
    def __init__(self, schema_fields):
        self.schema = self.generate_schema(schema_fields)

    def generate_schema(self, schema_fields):
        struct_fields = []

        type_mapping = {
            "integer": IntegerType,
            "string": StringType,
            "float": FloatType,
            "double": DoubleType,
            "boolean": BooleanType,
            "date": DateType,
            "timestamp": TimestampType,
            "array": ArrayType,
            "map": MapType,
            "struct": StructType
        }

        for field in schema_fields:
            field_name = field.get("name")
            field_key = field.get("key")
            field_type = field.get("type")
            field_nullable = field.get("nullable", True)
            field_aggregation = field.get("aggregation", None)

            if field_name and field_type in type_mapping:
                struct_field = StructField(
                    field_name,
                    type_mapping[field_type](),
                    field_nullable,
                    metadata={"aggregation": field_aggregation, "key": field_key}  # add "key" to metadata
                )
                struct_fields.append(struct_field)

        return StructType(struct_fields)
