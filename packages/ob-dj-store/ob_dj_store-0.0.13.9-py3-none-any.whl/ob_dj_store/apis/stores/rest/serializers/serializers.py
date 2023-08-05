import calendar
import typing
from datetime import time, timedelta

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from django.utils.timezone import localtime, now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from config import settings as store_settings
from ob_dj_store.core.stores.models import (
    Attribute,
    AttributeChoice,
    AvailabilityHours,
    Cart,
    CartItem,
    Category,
    Favorite,
    FavoriteExtra,
    Feedback,
    FeedbackAttribute,
    FeedbackConfig,
    OpeningHours,
    Order,
    OrderHistory,
    OrderItem,
    Payment,
    PaymentMethod,
    PhoneContact,
    Product,
    ProductAttribute,
    ProductMedia,
    ProductTag,
    ProductVariant,
    ShippingMethod,
    Store,
    Tax,
    Wallet,
    WalletMedia,
    WalletTransaction,
)
from ob_dj_store.core.stores.models._inventory import Inventory
from ob_dj_store.core.stores.utils import distance


class AttributeChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeChoice
        fields = (
            "id",
            "name",
            "price",
            "label",
            "is_default",
        )


class AttributeSerializer(serializers.ModelSerializer):
    attribute_choices = AttributeChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = (
            "id",
            "name",
            "attribute_choices",
        )


class InventoryValidationMixin:
    def validate(self, attrs: typing.Dict) -> typing.Dict:
        validated_data = super().validate(attrs)
        inventory = None
        try:
            inventory = validated_data["product_variant"].inventories.get(
                store=validated_data["store"]
            )
        except:
            raise serializers.ValidationError(_("Product has no inventory"))
        if validated_data["quantity"] < 1:
            raise serializers.ValidationError(_("Quantity must be greater than 0."))
        # validate quantity in inventory
        if not inventory.is_uncountable:
            stock_quantity = inventory.quantity
            if validated_data["quantity"] > stock_quantity:
                raise serializers.ValidationError(
                    _("Quantity is greater than the stock quantity.")
                )
        return validated_data


class OpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = "__all__"


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = "__all__"


class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = (
            "id",
            "order",
            "status",
            "created_at",
        )


