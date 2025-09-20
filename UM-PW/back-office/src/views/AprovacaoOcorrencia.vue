<template>
  <div class="dashboard-container">
    <div class="dashboard-layout">
      <aside class="sidebar-column">
        <nav class="sidebar-nav">
          <div class="sidebar-background">
            <NavigationList />
          </div>
        </nav>
      </aside>
      <main class="main-content">
        <div class="content-wrapper">
          <div class="page-header">
            <h2>Plano de Auditoria</h2>
          </div>
          <div class="audit-form">
            <div class="form-group">
              <label>Descrição</label>
              <textarea v-model="ocorrencia.descricao" disabled class="input"></textarea>
            </div>
            <div class="form-group">
              <label>Tipo de Ocorrência</label>
              <input :value="tipoLabels[ocorrencia.tipoOcorrencia] ||
                ocorrencia.tipoOcorrencia
                " disabled class="input" />
            </div>
            <div class="form-group">
              <label>Endereço</label>
              <input v-model="ocorrencia.endereco" disabled class="input" />
            </div>

            <div class="map-container">
              <iframe :src="mapUrl" width="100%" height="100%" frameborder="0" style="border: 0" allowfullscreen
                loading="lazy"></iframe>
            </div>

            <div class="suggestion-section">
              <button @click="pedirSugestao" class="btn btn-primary suggestion-btn" :disabled="sugestaoLoading">
                <span v-if="!sugestaoLoading"> Pedir Sugestão </span>
                <span v-else class="loading-spinner">
                  <span class="spinner"></span>
                  Gerando...
                </span>
              </button>

              <transition name="fade">
                <div v-if="sucessoSugestao" class="success-toast">
                  <i class="check-icon"></i>
                  <span>Sugestão aplicada com sucesso!</span>
                </div>
              </transition>
            </div>

            <transition name="slide">
              <div v-if="sugestao" class="suggestion-result">
                <div class="suggestion-header">
                  <h3><i class="lightbulb-icon"></i> Sugestão do Sistema</h3>
                  <span class="badge">IA</span>
                </div>
                <div class="suggestion-content">
                  <p>{{ sugestao }}</p>
                </div>
              </div>
            </transition>

            <div class="section-divider"></div>

            <h3 class="section-title">Seleção de Perito</h3>
            <GenericTable :columns="columnsPeritos" :data="peritosList" class="table-scroll">
              <template #cell-select="{ row }">
                <div class="radio-container">
                  <input type="radio" name="perito" :value="row.uid" v-model="selectedPerito"
                    id="perito-radio-{{ row.uid }}" />
                  <span class="radio-checkmark"></span>
                </div>
              </template>
            </GenericTable>

            <div class="section-divider"></div>
            <div class="form-group">
              <h3>Nível de Criticidade</h3>
              <div class="criticality-selector">
                <div v-for="level in criticalityLevels" :key="level.value" class="criticality-option" :class="{
                  'selected': selectedCriticality === level.value,
                  [`level-${level.value}`]: true
                }" @click="selectedCriticality = level.value">
                  <div class="criticality-number">{{ level.value }}</div>
                  <div class="criticality-info">
                    <div class="criticality-label">{{ level.label }}</div>
                    <div class="criticality-description">{{ level.description }}</div>
                  </div>
                  <div class="criticality-indicator">
                    <div class="indicator-bar" :style="{ width: (level.value * 20) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>

            <h3 class="section-title">Seleção de Materiais</h3>
            <GenericTable :columns="columnsMateriais" :data="materiaisList" class="table-scroll">
              <template #cell-qtd="{ row }">
                <div class="quantity-input">
                  <button class="qty-btn minus" @click="decrementQty(row)" :disabled="row.qtd <= 0">
                    −
                  </button>
                  <input type="number" min="0" :max="row.quantidade" v-model.number="row.qtd" @input="
                    row.qtd =
                    row.qtd > row.quantidade ? row.quantidade : row.qtd
                    " class="input qty-input" />
                  <button class="qty-btn plus" @click="incrementQty(row)" :disabled="row.qtd >= row.quantidade">
                    +
                  </button>
                </div>
              </template>
            </GenericTable>

            <h3 class="section-title">Seleção de Profissionais</h3>
            <GenericTable :columns="columnsProfissionais" :data="profissionaisList" class="table-scroll">
              <template #cell-qtd="{ row }">
                <div class="quantity-input">
                  <button class="qty-btn minus" @click="decrementQty(row)" :disabled="row.qtd <= 0">
                    −
                  </button>
                  <input type="number" min="0" :max="row.quantidade" v-model.number="row.qtd" @input="
                    row.qtd =
                    row.qtd > row.quantidade ? row.quantidade : row.qtd
                    " class="input qty-input" />
                  <button class="qty-btn plus" @click="incrementQty(row)" :disabled="row.qtd >= row.quantidade">
                    +
                  </button>
                </div>
              </template>
            </GenericTable>

            <div class="schedule-section">
              <div class="form-group">
                <label>Data de Fim de Obra</label>
                <input type="date" v-model="deadline" class="input date-input" />
              </div>
              <div class="form-group">
                <label>Tempo Estimado (horas)</label>
                <div class="time-input">
                  <input type="number" v-model.number="estimatedTime" class="input" />
                  <span class="time-unit">horas</span>
                </div>
              </div>
            </div>

            <button @click="submitAuditoria" class="btn btn-submit">
              Aprovar Ocorrência
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import NavigationList from "@/components/NavigationList.vue";
import GenericTable from "@/components/GenericTable.vue";
import {
  doc,
  getDoc,
  collection,
  getDocs,
  setDoc,
  updateDoc,
  query,
  where,
} from "firebase/firestore";
import { db } from "@/firebase";
import { obterSugestaoAuditoria } from "../openai_service";

