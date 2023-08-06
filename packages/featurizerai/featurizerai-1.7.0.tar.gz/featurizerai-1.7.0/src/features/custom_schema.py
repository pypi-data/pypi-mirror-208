from pyspark.sql.types import IntegerType, StringType, StructField, StructType
class custom_schema:
    def __init__(self, schema_fields):
        self.schema = self.generate_schema(schema_fields)

    def generate_schema(self, schema_fields):
        struct_fields = []

        type_mapping = {
            "integer": IntegerType,
            "string": StringType
        }

        for field in schema_fields:
            field_name = field.get("key")
            field_type = field.get("type")
            field_nullable = field.get("nullable", True)
            field_aggregation = field.get("aggregation", None)
            field_desc = field.get("name", None)

            if field_name and field_type in type_mapping:
                struct_field = StructField(
                    field_name, type_mapping[field_type](), field_nullable, metadata={"aggregation": field_aggregation, "name": field_desc}
                )
                struct_fields.append(struct_field)

        return StructType(struct_fields)
