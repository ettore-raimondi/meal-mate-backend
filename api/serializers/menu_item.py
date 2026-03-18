from api.models import MenuItem
from rest_framework import serializers


class MenuItemListSerializer(serializers.ListSerializer):
    def update(self, queryset, validated_data):
        restaurant = self.context.get("restaurant")
        item_map = {item.id: item for item in queryset}
        updated_items = []

        for item_data in validated_data:
            item_id = item_data.get("id")
            if item_id and item_id in item_map:
                instance = item_map[item_id]
                for attr, value in item_data.items():
                    if attr in {"id", "restaurant_id"}:
                        continue
                    setattr(instance, attr, value)
                instance.save()
                updated_items.append(instance)
            else:
                if not restaurant:
                    raise serializers.ValidationError(
                        "Restaurant context is required to create menu items.",
                    )
                create_payload = {key: value for key, value in item_data.items() if key != "id"}
                new_item = MenuItem.objects.create(restaurant=restaurant, **create_payload)
                updated_items.append(new_item)

        return updated_items


class MenuItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = MenuItem
        list_serializer_class = MenuItemListSerializer
        fields = ["id", "name", "description", "price", "restaurant_id"]
        extra_kwargs = {
            "restaurant_id": {"read_only": True},
        }