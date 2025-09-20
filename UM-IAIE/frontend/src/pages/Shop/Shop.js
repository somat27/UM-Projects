import React, { useState, useEffect } from "react";
import Breadcrumbs from "../../components/pageProps/Breadcrumbs";
import Pagination from "../../components/pageProps/shopPage/Pagination";
import CategoriesFilter from "../../components/pageProps/shopPage/CategoriesFilter";
import axios from "axios";

const Shop = () => {
  const [itemsPerPage] = useState(8);
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [error, setError] = useState("");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [sortOrder, setSortOrder] = useState("default");
  const [priceRange, setPriceRange] = useState([0, 0]); // [min, max]
  const [maxPrice, setMaxPrice] = useState(0);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/moloni/products", {
          company_id: 322336,
        });

        if (response.status === 200) {
          setProducts(response.data);
          setFilteredProducts(response.data);

          const prices = response.data.map((product) => product.price || 0);
          const max = Math.max(...prices);
          setPriceRange([0, max]);
          setMaxPrice(max);
        } else {
          setError("Erro ao carregar produtos. Tente novamente mais tarde.");
          console.error("Erro ao buscar produtos:", response.statusText);
        }
      } catch (error) {
        setError("Erro ao carregar produtos. Verifique sua conexão.");
        console.error("Erro ao buscar produtos:", error);
      }
    };

    fetchProducts();
  }, []);

  useEffect(() => {
    // Reaplicar filtros sempre que os filtros mudarem
    let updatedProducts = [...products];

    if (selectedCategory) {
      updatedProducts = updatedProducts.filter(
        (product) => product.category?.name === selectedCategory
      );
    }

    updatedProducts = updatedProducts.filter((product) => {
      const price = product.price || 0;
      return price >= priceRange[0] && price <= priceRange[1];
    });

    updatedProducts = updatedProducts.filter((product) => product.stock > 0);

    if (sortOrder === "alphabetical") {
      updatedProducts.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortOrder === "priceLowToHigh") {
      updatedProducts.sort((a, b) => (a.price || 0) - (b.price || 0));
    } else if (sortOrder === "priceHighToLow") {
      updatedProducts.sort((a, b) => (b.price || 0) - (a.price || 0));
    }

    setFilteredProducts(updatedProducts);
  }, [selectedCategory, priceRange, sortOrder, products]);

  const handleMinPriceChange = (e) => {
    let value = parseFloat(e.target.value) || 0;
    value = Math.max(0, Math.min(value, priceRange[1])); // Garantir que não seja menor que 0 ou maior que o máximo atual
    setPriceRange([value, priceRange[1]]);
  };

  const handleMaxPriceChange = (e) => {
    let value = parseFloat(e.target.value) || 0;
    value = Math.max(priceRange[0], Math.min(value, maxPrice)); // Garantir que não seja menor que o mínimo atual ou maior que o máximo permitido
    setPriceRange([priceRange[0], value]);
  };

  return (
    <div className="max-w-container mx-auto px-4">
      {/* Breadcrumb e Ordenação */}
      <div className="flex justify-between items-center mb-4">
        <Breadcrumbs title="Produtos" />
        <select
          className="p-2 border rounded"
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
        >
          <option value="default">Ordenar por</option>
          <option value="alphabetical">Alfabética (A-Z)</option>
          <option value="priceLowToHigh">Preço: Menor para Maior</option>
          <option value="priceHighToLow">Preço: Maior para Menor</option>
        </select>
      </div>

      <div className="flex">
        {/* Barra lateral de filtros */}
        <aside className="w-1/4 bg-gray-100 p-4 rounded-md shadow-lg">
          <h3 className="font-bold mb-4">Filtros</h3>

          {/* Filtro por categorias */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold mb-2">Categorias</h4>
            <CategoriesFilter
              products={products}
              setSelectedCategory={setSelectedCategory}
            />
          </div>

          {/* Filtro por preço */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold mb-2">Preço</h4>
            <div className="flex flex-col gap-4">
              <label className="flex items-center">
                <span className="w-16 text-sm">Mínimo</span>
                <input
                  type="number"
                  className="p-2 border rounded w-full"
                  value={priceRange[0]}
                  onChange={handleMinPriceChange}
                />
              </label>
              <label className="flex items-center">
                <span className="w-16 text-sm">Máximo</span>
                <input
                  type="number"
                  className="p-2 border rounded w-full"
                  value={priceRange[1]}
                  onChange={handleMaxPriceChange}
                />
              </label>
            </div>
          </div>
        </aside>

        {/* Produtos */}
        <div className="w-3/4 pl-6">
          <div className="w-full h-full flex justify-center pb-20">
            <div className="max-w-[1200px] w-full px-4 h-full flex flex-col gap-10">
              {error ? (
                <div className="text-red-500 text-center">{error}</div>
              ) : filteredProducts.length > 0 ? (
                <Pagination itemsPerPage={itemsPerPage} items={filteredProducts} />
              ) : (
                <div className="text-center text-gray-500 py-10">
                  Nenhum produto disponível.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Shop;
