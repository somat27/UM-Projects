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

          <StatisticsGridPeritos>
            <StatisticsCard
              title="Peritos Totais"
              :value="totalPeritos"
              icon="users"
            />
            <StatisticsCard
              title="Peritos ativos"
              :value="countAtivos"
              icon="check-circle"
            />
            <StatisticsCard
              title="Peritos em espera"
              :value="countAguardando"
              icon="clock"
            />
          </StatisticsGridPeritos>

          <div id="chart">
            <apexchart
              type="bar"
              :options="chartOptions"
              :series="chartSeries"
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
import { ref, computed, onMounted, onUnmounted } from "vue";
import NavigationList from "@/components/NavigationList.vue";
import StatisticsGridPeritos from "@/components/StatisticsGridPeritos.vue";
import StatisticsCard from "@/components/StatisticsCard.vue";
import { collection, onSnapshot, getDocs } from "firebase/firestore";
import { db } from "@/firebase";

const activeTab = ref("peritos");

// Dados principais
const peritos = ref([]);
const auditorias = ref([]);
const dataCarregado = ref(false);
const ultimaAtualizacao = ref(null);

// Configuração do localStorage
const STORAGE_KEY = "dashboard-peritos-data";
const TIMESTAMP_KEY = "dashboard-peritos-timestamp";
const UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutos em milissegundos

// Regiões para categorização
const regioes = [
  "Norte",
  "Centro",
  "Lisboa e Vale do Tejo",
  "Alentejo",
  "Algarve",
];

// Determinar status dos peritos (ativo ou em espera)
const peritosStatus = computed(() => {
  const statusMap = {};
  const auditoriasMap = {};

  // Criar um mapa de auditorias por perito para otimizar a busca
  auditorias.value.forEach((auditoria) => {
    if (auditoria.perito) {
      if (!auditoriasMap[auditoria.perito]) {
        auditoriasMap[auditoria.perito] = [];
      }
      auditoriasMap[auditoria.perito].push(auditoria);
    }
  });

  // Determinar o status de cada perito
  peritos.value.forEach((perito) => {
    const peritoAuditorias = auditoriasMap[perito.uid] || [];
    const temAuditoriaAtiva = peritoAuditorias.some(
      (a) => a.status !== "Concluído"
    );
    statusMap[perito.uid] = temAuditoriaAtiva ? "ativo" : "espera";
  });

  return statusMap;
});

// Computar listas filtradas de peritos
const peritosAtivos = computed(() =>
  peritos.value.filter((p) => peritosStatus.value[p.uid] === "ativo")
);

const peritosEspera = computed(() =>
  peritos.value.filter((p) => peritosStatus.value[p.uid] === "espera")
);

// Distribuição de peritos por região
// Cada perito deve aparecer em UMA ÚNICA região com base em sua localidade principal
const peritosPorRegiao = computed(() => {
  const distribuicao = {
    Norte: [],
    Centro: [],
    "Lisboa e Vale do Tejo": [],
    Alentejo: [],
    Algarve: [],
  };

  peritos.value.forEach((perito) => {
    if (Array.isArray(perito.localidades) && perito.localidades.length > 0) {
      perito.localidades.forEach((regiaoDoPerito) => {
        if (distribuicao[regiaoDoPerito]) {
          distribuicao[regiaoDoPerito].push(perito.uid);
        }
      });
    }
    // Caso contrário, não adiciona o perito em nenhuma região
  });

  return distribuicao;
});

// Contadores por região
const ativosPorRegiao = computed(() => {
  const result = {};

  regioes.forEach((regiao) => {
    const peritosUnicos = new Set(
      peritosPorRegiao.value[regiao]?.filter(
        (peritoId) => peritosStatus.value[peritoId] === "ativo"
      )
    );
    result[regiao] = peritosUnicos.size;
  });

  return result;
});

const esperaPorRegiao = computed(() => {
  const result = {};

  regioes.forEach((regiao) => {
    const peritosUnicos = new Set(
      peritosPorRegiao.value[regiao]?.filter(
        (peritoId) => peritosStatus.value[peritoId] === "espera"
      )
    );
    result[regiao] = peritosUnicos.size;
  });

  return result;
});

// Subscrever coleções
let unsubPeritos, unsubAud;

// Funções auxiliares para localStorage
function salvarDadosLocal() {
  try {
    const dadosParaSalvar = {
      peritos: peritos.value,
      auditorias: auditorias.value,
      timestamp: Date.now(),
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(dadosParaSalvar));
    localStorage.setItem(TIMESTAMP_KEY, Date.now().toString());

    console.log("Dados salvos no localStorage com sucesso");
    ultimaAtualizacao.value = new Date();
  } catch (error) {
    console.error("Erro ao salvar dados no localStorage:", error);
  }
}

