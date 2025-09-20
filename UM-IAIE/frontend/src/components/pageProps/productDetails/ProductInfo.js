import React, { useState } from "react"; // Adicionado useState
import { useDispatch } from "react-redux";
import { addToCart } from "../../../redux/orebiSlice";
import Notification from "../../../components/designLayouts/Notification";

const ProductInfo = ({ productInfo }) => {
  const [notifications, setNotifications] = useState([]);

  const showNotification = (message, type = "success") => {
    const id = Math.random().toString(36).substring(2, 9) + Date.now();
    setNotifications([...notifications, { id, message, type }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((notification) => notification.id !== id));
    }, 3000);
  };  

  const dispatch = useDispatch();

  return (
    <div className="flex flex-col gap-8">
      <Notification notifications={notifications} />
      
      <div className="flex flex-col gap-5">
      <h2 className="text-4xl font-semibold">{productInfo.productName || productInfo.name}</h2>
        <p className="text-xl font-semibold">{productInfo.price}€</p>
        <p className="font-normal text-sm">
          <span className="text-base font-medium">Categoria:</span> {productInfo.category}
        </p>
        <p className="text-[#767676] text-[14px] overflow-hidden text-ellipsis whitespace-nowrap transition-transform duration-200">
          Stock: {productInfo.stock > 0 ? `${productInfo.stock} unidades` : "Sem stock"}
        </p>
        
        <button
          onClick={() => {
            dispatch(
              addToCart({
                _id: productInfo._id,
                name: productInfo.productName || productInfo.name,
                quantity: 1,
                image: productInfo.img,
                price: productInfo.price,
                colors: productInfo.color,
                category: productInfo.category,
                taxes: productInfo.taxes || [],
                stock: productInfo.stock || 0,
                summary: productInfo.summary
              })
            );
            showNotification(`${productInfo.productName} foi adicionado ao carrinho!`);
          }}
          className="text-[#767676] hover:text-white text-black font-titleFont bg-gray-200 hover:bg-primeColor flex items-center justify-center gap-2 cursor-pointer py-2 px-4 rounded-md duration-300 w-full"
        >
          Adicionar ao Carrinho
        </button>
      </div>
    </div>
  );
};

export default ProductInfo;
