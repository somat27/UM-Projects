import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

const SignIn = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [vat, setVat] = useState("");
  const [error, setError] = useState("");

  const handleSignIn = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:5000/api/moloni/signin", {
        name,
        vat,
      });

      if (response.status === 200) {
        const customerData = response.data;
        localStorage.setItem("customerData", JSON.stringify(customerData));
        navigate("/conta");
      } else {
        setError("Nome ou NIF incorretos.");
      }
    } catch (err) {
      console.error("Erro ao fazer login:", err);
      setError("Erro ao fazer login. Tente novamente.");
    }
  };

  return (
    <div className="w-full h-screen flex items-center justify-center">
      <div className="w-full lgl:w-[500px] h-full flex flex-col justify-center">
        <div className="mb-4">
          <button
            onClick={() => (window.location.href = "/")}
            className="text-blue-500 hover:underline text-sm absolute top-4 left-4"
          >
            &larr; Voltar para a página inicial
          </button>
        </div>
        <form
          className="w-full bg-white p-6 shadow-md rounded-lg"
          onSubmit={handleSignIn}
        >
          <h1 className="font-titleFont underline underline-offset-4 decoration-[1px] font-semibold text-3xl mdl:text-4xl mb-4">
            Página de Login
          </h1>
          {error && (
            <p className="text-red-500 text-center mb-4">{error}</p>
          )}
          <div className="flex flex-col gap-4">
            <input
              type="text"
              placeholder="Nome"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full h-10 border border-gray-300 rounded-md px-2"
              required
            />
            <input
              type="text"
              placeholder="NIF (VAT)"
              value={vat}
              onChange={(e) => setVat(e.target.value)}
              className="w-full h-10 border border-gray-300 rounded-md px-2"
              required
            />
            <button
              type="submit"
              className="w-full h-10 bg-primeColor text-white rounded-md text-base font-semibold tracking-wide hover:bg-black hover:text-white duration-300"
            >
              Entrar
            </button>
            <p className="text-sm text-center font-titleFont font-medium">
              Não tem conta?{" "}
              <Link to="/signup" className="text-blue-600 hover:underline">
                Crie agora
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignIn;
