import React, { useState, useEffect } from "react";
import axios from "axios";
import Image from "../../components/designLayouts/Image";

const InternalDocumentManagement = () => {
  const [internalDocuments, setInternalDocuments] = useState([]);
  const [, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [showProductsModal, setShowProductsModal] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchInternalDocuments = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/moloni/internal-documents");
        console.log(response);
        setInternalDocuments(response.data.length > 0 ? response.data : []);
      } catch (err) {
        console.error("Erro ao buscar documentos internos do backend:", err);
        setInternalDocuments([]);
      } finally {
        setLoading(false);
      }
    };
    fetchInternalDocuments();
  }, []);

  const fetchProducts = async (documentId) => {
    try {
      setLoadingProducts(true);
      setSelectedDocumentId(documentId);
      const response = await axios.post(`http://localhost:5000/api/moloni/documents/details/${documentId}`);
      setProducts(response.data || []);
      setShowProductsModal(true);
    } catch (error) {
      console.error("Erro ao carregar produtos do documento:", error);
      setProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const formatDate = (dateString) => {
    return dateString.split("T")[0];
  };
  
  const totalDocuments = internalDocuments.length;

  const filteredDocuments = internalDocuments.filter((doc) => {
    const searchTerm = searchQuery.toLowerCase();
  
    return (
      String(doc.number).toLowerCase().includes(searchTerm) ||
      formatDate(doc.date).includes(searchTerm) ||
      doc.entity_name?.toLowerCase().includes(searchTerm) ||
      doc.entity_vat?.toLowerCase().includes(searchTerm) ||
      (doc.status === 1 ? "fechado" : "rascunho").includes(searchTerm) ||
      String(doc.net_value).toLowerCase().includes(searchTerm) ||
      String(doc.gross_value).toLowerCase().includes(searchTerm)
    );
  });     

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Gestão de Documentos Internos - Total: {totalDocuments}</h2>

      {/* Barra de Pesquisa */}
      <div className="my-4">
        <input
          type="text"
          placeholder="Procurar por Número, Data, Cliente, Contribuinte, Status, Total Líquido ou Total Bruto..."
          className="p-2 border border-gray-300 rounded w-full"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Tabela de Documentos Internos */}
      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300 text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 px-4 py-2 text-center w-1/6">Data</th>
              <th className="border border-gray-300 px-4 py-2 text-center w-1/6">Cliente</th>
              <th className="border border-gray-300 px-4 py-2 text-center w-1/6">Contribuinte</th>
              <th className="border border-gray-300 px-4 py-2 text-center w-1/3">Total</th>
              <th className="border border-gray-300 px-4 py-2 text-center w-1/6">Produtos</th>
            </tr>
          </thead>
          <tbody>
            {filteredDocuments.length > 0 ? (
              filteredDocuments.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 text-center">{formatDate(doc.date)}</td>
                  <td className="border border-gray-300 px-4 py-2 text-center">{doc.entity_name}</td>
                  <td className="border border-gray-300 px-4 py-2 text-center">{doc.entity_vat}</td>
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
              ))
            ) : (
              <tr>
                <td colSpan="5" className="text-center text-gray-500 py-4">
                  Nenhum documento disponível.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>




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

export default InternalDocumentManagement;
