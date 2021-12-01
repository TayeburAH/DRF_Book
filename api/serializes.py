from rest_framework import serializers
from .models import Book, Order, BookImage
import magic


class BookImageSerializer(serializers.ModelSerializer):
    # image_id = serializers.SerializerMethodField('get_image_id', read_only=True)

    class Meta:
        model = BookImage
        fields = ['id', 'name', 'image']

    # def get_image_id(self,obj):
    #     return obj.id


class BookSerializer(serializers.ModelSerializer):
    bookimage_set = BookImageSerializer(many=True, read_only=True)
    # book_images = BookImageSerializer(many=True, read_only=True, source='bookimage_set')
    image_id_delete = serializers.IntegerField(write_only=True)

    # image = serializers.ListField(child=serializers.ImageField, max_length=2)

    # < model >_set as i am looking for book.bookimage_set
    class Meta:
        model = Book
        fields = ['id', 'name', 'price', 'author', 'rating', 'in_stock', 'quantity_stock', 'bookimage_set',
                  'image_id_delete']
        # id is not shown until mentioned
        # even if there is no model field
        read_only_fields = ['id']  # cannot be altered or created, its set to null
        # you cannot use source here as Book model does not have any table inside it

    # def validate_name(self, data):
    #     print('name') # name
    #     print(data) # In search of lost time
    #     return data
    #
    # def validate(self, data):
    #     print("data")
    #     print('using get')
    #     print(data.get('name'))
    #     print(data['name'] == data['author']) # this is in OrderedDict() i.e you can only use data.get('')
    #     print(data)
    #     return data

    def create(self, validated_data):
        # doing validation here
        print(validated_data)
        valid_mime_types = ['image/jpg', 'image/jpeg']
        images = self.context['request'].FILES.getlist('image')
        print(images)
        if len(images) > 4:
            raise serializers.ValidationError("maximum of 5 images can be loaded")

        for im in images:
            if im.size > 1 * 1024 * 1024:
                raise serializers.ValidationError(f"{im.name} file is larger than 1mb.")
            im.seek(0)
            type_of_file = magic.from_buffer(im.read(2048), mime=True)
            if type_of_file not in valid_mime_types:
                raise serializers.ValidationError(f"{im.name} is unsupported.")
        # validation ends here
        try:
            book = Book.objects.create(**validated_data)
            for im in images:
                BookImage.objects.create(book=book, name=im.name, image=im)
            return book
        except Exception as e:
            print(f'{e}')
            raise serializers.ValidationError(f'{e}')

    def update(self, instance, validated_data):
        # doing validation here
        print(validated_data)
        valid_mime_types = ['image/jpg', 'image/jpeg']
        images = self.context['request'].FILES.getlist('add_image')
        print(images)
        if len(images) > 4:
            raise serializers.ValidationError("maximum of 5 images can be loaded")

        for im in images:
            if im.size > 1 * 1024 * 1024:
                raise serializers.ValidationError(f"{im.name} file is larger than 1mb.")
            im.seek(0)
            type_of_file = magic.from_buffer(im.read(2048), mime=True)
            if type_of_file not in valid_mime_types:
                raise serializers.ValidationError(f"{im.name} is unsupported.")
        # validation ends here

        # instance = book
        instance.name = validated_data.get('name', instance.name)
        instance.author = validated_data.get('author', instance.author)
        instance.in_stock = validated_data.get('in_stock', instance.in_stock)
        instance.price = validated_data.get('price', instance.price)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.quantity_stock = validated_data.get('quantity_stock', instance.quantity_stock)
        instance.save()
        # add_Image
        for im in images:
            BookImage.objects.create(book=instance, name=im.name, image=im)

        # image_id
        # print(validated_data['image_id']) # keyerror as you can't write it as you used read_only
        # so use image_id_delete
        bookimage = BookImage.objects.get(pk=validated_data['image_id_delete'])
        bookimage.delete()
        return instance


# https://django.cowhite.com/blog/create-and-update-django-rest-framework-nested-serializers/

class OrderSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_name = serializers.CharField(max_length=30, write_only=True)  # returns book name
    date_created = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'total_quantity', 'address', 'status', 'total_price', 'date_created', 'book_name', 'book']
        read_only_fields = ['order_id', 'status',
                            'total_price']

    def __init__(self, *args, **kwargs):

        add_fields = kwargs.pop('add_fields', None)

        field_sets = ['order_id', 'total_quantity', 'address', 'status', 'total_price', 'date_created', 'book_name',
                      'book']

        super(OrderSerializer, self).__init__(*args, **kwargs)

        if add_fields:
            remove_list = list(set(add_fields).symmetric_difference(set(field_sets)))

            for field_name in remove_list:
                self.fields.pop(field_name)

    # you need to customize create()
    def create(self, validated_data):
        user = self.context['request'].user
        total_quantity = validated_data['total_quantity']
        address = validated_data['address']
        name = validated_data['book_name']
        try:
            book = Book.objects.get(name=name)
            if book.quantity_stock == 0:
                book.in_stock = False
                book.save()
                raise serializers.ValidationError('Sorry we ran out of stock')
            if book.quantity_stock >= int(total_quantity):
                order = Order.objects.create(book=book, address=address, total_quantity=total_quantity, user=user)
                book.quantity_stock = book.quantity_stock - int(total_quantity)
                book.save()
                return order
            else:
                raise serializers.ValidationError(f'Sorry we currently have {book.quantity_stock} books only')
        except Exception as e:
            print(f'{e}')
            raise serializers.ValidationError(f'{e}')

    # you need to customize update
    def update(self, instance, validated_data):
        # instance is empty, we have to fill it up
        user = self.context['request'].user
        print(user)
        print(validated_data)
        instance.total_quantity = validated_data.get('total_quantity', instance.total_quantity)
        instance.address = validated_data.get('address', instance.address)
        name = validated_data['book']['name']  # 'book.name'
        # instance.book = instance.book # same thing assigned to it
        try:
            book = Book.objects.get(name=name)
            instance.book = book
        except Exception as e:
            instance.book = instance.book
        instance.save()
        return instance
