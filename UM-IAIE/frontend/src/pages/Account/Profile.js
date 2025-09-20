import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Image from "../../components/designLayouts/Image"

const Profile = () => {
  const [user, setUser] = useState(null);
  const [updatedUser, setUpdatedUser] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [products, setProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [showProductsModal, setShowProductsModal] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [zipCodeError, setZipCodeError] = useState("");
  const [vatError, setVatError] = useState("");
  const [phoneError, setPhoneError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const storedData = localStorage.getItem("customerData");
    if (storedData) {
      const parsedData = JSON.parse(storedData);
      setUser(parsedData);
      setUpdatedUser(parsedData);
    }
  }, []);

  useEffect(() => {
    const fetchDocuments = async () => {
      if (!user) return;
      try {
        setLoadingDocuments(true);
        const response = await axios.post(`http://localhost:5000/api/moloni/documents/${user.customer_id}`);
        console.log(response);
        setDocuments(response.data || []);
      } catch (error) {
        console.error("Erro ao carregar documentos:", error);
        setDocuments([]);
      } finally {
        setLoadingDocuments(false);
      }
    };

    fetchDocuments();
  }, [user]);

  const fetchProducts = async (documentId) => {
    try {
      setLoadingProducts(true);
      setSelectedDocumentId(documentId);
      const response = await axios.post(`http://localhost:5000/api/moloni/documents/details/${documentId}`);
      console.log(response);
      setProducts(response.data || []);
      setShowProductsModal(true);
    } catch (error) {
      console.error("Erro ao carregar produtos do documento:", error);
      setProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("customerData");
    navigate("/signin");
  };

  const handleSaveChanges = async () => {
    let isValid = true;

    // Validação do código postal
    if (!validateZipCode(updatedUser.zip_code)) {
      setZipCodeError("O código postal deve estar no formato 0000-000.");
      isValid = false;
    } else {
      setZipCodeError("");
    }

    // Validação do NIF
    if (!validatePortugueseNIF(updatedUser.vat)) {
      setVatError("O NIF deve ser um NIF português válido.");
      isValid = false;
    } else {
      setVatError("");
    }

    // Validação do número de telemóvel
    if (!validatePortuguesePhone(updatedUser.phone)) {
      setPhoneError("O número de telemóvel deve ser um número português válido.");
      isValid = false;
    } else {
      setPhoneError("");
    }

    if (!isValid) return;

    try {
      const updatedData = {
        company_id: 322336,
        customer_id: user.customer_id,
        vat: updatedUser.vat || user.vat,
        number: user.number,
        name: updatedUser.name,
        language_id: 1,
        address: updatedUser.address,
        city: updatedUser.city,
        zip_code: updatedUser.zip_code,
        country_id: 1,
        email: updatedUser.email || "",
        phone: updatedUser.phone || "",
        maturity_date_id: 2095441,
        payment_method_id: 2525311,
        document_type_id: 123456,
        copies: 1,
      };

      const response = await axios.post("http://localhost:5000/api/moloni/customers/update", updatedData);

      if (response.status === 200) {
        alert("Informações atualizadas com sucesso!");
        localStorage.setItem("customerData", JSON.stringify(updatedUser));
        setUser(updatedUser);
        setEditMode(false);
      } else {
        alert("Erro ao salvar informações no Moloni.");
      }
    } catch (error) {
      console.error("Erro ao salvar informações no Moloni:", error);
      alert("Erro ao tentar salvar as informações.");
    }
  };

  const formatDate = (dateString) => {
    return dateString.split("T")[0];
  };

  const validateZipCode = (zipCode) => {
    const zipCodePattern = /^\d{4}-\d{3}$/;
    return zipCodePattern.test(zipCode);
  };

  const validatePortugueseNIF = (vat) => {
    const vatPattern = /^\d{9}$/;
    if (!vatPattern.test(vat)) return false;

    const firstDigit = parseInt(vat[0], 10);
    if (![1, 2, 3, 5, 6, 7, 8, 9].includes(firstDigit)) return false;

    let sum = 0;
    for (let i = 0; i < 8; i++) {
      sum += parseInt(vat[i], 10) * (9 - i);
    }

    const checkDigit = 11 - (sum % 11);
    return checkDigit === parseInt(vat[8], 10) || (checkDigit >= 10 && parseInt(vat[8], 10) === 0);
  };

  const validatePortuguesePhone = (phone) => {
    const phonePattern = /^(91|92|93|96|97|98|99)\d{7}$/;
    return phonePattern.test(phone);
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Carregando informações do cliente...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="mb-4 flex justify-between items-center">
        <button onClick={() => navigate("/")} className="text-blue-500 hover:underline text-sm">
          &larr; Voltar para a página inicial
        </button>
        <button onClick={handleLogout} className="text-red-500 hover:underline text-sm">
          Sair da Conta
        </button>
      </div>

      <div className="max-w-4xl mx-auto bg-white p-8 rounded shadow-lg">
        <h1 className="text-3xl font-bold mb-6 text-center">Meu Perfil</h1>

        <div className="mb-8 text-gray-700">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold mb-4">Informações do Cliente</h2>
            <button onClick={() => setEditMode(true)} className="text-blue-500 hover:underline text-sm">
              Editar Informações
            </button>
          </div>
          <p className="mb-2"><strong>Nome:</strong> {user.name}</p>
          <p className="mb-2"><strong>NIF:</strong> {user.vat}</p>
          <p className="mb-2"><strong>Morada:</strong> {user.address}</p>
          <p className="mb-2"><strong>Cidade:</strong> {user.city}</p>
          <p className="mb-2"><strong>Código Postal:</strong> {user.zip_code || "N/A"}</p>
          <p className="mb-2"><strong>Telefone:</strong> {user.phone || "N/A"}</p>
        </div>

        <div className="text-gray-700">
          <h2 className="text-xl font-semibold mb-4">Documentos Associados</h2>
          {loadingDocuments ? (
            <p className="text-center">Carregando documentos...</p>
          ) : documents.length === 0 ? (
            <p className="text-center text-gray-500">Nenhum documento encontrado.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full border border-gray-300 text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="border border-gray-300 px-4 py-2 text-center w-1/4">Data</th>
                    <th className="border border-gray-300 px-4 py-2 text-center w-1/2">Preço Total</th>
                    <th className="border border-gray-300 px-4 py-2 text-center w-1/4">Produtos</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 text-center">{formatDate(doc.date)}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center font-semibold">{doc.net_value.toFixed(2)}€</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        <button
                          onClick={() => fetchProducts(doc.document_id)}
                          className="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600 transition duration-300"
                        >
                          Ver Detalhes
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal para editar informações */}
      {editMode && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div
            className="bg-white p-6 rounded shadow-lg relative"
            style={{
              width: "80%",
              maxWidth: "900px",
            }}
          >
            <button
              onClick={() => setEditMode(false)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
            <h2 className="text-xl font-bold mb-4">Editar Informações</h2>
            <div className="relative mb-4">
              <input
                type="text"
                placeholder=""
                value={updatedUser.name || ""}
                onChange={(e) => setUpdatedUser({ ...updatedUser, name: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded pr-16"
              />
              <span className="absolute top-1/2 right-4 transform -translate-y-1/2 text-gray-500 text-sm">Nome</span>
            </div>

            <div className="relative mb-4">
              <input
                type="text"
                placeholder=""
                value={updatedUser.vat || ""}
                onChange={(e) => setUpdatedUser({ ...updatedUser, vat: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded pr-16"
              />
              <span className="absolute top-1/2 right-4 transform -translate-y-1/2 text-gray-500 text-sm">NIF</span>
              {vatError && <p className="text-red-500 text-sm mb-2">{vatError}</p>}
            </div>

            <div className="relative mb-4">
              <input
                type="text"
                placeholder=""
                value={updatedUser.address || ""}
                onChange={(e) => setUpdatedUser({ ...updatedUser, address: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded pr-16"
              />
              <span className="absolute top-1/2 right-4 transform -translate-y-1/2 text-gray-500 text-sm">Morada</span>
            </div>

            <div className="relative mb-4">
              <input
                type="text"
                placeholder=""
                value={updatedUser.city || ""}
                onChange={(e) => setUpdatedUser({ ...updatedUser, city: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded pr-16"
              />
              <span className="absolute top-1/2 right-4 transform -translate-y-1/2 text-gray-500 text-sm">Cidade</span>
            </div>

            <div className="relative mb-4">
              <input
                type="text"
                placeholder=""
                value={updatedUser.zip_code || ""}
                onChange={(e) => setUpdatedUser({ ...updatedUser, zip_code: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded pr-16"
              />
              <span className="absolute top-1/2 right-4 transform -translate-y-1/2 text-gray-500 text-sm">Código Postal</span>
              {zipCodeError && <p className="text-red-500 text-sm mb-2">{zipCodeError}</p>}
            </div>

            <div className="relative mb-4">
              <input
                type="text"
                placeholder=""
                value={updatedUser.phone || ""}
                onChange={(e) => setUpdatedUser({ ...updatedUser, phone: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded pr-16"
              />
              <span className="absolute top-1/2 right-4 transform -translate-y-1/2 text-gray-500 text-sm">Telefone</span>
              {phoneError && <p className="text-red-500 text-sm mb-2">{phoneError}</p>}
            </div>

            <button onClick={handleSaveChanges} className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
              Salvar
            </button>
          </div>
        </div>
      )}

      {/* Modal para Visualizar Produtos */}
      {showProductsModal && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg relative" style={{ width: "80%", maxWidth: "900px" }}>
            <button onClick={() => setShowProductsModal(false)} className="absolute top-4 right-4 text-gray-500 hover:text-gray-700">
              ✕
            </button>
            <h2 className="text-2xl font-bold mb-4">Produtos do Documento #{selectedDocumentId}</h2>
            {loadingProducts ? (
              <p className="text-center">Carregando produtos...</p>
            ) : products.length === 0 ? (
              <p className="text-center text-gray-500">Nenhum produto encontrado.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-300">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border border-gray-300 px-4 py-2 text-left">Imagem</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Nome</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Quantidade</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Preço Unitário</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Total s/ IVA</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Total c/ IVA</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((product, index) => {
                      const totalWithoutVAT = product.qty * product.price;
                      const totalWithVAT = totalWithoutVAT * 1.23; // Considerando IVA de 23%
                      return (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="border border-gray-300 px-4 py-2">
                            <Image className="w-20 object-cover" imgSrc={product.summary} />
                          </td>
                          <td className="border border-gray-300 px-4 py-2">{product.name}</td>
                          <td className="border border-gray-300 px-4 py-2">{product.qty}</td>
                          <td className="border border-gray-300 px-4 py-2">{product.price.toFixed(2)}€</td>
                          <td className="border border-gray-300 px-4 py-2">{totalWithoutVAT.toFixed(2)}€</td>
                          <td className="border border-gray-300 px-4 py-2">{totalWithVAT.toFixed(2)}€</td>
                        </tr>
                      );
                    })}
                    {/* Linha de Totais */}
                    <tr className="font-bold bg-gray-100">
                      <td colSpan="4" className="border border-gray-300 px-4 py-2 text-right">Total:</td>
                      <td className="border border-gray-300 px-4 py-2">
                        {products
                          .reduce((sum, product) => sum + product.qty * product.price, 0)
                          .toFixed(2)}€
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {products
                          .reduce((sum, product) => sum + product.qty * product.price * 1.23, 0)
                          .toFixed(2)}€
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
