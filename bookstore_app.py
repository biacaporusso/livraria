import streamlit as st
import grpc
import bookstore_pb2
import bookstore_pb2_grpc

# Configuração do canal gRPC
auth_channel = grpc.insecure_channel('localhost:50051')
auth_stub = bookstore_pb2_grpc.AuthServiceStub(auth_channel)

catalog_channel = grpc.insecure_channel('localhost:50051')  # Usando a mesma porta para todos os serviços
catalog_stub = bookstore_pb2_grpc.BookCatalogServiceStub(catalog_channel)

order_channel = grpc.insecure_channel('localhost:50051')  # Usando a mesma porta para todos os serviços
order_stub = bookstore_pb2_grpc.OrderServiceStub(order_channel)

# Função de registro
def register_user(username, password):
    response = auth_stub.Register(bookstore_pb2.User(username=username, password=password))
    return response.message

# Função de login
def login_user(username, password):
    response = auth_stub.Login(bookstore_pb2.User(username=username, password=password))
    return response.token, response.message

# Função para obter lista de livros
def get_books():
    response = catalog_stub.GetBooks(bookstore_pb2.Empty())
    return response.books

# Função para obter detalhes de um livro por título
def get_book_details(title):
    response = catalog_stub.GetBookDetails(bookstore_pb2.BookRequest(title=title))
    return response

# Função para obter detalhes de um livro por ID
def get_book_details_by_id(book_id):
    response = catalog_stub.GetBookDetailsByID(bookstore_pb2.BookRequestByID(id=book_id))
    return response

# Função para realizar pedido
def place_order(username, order_items):
    response = order_stub.PlaceOrder(bookstore_pb2.OrderRequest(username=username, order_items=order_items))
    return response.order_id, response.message

# Função para obter histórico de pedidos
def get_order_history(username):
    response = order_stub.GetOrderHistory(bookstore_pb2.User(username=username))
    return response.orders

# Função para verificar se o usuário está autenticado
def is_authenticated():
    return 'token' in st.session_state

# Interface Streamlit
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Sistema de Livraria</h1>", unsafe_allow_html=True)

# Seção de autenticação
st.sidebar.markdown("<h2 style='color: #2196F3;'>Autenticação</h2>", unsafe_allow_html=True)
auth_choice = st.sidebar.radio("Escolha uma opção:", ("Registrar", "Login"))

if auth_choice == "Registrar":
    reg_username = st.sidebar.text_input("Nome de usuário para registro")
    reg_password = st.sidebar.text_input("Senha para registro", type="password")
    if st.sidebar.button("Registrar"):
        reg_message = register_user(reg_username, reg_password)
        st.sidebar.success(reg_message)

elif auth_choice == "Login":
    login_username = st.sidebar.text_input("Nome de usuário para login")
    login_password = st.sidebar.text_input("Senha para login", type="password")
    if st.sidebar.button("Login"):
        token, login_message = login_user(login_username, login_password)
        st.session_state['token'] = token
        st.session_state['username'] = login_username
        st.sidebar.success(login_message)

# Verifica se o usuário está autenticado
if is_authenticated():
    st.sidebar.success(f"Usuário logado como {st.session_state['username']}")

    # Seção de catálogo de livros
    st.markdown("<h2 style='color: #FF9800;'>Catálogo de Livros</h2>", unsafe_allow_html=True)
    books = get_books()
    selected_books = []
    quantities = []

    for book in books:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<p><strong>{book.title}</strong> - {book.author}<br>Ano: {book.year}<br>Estoque: {book.stock}<br>Preço: R$ {book.price}</p>", unsafe_allow_html=True)
        with col2:
            quantity = st.number_input(f"Quantidade desejada", min_value=0, max_value=book.stock, key=book.id)
            if quantity > 0:
                selected_books.append(book)
                quantities.append(quantity)

    if st.button("Realizar Pedido"):
        order_items = [bookstore_pb2.OrderItem(book_id=book.id, quantity=qty) for book, qty in zip(selected_books, quantities)]
        order_id, order_message = place_order(st.session_state['username'], order_items)
        if order_id:
            st.success(f"{order_message} (ID do Pedido: {order_id})")
        else:
            st.error(order_message)

    # Seção para obter histórico de pedidos
    st.markdown("<h2 style='color: #E91E63;'>Histórico de Pedidos</h2>", unsafe_allow_html=True)
    if st.button("Obter Histórico de Pedidos"):
        orders = get_order_history(st.session_state['username'])

        if not orders:
            st.warning("Histórico de pedidos vazio.")
        else:
            for order in orders:
                st.markdown(f"<p><strong>ID do pedido:</strong> {order.order_id}<br><strong>Data do pedido:</strong> {order.order_date}</p>", unsafe_allow_html=True)
                for item in order.order_items:
                    book = item.book
                    st.markdown(f"<p>- <strong>Título:</strong> {book.title}, <strong>Autor(a):</strong> {book.author}, <strong>Ano de lançamento:</strong> {book.year}, <strong>Preço:</strong> {book.price}, <strong>Quantidade:</strong> {item.quantity}</p>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)  # Adiciona um separador entre os pedidos

else:
    st.warning("Por favor, faça login ou registre-se para realizar pedidos.")

# Para rodar o Streamlit:
# No terminal, execute: streamlit run bookstore_app.py