const route = useRoute();
const router = useRouter();
const ocorrencia = ref({
  descricao: "",
  tipoOcorrencia: "",
  endereco: "",
  coordenadas: { latitude: 0, longitude: 0 },
});
const peritosList = ref([]);
const materiaisList = ref([]);
const profissionaisList = ref([]);
const selectedPerito = ref(null);
const deadline = ref("");
const estimatedTime = ref(0);
const sugestao = ref("");
const sugestaoLoading = ref(false);
const sucessoSugestao = ref(false);

const selectedCriticality = ref(null);

const criticalityLevels = [
  {
    value: 1,
    label: "Muito Baixa",
    description: "Sem urgência, pode aguardar"
  },
  {
    value: 2,
    label: "Baixa",
    description: "Resolução em alguns dias"
  },
  {
    value: 3,
    label: "Média",
    description: "Atenção necessária em breve"
  },
  {
    value: 4,
    label: "Alta",
    description: "Requer resposta rápida"
  },
  {
    value: 5,
    label: "Muito Alta",
    description: "Resposta imediata necessária"
  }
];

const tipoLabels = {
  sinals: "Sinalização em Falta",
  roads: "Vias e Passeios",
  lights: "Iluminação Pública",
};

const columnsPeritos = [
  { key: "select", label: "" },
  { key: "displayName", label: "Nome" },
  { key: "specialty", label: "Especialidade" },
  { key: "localidades", label: "Localidade" },
];
const columnsMateriais = [
  { key: "nome", label: "Nome" },
  { key: "categoria", label: "Categoria" },
  { key: "quantidade", label: "Disponível" },
  { key: "qtd", label: "Qtd Requerida" },
];
const columnsProfissionais = [
  { key: "nome", label: "Nome" },
  { key: "area", label: "Área" },
  { key: "quantidade", label: "Disponível" },
  { key: "qtd", label: "Qtd Requerida" },
];

const mapUrl = computed(() => {
  const { latitude, longitude } = ocorrencia.value.coordenadas;
  return `https://www.google.com/maps?q=${latitude},${longitude}&hl=pt&z=15&output=embed`;
});

function incrementQty(row) {
  if (row.qtd < row.quantidade) {
    row.qtd++;
  }
}

function decrementQty(row) {
  if (row.qtd > 0) {
    row.qtd--;
  }
}