class OrderItemSerializer(InventoryValidationMixin, serializers.ModelSerializer):
    store = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_variant",
            "quantity",
            "store",
            "total_amount",
            "preparation_time",
            "notes",
            "attribute_choices",
            "attribute_choices_total_amount",
        )

    def create(self, validated_data):
        validated_data.pop("store")
        return super().create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["attribute_choices"] = AttributeChoiceSerializer(
            instance.attribute_choices.all(), many=True
        ).data

        return representation


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    history = OrderHistorySerializer(many=True, read_only=True)
    estimated_timeline = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "store",
            "shipping_method",
            "payment_method",
            "shipping_address",
            "customer",
            "type_of_order",
            "status",
            "items",
            "total_amount",
            "preparation_time",
            "estimated_timeline",
            "history",
            "car_id",
            "pickup_time",
            "extra_infos",
            "created_at",
            "updated_at",
            "store_name",
        )
        extra_kwargs = {
            "customer": {"read_only": True},
            "store": {"read_only": True, "required": False},
            "type_of_order": {"read_only": True, "required": False},
        }

    def get_estimated_timeline(self, obj):
        timeline = {
            "pending": obj.created_at,
            "received": None,
            "order_ready": None,
            "delivering": None,
            "ready": None,
        }
        payment = obj.payments.all().first()
        if not payment:
            return timeline
        if payment.payment_post_at:
            timeline["received"] = payment.payment_post_at
            timeline["order_ready"] = payment.payment_post_at + timedelta(
                minutes=obj.preparation_time
            )
            if not obj.is_scheduled_for_pickup and obj.shipping_method:
                timeline["delivering"] = timeline["order_ready"] + timedelta(
                    minutes=store_settings.ESTIMATED_DELIVERING_TIME
                )
            timeline["ready"] = timeline["delivering"] or timeline["order_ready"]
        return timeline

    def get_store_name(self, obj):
        return obj.store.name if obj.store else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def _get_store(self):
        store_pk = self.context["view"].kwargs["store_pk"]
        try:
            store = Store.objects.get(pk=store_pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_("Store does not exist!"))
        return store

    def validate(self, attrs):
        user = self.context["request"].user
        attrs["store"] = self._get_store()
        if not "extra_infos" in attrs:
            attrs["extra_infos"] = {}
        stores = Store.objects.filter(store_items__cart=user.cart).distinct()
        if not store_settings.DIFFERENT_STORE_ORDERING and len(stores) > 1:
            raise ValidationError(_("You cannot order from different stores"))
        gift_details = attrs["extra_infos"].get("gift_details", None)
        if gift_details:
            errors = []
            for key in settings.DIGITAL_PRODUCTS_REQUIRED_KEYS:
                if not (key in gift_details.keys() and len(str(gift_details.get(key)))):
                    errors.append({key: "This field should be filled."})
            if len(errors) > 0:
                raise serializers.ValidationError(errors)
            try:
                product = Product.objects.get(id=gift_details["digital_product"])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(_("Digital product does not exist!"))
            if product.type == Product.ProductTypes.PHYSICAL:
                raise serializers.ValidationError(
                    _("You must not fill extra infos for physical products.")
                )
        # The Cart items must not be empty
        elif not user.cart.items.exists():
            raise serializers.ValidationError(_("The Cart must not be empty"))

        if "pickup_time" in attrs:
            if attrs["pickup_time"]:
                # validate that the pickup_time is always in the future
                if attrs["pickup_time"] < localtime(now()):
                    raise serializers.ValidationError(
                        _("Pickup time must be in the future")
                    )
                # validate that the pickup_time is part of day (between 00:00 and 23:59)
                if not (
                    attrs["pickup_time"].time() >= time(hour=0, minute=0)
                    and attrs["pickup_time"].time() <= time(hour=23, minute=59)
                ):
                    raise serializers.ValidationError(
                        _("Pickup time must be part of day")
                    )
                # validate that the pickup_time is between store's opening hours and closing hours
                if (
                    attrs["store"]
                    .opening_hours.filter(weekday=attrs["pickup_time"].weekday() + 1)
                    .exists()
                ) and (
                    attrs["pickup_time"].hour
                    > (
                        attrs["store"]
                        .opening_hours.filter(
                            weekday=attrs["pickup_time"].weekday() + 1
                        )
                        .first()
                        .to_hour.hour
                    )
                    or attrs["pickup_time"].hour
                    < (
                        attrs["store"]
                        .opening_hours.filter(
                            weekday=attrs["pickup_time"].weekday() + 1
                        )
                        .first()
                        .from_hour.hour
                    )
                ):
                    raise serializers.ValidationError(
                        _("Pickup time must be between store's opening hours")
                    )
        payment_method = attrs.get("payment_method")
        if payment_method:
            if payment_method.payment_provider == store_settings.WALLET:
                try:
                    wallet = user.wallets.get(currency=attrs["store"].currency)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(
                        {
                            "wallet": _(
                                "The currency of our store is not compatible with your wallet. Please checkout with products using different currency"
                            )
                        }
                    )

                if gift_details:
                    amount = gift_details["price"]
                else:
                    amount = user.cart.total_price
                if wallet.balance < amount:
                    raise serializers.ValidationError(
                        {"wallet": _("Insufficient Funds")},
                    )
            elif payment_method.payment_provider == store_settings.GIFT:
                if not attrs["extra_infos"].get("gift_card", None):
                    raise serializers.ValidationError(
                        {"gift": _("The Gift card is missing")}
                    )

        return super().validate(attrs)

    def perform_payment(self, amount, payment_method, order_store, orders):
        from ob_dj_store.core.stores.gateway.tap.utils import TapException

        try:
            payment = Payment.objects.create(
                user=self.context["request"].user,
                amount=amount,
                method=payment_method,
                currency=order_store.currency,
                orders=orders,
            )
        except ValidationError as err:
            raise serializers.ValidationError(detail=err.message_dict)
        except TapException as err:
            raise serializers.ValidationError({"tap": _(str(err))})
        return {
            "orders": orders,
            "payment_url": payment.payment_url,
        }

    def create(self, validated_data: typing.Dict):
        user = self.context["request"].user
        orders = []
        order_store = validated_data["store"]
        gift_details = validated_data["extra_infos"].get("gift_details", None)
        if gift_details:
            amount = gift_details["price"]
            order = Order.objects.create(customer=user, **validated_data)
            orders.append(order)
        else:
            cart = user.cart
            amount = cart.total_price
            stores = Store.objects.filter(store_items__cart=cart).distinct()
            orders = []
            validated_data.pop("store")
            for store in stores:
                order = Order.objects.create(
                    store=store, customer=cart.customer, **validated_data
                )
                items = store.store_items.filter(cart=cart)
                for item in items:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product_variant=item.product_variant,
                        quantity=item.quantity,
                    )
                    order_item.attribute_choices.set(item.attribute_choices.all())
                orders.append(order)
        payment_method = validated_data.get("payment_method")
        return self.perform_payment(
            amount=amount,
            payment_method=payment_method,
            order_store=order_store,
            orders=orders,
        )


