import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Cargar las credenciales desde el archivo secrets.toml
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="products-project")
dbNames = db.collection("products")

# Formulario de producto
st.header("Registrar nuevo producto")
id_product = st.text_input("Código")
name = st.text_input("Nombre del producto")
price = st.text_input("Precio del producto")
stock = st.text_input("Existencias actuales")
stock_min = st.text_input("Stock mínimo")
stock_max = st.text_input("Stock máximo")
submit = st.button("Registrar")

# Conectar a firestone
if submit and all([id_product, name, price, stock, stock_min, stock_max]):
    doc_ref = dbNames.document(id_product)  # Usar ID como clave primaria
    doc_ref.set({
        'id': id_product,
        'name': name,
        'price': float(price),
        'stock': int(stock),
        'stock_min': int(stock_min),
        'stock_max': int(stock_max)
    })
    st.success(" Producto registrado correctamente")

#Función para cargar por nombre
def load_by_name(product_name):
    query = dbNames.where("name", "==", product_name)
    docs = list(query.stream())
    return docs[0] if docs else None

#Buscar producto
st.sidebar.subheader("Buscar producto")
name_search = st.sidebar.text_input("Nombre de producto a buscar")
btn_search = st.sidebar.button("Buscar")

if btn_search:
    doc = load_by_name(name_search)
    st.sidebar.write(doc.to_dict() if doc else " Producto no encontrado")

#Eliminar producto
st.sidebar.markdown("---")
btn_delete = st.sidebar.button("Eliminar")

if btn_delete:
    doc = load_by_name(name_search)
    if doc:
        doc.reference.delete()
        st.sidebar.success(f"Producto '{name_search}' eliminado")
    else:
        st.sidebar.error(f"Producto '{name_search}' no encontrado")

# Actualizar nombre
st.sidebar.markdown("---")
new_name = st.sidebar.text_input("Nuevo nombre del producto")
btn_update = st.sidebar.button("Actualizar")

if btn_update:
    doc = load_by_name(name_search)
    if doc:
        doc.reference.update({"name": new_name})
        st.sidebar.success(f"Producto actualizado a '{new_name}'")
    else:
        st.sidebar.error(f"Producto '{name_search}' no encontrado")

# Mostrar inventario completo
st.markdown("---")
st.subheader("Inventario actual")

all_docs = dbNames.stream()
all_data = [doc.to_dict() for doc in all_docs]
df = pd.DataFrame(all_data)

if not df.empty:
    st.dataframe(df)
else:
    st.info("No hay productos registrados aún.")