async function loadData() {
  const id = route.params.id;
  // Ocorrência
  const ocRef = doc(db, "ocorrencias", id);
  const ocSnap = await getDoc(ocRef);
  if (ocSnap.exists()) {
    ocorrencia.value = ocSnap.data();
    if (ocorrencia.value.criticidade) {
      selectedCriticality.value = ocorrencia.value.criticidade;
    }
  }

  // Peritos
  const peritosQuery = query(
    collection(db, "peritos"),
    where("status", "==", "Ativo")
  );
  const peritosSnap = await getDocs(peritosQuery);
  const peritosData = peritosSnap.docs.map((d) => ({ uid: d.id, ...d.data() }));

  // 2. Buscamos todos os users com role = 'perito'
  const usersQuery = query(
    collection(db, "users"),
    where("role", "==", "perito")
  );
  const usersSnap = await getDocs(usersQuery);
  const userIds = usersSnap.docs.map((d) => d.id);

  // 3. Filtramos só os peritos cujo UID está na lista dos users-perito
  peritosList.value = peritosData.filter((p) => userIds.includes(p.uid));

  const auditoriasSnap = await getDocs(collection(db, "auditorias"));
  const listaDePeritos = auditoriasSnap.docs.filter(doc => doc.data().status !== "Concluido").flatMap(doc => doc.data().perito)
  //.map(doc => doc.data().filter(a => a.status !== 'Concluido').perito);

  console.log(listaDePeritos)

  const contagens = {};
  listaDePeritos.forEach(uid => {
    contagens[uid] = (contagens[uid] || 0) + 1;
  });

  peritosList.value = peritosList.value.filter(perito => {
    return (contagens[perito.uid] || 0) < 3;
  });

  // Materiais
  const matSnap = await getDocs(collection(db, "materiais"));
  materiaisList.value = matSnap.docs.map((d) => ({
    id: d.id,
    ...d.data(),
    qtd: 0,
  }));

  // Profissionais
  const profSnap = await getDocs(collection(db, "profissionais"));
  profissionaisList.value = profSnap.docs.map((d) => ({
    id: d.id,
    ...d.data(),
    qtd: 0,
  }));
}

