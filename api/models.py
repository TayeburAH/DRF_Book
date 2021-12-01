from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete, pre_save, post_save

User = get_user_model()


# user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

# Create your models here.
# Books
class Book(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    in_stock = models.BooleanField(default=False)  # we will get it as a checkbox
    quantity_stock = models.IntegerField(default=0)
    type = models.CharField(max_length=50)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    author = models.CharField(max_length=100)

    # book_id = models.CharField(max_length=36, null=True, blank=True)  # 36 Character

    def __str__(self):
        return self.name

    def ID(self):
        return str(self.pk)

    def author_name(self):
        # print(self.user.order_set.all())  # book.user.order_set.all() does not exist
        print(self.order_set.all())  # book.order_set.all()
        return str(self.author)

    @property
    def hello(self):
        return Order.show
        # To call another model methode you need self. and decorator
        # since self is not possible as there is no relation,
        # its returns an object <property object at 0x000001AAAA778950>


def upload_path(self, filename):
    return f'bookImages/{self.book.name}/{filename}'
    # don't use self.id as BookImage s not saved yet, use its self.book.name


class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, null=True)
    image = models.ImageField(upload_to=upload_path)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)


class Order(models.Model):  # can have only one book at a time
    Status_CHOICES = (
        ("Pending", "Pending"),
        ("On the way", "On the way"),
        ("Delivered", "Delivered"),
    )
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_quantity = models.PositiveIntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    address = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status_CHOICES, default='Pending')
    order_id = models.CharField(max_length=36, null=True, blank=True)  # 36 Character
    total_price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        return str(self.pk)

    def hello(self):
        return self.show

    def ordered_price(self):
        # if you want to use this =>
        # [ self.book_set.all()] This model 'order' must be inside(as foreign key) books
        # [ item.price for item in self.book_set.all()]
        self.total_price = round(float(self.total_quantity) * float(self.book.price), 2)  # float and deci
        self.save()  # must save the data
        return self.total_price

    @property
    def show(self):
        return 'I like your book'


@receiver(pre_save, sender=Order)
def create_order_id(sender, instance, *args, **kwargs):
    # pre_save => For new Order,instance.pk will be blank
    # post_save => For new Order, created
    if not instance.pk:
        print(instance.total_quantity)  # 3
        print(instance.book)
        import uuid
        instance.order_id = uuid.uuid4()  # 36 character
        print(instance.order_id)

        # same has to be for total_price other wise its empty
        instance.total_price = round(float(instance.total_quantity) * float(instance.book.price), 2)
        print(instance.total_price)
        print('order_id, total_price saved')
    else:
        print('Order exist')

    # Works too
    # import uuid
    # instance.order_id = uuid.uuid4() # 36 character
    # instance.save()
    # print('order_id saved')

# @receiver(pre_save, sender=Order)
# def create_book_id(sender, instance, *args, **kwargs):
#     # pre_save => For new Order,instance.pk will be blank
#     # post_save => For new Order, created
#     if not instance.pk:
#         print(instance.total_quantity)  # 3
#         print(instance.book)
#         import uuid
#         instance.book_id = uuid.uuid4()  # 36 character
#         print(instance.order_id)
#         print('book_id')
#     else:
#         print('book_id already exist')
