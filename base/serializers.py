from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Serializador personalizado para especificar quais campos ou quais campos
    não devem ser incluídos no retorno do serializer
    Ex: serializer = ProdutorSerializer(fields=["nome", "cnpj"])
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        exclude_fields = kwargs.pop("exclude_fields", None)
        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif exclude_fields:
            not_allowed = set(exclude_fields)
            for field_name in not_allowed:
                self.fields.pop(field_name)