async function pedirSugestao() {
  try {
    sugestaoLoading.value = true;
    sugestao.value = "";
    sucessoSugestao.value = false;

    // Preparar dados para enviar ao serviço OpenAI
    const dadosSugestao = {
      ocorrencia: {
        id: route.params.id,
        descricao: ocorrencia.value.descricao,
        tipo: ocorrencia.value.tipoOcorrencia,
        endereco: ocorrencia.value.endereco,
        coordenadas: ocorrencia.value.coordenadas,
        criticidade: selectedCriticality.value,
      },
      peritos: peritosList.value,
      materiais: materiaisList.value,
      profissionais: profissionaisList.value,
    };

    // Chamar o serviço OpenAI para obter sugestões
    const resposta = await obterSugestaoAuditoria(dadosSugestao);

    // Verificar se a resposta é um JSON ou texto
    let respostaObj;
    if (typeof resposta === "string") {
      try {
        respostaObj = JSON.parse(resposta);
      } catch (e) {
        // Se não conseguir fazer parse, usar como texto
        sugestao.value = resposta;
        return;
      }
    } else {
      respostaObj = resposta;
    }

    console.log("Resposta recebida:", respostaObj);

    // Aplicar as sugestões recebidas aos campos do formulário
    if (respostaObj) {
      if (respostaObj.motivoNaoNecessidade) {
        sugestao.value = respostaObj.motivoNaoNecessidade;
        return;
      }
      // Selecionar o perito sugerido
      if (respostaObj.perito) {
        console.log("ID do perito sugerido:", respostaObj.perito);
        console.log(
          "Lista de peritos disponíveis:",
          peritosList.value.map((p) => ({ uid: p.uid, nome: p.displayName }))
        );

        // Verificar se o ID existe diretamente na lista
        const peritoExiste = peritosList.value.some(
          (p) => p.uid === respostaObj.perito
        );
        console.log("Perito existe na lista?", peritoExiste);

        // Definir o perito selecionado
        selectedPerito.value = respostaObj.perito;
      }

      // Aplicar materiais sugeridos
      if (respostaObj.materiais && Array.isArray(respostaObj.materiais)) {
        // Resetar qtd para todos os materiais
        materiaisList.value.forEach((material) => (material.qtd = 0));

        // Aplicar as qtds sugeridas
        respostaObj.materiais.forEach((materialSugerido) => {
          // Procurar por correspondência exata em id e nome
          let encontrado = false;

          for (const material of materiaisList.value) {
            // Verificar correspondência exata
            if (
              material.id === materialSugerido.id ||
              material.nome === materialSugerido.id
            ) {
              material.qtd = Math.min(
                materialSugerido.quantidade,
                material.quantidade
              );
              encontrado = true;
              break;
            }

            // Verificar se contém as palavras-chave
            if (!encontrado) {
              const idSugeridoLower = materialSugerido.id.toLowerCase();
              const idMaterialLower = material.id.toLowerCase();
              const nomeMaterialLower = material.nome
                ? material.nome.toLowerCase()
                : "";

              if (
                idMaterialLower.includes(idSugeridoLower) ||
                idSugeridoLower.includes(idMaterialLower) ||
                (nomeMaterialLower &&
                  nomeMaterialLower.includes(idSugeridoLower)) ||
                (nomeMaterialLower &&
                  idSugeridoLower.includes(nomeMaterialLower))
              ) {
                material.qtd = Math.min(
                  materialSugerido.quantidade,
                  material.quantidade
                );
                encontrado = true;
                break;
              }
            }
          }

          console.log(
            `Material ${materialSugerido.id}: ${encontrado ? "Encontrado" : "Não encontrado"
            }`
          );
        });
      }

      // Aplicar profissionais sugeridos
      if (
        respostaObj.profissionais &&
        Array.isArray(respostaObj.profissionais)
      ) {
        // Resetar qtd para todos os profissionais
        profissionaisList.value.forEach(
          (profissional) => (profissional.qtd = 0)
        );

        // Aplicar as qtds sugeridas
        respostaObj.profissionais.forEach((profissionalSugerido) => {
          // Procurar por correspondência exata em id e nome
          let encontrado = false;

          for (const profissional of profissionaisList.value) {
            // Verificar correspondência exata
            if (
              profissional.id === profissionalSugerido.id ||
              profissional.nome === profissionalSugerido.id
            ) {
              profissional.qtd = Math.min(
                profissionalSugerido.quantidade,
                profissional.quantidade
              );
              encontrado = true;
              break;
            }

            // Verificar se contém as palavras-chave
            if (!encontrado) {
              const idSugeridoLower = profissionalSugerido.id.toLowerCase();
              const idProfissionalLower = profissional.id.toLowerCase();
              const nomeProfissionalLower = profissional.nome
                ? profissional.nome.toLowerCase()
                : "";

              if (
                idProfissionalLower.includes(idSugeridoLower) ||
                idSugeridoLower.includes(idProfissionalLower) ||
                (nomeProfissionalLower &&
                  nomeProfissionalLower.includes(idSugeridoLower)) ||
                (nomeProfissionalLower &&
                  idSugeridoLower.includes(nomeProfissionalLower))
              ) {
                profissional.qtd = Math.min(
                  profissionalSugerido.quantidade,
                  profissional.quantidade
                );
                encontrado = true;
                break;
              }
            }
          }

          console.log(
            `Profissional ${profissionalSugerido.id}: ${encontrado ? "Encontrado" : "Não encontrado"
            }`
          );
        });
      }

      // Aplicar tempo estimado
      if (respostaObj.tempoEstimado) {
        estimatedTime.value = respostaObj.tempoEstimado;
      }

      // Aplicar data fim sugerida
      if (respostaObj.dataFimSugerida) {
        deadline.value = respostaObj.dataFimSugerida;
      }

      // Aplicar nivel de criticidade
      if (respostaObj.criticidadeSugerida) {
        selectedCriticality.value = respostaObj.criticidadeSugerida;
      }

      // Encontrar nome do perito selecionado
      const peritoSelecionado = peritosList.value.find(
        (p) => p.uid === selectedPerito.value
      );
      const nomePerito = peritoSelecionado
        ? peritoSelecionado.displayName
        : "Não especificado";

      // Contar materiais e profissionais aplicados
      const materiaisAplicados = materiaisList.value.filter(
        (m) => m.qtd > 0
      ).length;
      const profissionaisAplicados = profissionaisList.value.filter(
        (p) => p.qtd > 0
      ).length;

      // Gerar texto resumo da sugestão
      sugestao.value = `Sugestão gerada com base na ocorrência:
      - Perito: ${nomePerito} (ID: ${selectedPerito.value || "não selecionado"})
      - Criticidade: ${selectedCriticality.value}
      - Materiais: ${materiaisAplicados} de ${materiaisList.value?.length || 0} sugeridos
      - Profissionais aplicados: ${profissionaisAplicados} de ${profissionaisList.value?.length || 0} sugeridos
      - Tempo estimado: ${estimatedTime.value} horas
      - Data fim: ${deadline.value}`;

      // Mostrar mensagem de sucesso
      sucessoSugestao.value = true;
      setTimeout(() => {
        sucessoSugestao.value = false;
      }, 5000); // Ocultar após 5 segundos
    }
  } catch (error) {
    console.error("Erro ao obter sugestão:", error);
    sugestao.value =
      "Ocorreu um erro ao gerar a sugestão. Por favor, tente novamente.";
  } finally {
    sugestaoLoading.value = false;
  }
}