function carregarDadosLocal() {
  try {
    const dadosSalvos = localStorage.getItem(STORAGE_KEY);
    const timestampSalvo = localStorage.getItem(TIMESTAMP_KEY);

    if (!dadosSalvos || !timestampSalvo) {
      console.log("Nenhum dado encontrado no localStorage");
      return false;
    }

    const agora = Date.now();
    const dataUltimaAtualizacao = parseInt(timestampSalvo);

    if (agora - dataUltimaAtualizacao > UPDATE_INTERVAL) {
      console.log("Dados do localStorage estão vencidos, buscando novos dados");
      return false;
    }

    const dados = JSON.parse(dadosSalvos);
    peritos.value = dados.peritos;
    auditorias.value = dados.auditorias;

    ultimaAtualizacao.value = new Date(dataUltimaAtualizacao);
    dataCarregado.value = true;

    console.log("Dados carregados do localStorage com sucesso");
    return true;
  } catch (error) {
    console.error("Erro ao carregar dados do localStorage:", error);
    return false;
  }
}

// Função para forçar a atualização dos dados
async function forcarAtualizacao() {
  console.log("Forçando atualização dos dados...");

  try {
    // Limpar os dados do localStorage
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(TIMESTAMP_KEY);

    // Buscar novos dados do Firestore
    const peritosSnap = await getDocs(collection(db, "peritos"));
    peritos.value = peritosSnap.docs.map((d) => ({
      ...d.data(),
      id: d.id,
    }));

    const auditoriasSnap = await getDocs(collection(db, "auditorias"));
    auditorias.value = auditoriasSnap.docs.map((d) => ({
      ...d.data(),
      id: d.id,
    }));

    // Salvar os novos dados no localStorage
    salvarDadosLocal();

    console.log("Dados atualizados com sucesso!");
  } catch (error) {
    console.error("Erro ao forçar atualização dos dados:", error);
  }
}

onMounted(async () => {
  // Tentar carregar dados do localStorage primeiro
  const dadosCarregados = carregarDadosLocal();

  if (!dadosCarregados) {
    // Se não houver dados no localStorage ou estiverem vencidos, buscar do Firestore
    unsubPeritos = onSnapshot(
      collection(db, "peritos"),
      (snap) => {
        peritos.value = snap.docs.map((d) => ({
          ...d.data(),
          id: d.id,
        }));
        console.log(`Carregados ${peritos.value.length} peritos`);
        dataCarregado.value = true;
      },
      (err) => console.error("Erro ao carregar peritos:", err)
    );

    unsubAud = onSnapshot(
      collection(db, "auditorias"),
      (snap) => {
        auditorias.value = snap.docs.map((d) => ({
          ...d.data(),
          id: d.id,
        }));
        console.log(`Carregadas ${auditorias.value.length} auditorias`);

        // Salvar os dados no localStorage após carregar tudo
        if (peritos.value.length > 0 && auditorias.value.length > 0) {
          salvarDadosLocal();
        }
      },
      (err) => console.error("Erro ao carregar auditorias:", err)
    );
  }
});

onUnmounted(() => {
  // Desinscrever dos listeners do Firestore
  if (unsubPeritos) unsubPeritos();
  if (unsubAud) unsubAud();

  // Salvar dados antes de sair
  if (dataCarregado.value) {
    salvarDadosLocal();
  }
});

// Métricas para cartões
const totalPeritos = computed(() => peritos.value.length);
const countAtivos = computed(() => peritosAtivos.value.length);
const countAguardando = computed(() => peritosEspera.value.length);

// Configuração do gráfico
const chartOptions = computed(() => ({
  chart: {
    id: "peritos-chart",
    stacked: false,
    animations: {
      enabled: true,
    },
  },
  xaxis: {
    categories: regioes,
    title: {
      text: "Regiões",
    },
  },
  yaxis: {
    title: {
      text: "Número de Peritos",
    },
  },
  colors: ["#33b2df", "#546E7A"],
  dataLabels: {
    enabled: true,
    formatter: function (val) {
      return val || "0";
    },
    style: {
      fontSize: "12px",
    },
  },
  legend: {
    position: "top",
    horizontalAlign: "center",
  },
  tooltip: {
    y: {
      formatter: function (value) {
        return value || "0";
      },
    },
  },
  plotOptions: {
    bar: {
      borderRadius: 3,
      columnWidth: "50%",
    },
  },
}));

const chartSeries = computed(() => [
  {
    name: "Peritos Ativos",
    data: regioes.map((regiao) => ativosPorRegiao.value[regiao] || 0),
  },
  {
    name: "Peritos em Espera",
    data: regioes.map((regiao) => esperaPorRegiao.value[regiao] || 0),
  },
]);
</script>

<style scoped>
.dashboard-container {
  background: #fff;
}

.dashboard-layout {
  display: flex;
  gap: 20px;
  max-height: 100vh;
}

.sidebar-column {
  width: 20%;
}

.main-content {
  flex: 1;
  margin-right: 10px;
}

.content-wrapper {
  margin-top: 40px;
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
  background-color: #2d6b99;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.refresh-button:active {
  background-color: #183a54;
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
