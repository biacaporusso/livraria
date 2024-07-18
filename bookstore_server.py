from concurrent import futures
import grpc
import bookstore_pb2
import bookstore_pb2_grpc
import uuid
from datetime import datetime

# Lista de livros
books = [
    bookstore_pb2.Book(id=1, title="Dom Quixote", author="Miguel de Cervantes", year=1605, stock=6, price=20.0),
    bookstore_pb2.Book(id=2, title="O Pequeno Príncipe", author="Antoine de Saint-Exupéry", year=1943, stock=16, price=15.0),
    bookstore_pb2.Book(id=3, title="O Senhor dos Anéis", author="J.R.R. Tolkien", year=2002, stock=8, price=30.0),
    bookstore_pb2.Book(id=4, title="É Assim Que Começa", author="Colleen Hoover", year=2017, stock=12, price=60.0),
    bookstore_pb2.Book(id=5, title="Harry Potter e a Pedra Filosofal", author="J.K. Rowling", year=2001, stock=10, price=45.0)
]

# Armazenamento em memória dos pedidos
orders = []

class AuthService(bookstore_pb2_grpc.AuthServiceServicer):
    def Register(self, request, context):
        return bookstore_pb2.AuthResponse(message="Registrado com sucesso")

    def Login(self, request, context):
        return bookstore_pb2.AuthResponse(message="Login bem-sucedido", token="token_dummy")

class BookCatalogService(bookstore_pb2_grpc.BookCatalogServiceServicer):
    def GetBooks(self, request, context):
        return bookstore_pb2.BookList(books=books)

    def GetBookDetails(self, request, context):
        for book in books:
            if book.title == request.title:
                return book
        return bookstore_pb2.Book()

    def GetBookDetailsByID(self, request, context):
        for book in books:
            if book.id == request.id:
                return book
        return bookstore_pb2.Book()

class OrderService(bookstore_pb2_grpc.OrderServiceServicer):
    def PlaceOrder(self, request, context):
        if not request.order_items:
            return bookstore_pb2.OrderResponse(order_id="", message="Erro: O pedido não pode ser vazio.")
        
        ordered_books = []
        order_id = str(uuid.uuid4())
        order_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Data e hora atual formatada
        for order_item in request.order_items:
            for book in books:
                if book.id == order_item.book_id:
                    if order_item.quantity > book.stock:
                        return bookstore_pb2.OrderResponse(order_id="", message=f"Erro: Quantidade desejada de '{book.title}' supera o estoque disponível ({book.stock}).")
                    book.stock -= order_item.quantity
                    ordered_books.append(bookstore_pb2.OrderItem(book=book, quantity=order_item.quantity))
                    break
        order = bookstore_pb2.Order(order_id=order_id, username=request.username, order_items=ordered_books, order_date=order_date)
        orders.append(order)  # Adiciona o pedido à lista de pedidos
        return bookstore_pb2.OrderResponse(order_id=order_id, message="Pedido realizado com sucesso")

    def GetOrderDetails(self, request, context):
        for order in orders:
            if order.order_id == request.order_id:
                return order
        return bookstore_pb2.Order()

    def GetOrderHistory(self, request, context):
        user_orders = [order for order in orders if order.username == request.username]
        return bookstore_pb2.OrderHistory(orders=user_orders)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bookstore_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    bookstore_pb2_grpc.add_BookCatalogServiceServicer_to_server(BookCatalogService(), server)
    bookstore_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50051')  # Usando a mesma porta para todos os serviços
    server.start()
    print("Server started, listening on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
