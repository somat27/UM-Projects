import React from "react";

const CategoriesFilter = ({ products, setSelectedCategory }) => {
  const categories = Array.from(
    new Set(products.map((product) => product.category?.name).filter(Boolean))
  );

  return (
    <div>
      <select
        className="p-2 border rounded w-full"
        onChange={(e) => setSelectedCategory(e.target.value)}
      >
        <option value="">Todas as Categorias</option>
        {categories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>
    </div>
  );
};

export default CategoriesFilter;