class CreateOrderResponseSerializer(serializers.Serializer):
    orders = OrderSerializer(many=True, read_only=True)
    payment_url = serializers.CharField(read_only=True)
    extra_infos = serializers.JSONField(
        required=False,
        help_text=f"""
                gift_details :  {",".join(settings.DIGITAL_PRODUCTS_REQUIRED_KEYS)}  \n
                gift_card : the id of the gift_card

                    """,
    )
    car_id = serializers.IntegerField(required=False)

    # write only fields
    shipping_method = serializers.IntegerField(write_only=True, required=False)
    payment_method = serializers.IntegerField(write_only=True, required=False)
    shipping_address = serializers.IntegerField(write_only=True, required=False)
    pickup_time = serializers.DateTimeField(write_only=True, required=False)


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = (
            "id",
            "name",
            "text_color",
            "background_color",
        )


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_choices = AttributeChoiceSerializer(many=True)

    class Meta:
        model = ProductAttribute
        fields = (
            "id",
            "name",
            "is_mandatory",
            "attribute_choices",
            "type",
            "label",
            "min",
            "max",
        )


class ProductVariantSerializer(serializers.ModelSerializer):
    product_attributes = ProductAttributeSerializer(many=True)
    is_primary = serializers.SerializerMethodField()
    inventory = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "name",
            "label",
            "sku",
            "product_attributes",
            "is_primary",
            "inventory",
            "image",
            "image_thumbnail_medium",
            "description",
        )
        extra_kwargs = {"image_thumbnail_medium": {"read_only": True}}

    def get_is_primary(self, obj):
        return True if obj.inventories.filter(is_primary=True).exists() else False

    def get_inventory(self, obj):
        inventory = None
        if self.context.get("view"):
            if self.context["view"].kwargs.get("store_pk"):
                store_pk = self.context["view"].kwargs["store_pk"]
                qs = obj.inventories.filter(store=store_pk)
                if qs.exists():
                    inventory = qs.values("price", "discount_percent", "quantity")[0]
        return inventory


