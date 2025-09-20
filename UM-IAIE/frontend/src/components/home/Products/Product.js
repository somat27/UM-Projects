import React, { useState } from "react";
import Image from "../../designLayouts/Image";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { addToCart } from "../../../redux/orebiSlice";
import Notification from "../../../components/designLayouts/Notification";

// Função para verificar se o usuário está logado
const isAuthenticated = () => {
  return !!localStorage.getItem("customerData");
};

const Product = (props) => {
  const dispatch = useDispatch();
  const _id = props.productName;
  const idString = (_id) => {
    return String(_id).toLowerCase().split(" ").join("");
  };
  const rootId = idString(_id);

  const navigate = useNavigate();
  const productItem = props;

  const handleProductDetails = () => {
    if (!isAuthenticated()) {
      alert("Você precisa estar logado para visualizar os detalhes do produto.");
      navigate("/signin");
      return;
    }
    navigate(`/product/${rootId}`, {
      state: {
        item: productItem,
      },
    });
  };

  const [notifications, setNotifications] = useState([]);

  const showNotification = (message, type = "success") => {
    const id = Math.random().toString(36).substring(2, 9) + Date.now();
    setNotifications([...notifications, { id, message, type }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((notification) => notification.id !== id));
    }, 3000);
  };

  const handleAddToCart = () => {
    if (!isAuthenticated()) {
      alert("Você precisa estar logado para adicionar produtos ao carrinho.");
      navigate("/signin");
      return;
    }

    dispatch(
      addToCart({
        _id: props._id,
        name: props.productName,
        quantity: 1,
        image: props.img,
        price: props.price,
        category: props.category,
        taxes: props.taxes || [],
        stock: props.stock || 0,
        summary: props.summary,
      })
    );
    showNotification(`${props.productName} foi adicionado ao carrinho!`);
  };

  return (
    <div className="w-full relative group rounded-lg overflow-hidden border border-gray-300 shadow-md">
      <Notification notifications={notifications} />

      {/* Imagem */}
      <div className="max-w-80 max-h-80 relative overflow-y-hidden">
        <div>
          <Image className="w-full h-full" imgSrc={props.summary} />
        </div>
      </div>

      {/* Informações do Produto */}
      <div className="max-w-80 py-6 flex flex-col gap-1 border-[1px] border-t-0 px-4">
        <div className="flex items-center justify-between font-titleFont">
          <h2
            onClick={handleProductDetails}
            className="hover:cursor-pointer text-lg text-primeColor font-bold overflow-hidden text-ellipsis whitespace-nowrap hover:scale-105 transition-transform duration-200"
          >
            {props.productName}
          </h2>
          <p className="text-[#767676] text-[14px]">{props.price}€</p>
        </div>
        <div>
          <p className="text-[#767676] text-[14px] overflow-hidden text-ellipsis whitespace-nowrap transition-transform duration-200">
            Categoria: {props.category || "Sem Categoria"}
          </p>
        </div>
        <div className="flex items-center justify-between font-titleFont">
          {/* Adicionar ao Carrinho */}
          <li
            onClick={handleAddToCart}
            className="text-xs text-[#767676] hover:text-white text-black font-small bg-gray-200 hover:bg-primeColor flex items-center justify-center gap-2 cursor-pointer py-1 px-3 rounded-md duration-300 w-full"
          >
            Adicionar ao Carrinho
          </li>
        </div>
      </div>
    </div>
  );
};

export default Product;
