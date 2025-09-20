import React, { useState } from "react";
import "react-vertical-timeline-component/style.min.css";
import CustomerManagement from "./CustomerManagement";
import StockManagement from "./StockManagement";
import InvoiceManagement from "./InvoiceManagement";

const Admin = () => {
  const [activeTab, setActiveTab] = useState("stock");

  const renderContent = () => {
    switch (activeTab) {
      case "stock":
        return <StockManagement />;
      case "customers":
        return <CustomerManagement />;
      case "invoices":
        return <InvoiceManagement />;
      default:
        return <StockManagement />;
    }
  };

  const handleGoBack = () => {
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="mb-4">
        <button
          onClick={handleGoBack}
          className="text-blue-500 hover:underline text-sm"
        >
          &larr; Voltar para a página inicial
        </button>
        <h2 className="text-3xl font-bold text-center mb-6">Administração - Voltix</h2>
      </div>

      <div className="flex justify-center space-x-4 mb-6">
        <button
          onClick={() => setActiveTab("stock")}
          className={`px-4 py-2 rounded ${
            activeTab === "stock" ? "bg-blue-500 text-white" : "bg-gray-200"
          }`}
        >
          Gestão de Stock
        </button>
        <button
          onClick={() => setActiveTab("customers")}
          className={`px-4 py-2 rounded ${
            activeTab === "customers" ? "bg-blue-500 text-white" : "bg-gray-200"
          }`}
        >
          Gestão de Clientes
        </button>
        <button
          onClick={() => setActiveTab("invoices")}
          className={`px-4 py-2 rounded ${
            activeTab === "invoices" ? "bg-blue-500 text-white" : "bg-gray-200"
          }`}
        >
          Gestão de Faturas
        </button>
      </div>

      <div className="bg-white p-6 rounded shadow-md">{renderContent()}</div>
    </div>
  );
};

export default Admin;