async function submitAuditoria() {
  try {
    const id = route.params.id;

    // Atualizar status da ocorrência
    const ocRef = doc(db, "ocorrencias", id);
    await updateDoc(ocRef, { status: "Analise" });

    // Preparar dados da auditoria
    const auditoria = {
      descricao: ocorrencia.value.descricao || "",
      tipo: ocorrencia.value.tipoOcorrencia || "",
      endereco: ocorrencia.value.endereco || "",
      coordenadas: ocorrencia.value.coordenadas || {
        latitude: 0,
        longitude: 0,
      },
      perito: selectedPerito.value || null,
      dataInicio: new Date(),
      tempoEstimado:
        typeof estimatedTime.value === "number" ? estimatedTime.value : 0,
      status: "Incompleto",
      criticidade: selectedCriticality.value || null,
    };

    if (deadline.value) {
      auditoria.dataFim = new Date(deadline.value);
    }

    // Converter o array de links de imagens/vídeos para o formato desejado
    if (
      ocorrencia.value.imagemVideo &&
      Array.isArray(ocorrencia.value.imagemVideo)
    ) {
      auditoria.imagemVideo = ocorrencia.value.imagemVideo.map((url) => {
        // Determinar o tipo baseado na extensão do arquivo
        let tipo = "image/jpeg"; // valor padrão
        if (url.toLowerCase().endsWith(".png")) {
          tipo = "image/png";
        } else if (
          url.toLowerCase().endsWith(".jpeg") ||
          url.toLowerCase().endsWith(".jpg")
        ) {
          tipo = "image/jpeg";
        } else if (url.toLowerCase().endsWith(".mp4")) {
          tipo = "video/mp4";
        } else if (url.toLowerCase().endsWith(".webm")) {
          tipo = "video/webm";
        } else if (url.toLowerCase().endsWith(".mov")) {
          tipo = "video/quicktime";
        }

        return {
          tipo: tipo,
          url: url,
        };
      });
    }

    // NOVO: Processar materiais - desconto no estoque e adição à auditoria
    const materiaisPromises = [];
    const materiaisAuditoria = [];

    for (const material of materiaisList.value.filter(
      (m) => Number(m.qtd) > 0
    )) {
      const materialRef = doc(db, "materiais", material.id);

      // Adicionar à lista de materiais da auditoria
      materiaisAuditoria.push({
        id: material.id,
        nome: material.nome,
        quantidade: Number(material.qtd),
      });

      // Descontar do estoque na base de dados
      materiaisPromises.push(
        updateDoc(materialRef, {
          quantidade: material.quantidade - Number(material.qtd),
        })
      );
    }

    // NOVO: Processar profissionais - desconto na disponibilidade e adição à auditoria
    const profissionaisPromises = [];
    const profissionaisAuditoria = [];

    for (const profissional of profissionaisList.value.filter(
      (p) => Number(p.qtd) > 0
    )) {
      const profissionalRef = doc(db, "profissionais", profissional.id);

      // Adicionar à lista de profissionais da auditoria
      profissionaisAuditoria.push({
        id: profissional.id,
        nome: profissional.nome,
        quantidade: Number(profissional.qtd),
      });

      // Descontar da disponibilidade na base de dados
      profissionaisPromises.push(
        updateDoc(profissionalRef, {
          quantidade: profissional.quantidade - Number(profissional.qtd),
        })
      );
    }

    // Atribuir materiais e profissionais processados à auditoria
    auditoria.materiais = materiaisAuditoria;
    auditoria.profissionais = profissionaisAuditoria;

    // Criar documento de auditoria
    await setDoc(doc(db, "auditorias", id), auditoria);

    // Esperar todas as promessas de atualização de estoque concluírem
    await Promise.all([...materiaisPromises, ...profissionaisPromises]);

    // Redirecionar para a página de gestão
    router.push("/GestaoOcorrencias");
  } catch (error) {
    console.error("Erro ao submeter auditoria:", error);
    alert(
      "Ocorreu um erro ao aprovar a ocorrência. Por favor, tente novamente."
    );
  }
}

