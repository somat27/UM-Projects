import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import Breadcrumbs from "../../components/pageProps/Breadcrumbs";
import Notification from "../../components/designLayouts/Notification";
import { 
  resetCart,  
  deleteItem, 
  updateCartItemQuantity 
} from "../../redux/orebiSlice";
import ItemCard from "./ItemCard";
import Image from "../../components/designLayouts/Image";

const Cart = () => {
  const dispatch = useDispatch();
  const products = useSelector((state) => state.orebiReducer.products);
  const [totalAmt, setTotalAmt] = useState(0); // Total do carrinho
  const [taxAmount, setTaxAmount] = useState(0); // Total de impostos
  const [notifications, setNotifications] = useState([]);

  const showNotification = (message, type = "error") => {
    const id = Math.random().toString(36).substring(2, 9) + Date.now();
    setNotifications([...notifications, { id, message, type }]);
    setTimeout(() => {
      setNotifications((prev) =>
        prev.filter((notification) => notification.id !== id)
      );
    }, 3000);
  };

  useEffect(() => {
    let price = 0;
    let taxes = 0;

    products.forEach((item) => {
      const itemPrice = parseFloat(item.price) || 0; 
      const itemQuantity = parseInt(item.quantity) || 1; 
      price += itemPrice * itemQuantity;
      
      if (item.taxes && item.taxes.length > 0) {
        item.taxes.forEach((tax) => {
          taxes += (itemPrice * itemQuantity * tax.tax.value) / 100;
        });
      }
    });

    setTotalAmt(price); 
    setTaxAmount(taxes);
  }, [products]); 

  const handleRemoveAll = () => {
    dispatch(resetCart());
    showNotification("Todos os produtos foram removidos do carrinho.", "error");
  };

  const handleQuantityChange = (productId, newQuantity, stock) => {
    if (newQuantity > stock) {
      showNotification(`A quantidade máxima de ${stock} foi atingida.`, "error");
      return;
    }
  
    if (newQuantity <= 0) {
      dispatch(deleteItem(productId));
      showNotification("Produto removido do carrinho.", "error");
    } else {
      dispatch(updateCartItemQuantity({ productId, quantity: newQuantity }));
    }
  };
  
  return (
    <div className="max-w-container mx-auto px-4">
      <Breadcrumbs title="Carrinho" />
      <Notification notifications={notifications} />
      {products.length > 0 ? (
        <div className="pb-20">
          <div className="w-full h-20 bg-[#F5F7F7] text-primeColor hidden lgl:grid grid-cols-5 place-content-center px-6 text-lg font-titleFont font-semibold">
            <h2 className="col-span-2">Produto</h2>
            <h2>Preço</h2>
            <h2>Quantidade</h2>
            <h2>Total</h2>
          </div>
          <div className="mt-5">
            {products.map((item) => (
              <div key={item._id}>
                <ItemCard
                  item={item}
                  showNotification={showNotification}
                  onQuantityChange={(productId, newQuantity) => handleQuantityChange(productId, newQuantity, item.stock)}
                />
              </div>
            ))}
          </div>
          <button
            onClick={handleRemoveAll}
            className="py-2 px-10 bg-gray-500 text-white font-semibold uppercase mb-4 hover:text-white hover:bg-red-500 justify-center cursor-pointer rounded-md duration-300"
          >
            Remover Tudo
          </button>
          <div className="max-w-7xl gap-4 flex justify-end mt-4">
            <div className="w-96 flex flex-col gap-4">
              <h1 className="text-2xl font-semibold text-right">Total do Carrinho</h1>
              <div>
                <p className="flex items-center justify-between border-[1px] border-gray-400 border-b-0 py-1.5 text-lg px-4 font-medium">
                  Produtos
                  <span className="font-semibold tracking-wide font-titleFont">
                    {totalAmt.toFixed(2)}€
                  </span>
                </p>
                <p className="flex items-center justify-between border-[1px] border-gray-400 border-b-0 py-1.5 text-lg px-4 font-medium">
                  IVA (Impostos)
                  <span className="font-semibold tracking-wide font-titleFont">
                    {taxAmount.toFixed(2)}€
                  </span>
                </p>
                <p className="flex items-center justify-between border-[1px] border-gray-400 py-1.5 text-lg px-4 font-medium">
                  Total
                  <span className="font-bold tracking-wide text-lg font-titleFont">
                    {(totalAmt + taxAmount).toFixed(2)}€
                  </span>
                </p>
              </div>
              <div className="flex justify-end">
                <Link to="/paymentgateway">
                  <button className="w-96 h-10 bg-gray-500 py-2 px-10 font-semibold hover:text-white text-white hover:bg-primeColor justify-center cursor-pointer rounded-md duration-300">
                    Continuar para o pagamento
                  </button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="flex flex-col mdl:flex-row justify-center items-center gap-4 pb-20"
        >
          <div>
            <Image className="w-80 rounded-lg p-4 mx-auto" imgSrc={"emptyCart"} />
          </div>
          <div className="max-w-[500px] p-4 py-8 bg-white flex gap-4 flex-col items-center rounded-md shadow-lg">
            <h1 className="font-titleFont text-xl font-bold uppercase">
              O seu carrinho está vazio.
            </h1>
            <p className="text-sm text-center px-10 -mt-2">
              O seu carrinho existe para o servir. Dê-lhe um propósito - encha-o com eletrónicos, acessórios e muito mais da Voltix para o deixar feliz.
            </p>
            <Link to="/shop">
              <button className="bg-primeColor rounded-md cursor-pointer hover:bg-black active:bg-gray-900 px-8 py-2 font-titleFont font-semibold text-lg text-gray-200 hover:text-white duration-300">
                Continuar a Comprar
              </button>
            </Link>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Cart;
