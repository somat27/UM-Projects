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
          <nav class="navigation-tabs">
            <router-link
              to="/dashboards/auditorias"
              class="tab-link"
              :class="{ active: activeTab === 'auditorias' }"
              @click="activeTab = 'auditorias'"
            >
              Auditorias por região
            </router-link>
            <router-link
              to="/dashboards/ocorrencias"
              class="tab-link"
              :class="{ active: activeTab === 'ocorrencias' }"
              @click="activeTab = 'ocorrencias'"
            >
              Ocorrências por região
            </router-link>
            <router-link
              to="/dashboards/peritos"
              class="tab-link"
              :class="{ active: activeTab === 'peritos' }"
              @click="activeTab = 'peritos'"
            >
              Peritos Ativos e em Espera
            </router-link>
            <router-link
              to="/dashboards/materiais"
              class="tab-link"
              :class="{ active: activeTab === 'materiais' }"
              @click="activeTab = 'materiais'"
            >
              Materiais Usados & Por Usar
            </router-link>
            <router-link
              to="/dashboards/mapa"
              class="tab-link"
              :class="{ active: activeTab === 'mapa' }"
              @click="activeTab = 'mapa'"
            >
              Auditorias e Ocorrências no Terreno
            </router-link>
          </nav>

          <div class="stats-search-row">
            <StatisticsGridAuditorias
              :labels="filteredLabels"
              :values="filteredValues"
            />
            <div class="search-section inline">
              <div class="search-input">
                <input
                  type="text"
                  v-model="searchQuery"
                  placeholder="Pesquisar Localidade..."
                  class="search-container"
                />
              </div>
            </div>
          </div>

          <div id="chart">
            <apexchart
              type="bar"
              :options="chartOptions"
              :series="series"
              height="350"
            />
            <div class="dashboard-info" v-if="ultimaAtualizacao">
              <span class="info-text"
                >Dados atualizados em:
                {{ ultimaAtualizacao.toLocaleString() }}</span
              >
              <button class="refresh-button" @click="forcarAtualizacao">
                Atualizar dados
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { collection, onSnapshot, getDocs } from "firebase/firestore";
import { db } from "@/firebase.js";
import StatisticsGridAuditorias from "@/components/StatisticsGridAuditorias.vue";
import NavigationList from "@/components/NavigationList.vue";

const activeTab = ref("auditorias");
const searchQuery = ref("");
const auditorias = ref([]);
const contagem = ref({});
const cache = ref({});
const dataCarregado = ref(false);
const ultimaAtualizacao = ref(null);

// Configuração do localStorage
const STORAGE_KEY = "dashboard-auditorias-data";
const TIMESTAMP_KEY = "dashboard-auditorias-timestamp";
const UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutos em milissegundos

