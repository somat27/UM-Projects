import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import Image from "../../designLayouts/Image";
import Flex from "../../designLayouts/Flex";
import axios from "axios";
import { FaSearch, FaUser, FaCaretDown, FaShoppingCart } from "react-icons/fa";
import { useSelector } from "react-redux";

const Header = () => {
  const reduxProducts = useSelector((state) => state.orebiReducer.products);
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showUser, setShowUser] = useState(false);
  const [user, setUser] = useState(null); // Adicionado para usuário
  const navigate = useNavigate();
  const ref = useRef();

  // Buscar produtos
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/moloni/products");
        setProducts(response.data.length > 0 ? response.data : []);
      } catch (err) {
        console.error("Erro ao buscar produtos do Moloni:", err);
      }
    };

    fetchProducts();
  }, []);

  // Buscar usuário logado do localStorage
  useEffect(() => {
    const storedData = localStorage.getItem("customerData");
    if (storedData) {
      setUser(JSON.parse(storedData));
    }
  }, []);

  // Filtrar produtos com base na busca
  useEffect(() => {
    const filtered = products.filter((item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredProducts(filtered);
  }, [searchQuery, products]);

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setShowUser(false);
      }
    };
    document.body.addEventListener("click", handleClickOutside);
    return () => document.body.removeEventListener("click", handleClickOutside);
  }, []);

  return (
    <div className="w-full h-20 bg-white sticky top-0 z-50 border-b-[1px] border-b-gray-200">
      <nav className="h-full px-4 max-w-container mx-auto relative">
        <Flex className="flex items-center justify-between h-full">
          <Link to="/">
            <div>
              <Image className="w-20 object-cover" imgSrc="Voltix_LOGO" />
            </div>
          </Link>
          <div className="relative w-full lg:w-[600px] h-[50px] text-base text-primeColor bg-white flex items-center gap-2 justify-between px-6 rounded-xl shadow-lg">
            <input
              className="flex-1 h-full outline-none placeholder:text-[#C4C4C4] placeholder:text-[14px]"
              type="text"
              onChange={(e) => setSearchQuery(e.target.value)}
              value={searchQuery}
              placeholder="Pesquise os produtos aqui"
            />
            <FaSearch className="w-5 h-5" />
            {searchQuery && (
              <div
                className={`w-full mx-auto h-96 bg-white top-16 absolute left-0 z-50 overflow-y-scroll shadow-2xl scrollbar-hide cursor-pointer`}
              >
                {filteredProducts.map((item, index) => (
                  <div
                    onClick={() => {
                      const productName = item.name?.toLowerCase().split(" ").join("") || "produto";
                      navigate(`/product/${productName}`, {
                        state: {
                          item: {
                            productId: item.product_id,
                            name: item.name || "Produto Sem Nome",
                            img: item.image || "default-image.png",
                            price: item.price || 0,
                            category: item.category?.name || "Sem Categoria",
                            stock: item.stock || 0,
                            tax: item.taxes?.[0]?.tax?.name || "Sem Taxa",
                            unit: item.measurement_unit?.name || "Unidade",
                            summary: typeof item.summary === "string" ? item.summary : "Sem Descrição",
                          },
                        },
                      });
                      setSearchQuery("");
                    }}
                    key={item.product_id}
                    className="max-w-[600px] h-28 bg-gray-100 mb-3 flex items-center gap-3"
                  >
                    <div className="w-24 h-24 flex-shrink-0 overflow-hidden rounded-md">
                      <Image className="w-full h-full object-contain" imgSrc={item.summary} />
                    </div>
                    <div className="flex flex-col gap-1">
                      <p className="font-semibold text-lg">{item.name || "Sem Nome"}</p>
                      <p className="text-sm">
                        Preço:{" "}
                        <span className="text-primeColor font-semibold">
                          {item.price ? `${item.price}€` : "Preço Indisponível"}
                        </span>
                      </p>
                      <p className="text-xs">
                        Categoria:{" "}
                        {typeof item.category === "object" && item.category.name
                          ? item.category.name
                          : "Sem Categoria"}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="flex gap-4 mt-2 lg:mt-0 items-center pr-6 cursor-pointer relative">
            <div onClick={() => setShowUser(!showUser)} className="flex">
              <FaUser />
              <FaCaretDown />
            </div>
            {showUser && (
              <motion.ul
                initial={{ y: 30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="absolute top-6 left-0 z-50 bg-primeColor w-44 text-[#767676] h-auto p-4 pb-6"
              >
                {!user ? (
                  <Link to="/signin">
                    <li className="text-gray-400 px-4 py-1 border-b-[1px] border-b-gray-400 hover:border-b-white hover:text-white duration-300 cursor-pointer">
                      Login
                    </li>
                  </Link>
                ) : (
                  <>
                    <Link to="/conta">
                      <li className="text-gray-400 px-4 py-1 border-b-[1px] border-b-gray-400 hover:border-b-white hover:text-white duration-300 cursor-pointer">
                        Conta
                      </li>
                    </Link>
                    {(user.email === "admin@voltix.pt" || user.contact_email === "admin@voltix.pt") && (
                      <Link to="/admin">
                        <li className="text-gray-400 px-4 py-1 border-b-[1px] border-b-gray-400 hover:border-b-white hover:text-white duration-300 cursor-pointer">
                          Admin
                        </li>
                      </Link>
                    )}
                  </>
                )}
              </motion.ul>
            )}
            <Link to="/cart">
              <div className="relative">
                <FaShoppingCart />
                <span className="absolute font-titleFont top-3 -right-2 text-xs w-4 h-4 flex items-center justify-center rounded-full bg-primeColor text-white">
                  {reduxProducts.length > 0 ? reduxProducts.length : 0}
                </span>
              </div>
            </Link>
          </div>
        </Flex>
      </nav>
    </div>
  );
};

export default Header;