onMounted(loadData);
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  gap: 20px;
  height: 100%;
  max-height: 100vh;
}

.sidebar-column {
  width: 20%;
}

.main-content {
  flex: 1;
  margin-right: 10px;
  overflow-y: auto;
}

.content-wrapper {
  margin-top: 40px;
  min-height: 100%;
}

.page-header h2 {
  margin: 0 0 1em;
  font-weight: 600;
  color: #2c3e50;
}

.audit-form {
  background: #fff;
  padding: 1.5em;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 1.5em 0 1em;
  padding-bottom: 0.5em;
  border-bottom: 2px solid #f0f2f5;
}

.map-container {
  width: 100%;
  height: 300px;
  margin-bottom: 1.5em;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Suggestion section styling */
.suggestion-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1.5em 0;
  position: relative;
}

.suggestion-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0.75em 1.5em;
  font-weight: 500;
  transition: all 0.2s ease;
  width: 180px;
}

.btn-primary {
  background-color: #4c6ef5;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #3b5bdb;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 91, 219, 0.2);
}

.btn-primary:disabled {
  background-color: #a5b4fc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.suggestion-icon::before {
  content: "💡";
  font-size: 1.1em;
}

.lightbulb-icon::before {
  content: "💡";
  margin-right: 6px;
}

/* Loading spinner */
.loading-spinner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Success toast notification */
.success-toast {
  position: absolute;
  top: -50px;
  right: 0;
  background-color: #d4edda;
  color: #155724;
  padding: 0.75em 1.25em;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 10;
}

.check-icon::before {
  content: "✓";
  font-weight: bold;
  font-size: 1.2em;
  color: #28a745;
}

/* Suggestion result box */
.suggestion-result {
  margin: 0 0 2em;
  padding: 1.25em;
  background-color: #f8f9ff;
  border-radius: 8px;
  border-left: 4px solid #4c6ef5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.suggestion-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.75em;
  justify-content: space-between;
}

.suggestion-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
}

.badge {
  background-color: #4c6ef5;
  color: white;
  font-size: 0.75rem;
  padding: 0.25em 0.75em;
  border-radius: 12px;
  font-weight: 600;
}

.suggestion-content {
  color: #495057;
  line-height: 1.6;
}

.suggestion-content p {
  margin: 0;
  white-space: pre-line;
}

/* Section divider */
.section-divider {
  height: 1px;
  background-color: #e9ecef;
  margin: 2em 0;
}

