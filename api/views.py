from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializes import BookSerializer, OrderSerializer
from .models import Book, Order
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework.throttling import ScopedRateThrottle
from .custom_pagination import StandardResultsSetPagination
from .custom_permission import ViewCurrentUserOrder
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
import magic

# @action(detail=True, methods=['post'])
# from custom_user.custom_drf_backend import DrfAuthBackend
User = get_user_model()


# <---------------------------- JWT Authentication is used ----------------------------------------->
# Create your views here.
def home(request):
    user = User.objects.get(is_superuser=True).email
    context = {
        'user': user,
    }
    return render(request, 'api/main.html', context)


@api_view(('GET',))
def test(request):
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class BookView(ListCreateAPIView):
    serializer_class = BookSerializer  # class_variable
    queryset = Book.objects.all()
    # filter_backends = [OrderingFilter]
    ordering_fields = ['price', 'rating']  # works individually
    ordering = ['-rating']
    #
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'my_user'

    # Pagination
    pagination_class = StandardResultsSetPagination

    # permission_classes = [IsAuthenticated]

    # def get(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            if request.data['name'] or request.data['author'] or request.data['price'] or request.FILES:
                if not bool(Book.objects.filter(Q(name=request.data['name']) & Q(author=request.data['author']))):
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    return Response({'status': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Book already exist'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'data insufficient'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'You must be the admin to enter books'}, status=status.HTTP_400_BAD_REQUEST)

    # In order
    # 1. Decide which filter to use depending on parameter, must only return queryset
    def filter_queryset(self, queryset):  # chose the filter you want to use
        filter_backends = []  # default filter
        if self.request.query_params.get('in_stock', None):
            if self.request.query_params['in_stock'] in [True, False]:
                filter_backends = [OrderingFilter]
        for backend in list(filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset

    # 2. Override queryset on top, must only return queryset
    def get_queryset(self):
        dict = {}
        if self.request.GET.get("rating"):
            dict["rating__exact"] = self.request.GET.get("rating")

        if self.request.GET.get("name"):
            dict["name__icontains"] = self.request.GET.get("name")

        if self.request.query_params.get('in_stock'):  # using request.query_params.get
            dict["in_stock__exact"] = self.request.GET.get("in_stock")

        try:
            queryset = Book.objects.filter(**dict)
            return queryset
        except Exception as e:
            print(e)
            return None


class BookChange(RetrieveUpdateDestroyAPIView):  # Has to be sent in body{}
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    # permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_url_kwarg = 'book_id'

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=self.kwargs.get('book_id'))  # As it has a lookup_url_kwarg = 'book_id'
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):  # destroy does the same work
        if request.user.is_superuser:
            book = get_object_or_404(Book, pk=self.kwargs.get('book_id'))
            serializer = self.get_serializer(book, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'status': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'You must be the admin to enter books'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):  # destroy does the same work
        book = get_object_or_404(Book, pk=self.kwargs.get('book_id'))
        book.delete()
        dict = {'message': 'Deleted book'}
        return Response(dict, status=status.HTTP_200_OK)




class OrderView(ListCreateAPIView):
    serializer_class = OrderSerializer  # class_variable
    # see own order
    permission_classes = [IsAuthenticated, ViewCurrentUserOrder]

    def get_queryset(self):
        queryset = self.request.user.order_set.all()  # only this particular user can view its orders
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print(request.query_params)  # <QueryDict: {'only': ['order_id,status']}>
        if 'only' in request.query_params:
            print(request.query_params['only'])
            print(request.query_params['only'].split(','))
            list_of_fields = request.query_params['only'].split(',')
            serializer = OrderSerializer(queryset, many=True,
                                         add_fields=list_of_fields, )
        else:
            serializer = OrderSerializer(queryset, many=True,
                                         add_fields=['order_id', 'date_created', 'book_name'])
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # saves the data, serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderChange(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer  # class_variable
    permission_classes = [IsAuthenticated, ViewCurrentUserOrder]
    lookup_url_kwarg = 'order_id'

    def get_queryset(self):  # uses parameter http://127.0.0.1:8000/api/books/?rating=5&name=To Kill a Mocking bird
        queryset = get_object_or_404(Order, order_id=self.kwargs.get('order_id'))
        return queryset

    def put(self, request, *args, **kwargs):
        order = get_object_or_404(Order, order_id=self.kwargs.get('order_id'))
        serializer = self.get_serializer(order, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            temp = serializer.data
            del temp['book_name']
            print(temp)
            return Response(temp, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, order_id=self.kwargs.get('order_id'))
        serializer = OrderSerializer(order, many=False,
                                     add_fields=['order_id', 'total_quantity', 'address', 'status', 'total_price',
                                                 'date_created', 'book'])
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):  # destroy does the same work
        order = get_object_or_404(Order, order_id=self.kwargs.get('order_id'))
        order.delete()
        dict = {'message': 'Deleted'}
        return Response(dict)
