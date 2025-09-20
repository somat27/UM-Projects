import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Image from "../../components/designLayouts/Image";

const StockManagement = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [editProduct, setEditProduct] = useState(null);
  const [, setShowCategoryForm] = useState(false);
  const [newCategory, setNewCategory] = useState({ name: "", description: "" });
  const [showCategoryManagement, setShowCategoryManagement] = useState(false);

  //console.log(products[1].summary);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/moloni/products");
        setProducts(response.data.length > 0 ? response.data : []);
      } catch (err) {
        console.error("Erro ao buscar produtos do backend:", err);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    const fetchCategories = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/moloni/categories", {
          company_id: 322336,
          parent_id: 0,
        });
        setCategories(response.data);
      } catch (err) {
        console.error("Erro ao buscar categorias:", err);
        setCategories([]);
      }
    };

    fetchProducts();
    fetchCategories();
  }, []);

  const filteredProducts = products.filter((product) =>
    product.name?.toLowerCase().includes(search.toLowerCase())
  );

  const totalStock = products.reduce((sum, product) => sum + (product.stock || 0), 0);
  const lowStockProducts = products.filter((product) => product.stock < 20).length;

  const handleNavigateToBuy = () => {
    navigate("/comprar");
  };

  const handleSaveChanges = async () => {
    try {
      const updatedProduct = {
        company_id: 322336, // Substituir pelo seu ID da empresa
        product_id: editProduct.product_id,
        category_id: editProduct.category_id, // Pega o ID da categoria
        type: 1, // Exemplo: 1 = Produto
        name: editProduct.name,
        price: editProduct.price,
        unit_id: editProduct.unit_id || 2985681, // Substituir pelo ID de unidade padrão
        has_stock: editProduct.has_stock || 1,
        stock: editProduct.stock || 0,
        imagem: editProduct.imagem, 
        summary: editProduct.description,    
        'taxes[0][tax_id]': 3414531,
        'taxes[0][value]': 23,
        'taxes[0][order]': 1,
        'taxes[0][cumulative]': 0
      };
  
      const response = await axios.post("http://localhost:5000/api/moloni/products/update", updatedProduct);
      console.log(response);
      if (response.status === 200) {
        alert("Produto atualizado com sucesso!");
  
        // Atualize a lista de produtos, incluindo a categoria atualizada
        setProducts((prevProducts) =>
          prevProducts.map((product) =>
            product.product_id === editProduct.product_id
              ? { ...product, ...updatedProduct }
              : product
          )
        );

        fetchProducts();
      } else {
        alert(`Erro ao atualizar produto: ${response.data.error}`);
      }
    } catch (error) {
      console.error("Erro ao atualizar o produto:", error);
      alert("Erro ao tentar atualizar o produto.");
    } finally {
      setEditProduct(null); // Fecha o modal
    }
  };
  

  const handleAddCategory = async () => {
    if (!newCategory.name) {
      alert("O nome da categoria é obrigatório!");
      return;
    }
  
    try {
      const response = await axios.post("http://localhost:5000/api/moloni/categories/insert", {
        company_id: 322336,
        parent_id: 0,
        name: newCategory.name,
        description: newCategory.description || "",
        pos_enabled: 1,
      });
  
      if (response.status === 200) {
        alert("Categoria criada com sucesso!");
  
        const newCategoryDetails = response.data.details;
        
        setCategories((prev) => [
          ...prev,
          {
            category_id: newCategoryDetails.category_id,
            name: newCategoryDetails.name || newCategory.name, // Certifique-se de que o nome está definido
          },
        ]);
  
        // Atribuir a nova categoria ao produto em edição
        setEditProduct((prevEditProduct) => ({
          ...prevEditProduct,
          category_id: newCategoryDetails.category_id,
        }));
  
        // Fechar formulário de categoria e resetar valores
        setShowCategoryForm(false);
        setNewCategory({ name: "", description: "" });
      } else {
        alert(`Erro ao criar categoria: ${response.data.error}`);
      }
    } catch (error) {
      console.error("Erro ao criar categoria:", error);
      alert("Erro ao tentar criar a categoria.");
    }
  };
  
  const handleRemoveCategory = async (categoryId) => {
    try {
      const response = await axios.post("http://localhost:5000/api/moloni/categories/delete", {
        company_id: 322336, // Substituir pelo ID da empresa
        category_id: categoryId, // ID da categoria a ser removida
      });
      
      if (response.status === 200) {
        alert("Categoria removida com sucesso!");
        // Atualizar a lista de categorias no frontend
        setCategories((prev) =>
          prev.filter((category) => category.category_id !== categoryId)
        );
      } else {
        alert(`Erro ao remover categoria: ${response.data.error}`);
      }
    } catch (error) {
      console.error("Erro ao remover categoria:", error);
      alert("Erro ao tentar remover a categoria.");
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) {
      alert("Por favor, selecione um arquivo para fazer o upload.");
      return;
    }
  
    const formData = new FormData();
    formData.append("image", file);
  
    try {
      const response = await axios.post("http://localhost:5000/api/imgur/upload", formData);
  
      console.log(response);
      if (response.status === 200) {
        const imageUrl = response.data.link;
  
        // Adiciona o link da imagem à descrição do produto
        setEditProduct((prev) => ({
          ...prev,
          description: prev.description ? `${prev.description} ${imageUrl}` : imageUrl,
        }));
  
        alert("Imagem carregada com sucesso!");
      } else {
        alert("Erro ao fazer upload da imagem.");
      }
    } catch (error) {
      console.error("Erro ao fazer upload da imagem:", error);
      alert("Erro ao fazer upload da imagem.");
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await axios.post("http://localhost:5000/api/moloni/products");
      setProducts(response.data.length > 0 ? response.data : []);
    } catch (err) {
      console.error("Erro ao buscar produtos do backend:", err);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchProducts();
  }, []);
  
 
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Gestão de Stock</h2>

      {/* Indicadores de resumo */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-yellow-100 p-4 rounded shadow-md">
          <h3 className="text-lg font-bold">Produtos com Stock Baixo  (&lt;20)</h3>
          <p className="text-2xl">{!loading ? lowStockProducts : 0}</p>
        </div>
        <div className="bg-green-100 p-4 rounded shadow-md">
          <h3 className="text-lg font-bold">Quantidade Total em Stock</h3>
          <p className="text-2xl">{!loading ? totalStock : 0}</p>
        </div>
      </div>

      {/* Gráfico */}
      <div className="w-full h-96 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={!loading && products.length > 0 ? products : [{ name: "Sem Dados", stock: 0 }]}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="stock" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold">Produtos - Total: {products.length}</h3>


        <div className="flex gap-2">
          <button
            onClick={() => setShowCategoryManagement(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Gerenciar Categorias
          </button>
          <button
            onClick={handleNavigateToBuy}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Comprar Produtos
          </button>
          </div>
      </div>

      {/* Barra de procura */}
      <div className="my-4">
        <input
          type="text"
          placeholder="Procurar produto..."
          className="p-2 border border-gray-300 rounded w-full"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Tabela de produtos */}
      <table className="table-auto w-full border-collapse border border-gray-300 mb-6">
        <thead className="bg-gray-200">
          <tr>
            <th className="border border-gray-300 px-4 py-2 text-left">Imagem</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Nome</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Categoria</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Quantidade</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Preço</th>
            <th className="border border-gray-300 px-4 py-2 text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          {filteredProducts.length > 0 ? (
            filteredProducts.map((product) => (
              <tr key={product.product_id}>
                <td className="border border-gray-300 px-4 py-2">
                  {product.summary ? (
                    <Image className="w-16 h-16 object-cover rounded" imgSrc={product.summary}/>
                  ) : (
                    "Sem Imagem"
                  )}
                </td>
                <td className="border border-gray-300 px-4 py-2">{product.name}</td>
                <td className="border border-gray-300 px-4 py-2">{product.category?.name || "N/A"}</td>
                <td className="border border-gray-300 px-4 py-2">{product.stock || 0}</td>
                <td className="border border-gray-300 px-4 py-2">
                  {product.price ? `${product.price.toFixed(2)}€` : "N/A"}
                </td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  <button
                    onClick={() => setEditProduct(product)}
                    className="bg-yellow-500 text-white px-2 py-1 rounded"
                  >
                    Editar
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" className="text-center text-gray-500 py-4">
                Nenhum produto disponível.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Modal de edição */}
      {editProduct && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div
            className="bg-white p-6 rounded shadow-lg relative"
            style={{
              width: "80%",
              maxWidth: "900px",
            }}
          >
            {/* Botão de fechar no canto superior direito */}
            <button
              onClick={() => setEditProduct(null)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>

            <h3 className="text-lg font-bold mb-4">Editar Produto</h3>
            <div className="grid grid-cols-1 gap-4">
              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editProduct.name || ""}
                  onChange={(e) => setEditProduct({ ...editProduct, name: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Nome
                </span>
              </div>
              <div className="relative">
                <select
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editProduct.category_id || ""}
                  onChange={(e) => setEditProduct({ ...editProduct, category_id: parseInt(e.target.value) })}
                >
                  <option value="" disabled>
                    Selecione uma categoria
                  </option>
                  {categories.map((category) => (
                    <option key={category.category_id} value={category.category_id}>
                      {category.name || "Categoria Sem Nome"}
                    </option>
                  ))}
                </select>
                <span className="absolute top-1/2 right-4 transform -translate-y-1/2 text-gray-500 text-sm">
                  Categoria
                </span>
              </div>
              <div className="relative">
                <input
                  type="number"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editProduct.price || ""}
                  onChange={(e) => setEditProduct({ ...editProduct, price: parseFloat(e.target.value) })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Preço
                </span>
              </div>
              <div className="relative">
                <input
                  type="file"
                  className="p-2 border border-gray-300 rounded w-full"
                  accept="image/*"
                  onChange={(e) => handleImageUpload(e, editProduct.product_id)}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Imagem
                </span>
              </div>
              {editProduct?.imagem && (
                <div className="mt-4">
                  <img
                    src={editProduct.imagem}
                    alt="Imagem do Produto"
                    className="w-32 h-32 object-cover rounded"
                  />
                </div>
              )}
            </div>
            <div className="flex justify-end items-center mt-4">
              <div className="flex gap-2">
                <button
                  onClick={handleSaveChanges}
                  className="bg-green-500 text-white px-4 py-2 rounded"
                >
                  Salvar
                </button>
                <button
                  onClick={async () => {
                    if (window.confirm("Tem certeza de que deseja remover este produto?")) {
                      try {
                        const response = await axios.post("http://localhost:5000/api/moloni/products/delete", {
                          company_id: 322336, 
                          product_id: editProduct.product_id, 
                        });

                        console.log(response);

                        if (response.status === 200) {
                          alert("Produto removido com sucesso!");
                          setProducts((prevProducts) =>
                            prevProducts.filter((product) => product.product_id !== editProduct.product_id)
                          );
                          setEditProduct(null); // Fechar modal
                        } else {
                          alert(`Erro ao remover produto: ${response.data.error}`);
                        }
                      } catch (error) {
                        console.error("Erro ao remover produto:", error);
                        alert("Erro ao tentar remover o produto.");
                      }
                    }
                  }}
                  className="bg-red-500 text-white px-4 py-2 rounded"
                >
                  Remover
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {showCategoryManagement && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div
            className="bg-white p-6 rounded shadow-lg relative"
            style={{
              width: "80%",
              maxWidth: "700px",
            }}
          >
            {/* Botão de fechar no canto superior direito */}
            <button
              onClick={() => setShowCategoryManagement(false)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>

            <h3 className="text-lg font-bold mb-4">Gerenciar Categorias</h3>

            {/* Formulário para adicionar nova categoria */}
            <div className="mb-6 flex items-center gap-2">
              <input
                type="text"
                className="p-2 border border-gray-300 rounded w-full"
                placeholder="Nome da Categoria"
                value={newCategory.name || ""}
                onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
              />
              <button
                onClick={handleAddCategory}
                className="bg-green-500 text-white px-4 py-2 rounded whitespace-nowrap"
              >
                Criar Categoria
              </button>
            </div>

            {/* Lista de categorias existentes */}
            <ul className="space-y-2">
              {categories.map((category) => (
                <li
                  key={category.category_id}
                  className="flex items-center justify-between bg-gray-100 p-2 rounded"
                >
                  <span>{category.name || "Categoria Sem Nome"}</span>
                  <button
                    onClick={() => {
                      if (window.confirm("Tem certeza de que deseja remover esta categoria?")) {
                        handleRemoveCategory(category.category_id);
                      }
                    }}
                    className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                  >
                    Remover
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockManagement;
