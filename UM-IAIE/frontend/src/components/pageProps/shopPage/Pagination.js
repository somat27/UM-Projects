import React, { useState } from "react";
import ReactPaginate from "react-paginate";
import Product from "../../home/Products/Product";

function Items({ currentItems }) {
  return (
    <>
      {currentItems &&
        currentItems.map((item) => (
          <div key={item.product_id} className="w-full">
            <Product
              _id={item.product_id}
              img={item.name || "default-image.png"}
              productName={item.name || "Produto Sem Nome"}
              price={item.price || 0} 
              category={item.category?.name || "Sem Categoria"} 
              stock={item.stock || 0}
              taxes={item.taxes || []}                  
              unit={item.measurement_unit?.name || "Unidade"} 
              summary={item.summary || "Sem Descrição"} 
            />
          </div>
        ))}
    </>
  );
}


const Pagination = ({ itemsPerPage, items }) => {
  const [itemOffset, setItemOffset] = useState(0);
  const [itemStart, setItemStart] = useState(1);

  const endOffset = itemOffset + itemsPerPage;
  const currentItems = items.slice(itemOffset, endOffset);
  const pageCount = Math.ceil(items.length / itemsPerPage);

  const handlePageClick = (event) => {
    const newOffset = (event.selected * itemsPerPage) % items.length;
    setItemOffset(newOffset);
    setItemStart(newOffset);
  };

  return (
    <div>
      <div className="w-full flex justify-center">
        <div className="max-w-[1200px] w-full px-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <Items currentItems={currentItems} />
          </div>
        </div>
      </div>

      <div className="flex flex-col mdl:flex-row justify-center mdl:justify-between items-center">
        <ReactPaginate
          nextLabel=""
          onPageChange={handlePageClick}
          pageRangeDisplayed={3}
          marginPagesDisplayed={2}
          pageCount={pageCount}
          previousLabel=""
          pageLinkClassName="w-9 h-9 border-[1px] border-lightColor hover:border-gray-500 duration-300 flex justify-center items-center"
          pageClassName="mr-6"
          containerClassName="flex text-base font-semibold font-titleFont py-10"
          activeClassName="bg-black text-white"
        />
        <p className="text-base font-normal text-lightText">
          Produtos : {itemStart === 0 ? 1 : itemStart} - {Math.min(endOffset, items.length)} de {items.length}
        </p>
      </div>
    </div>
  );
};


export default Pagination;