class CartItemSerializer(InventoryValidationMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    inventory_quantity = serializers.SerializerMethodField()
    is_uncountable = serializers.SerializerMethodField()
    is_available_in_store = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_variant",
            "product_id",
            "quantity",
            "store",
            "unit_price",
            "total_price",
            "notes",
            "attribute_choices",
            "extra_infos",
            "attribute_choices_total_price",
            "image",
            "inventory_quantity",
            "is_uncountable",
            "is_available_in_store",
            "favorite",
            "is_favorite",
        )
        extra_kwargs = {
            "store": {
                "required": True,
            },
        }

    def get_is_available_in_store(self, obj):
        return True if obj.inventory else False

    def get_product_id(self, obj):
        return obj.product_variant.product.id

    def get_inventory_quantity(self, obj):
        if obj.inventory:
            return obj.inventory.quantity
        return None

    def get_is_uncountable(self, obj):
        if obj.inventory:
            return obj.inventory.is_uncountable
        return None

    def validate(self, attrs: typing.Dict) -> typing.Dict:
        return super(CartItemSerializer, self).validate(attrs)

    def get_image(self, obj):
        qs = ProductMedia.objects.filter(product=obj.product_variant.product)
        if qs:
            return qs.first().image.url
        else:
            return None

    def _get_favorite(self, obj):
        user = self.context["request"].user
        favorites = Favorite.objects.favorites_for_object(
            obj.product_variant.product, user
        )
        customization = [
            obj.product_variant,
        ] + [attribute_choice for attribute_choice in obj.attribute_choices.all()]
        for favorite in favorites:
            content_objects = [
                instance.content_object for instance in favorite.extras.all()
            ]
            if set(customization) == set(content_objects):
                return favorite.id
        return None

    def get_favorite(self, obj) -> int:
        return self.favorite

    def get_is_favorite(self, obj) -> bool:
        return self.favorite is not None

    def to_representation(self, instance: CartItem):
        self.favorite = self._get_favorite(instance)
        data = super().to_representation(instance)
        data["product_variant"] = ProductVariantSerializer(
            instance=instance.product_variant
        ).data
        data["product_name"] = instance.product_variant.product.name
        data["attribute_choices"] = AttributeChoiceSerializer(
            instance.attribute_choices.all(),
            many=True,
        ).data
        return data

    def create(self, validated_data):
        return super().create(**validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = (
            "customer",
            "items",
            "total_price",
            "tax_amount",
            "total_price_with_tax",
        )
        read_only_fields = (
            "id",
            "total_price",
            "tax_amount",
            "total_price_with_tax",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        stores = set([item["store"] for item in attrs["items"]])
        if not store_settings.DIFFERENT_STORE_ORDERING and len(stores) > 1:
            raise ValidationError(_("You cannot order from different stores"))
        return attrs

    def update(self, instance, validated_data):
        instance.items.all().delete()
        # update or create instance items
        for item in validated_data["items"]:
            attribute_choices = item.pop("attribute_choices", None)
            cart_item = CartItem.objects.create(
                cart=instance,
                **item,
            )
            if attribute_choices:
                cart_item.attribute_choices.set(attribute_choices)
            cart_item.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        stores = Store.objects.filter(store_items__cart=instance)
        data["store"] = StoreSerializer(stores, many=True, context=self.context).data
        return data


class ProductMediaSerializer(serializers.ModelSerializer):
    image_thumbnail_medium = serializers.ImageField(read_only=True)
    image_thumbnail_small = serializers.ImageField(read_only=True)

    class Meta:
        model = ProductMedia
        fields = (
            "id",
            "is_primary",
            "image",
            "image_thumbnail_small",
            "image_thumbnail_medium",
            "order_value",
        )


class FavoriteMixin:
    def to_representation(self, instance):
        if self.context.get("request"):
            self.favorites = self._get_favorite_object(instance)
        else:
            self.favorites = []
        return super().to_representation(instance)

    def _get_favorite_object(self, instance):
        user = self.context["request"].user
        qs = Favorite.objects.favorites_for_object(instance, user.id).values_list(
            "id", flat=True
        )
        return qs

    def get_favorites(self, obj):
        return self.favorites


class ProductSerializer(FavoriteMixin, serializers.ModelSerializer):
    product_variants = ProductVariantSerializer(many=True)
    product_images = ProductMediaSerializer(many=True, source="images")
    default_variant = ProductVariantSerializer(read_only=True, many=False)
    favorites = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "product_images",
            "product_variants",
            "default_variant",
            "favorites",
        )

    def to_representation(self, instance: Product):
        data = super().to_representation(instance=instance)
        data["is_favorite"] = len(self.favorites) > 0
        return data


class ProductListSerializer(serializers.ModelSerializer):
    product_images = ProductMediaSerializer(many=True, source="images")

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "product_images",
            "type",
        )


class SubCategorySerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True)
    image_thumbnail_medium = serializers.ImageField(read_only=True)
    image_thumbnail_small = serializers.ImageField(read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "description",
            "is_active",
            "products",
            "image",
            "image_thumbnail_medium",
            "image_thumbnail_small",
            "parent",
            "is_available",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def get_is_available(self, obj) -> bool:
        store_id = self.context["request"].query_params.get("store", None)
        if store_id:
            try:
                current_availability_hours = AvailabilityHours.objects.get(
                    weekday=now().weekday() + 1,
                    store=store_id,
                    category=obj,
                )
                return (
                    current_availability_hours.from_hour
                    <= now().time()
                    <= current_availability_hours.to_hour
                )
            except ObjectDoesNotExist:
                pass
        return False


class CategorySerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True)
    subcategories = SubCategorySerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "description",
            "products",
            "is_active",
            "subcategories",
            "parent",
            "image",
            "image_thumbnail_medium",
            "image_thumbnail_small",
            "is_available",
        )

    def get_is_available(self, obj) -> bool:
        store_id = self.context["request"].query_params.get("store", None)
        if store_id:
            try:
                current_availability_hours = AvailabilityHours.objects.get(
                    weekday=localtime(now()).weekday() + 1,
                    store=store_id,
                    category=obj,
                )
                return (
                    current_availability_hours.from_hour
                    <= localtime(now()).time()
                    <= current_availability_hours.to_hour
                )
            except ObjectDoesNotExist:
                pass
        return False


class FeedbackConfigSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    attribute = serializers.CharField(read_only=True)

    class Meta:
        model = FeedbackConfig
        fields = ("id", "attribute", "attribute_label", "values")


class FeedbackAttributeSerializer(serializers.ModelSerializer):
    config = FeedbackConfigSerializer(many=False, read_only=True)
    attribute = serializers.CharField(write_only=True)

    class Meta:
        model = FeedbackAttribute
        fields = ("attribute", "config", "value", "review")

    # TODO: do we need validations when creating the value


class FeedbackSerializer(serializers.ModelSerializer):
    attributes = FeedbackAttributeSerializer(many=True, required=False)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "attributes",
            "notes",
            "review",
        )

    def validate(self, attrs: typing.Dict):
        # Validate Order Status
        if self.instance.status not in [
            Order.OrderStatus.PAID,
            Order.OrderStatus.CANCELLED,
        ]:
            raise serializers.ValidationError(
                _("The Order must be PAID or CANCELLED to give a feedback")
            )
        return attrs

    def update(self, instance: Order, validated_data: typing.Dict):
        user = self.context["request"].user
        attributes = validated_data.pop("attributes", [])
        feedback = Feedback.objects.create(
            order=self.instance, user=user, **validated_data
        )

        for attr in attributes:
            feedback.attributes.create(**attr)
        feedback.order.save()
        return feedback


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = (
            "id",
            "variant",
            "store",
            "quantity",
            "price",
            "plu",
            "preparation_time",
            "discount_percent",
            "discounted_price",
            "is_primary",
        )

    def to_representation(self, instance):
        data = super(InventorySerializer, self).to_representation(instance)
        data["variant"] = ProductVariantSerializer(instance=instance.variant).data
        return data


class PhoneContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneContact
        fields = (
            "id",
            "national_number",
            "country_code",
            "is_default",
            "is_active",
        )


