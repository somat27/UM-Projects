import React, { useState, useEffect } from "react";
import axios from "axios";

const CustomerManagement = () => {
  const [customers, setCustomers] = useState([]);
  const [, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [editCustomer, setEditCustomer] = useState(null);

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/moloni/customers");
        setCustomers(response.data.length > 0 ? response.data : []);
      } catch (err) {
        console.error("Erro ao buscar clientes do backend:", err);
        setCustomers([]);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.name?.toLowerCase().includes(search.toLowerCase()) ||
      customer.email?.toLowerCase().includes(search.toLowerCase()) ||
      customer.phone?.toLowerCase().includes(search.toLowerCase())
  );

  const totalCustomers = customers.length;

  const handleSaveChanges = async () => {
    if (!editCustomer) return;

    try {
      const payload = {
        company_id: 322336,
        customer_id: editCustomer.customer_id,
        vat: editCustomer.vat,
        number: editCustomer.number,
        name: editCustomer.name,
        language_id: 1,
        address: editCustomer.address,
        city: editCustomer.city,
        zip_code: editCustomer.zip_code,
        country_id: 1,
        email: editCustomer.email || "",
        phone: editCustomer.phone || "",
        maturity_date_id: 2095441,
        payment_method_id: 2525311,
        document_type_id: 123456,
        copies: 1,
      };

      const response = await axios.post("http://localhost:5000/api/moloni/customers/update", payload);

      if (response.status === 200) {
        alert("Cliente atualizado com sucesso!");
        setCustomers((prevCustomers) =>
          prevCustomers.map((customer) =>
            customer.customer_id === editCustomer.customer_id ? editCustomer : customer
          )
        );
        setEditCustomer(null);
      } else {
        alert(`Erro ao atualizar cliente: ${response.data.error}`);
      }
    } catch (error) {
      console.error("Erro ao atualizar cliente:", error);
      alert("Erro ao tentar atualizar o cliente.");
    }
  };

  const handleRemoveCustomer = async (customerId) => {
    if (!window.confirm("Tem certeza de que deseja remover este cliente?")) {
      return;
    }
  
    try {
      const payload = {
        company_id: 322336,
        customer_id: customerId,
      };
  
      const response = await axios.post("http://localhost:5000/api/moloni/customers/delete",payload);
  
      if (response.status === 200) {
        alert("Cliente removido com sucesso!");
        setCustomers((prevCustomers) =>
          prevCustomers.filter((customer) => customer.customer_id !== customerId)
        );
        setEditCustomer(null);
      } else {
        alert(`Erro ao remover cliente: ${response.data.error}`);
      }
    } catch (error) {
      console.error("Erro ao remover cliente:", error);
      alert("Erro ao tentar remover o cliente.");
    }
  };
  

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Gestão de Clientes - Total: {totalCustomers}</h2>

      {/* Barra de Pesquisa */}
      <div className="flex items-center mb-4">
        <input
          type="text"
          placeholder="Procurar cliente por nome, email ou telefone..."
          className="p-2 border border-gray-300 rounded w-full"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Tabela de Clientes */}
      <table className="table-auto w-full border-collapse border border-gray-300 mb-6">
        <thead className="bg-gray-200">
          <tr>
            <th className="border border-gray-300 px-4 py-2 text-center">Nome</th>
            <th className="border border-gray-300 px-4 py-2 text-center">Email</th>
            <th className="border border-gray-300 px-4 py-2 text-center">Telefone</th>
            <th className="border border-gray-300 px-4 py-2 text-center">Endereço</th>
            <th className="border border-gray-300 px-4 py-2 text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          {filteredCustomers.length > 0 ? (
            filteredCustomers.map((customer) => (
              <tr key={customer.customer_id}>
                <td className="border border-gray-300 px-4 py-2 text-center">{customer.name}</td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  {customer.email || customer.contact_email || "N/A"}
                </td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  {customer.phone || customer.contact_phone || "N/A"}
                </td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  {`${customer.address}, ${customer.city}, ${customer.zip_code}`}
                </td>
                <td className="border border-gray-300 px-4 py-2 text-center">
                  <button
                    onClick={() => setEditCustomer(customer)}
                    className="bg-yellow-500 text-white px-2 py-1 rounded"
                  >
                    Editar
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6" className="text-center text-gray-500 py-4">
                Nenhum cliente disponível.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Modal de Edição */}
      {editCustomer && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div
            className="bg-white p-6 rounded shadow-lg relative"
            style={{
              width: "80%",
              maxWidth: "900px",
            }}
          >
            {/* Botão de Fechar */}
            <button
              onClick={() => setEditCustomer(null)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>

            <h3 className="text-lg font-bold mb-4">Editar Cliente</h3>
            <div className="grid gap-4">
              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editCustomer.name || ""}
                  onChange={(e) => setEditCustomer({ ...editCustomer, name: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Nome
                </span>
              </div>
              <div className="relative">
                <input
                  type="email"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editCustomer.email || editCustomer.contact_email || ""}
                  onChange={(e) => setEditCustomer({ ...editCustomer, email: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Email
                </span>
              </div>
              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editCustomer.phone || editCustomer.contact_phone || ""}
                  onChange={(e) => setEditCustomer({ ...editCustomer, phone: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Telefone
                </span>
              </div>
              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editCustomer.address || ""}
                  onChange={(e) => setEditCustomer({ ...editCustomer, address: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Endereço
                </span>
              </div>
              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editCustomer.city || ""}
                  onChange={(e) => setEditCustomer({ ...editCustomer, city: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Cidade
                </span>
              </div>
              <div className="relative">
                <input
                  type="text"
                  className="p-2 border border-gray-300 rounded w-full pr-16"
                  value={editCustomer.zip_code || ""}
                  onChange={(e) => setEditCustomer({ ...editCustomer, zip_code: e.target.value })}
                />
                <span className="absolute top-1/2 right-3 transform -translate-y-1/2 text-gray-500 text-sm">
                  Código Postal
                </span>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={handleSaveChanges}
                className="bg-green-500 text-white px-4 py-2 rounded"
              >
                Salvar
              </button>
              <button
                onClick={() => handleRemoveCustomer(editCustomer.customer_id)}
                className="bg-red-500 text-white px-4 py-2 rounded"
              >
                Remover
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomerManagement;
