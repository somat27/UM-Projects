import axios from "axios";

const OPENAI_API_KEY = process.env.VUE_APP_OPENAI_API_KEY;
const OPENAI_API_URL = "https://api.openai.com/v1/chat/completions";

export async function obterSugestaoAuditoria(dados) {
  try {
    const { ocorrencia, peritos, materiais, profissionais } = dados;

    if (!ocorrencia || !peritos || !materiais || !profissionais) {
      throw new Error(
        "Missing required input data (ocorrencia, peritos, materiais, profissionais)."
      );
    }

    const hoje = new Date().toISOString().split("T")[0];
    
    const prompt = `
    You are an assistant specialized in audit planning and municipal resource management.

    Today's date is ${hoje}.

    Based on the following data, critically evaluate whether an audit is necessary.
    If yes, propose a detailed audit plan.
    If not, briefly explain why not in the field "motivoNaoNecessidade" of the JSON.

    When selecting the expert (perito), always prefer the one whose location (localidades) is closest to the occurrence address or coordinates.

    ## OCCURRENCE:
    - ID: ${ocorrencia.id}
    - Description: ${ocorrencia.descricao}
    - Type: ${ocorrencia.tipoLabel || ocorrencia.tipo}
    - Address: ${ocorrencia.endereco}
    - Coordinates: Latitude ${ocorrencia.coordenadas.latitude}, Longitude ${ocorrencia.coordenadas.longitude}
    - Criticity: ${ocorrencia.criticidade}

    ## AVAILABLE EXPERTS:
    ${peritos
      .map(
        (p) =>
          `- ID: ${p.uid}, Name: ${p.displayName}, Specialty: ${p.specialty}, Location: ${p.localidades}`
      )
      .join("\n")}

    ## AVAILABLE MATERIALS:
    ${materiais
      .map(
        (m) =>
          `- Name: ${m.nome}, Category: ${m.categoria}, Available Quantity: ${m.quantidade}`
      )
      .join("\n")}

    ## AVAILABLE PROFESSIONALS:
    ${profissionais
      .map(
        (p) =>
          `- Name: ${p.nome}, Area: ${p.area}, Available Quantity: ${p.quantidade}`
      )
      .join("\n")}

    Respond ONLY in JSON with one of the following two structures:

    1. If an audit is required:
    {
      "necessidadeAuditoria": true,
      "perito": "expert_uid",
      "materiais": [
        { "id": "material_id", "quantidade": <number> }
      ],
      "profissionais": [
        { "id": "professional_id", "quantidade": <number> }
      ],
      "tempoEstimado": <hours>,
      "dataFimSugerida": "<YYYY-MM-DD>"
      "criticidadeSugerida": "<1-5>"
    }

    2. If no audit is required:
    {
      "necessidadeAuditoria": false,
      "motivoNaoNecessidade": "Brief explanation why no audit is required."
    }

    Additional instructions:
    - dataFimSugerida must result from adding tempoEstimado (in hours) to the current date/time and then converting to ISO format YYYY-MM-DD.
    - Choose quantities for materiais and profissionais proportional to the needs of the occurrence, not exceeding the available quantities.
    - If a material or professional is not needed, omit it rather than specifying quantity 0.
    - criticidadeSugerida must be an integer from 1 to 5, corresponding to the table above:
      1 = Very Low
      2 = Low
      3 = Medium
      4 = High
      5 = Very High
    - Do not include any explanation outside the JSON.
    `;

    const response = await axios.post(
      OPENAI_API_URL,
      {
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content:
              "You are an assistant specialized in municipal audit planning, with critical thinking to evaluate necessity based on provided data.",
          },
          { role: "user", content: prompt },
        ],
        temperature: 0.3,
        max_tokens: 1200,
        response_format: { type: "json_object" },
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
      }
    );

    const sugestaoStr = response.data?.choices?.[0]?.message?.content;

    if (!sugestaoStr) {
      throw new Error("Empty response from OpenAI API.");
    }

    try {
      const sugestaoJSON = JSON.parse(sugestaoStr);

      return sugestaoJSON;
    } catch (parseError) {
      console.error("Error parsing JSON response:", parseError);
      console.error("Raw response content:", sugestaoStr);
      throw new Error("Invalid JSON format received from OpenAI.");
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Axios error:", error.message);
      if (error.response) {
        console.error("Response data:", error.response.data);
      }
      throw new Error("Error communicating with OpenAI API.");
    } else {
      console.error("General error:", error.message);
      throw error;
    }
  }
}