class StoreSerializer(FavoriteMixin, serializers.ModelSerializer):

    opening_hours = serializers.SerializerMethodField()
    phone_contacts = serializers.SerializerMethodField()
    in_range_delivery = serializers.SerializerMethodField()
    is_closed = serializers.SerializerMethodField()
    favorites = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    address_line = serializers.SerializerMethodField()
    shipping_methods = ShippingMethodSerializer(many=True, read_only=True)
    distance = serializers.SerializerMethodField()
    current_day_opening_hours = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = (
            "id",
            "name",
            "address",
            "address_line",
            "location",
            "distance",
            "is_active",
            "currency",
            "minimum_order_amount",
            "delivery_charges",
            "shipping_methods",
            "min_free_delivery_amount",
            "opening_hours",
            "in_range_delivery",
            "is_closed",
            "favorites",
            "is_favorite",
            "created_at",
            "updated_at",
            "phone_contacts",
            "current_day_opening_hours",
            "image",
            "always_open",
            "busy_mode",
        )
        extra_kwargs = {
            "image": {"read_only": True, "required": False},
        }

    def get_is_closed(self, obj):
        if obj.busy_mode:
            return True
        if obj.always_open:
            return False
        current_time = localtime(now())
        current_op_hour = obj.current_opening_hours
        if current_op_hour:
            return (
                not current_op_hour.from_hour
                <= current_time.time()
                <= current_op_hour.to_hour
            )
        return True

    def get_in_range_delivery(self, obj):
        user_location = self.context["request"].query_params.get("point")
        in_range_method = False
        for shipping_method in obj.shipping_methods.all():
            if shipping_method.type == ShippingMethod.ShippingType.DELIVERY:
                in_range_method = True
                break
        if not in_range_method:
            return True
        if user_location and obj.poly:
            long, lat = user_location.split(",")
            return obj.poly.contains(Point(float(long), float(lat)))

    def get_opening_hours(self, obj):
        if obj.always_open:
            return [
                "Sunday - Monday 00:00AM - 23:59PM",
            ]
        opening_hours = sorted(
            list(obj.opening_hours.all()), key=lambda op_hour: op_hour.weekday
        )
        formatted_hours = []
        if len(opening_hours) > 0:
            day_1 = calendar.day_name[opening_hours[0].weekday - 1]
            day_2 = None
            for i in range(len(opening_hours)):
                if not opening_hours[i] == opening_hours[-1]:
                    if (
                        opening_hours[i].from_hour == opening_hours[i + 1].from_hour
                        and opening_hours[i].to_hour == opening_hours[i + 1].to_hour
                    ):
                        day_2 = calendar.day_name[opening_hours[i + 1].weekday - 1]
                        continue
                formatted_days = day_1
                if day_2:
                    formatted_days = f"{formatted_days} - {day_2}"
                formatted_hours.append(
                    f"{formatted_days} {opening_hours[i].from_hour.strftime('%I:%M%p')} - {opening_hours[i].to_hour.strftime('%I:%M%p')}"
                )
                if not opening_hours[i] == opening_hours[-1]:
                    day_1 = calendar.day_name[opening_hours[i + 1].weekday - 1]
        return formatted_hours

    def get_is_favorite(self, obj):
        return len(self.favorites) > 0

    def get_address_line(self, obj):
        return obj.address.address_line

    def get_distance(self, obj):
        # get the distance between the user location and store location
        user_location = self.context["request"].query_params.get("point")
        if user_location and obj.location:
            unit = "km"
            lat, long = user_location.split(",")
            store_lat, store_long = obj.location.x, obj.location.y
            ds = round(distance((float(lat), float(long)), (store_lat, store_long)), 1)
            if ds < 1:
                ds = int(ds * 1000)
                unit = "m"
            return f"{ds}{unit}"

    def get_phone_contacts(self, obj):
        phone_contacts = obj.phone_contacts.all()
        return PhoneContactSerializer(phone_contacts, many=True).data

    def get_current_day_opening_hours(self, obj):
        if obj.always_open:
            return {
                "from_hour": "00:00AM",
                "to_hour": "23:59PM",
            }
        current_opening_hours = obj.current_opening_hours
        op_hour = {}
        if current_opening_hours:
            op_hour["from_hour"] = current_opening_hours.from_hour.strftime("%I:%M%p")
            op_hour["to_hour"] = current_opening_hours.to_hour.strftime("%I:%M%p")
        else:
            op_hour["from_hour"] = settings.DEFAULT_OPENING_HOURS[0]["from_hour"]
            op_hour["to_hour"] = settings.DEFAULT_OPENING_HOURS[0]["to_hour"]
        return op_hour

    def to_representation(self, instance):
        return super().to_representation(instance)


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = (
            "id",
            "payment_provider",
            "name",
            "description",
        )


class PaymentSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "method", "orders", "amount", "currency", "payment_post_at")


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = (
            "id",
            "rate",
            "name",
            "value",
            "country",
        )


class StoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class GenericSerializer(serializers.Serializer):
    """
    A generic serializer that automatically selects the appropriate serializer
    for a given instance.

    The `to_representation` method uses the `get_serializer_for_instance` method
    to determine which serializer to use for a given instance. If the serializer
    class is found, it returns the representation of the instance using that
    serializer. Otherwise, it raises a `NameError`.
    """

    def to_representation(self, value):
        context = self.context
        serializer_class = self.get_serializer_for_instance(value)
        return serializer_class(context=context).to_representation(value)

    def get_serializer_for_instance(self, instance):
        serializer_class = instance.__class__.__name__
        return import_string(
            store_settings.FAVORITES_SERIALIZERS_PATHS[serializer_class]
        )


def get_favorite_extras_models():
    extras_list = []
    for key, value in settings.FAVORITE_TYPES.items():
        if "extras" in value:
            extras_list.extend(value["extras"].keys())
    return extras_list


class FavoriteExtraSerializer(serializers.ModelSerializer):
    content_object = GenericSerializer(read_only=True)
    object_id = serializers.IntegerField(min_value=1)
    object_type = serializers.ChoiceField(
        write_only=True, choices=get_favorite_extras_models()
    )

    class Meta:
        model = FavoriteExtra
        fields = (
            "id",
            "content_object",
            "object_id",
            "object_type",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        extras = get_favorite_extras_models()
        model_name = instance.content_type.model
        for extra in extras:
            if model_name == extra.lower():
                data["object_type"] = extra
                break
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    content_object = GenericSerializer(read_only=True)
    extras = FavoriteExtraSerializer(many=True)
    object_id = serializers.IntegerField(min_value=1, required=False)
    object_type = serializers.ChoiceField(
        write_only=True,
        choices=list(store_settings.FAVORITE_TYPES.keys()),
        required=False,
    )
    is_available_in_store = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = (
            "id",
            "content_object",
            "extras",
            "object_id",
            "object_type",
            "name",
            "is_available_in_store",
        )
        extra_kwargs = {
            "name": {"required": True},
        }

    def get_is_available_in_store(self, obj):
        store_id = self.context["request"].query_params.get("store")
        type = self.context["request"].query_params.get("type")
        if type == "Product" and store_id:
            content_type = ContentType.objects.get_for_model(ProductVariant)
            try:
                extra = obj.extras.get(content_type=content_type)
                inventory = extra.content_object.inventories.get(store=store_id)
                if inventory.is_uncountable:
                    return True
                return inventory.quantity > 0
            except ObjectDoesNotExist:
                return False
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        model_name = instance.content_type.model
        for favorite in store_settings.FAVORITE_TYPES.keys():
            if model_name == favorite.lower():
                data["object_type"] = favorite
                break
        return data

    def _lookup_validation(self, data):
        content_type = ContentType.objects.get_for_model(data["content_object"])
        queryset = Favorite.objects.filter(
            content_type=content_type,
            object_id=data["content_object"].id,
            user=self.context["request"].user,
        ).prefetch_related("extras")
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            for favorite in queryset:
                content_objects = [
                    instance.content_object for instance in favorite.extras.all()
                ]
                if set(data["extras"]) == set(content_objects):
                    raise serializers.ValidationError(
                        _(f"You cannot favorite the same item twice")
                    )

    def get_object(self, model: models.Model, id: int):
        try:
            object = model.objects.get(pk=id)
            return object
        except model.DoesNotExist:
            raise serializers.ValidationError(
                _(f"{model.__name__} with the id of {id} does not exist")
            )

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        extras_data = {}
        if self.instance is None:
            object_type = validated_data["object_type"]
            object_type_model = import_string(
                store_settings.FAVORITE_TYPES[object_type]["path"]
            )
            object_instance = get_object_or_404(
                object_type_model, pk=validated_data["object_id"]
            )
        else:
            # when update
            model_name = self.instance.content_type.model
            for favorite in store_settings.FAVORITE_TYPES.keys():
                if model_name == favorite.lower():
                    object_type = favorite
            object_instance = self.instance.content_object

        for extra in validated_data["extras"]:
            if (
                extra["object_type"]
                not in store_settings.FAVORITE_TYPES[object_type]["extras"]
            ):
                raise serializers.ValidationError(
                    _(f"{extra['object_type']} Cannot be extra of {object_type}")
                )
            extra_object_type = extra["object_type"]
            extras_data.setdefault(
                extra_object_type,
                {
                    "model": import_string(
                        store_settings.FAVORITE_TYPES[object_type]["extras"][
                            extra_object_type
                        ]["path"]
                    ),
                    "ids": [],
                },
            )
            extras_data[extra_object_type]["ids"].append(extra["object_id"])

        extras = []
        for key, value in extras_data.items():
            type = store_settings.FAVORITE_TYPES[object_type]["extras"][key]["type"]
            if len(value["ids"]) > 1 and type == store_settings.SIGNLE_FAVORITE_EXTRA:
                raise serializers.ValidationError(_(f"Cannot set multiple {key}s"))
            for id in value["ids"]:
                extras.append(
                    self.get_object(value["model"], id)
                )  # get objects of extras instead of ids
        extras = list(set(extras))  # remove duplicated extras
        validated_data = {
            "content_object": object_instance,
            "extras": extras,
            "name": validated_data["name"],
        }
        self._lookup_validation(validated_data)
        return validated_data

    def create(self, validated_data):
        try:
            favorite = Favorite.add_favorite(
                content_object=validated_data["content_object"],
                user=self.context["request"].user,
                name=validated_data["name"],
                extras=validated_data["extras"],
            )
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.message_dict)
        return favorite

    def update(self, instance, validated_data):
        try:
            favorite = instance.update_favorite(
                validated_data["name"],
                validated_data["extras"],
            )
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.message_dict)
        return favorite


class WalletMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletMedia
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "user", "balance", "name", "media_image", "image_url"]
        extra_kwargs = {
            "user": {"read_only": True},
        }


class WalletTopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=1, required=True
    )
    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(
            payment_provider__in=[
                store_settings.TAP_CREDIT_CARD,
                store_settings.TAP_KNET,
                store_settings.TAP_ALL,
            ]
        ),
        required=True,
    )

    def top_up_wallet(self, wallet):
        amount = self.validated_data["amount"]
        payment_method = self.validated_data["payment_method"]
        return wallet.top_up_wallet(amount=amount, payment_method=payment_method)


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "type",
            "amount",
            "created_at",
            "wallet",
            "is_cashback",
            "is_refund",
        ]


class ReorderSerializer(serializers.Serializer):
    force_cart = serializers.BooleanField(default=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        order = self.context["view"].get_object()
        cart = self.context["request"].user.cart
        stores = Store.objects.filter(store_items__cart=cart).distinct()
        if attrs["force_cart"]:
            cart.items.all().delete()
        elif stores.exists():
            if stores[0] != order.store or stores.count() > 1:
                raise ValidationError(
                    _("Your cart contains items from different store")
                )
        return attrs


class OrderDataSerializer(serializers.ModelSerializer):
    """
    This class takes an Order object and returns a dictionary of initialization data
    """

    store_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    payment_method_name = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    shipping_method_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "store_name",
            "customer_email",
            "payment_method_name",
            "shipping_method_name",
            "shipping_address",
        )

    def get_store_name(self, obj):
        return obj.store.name if obj.store else None

    def get_customer_email(self, obj):
        return obj.customer.email if obj.customer else None

    def get_payment_method_name(self, obj):
        return obj.payment_method.name if obj.payment_method else None

    def get_shipping_address(self, obj):
        return obj.shipping_address.address_line if obj.shipping_address else None

    def get_shipping_method_name(self, obj):
        return obj.shipping_method.name if obj.shipping_method else None
