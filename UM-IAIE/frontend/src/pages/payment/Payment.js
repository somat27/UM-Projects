import React, { useState, useEffect } from "react";
import Breadcrumbs from "../../components/pageProps/Breadcrumbs";
import { useSelector } from "react-redux";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Payment = () => {
  const products = useSelector((state) => state.orebiReducer.products); // Produtos no carrinho
  const user = JSON.parse(localStorage.getItem("customerData")); // Cliente logado
  const [paymentMethods, setPaymentMethods] = useState([]); // Métodos de pagamento
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(""); // Método de pagamento selecionado
  const [totalAmount, setTotalAmount] = useState(0); // Total do carrinho
  const [totalTax, setTotalTax] = useState(0); // Total de IVA
  const [, setLoading] = useState(false); // Adicionado
  const navigate = useNavigate(); // Adicionado

  // Carregar os métodos de pagamento
  useEffect(() => {
    const fetchPaymentMethods = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/moloni/paymentMethods");
        if (response.status === 200) {
          setPaymentMethods(response.data);
        }
      } catch (error) {
        console.error("Erro ao carregar métodos de pagamento:", error);
      }
    };
    fetchPaymentMethods();
  }, []);

  useEffect(() => {
    let price = 0;
    let taxes = 0;
  
    products.forEach((item) => {
      const itemPrice = parseFloat(item.price) || 0; // Garantir que o preço é numérico
      const itemQuantity = parseInt(item.quantity) || 1; // Garantir que a quantidade é numérica
      price += itemPrice * itemQuantity;
  
      // Calcular os impostos baseados no preço e na quantidade
      if (Array.isArray(item.taxes) && item.taxes.length > 0) {
        item.taxes.forEach((tax) => {
          const taxValue = tax?.tax?.value || 0; // Verificar se `tax` e `value` existem
          taxes += (itemPrice * itemQuantity * taxValue) / 100; // Calcular o imposto total
        });
      }
    });
  
    setTotalAmount(price.toFixed(2)); 
    setTotalTax(taxes.toFixed(2));
  }, [products]);
  
  const addStockMovement = async (product, quantity) => {
    try {
      const stockMovementData = {
        company_id: 322336,
        product_id: product._id,
        movement_date: new Date().toISOString().split("T")[0],
        warehouse_id: 0, 
        qty: -quantity, 
        notes: `Saída de stock para venda do produto ${product.name}`,
      };
  
      const response = await axios.post(
        "http://localhost:5000/api/moloni/product_stocks/insert",
        stockMovementData,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
  
      if (response.status === 200) {
        console.log(`Movimento de stock para o produto ${product._id} registrado com sucesso.`);
      } else {
        console.error(`Erro ao registrar movimento de stock para o produto ${product._id}:`, response.data);
      }
    } catch (error) {
      console.error(`Erro ao registrar movimento de stock para o produto ${product._id}:`, error);
      alert(`Erro ao registrar movimento de stock para o produto ${product.name}.`);
    }
  };  
  
  const handlePayment = async () => {
    if (!selectedPaymentMethod) {
      alert("Por favor, selecione um método de pagamento.", "error");
      return;
    }
    setLoading(true);
    const documentData = {
      company_id: 322336,
      document_set_id: 761766, 
      date: new Date().toISOString().split("T")[0],
      expiration_date: "2025-01-31", 
      customer_id: user.customer_id, 
      payment_method_id: selectedPaymentMethod,
      products: products.map((product) => ({
        product_id: product._id || 123456,
        summary: product.summary,
        name: product.name,
        qty: product.quantity > 0 ? product.quantity : 1, 
        price: parseFloat(product.price) || 0,
        taxes: [
          {
            tax_id: 3414531
          }
        ]
      })),
    };
    try {
      const response = await axios.post(
        "http://localhost:5000/api/moloni/internal_documents/insert",
        documentData,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (response.status === 201) {
        for (const product of products) {
          await addStockMovement(product, product.quantity);
        }
        alert("Compra realizada com sucesso!");
        navigate("/");
      } else {
        alert(response.data.error || "Erro ao criar o documento.", "error");
      }
    } catch (error) {
      console.error("Erro ao enviar o pedido:", error);
      alert("Erro ao processar o pagamento.", "error");
    } finally {
      setLoading(false);
    }
  };
  
  
  return (
    <div className="max-w-container mx-auto px-4">
      <Breadcrumbs title="Terminal de Pagamento" />
      <div className="pb-10">
        <h1 className="text-2xl font-bold mb-6">Resumo do Pagamento</h1>
        <div className="bg-gray-100 p-4 rounded shadow">
          <h2 className="text-lg font-bold mb-2">Produtos</h2>
          <ul>
            {products.map((product) => (
              <li key={product._id} className="flex justify-between py-2 border-b">
                <span>{product.name || "Produto sem nome"}</span>
                <span>
                  {product.quantity || 1} x {(parseFloat(product.price) || 0).toFixed(2)}€
                </span>
              </li>
            ))}
          </ul>
          <p className="text-right mt-4 font-bold text-lg">
            Total: {totalAmount}€ + IVA: {totalTax}€ ={" "}
            {(parseFloat(totalAmount) + parseFloat(totalTax)).toFixed(2)}€
          </p>
        </div>

        <div className="mt-6">
          <label className="block text-lg font-bold mb-2">Método de Pagamento</label>
          <select
            value={selectedPaymentMethod}
            onChange={(e) => setSelectedPaymentMethod(e.target.value)}
            className="w-full border px-4 py-2 rounded"
          >
            <option value="">Selecione um método</option>
            {paymentMethods.map((method) => (
              <option key={method?.payment_method_id || 0} value={method?.payment_method_id || ""}>
                {method?.name || "Método sem nome"}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-8">
          <button
            onClick={handlePayment}
            className="w-52 h-10 bg-primeColor text-white text-lg hover:bg-black duration-300"
          >
            Finalizar Compra
          </button>
        </div>
      </div>
    </div>
  );
};

export default Payment;
