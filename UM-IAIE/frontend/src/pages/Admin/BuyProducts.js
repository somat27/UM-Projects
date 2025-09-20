import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const BuyProducts = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isModalOpen2, setIsModalOpen2] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [stock, setStock] = useState(1);
  const [resaleRate, setResaleRate] = useState(0);
  const [newProduct, setNewProduct] = useState({ name: "", category: "", price: 0 });

  const navigate = useNavigate();

  const calculateFinalPrice = () => {
    return selectedProduct ? (selectedProduct.ProductHierarchy * (1 + resaleRate / 100)).toFixed(2) : 0;
  };

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/sap/products");
        setProducts(response.data);
      } catch (err) {
        console.error("Erro ao buscar produtos do backend:", err);
        setError("Não foi possível carregar os produtos.");
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const handleGoBack = () => {
    navigate(-1);
  };

  const handleRegisterProduct = async (newProduct) => {
    try {
      const response = await axios.post("http://localhost:5000/api/sap/products", newProduct, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.status === 201) {
        alert("Produto registrado com sucesso no SAP!");
        await fetchProducts();
        setIsModalOpen(false);
      } else {
        alert("Erro ao registrar produto no SAP.");
      }
    } catch (err) {
      console.error("Erro ao registrar produto:", err.response ? err.response.data : err.message);
      alert(err.response?.data?.error || "Erro ao registrar o produto.");
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/sap/products");
      console.log(response);
      setProducts(response.data); 
    } catch (err) {
      console.error("Erro ao buscar produtos do backend:", err);
      setError("Não foi possível carregar os produtos.");
    }
  };

  const generateUniqueReference = (product) => {
    const description = product.ProductDescription.replace(/\s+/g, "_").toLowerCase(); // Substituir espaços por _
    const datePart = new Date().toISOString().replace(/[-:.TZ]/g, ""); // Data atual formatada como YYYYMMDDHHMMSS
    const randomPart = Math.random().toString(36).substring(2, 8); // Identificador aleatório
  
    return `ref_${description}_${datePart}_${randomPart}`;
  };
  
   
  const handleBuyProductMoloni = async () => {
    try {
      const productData = {
        company_id: 322336,            
        category_id: 8652948,  
        category_name: newProduct.category,             
        type: 1,                      
        name: selectedProduct.ProductDescription,
        reference: generateUniqueReference(selectedProduct),
        price: parseFloat(calculateFinalPrice()),
        unit_id: 2985681,                   
        has_stock: 1,             
        stock: stock > 0 ? stock : 0,       
        'taxes[0][tax_id]': 3414531,
        'taxes[0][value]': 23,
        'taxes[0][order]': 1,
        'taxes[0][cumulative]': 0
      };
      
      const insertResponse = await axios.post("http://localhost:5000/api/moloni/products/create", productData);

      console.log(insertResponse);
      alert("Produto comprado com sucesso!");
      setIsModalOpen2(false);
    } catch (err) {
      console.error("Erro ao enviar produto para o Moloni:", err);
      alert(err.response?.data?.error || "Erro ao enviar o produto.");
    }
  };

  const openModal = (product) => {
    setSelectedProduct(product);
    setNewProduct({
      ...newProduct,
      name: product.ProductDescription || "",
      category: product.SizeOrDimensionText || "", // Preencher a categoria
      price: product.ProductHierarchy || 0,        // Opcional: preencher o preço, se necessário
    });
    setIsModalOpen2(true);
  };

  if (loading) return <p>Carregando produtos...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={handleGoBack}
          className="text-blue-500 hover:underline text-sm"
        >
          &larr; Voltar para a página anterior
        </button>
        <h2 className="text-3xl font-bold text-center flex-grow text-center">
          Comprar Produtos
        </h2>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition duration-200"
        >
          Registar Produto SAP
        </button>
      </div>

      {loading && <p className="text-center text-gray-700">Carregando produtos...</p>}
      {error && <p className="text-center text-red-500">{error}</p>}

      {!loading && !error && (
        <table className="table-auto w-full border-collapse border border-gray-300 mb-6 bg-white rounded shadow-md">
          <thead className="bg-gray-200">
            <tr>
              <th className="border border-gray-300 px-4 py-2">Nome</th>
              <th className="border border-gray-300 px-4 py-2">Categoria</th>
              <th className="border border-gray-300 px-4 py-2">Preço</th>
              <th className="border border-gray-300 px-4 py-2 text-center">Ações</th>
            </tr>
          </thead>
          <tbody>
            {products.length > 0 ? (
              products.map((product, index) => (
                <tr
                  key={product.Product || `product-${index}`}
                  className="hover:bg-gray-100"
                >
                  <td className="border border-gray-300 px-4 py-2">{product.ProductDescription || "Nome Indisponível"}</td>
                  <td className="border border-gray-300 px-4 py-2">{product.SizeOrDimensionText || "Categoria Indisponível"}</td>
                  <td className="border border-gray-300 px-4 py-2">{product.ProductHierarchy || "Preço Indisponível"}</td>
                  <td className="border border-gray-300 px-4 py-2 text-center">
                    <button
                      onClick={() => openModal(product)}
                      className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
                    >
                      Comprar
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="text-center text-gray-500 py-4">
                  Não há produtos disponíveis.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg relative" style={{ width: "80%", maxWidth: "900px" }}>
            <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 text-gray-500 hover:text-gray-700">✕</button>
            <h3 className="text-lg font-bold mb-4">Registar Novo Produto</h3>

            <div className="grid grid-cols-1 gap-4">
              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Nome
                </span>
              </div>

              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={newProduct.category}
                  onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Categoria
                </span>
              </div>

              <div className="relative">
                <input
                  type="number"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={newProduct.price}
                  onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Preço
                </span>
              </div>
            </div>

            <div className="flex justify-end mt-4">
              <button onClick={() => handleRegisterProduct(newProduct)} className="bg-green-500 text-white px-4 py-2 rounded">
                Registar
              </button>
            </div>
          </div>
        </div>
      )}
      {isModalOpen2 && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg relative" style={{ width: "80%", maxWidth: "900px" }}>
            <button
              onClick={() => setIsModalOpen2(false)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
            <h2 className="text-2xl font-bold mb-4">Comprar Produto</h2>

            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Quantidade:</label>
              <input
                type="number"
                value={stock}
                onChange={(e) => setStock(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full p-2 border rounded"
                min="1"
              />
            </div>

            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Taxa de Revenda (%):</label>
              <input
                type="number"
                value={resaleRate}
                onChange={(e) => setResaleRate(Math.max(0, parseFloat(e.target.value) || 0))}
                className="w-full p-2 border rounded"
                min="0"
              />
            </div>

            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Preço Final:</label>
              <p className="w-full p-2 border rounded bg-gray-100">{calculateFinalPrice()}</p>
            </div>

            <div className="flex justify-end gap-2">
              <button onClick={handleBuyProductMoloni} className="bg-green-500 text-white px-4 py-2 rounded">
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BuyProducts;