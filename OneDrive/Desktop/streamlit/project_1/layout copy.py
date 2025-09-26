import streamlit as st
st.title("chai taste poll")
col1,col2=st.columns(2)
with col1:
    st.header("masala chai")
    vote1=st.button("vote masala chai")
    pass
with col2:
     st.header("adrak chai")
     vote2=st.button("vote adrak chai")
     st.image("https://media.istockphoto.com/id/1336601313/photo/top-view-of-indian-herbal-masala-chai-or-traditional-beverage-tea-with-milk-and-spices-kerala.jpg?s=2048x2048&w=is&k=20&c=ea2ueNfO3fSl_5m3OjD3DHJ0vw9GvwoI7JLQUc8ehLc=",width=200)
     pass

if vote1:
     st.success(" Thanks for masala chai")
elif vote2:
     st.success(" Thanks for adrak chai")  


name=st.sidebar.text_input("enter your name")
tea=st.sidebar.selectbox("enter chai",["masala","kesar","adrak"])

st.write(f"hello {name} ! your {tea} chai  is ready")