/* Input fields */
.input {
  width: 100%;
  padding: 0.7em;
  border: 1px solid #ced4da;
  border-radius: 6px;
  transition: border-color 0.2s ease;
  font-size: 0.95rem;
}

.input:focus {
  border-color: #4c6ef5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(76, 110, 245, 0.1);
}

.input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.form-group {
  margin-bottom: 1.25em;
}

.form-group label {
  display: block;
  margin-bottom: 0.5em;
  font-weight: 500;
  color: #495057;
}

/* Tables */
.table-scroll {
  margin-bottom: 1.5em;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.table-scroll .generic-table-wrapper {
  max-height: 250px;
  overflow-y: auto;
}

/* Radio buttons */
.radio-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
  user-select: none;
}

/* Quantity input */
.quantity-input {
  display: flex;
  align-items: center;
  max-width: 120px;
}

.qty-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #ced4da;
  background-color: #f8f9fa;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.qty-btn:hover:not(:disabled) {
  background-color: #e9ecef;
}

.qty-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qty-btn.minus {
  border-radius: 4px 0 0 4px;
}

.qty-btn.plus {
  border-radius: 0 4px 4px 0;
}

.qty-input {
  height: 28px;
  width: 50px;
  padding: 0 0.5em;
  text-align: center;
  border-radius: 0;
  border-left: 0;
  border-right: 0;
  border-top: 1px solid #ced4da;
  border-bottom: 1px solid #ced4da;
}

/* Schedule section */
.schedule-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5em;
  margin-bottom: 1.5em;
}

/* Date input */
.date-input {
  cursor: pointer;
}

/* Time input */
.time-input {
  position: relative;
}

.time-unit {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  font-size: 0.9rem;
}

/* Submit button */
.btn-submit {
  width: 100%;
  padding: 0.85em;
  background-color: #4c6ef5;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1em;
}

.btn-submit:hover {
  background-color: #3b5bdb;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 91, 219, 0.2);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease-out;
}

.slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsividade */
@media (max-width: 992px) {
  .schedule-section {
    grid-template-columns: 1fr;
    gap: 1em;
  }

  .suggestion-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 1em;
  }

  .suggestion-btn {
    width: 100%;
  }

  .success-toast {
    position: static;
    width: 100%;
    margin-top: 1em;
  }
}

@media (max-width: 768px) {
  .dashboard-layout {
    flex-direction: column;
  }

  .sidebar-column {
    width: 100%;
    margin-bottom: 1em;
  }
}

.criticality-selector {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.criticality-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease-in-out;
  background-color: #ffffff;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.criticality-option:hover,
.criticality-option:focus {
  border-color: #4263eb;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66, 99, 235, 0.2);
  background-color: #f8f9fc;
}

.criticality-option.selected {
  border-color: #4263eb;
  background: linear-gradient(to right, #edf2ff, #dbe4ff);
}

.criticality-number {
  font-size: 1.5rem;
  font-weight: bold;
  width: 40px;
  text-align: center;
  color: #4263eb;
}

.criticality-info {
  flex: 1;
  margin-left: 1rem;
}

.criticality-label {
  font-weight: 600;
  font-size: 1rem;
  color: #212529;
}

.criticality-description {
  font-size: 0.875rem;
  color: #6c757d;
}

.criticality-indicator {
  width: 100px;
  height: 10px;
  background-color: #e9ecef;
  border-radius: 5px;
  overflow: hidden;
  margin-left: 1rem;
}

.indicator-bar {
  height: 100%;
  background: linear-gradient(to right, #ff6b6b, #ffa94d);
  transition: width 0.3s ease-in-out;
  border-radius: 5px;
}

/* Níveis com cores distintas */
.level-1 .indicator-bar {
  background: #38d9a9;
}

.level-2 .indicator-bar {
  background: #69db7c;
}

.level-3 .indicator-bar {
  background: #ffd43b;
}

.level-4 .indicator-bar {
  background: #ffa94d;
}

.level-5 .indicator-bar {
  background: #ff6b6b;
}

/* Resumo visual abaixo da seleção */
.criticality-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.criticality-icon {
  font-size: 1.25rem;
  color: #fab005;
}
</style>