async function buscarCidade(lat, lon) {
  const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&addressdetails=1`;
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": "MeuAppUniversidade/1.0 (email@exemplo.com)" },
    });
    if (!res.ok) throw new Error(`Erro HTTP ${res.status}`);
    const data = await res.json();
    const address = data.address || {};
    return address.city || address.town || address.village || "Desconhecida";
  } catch (err) {
    console.error("Erro ao buscar cidade:", err);
    return "Desconhecida";
  }
}

async function buscarCidadeComCache(lat, lon) {
  const key = `${lat},${lon}`;
  if (cache.value[key]) return cache.value[key];
  try {
    const city = await buscarCidade(lat, lon);
    cache.value[key] = city;
    return city;
  } catch (err) {
    console.error("Erro geocodificação", err);
    return "Desconhecida";
  }
}

// Funções auxiliares para localStorage
function salvarDadosLocal() {
  try {
    // Estrutura de dados para salvar
    const dadosParaSalvar = {
      auditorias: auditorias.value,
      contagem: contagem.value,
      cache: cache.value,
      timestamp: Date.now(),
    };

    // Salvar no localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dadosParaSalvar));
    localStorage.setItem(TIMESTAMP_KEY, Date.now().toString());

    console.log("Dados das auditorias salvos no localStorage com sucesso");
    ultimaAtualizacao.value = new Date();
  } catch (error) {
    console.error(
      "Erro ao salvar dados das auditorias no localStorage:",
      error
    );
  }
}

function carregarDadosLocal() {
  try {
    // Verificar se temos dados no localStorage
    const dadosSalvos = localStorage.getItem(STORAGE_KEY);
    const timestampSalvo = localStorage.getItem(TIMESTAMP_KEY);

    if (!dadosSalvos || !timestampSalvo) {
      console.log("Nenhum dado de auditorias encontrado no localStorage");
      return false;
    }

    // Verificar se os dados estão vencidos
    const agora = Date.now();
    const dataUltimaAtualizacao = parseInt(timestampSalvo);

    if (agora - dataUltimaAtualizacao > UPDATE_INTERVAL) {
      console.log(
        "Dados de auditorias do localStorage estão vencidos, buscando novos dados"
      );
      return false;
    }

    // Carregar dados do localStorage
    const dados = JSON.parse(dadosSalvos);
    auditorias.value = dados.auditorias;
    contagem.value = dados.contagem;
    cache.value = dados.cache;

    ultimaAtualizacao.value = new Date(dataUltimaAtualizacao);
    dataCarregado.value = true;

    console.log("Dados de auditorias carregados do localStorage com sucesso");
    return true;
  } catch (error) {
    console.error(
      "Erro ao carregar dados de auditorias do localStorage:",
      error
    );
    return false;
  }
}

// Função para forçar a atualização dos dados
async function forcarAtualizacao() {
  console.log("Forçando atualização dos dados de auditorias...");

  try {
    // Limpar os dados atuais
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(TIMESTAMP_KEY);

    // Buscar novos dados do Firestore
    const auditoriasSnap = await getDocs(collection(db, "auditorias"));
    const docs = auditoriasSnap.docs.map((d) => ({ id: d.id, ...d.data() }));
    auditorias.value = docs;

    // Recalcular contagem por cidade
    const novo = {};
    for (const doc of docs) {
      if (
        doc.coordenadas &&
        doc.coordenadas.latitude &&
        doc.coordenadas.longitude
      ) {
        const lat = doc.coordenadas.latitude;
        const lon = doc.coordenadas.longitude;
        const cidade = await buscarCidadeComCache(lat, lon);
        novo[cidade] = (novo[cidade] || 0) + 1;
      }
    }
    contagem.value = novo;

    // Salvar os novos dados no localStorage
    salvarDadosLocal();

    console.log("Dados de auditorias atualizados com sucesso!");
  } catch (error) {
    console.error("Erro ao forçar atualização dos dados de auditorias:", error);
  }
}

// Configurar observadores para mudanças em dados importantes
watch(
  [auditorias, contagem, cache],
  () => {
    if (dataCarregado.value) {
      salvarDadosLocal();
    }
  },
  { deep: true }
);

// Variável para armazenar o unsubscribe do listener do Firestore
let unsubAuditorias;

onMounted(async () => {
  // Tentar carregar dados do localStorage primeiro
  const dadosCarregados = carregarDadosLocal();

  if (!dadosCarregados) {
    // Se não houver dados no localStorage ou estiverem vencidos, buscar do Firestore
    unsubAuditorias = onSnapshot(
      collection(db, "auditorias"),
      async (snapshot) => {
        const docs = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
        auditorias.value = docs;

        console.log(`Carregadas ${auditorias.value.length} auditorias`);

        // Calcular contagem por cidade
        const novo = {};
        for (const doc of docs) {
          if (
            doc.coordenadas &&
            doc.coordenadas.latitude &&
            doc.coordenadas.longitude
          ) {
            const lat = doc.coordenadas.latitude;
            const lon = doc.coordenadas.longitude;
            const cidade = await buscarCidadeComCache(lat, lon);
            novo[cidade] = (novo[cidade] || 0) + 1;
          }
        }
        contagem.value = novo;

        dataCarregado.value = true;

        // Salvar os dados atualizados no localStorage
        salvarDadosLocal();
      },
      (err) => console.error("Erro ao carregar auditorias:", err)
    );
  }
});

onUnmounted(() => {
  // Desinscrever do listener do Firestore quando o componente for desmontado
  if (unsubAuditorias) unsubAuditorias();

  // Salvar os dados atuais no localStorage antes de sair
  if (dataCarregado.value) {
    salvarDadosLocal();
  }
});

const localities = computed(() => Object.keys(contagem.value));
const dataValues = computed(() => Object.values(contagem.value));

const filteredIndices = computed(() => {
  return localities.value
    .map((loc, idx) => ({ loc, idx }))
    .filter(
      (item) =>
        !searchQuery.value ||
        item.loc.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    .map((item) => item.idx);
});

const filteredLabels = computed(() =>
  filteredIndices.value.map((i) => localities.value[i])
);
const filteredValues = computed(() =>
  filteredIndices.value.map((i) => dataValues.value[i])
);

const series = computed(() => [
  {
    name: "Auditorias",
    data: filteredValues.value,
  },
]);

const chartOptions = computed(() => ({
  chart: {
    id: "auditorias-por-cidade",
    toolbar: {
      show: true,
    },
    animations: {
      enabled: true,
    },
  },
  xaxis: {
    categories: filteredLabels.value,
    title: {
      text: "Localidades",
    },
  },
  yaxis: {
    title: {
      text: "Número de Auditorias",
    },
  },
  colors: ["#204C6D"],
  dataLabels: {
    enabled: true,
    formatter: function (val) {
      return val || "0";
    },
    style: {
      fontSize: "12px",
    },
  },
  plotOptions: {
    bar: {
      borderRadius: 3,
      columnWidth: "50%",
    },
  },
}));
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

/* Navigation Tabs Styles */
.navigation-tabs {
  margin-top: -15px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Public Sans", -apple-system, Roboto, Helvetica, sans-serif;
  padding: 8px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.tab-link {
  text-decoration: none;
  color: #6c757d;
  font-size: 14px;
  line-height: 1.5;
  padding: 10px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  position: relative;
  font-weight: 500;
  letter-spacing: 0.2px;
  white-space: nowrap;
}

.tab-link:hover {
  background-color: #f8f9fa;
  color: #495057;
}

.tab-link.active {
  color: #204c6d;
  background-color: rgba(24, 144, 255, 0.08);
  font-weight: 600;
}

.tab-link.active::after {
  content: "";
  position: absolute;
  bottom: -9px;
  left: 16px;
  right: 16px;
  height: 2px;
  background-color: #204c6d;
  border-radius: 2px 2px 0 0;
}

.tab-link::after {
  content: "";
  position: absolute;
  bottom: -9px;
  left: 50%;
  right: 50%;
  height: 2px;
  background-color: #204c6d;
  transition: all 0.3s ease;
  border-radius: 2px 2px 0 0;
}

.search-section {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.search-input {
  position: relative;
}

.search-container {
  padding: 8px 40px 8px 12px;
  border: 1px solid #204c6d;
  border-radius: 4px;
  width: 200px;
}

.search-button {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: none;
  cursor: pointer;
}

.stats-search-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-right: 20px;
}

.search-section.inline {
  margin: 0;
  margin-right: 16px;
}

input {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid #ccc;
}

/* Dashboard info styling */
.dashboard-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
}

.info-text {
  font-size: 13px;
  color: #6c757d;
}

.refresh-button {
  background-color: #204c6d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  letter-spacing: 0.3px;
}

.refresh-button:hover {
  background-color: #36cfc9;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.refresh-button:active {
  background-color: #08979c;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  transform: translateY(1px);
}

/* Main chart styling */
#chart {
  margin-top: 24px;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  background-color: #fff;
}
</style>
