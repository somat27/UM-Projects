import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

const SignUp = () => {
  const navigate = useNavigate();
  const handleGoBack = () => {
    window.location.href = "/";
  };

  const [formData, setFormData] = useState({
    vat: "",
    name: "",
    phone: "",
    language_id: 1, // Default: Português
    address: "",
    city: "",
    zip_code: "",
    country_id: 1, // Default: Portugal
    maturity_date_id: 2095441, // Default example
    payment_method_id: 2525311, // Default example
  });

  const [error, setError] = useState("");
  const [zipCodeError, setZipCodeError] = useState("");
  const [vatError, setVatError] = useState("");
  const [phoneError, setPhoneError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [checked, setChecked] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === "zip_code") {
      setZipCodeError(""); // Limpar mensagem de erro ao digitar novamente
    }

    if (name === "vat") {
      setVatError(""); // Limpar mensagem de erro ao digitar novamente
    }

    if (name === "phone") {
      setPhoneError("");
    }

    setFormData((prev) => ({ ...prev, [name]: value }));
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

  const handleSignUp = async (e) => {
    e.preventDefault();

    let isValid = true;

    if (!validateZipCode(formData.zip_code)) {
      setZipCodeError("O código postal deve estar no formato 0000-000.");
      isValid = false;
    }

    if (!validatePortugueseNIF(formData.vat)) {
      setVatError("O NIF deve ser um NIF português válido.");
      isValid = false;
    }

    if (!validatePortuguesePhone(formData.phone)) {
      setPhoneError("O número de telemóvel deve ser um número português válido.");
      isValid = false;
    }

    if (!isValid) return;

    try {
      const response = await axios.post(
        "http://localhost:5000/api/moloni/signup",
        formData
      );
      console.log(response);
      if (response.status === 201) {
        setSuccessMsg("Conta criada com sucesso!");
        setTimeout(() => navigate("/signin"), 3000);
      } else {
        setError("Erro ao criar a conta. Tente novamente.");
      }
    } catch (error) {
      console.error("Erro ao criar cliente no Moloni:", error);
      setError("Erro ao criar a conta. Verifique os dados e tente novamente.");
    }
  };

  return (
    <div className="w-full h-screen flex items-center justify-center">
      <div className="w-full lgl:w-[500px] h-full flex flex-col justify-center">
        <div className="mb-4">
          <button
            onClick={handleGoBack}
            className="text-blue-500 hover:underline text-sm absolute top-4 left-4"
          >
            &larr; Voltar para a página inicial
          </button>
        </div>
        {successMsg ? (
          <div className="w-[500px]">
            <p className="w-full px-4 py-10 text-green-500 font-medium font-titleFont">
              {successMsg}
            </p>
            <Link to="/signin">
              <button
                className="w-full h-10 bg-primeColor rounded-md text-gray-200 text-base font-titleFont font-semibold 
                tracking-wide hover:bg-black hover:text-white duration-300"
              >
                Login
              </button>
            </Link>
          </div>
        ) : (
          <form className="w-full w-full h-screen flex items-center justify-center" onSubmit={handleSignUp}>
            <div className="px-6 py-4 w-full h-[90%] flex flex-col justify-center overflow-y-scroll scrollbar-thin scrollbar-thumb-primeColor">
              <h1 className="font-titleFont underline underline-offset-4 decoration-[1px] font-semibold text-2xl mdl:text-3xl mb-4">
                Cria a tua conta
              </h1>
              <div className="flex flex-col gap-3">
                {[
                  { label: "NIF (VAT)", name: "vat", placeholder: "123456789", type: "text", error: vatError },
                  { label: "Nome Completo", name: "name", placeholder: "John Pork", type: "text" },
                  { label: "Número de Telemóvel", name: "phone", placeholder: "912345678", type: "text", error: phoneError },
                  { label: "Morada", name: "address", placeholder: "14 E. Snyder Avenue", type: "text" },
                  { label: "Cidade", name: "city", placeholder: "A tua cidade", type: "text" },
                  { label: "Codigo Postal", name: "zip_code", placeholder: "O teu codigo postal (0000-000)", type: "text", error: zipCodeError },
                ].map((field) => (
                  <div key={field.name} className="flex flex-col gap-.5">
                    <p className="font-titleFont text-base font-semibold text-gray-600">{field.label}</p>
                    <input
                      name={field.name}
                      onChange={handleInputChange}
                      value={formData[field.name]}
                      className="w-full h-8 placeholder:text-sm placeholder:tracking-wide px-4 text-base font-medium placeholder:font-normal rounded-md border-[1px] border-gray-400 outline-none"
                      type={field.type}
                      placeholder={field.placeholder}
                      required
                    />
                    {field.error && (
                      <p className="text-red-500 text-sm mt-1">{field.error}</p>
                    )}
                  </div>
                ))}

                <div className="flex items-start mdl:items-center gap-2">
                  <input
                    onChange={() => setChecked(!checked)}
                    className="w-4 h-4 mt-1 mdl:mt-0 cursor-pointer"
                    type="checkbox"
                  />
                  <p className="text-sm text-primeColor">
                    Eu concordo com os{" "}
                    <span className="text-blue-500">Terms of Service</span> e{" "}
                    <span className="text-blue-500">Privacy Policy</span>.
                  </p>
                </div>
                <button
                  type="submit"
                  className={`${
                    checked
                      ? "bg-primeColor hover:bg-black hover:text-white cursor-pointer"
                      : "bg-gray-500 hover:bg-gray-500 hover:text-gray-200 cursor-none"
                  } w-full text-gray-200 text-base font-medium h-10 rounded-md hover:text-white duration-300`}
                >
                  Criar Conta
                </button>
                <p className="text-sm text-center font-titleFont font-medium">
                  Já tem conta?{" "}
                  <Link to="/signin">
                    <span className="text-blue-600 hover:text-sm duration-300">
                      Login
                    </span>
                  </Link>
                </p>
                {error && (
                  <p className="text-sm text-red-500 text-center font-titleFont font-semibold px-4">
                    <span className="font-bold italic mr-1">!</span>
                    {error}
                  </p>
                )}
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default SignUp;
