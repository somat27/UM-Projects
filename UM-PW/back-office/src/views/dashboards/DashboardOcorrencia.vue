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

          <div class="filters-row">
            <select v-model="selectedRegion" class="filter-select">
              <option v-for="loc in localities" :key="loc" :value="loc">
                {{ loc }}
              </option>
            </select>

            <div class="filter-week-wrapper">
              <input type="week" v-model="selectedWeek" class="filter-week" />
            </div>

            <div class="spacer"></div>
          </div>

          <StatisticsGridOcorrencia :cards="weeklyCards" />

          <div id="chart">
            <apexchart
              type="area"
              height="350"
              :options="chartOptions"
              :series="series"
            />
            <div class="dashboard-info">
              <span class="info-text" v-if="ultimaAtualizacao">
                Dados atualizados em:
                {{ ultimaAtualizacao.toLocaleString() }}
              </span>
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
import NavigationList from "@/components/NavigationList.vue";
import StatisticsGridOcorrencia from "@/components/StatisticsGridOcorrencia.vue";
import { collection, getDocs } from "firebase/firestore";
import { db } from "@/firebase";

// Ref para dados e estado
const rawData = ref([]);
const dataCarregado = ref(false);
const ultimaAtualizacao = ref(null);

// Configuração do localStorage
const STORAGE_KEY = "dashboard-ocorrencias-data";
const TIMESTAMP_KEY = "dashboard-ocorrencias-timestamp";
const UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutos em milissegundos

// Regiões e seleção
const regions = [
  {
    name: "Norte",
    bounds: { latMin: 41.5, latMax: 42.3, lngMin: -8.7, lngMax: -6.2 },
  },
  {
    name: "Centro",
    bounds: { latMin: 39.9, latMax: 41.5, lngMin: -8.5, lngMax: -6.0 },
  },
  {
    name: "Lisboa e Vale do Tejo",
    bounds: { latMin: 38.4, latMax: 40.2, lngMin: -9.5, lngMax: -7.0 },
  },
  {
    name: "Alentejo",
    bounds: { latMin: 37.6, latMax: 39.3, lngMin: -8.2, lngMax: -6.0 },
  },
  {
    name: "Algarve",
    bounds: { latMin: 37.0, latMax: 37.6, lngMin: -9.7, lngMax: -7.7 },
  },
];
const localities = ["Portugal", ...regions.map((r) => r.name)];
const selectedRegion = ref(localities[0]);
const selectedWeek = ref(getCurrentISOWeek());

const activeTab = ref("ocorrencias");

// Mapeamento de distritos para regiões
const distritoRegiaoMap = {
  Porto: "Norte",
  "Viana do Castelo": "Norte",
  Braga: "Norte",
  "Vila Real": "Norte",
  Bragança: "Norte",
  Aveiro: "Centro",
  Coimbra: "Centro",
  Leiria: "Centro",
  "Castelo Branco": "Centro",
  Guarda: "Centro",
  Viseu: "Centro",
  Santarém: "Lisboa e Vale do Tejo",
  Lisboa: "Lisboa e Vale do Tejo",
  Setúbal: "Lisboa e Vale do Tejo",
  Évora: "Alentejo",
  Beja: "Alentejo",
  Portalegre: "Alentejo",
  Faro: "Algarve",
};

// Cache para geocodificação de regiões
const cacheRegiao = {};
async function buscarRegiao(lat, lon) {
  const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&addressdetails=1&accept-language=pt`;
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": "MeuAppUniversidade/1.0 (email@exemplo.com)" },
    });
    if (!res.ok) throw new Error(`Erro HTTP ${res.status}`);
    const data = await res.json();
    const addr = data.address || {};
    const district = addr.state || addr.county || addr.region || "";
    return distritoRegiaoMap[district] || "Desconhecida";
  } catch (err) {
    console.error("Erro ao buscar região:", err);
    return "Desconhecida";
  }
}

async function buscarRegiaoComCache(lat, lon) {
  const key = `${lat},${lon}`;
  if (cacheRegiao[key]) return cacheRegiao[key];
  try {
    const regiao = await buscarRegiao(lat, lon);
    cacheRegiao[key] = regiao;
    return regiao;
  } catch (err) {
    console.error("Erro geocodificação região", err);
    return "Desconhecida";
  }
}

// Funções de datas
const weekDates = computed(() =>
  selectedWeek.value ? isoWeekDates(selectedWeek.value) : []
);

function isoWeekDates(weekString) {
  const [year, wk] = weekString.split("-W").map(Number);
  const jan4 = new Date(Date.UTC(year, 0, 4));
  const dayOfWeek = jan4.getUTCDay() || 7;
  const week1Start = new Date(Date.UTC(year, 0, 4 - (dayOfWeek - 1)));
  const start = new Date(week1Start);
  start.setUTCDate(start.getUTCDate() + (wk - 1) * 7);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start);
    d.setUTCDate(d.getUTCDate() + i);
    return d.toISOString().slice(0, 10);
  });
}

function getCurrentISOWeek() {
  const now = new Date();
  const date = new Date(
    Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
  );
  const dayNum = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil(((date - yearStart) / 86400000 + 1) / 7);
  const weekStr = String(weekNo).padStart(2, "0");
  return `${date.getUTCFullYear()}-W${weekStr}`;
}

// Agregação de dados - CORRIGIDA para evitar perda de ocorrências
function aggregate(items) {
  // Agrupar as ocorrências por data e região, somando os totais
  const mapa = {};
  items.forEach((item) => {
    const key = item.region + "|" + item.date;
    if (!mapa[key]) {
      mapa[key] = {
        date: item.date,
        region: item.region,
        total: 0,
        resolved: 0,
      };
    }
    mapa[key].total += item.total || 1; // Garante que cada ocorrência conta como 1
    mapa[key].resolved += item.resolved || 0;
  });
  return Object.values(mapa);
}

// Computed para filtragem de dados
const weeklyData = computed(() => {
  // Filtrar os dados pela semana selecionada e região
  return rawData.value.filter(
    (item) =>
      weekDates.value.includes(item.date) &&
      (selectedRegion.value === "Portugal"
        ? true
        : item.region === selectedRegion.value)
  );
});

// Dados para cartões de estatísticas
const weeklyCards = computed(() => {
  if (!weeklyData.value.length) {
    return [
      { title: "Total Confirmadas", value: 0 },
      { title: "Total Resolvidas", value: 0 },
      { title: "Maior taxa (dia)", value: "–" },
      { title: "Menor taxa (dia)", value: "–" },
    ];
  }

  // Calcular totais por dia para os cards
  const total = weeklyData.value.reduce((s, d) => s + d.total, 0);
  const resolved = weeklyData.value.reduce((s, d) => s + d.resolved, 0);

  // Calcular taxas de resolução por dia
  const byDate = {};
  weeklyData.value.forEach((d) => {
    if (!byDate[d.date]) {
      byDate[d.date] = { total: 0, resolved: 0 };
    }
    byDate[d.date].total += d.total;
    byDate[d.date].resolved += d.resolved;
  });

  const rates = Object.entries(byDate).map(([date, data]) => ({
    date,
    pct: data.total > 0 ? Math.round((data.resolved / data.total) * 100) : 0,
  }));

  const max =
    rates.length > 0
      ? rates.reduce((a, b) => (b.pct > a.pct ? b : a), { pct: 0, date: "–" })
      : { pct: 0, date: "–" };

  const min =
    rates.length > 0
      ? rates.reduce((a, b) => (b.pct < a.pct ? b : a), { pct: 100, date: "–" })
      : { pct: 0, date: "–" };

  return [
    { title: "Total de Ocorrências Confirmadas", value: total },
    { title: "Total de Ocorrências Resolvidas", value: resolved },
    {
      title: "Dia com a maior taxa de resolução",
      value: `${max.date} (${max.pct}%)`,
    },
    {
      title: "Dia com a menor taxa de resolução",
      value: `${min.date} (${min.pct}%)`,
    },
  ];
});

// Dados para o gráfico - CORRIGIDO para mostrar totais corretos
const series = computed(() => {
  // Agrupar dados por data para o gráfico
  const dailyTotals = {};
  weekDates.value.forEach((date) => {
    dailyTotals[date] = { total: 0, resolved: 0 };
  });

  // Somar todas as ocorrências por data
  weeklyData.value.forEach((item) => {
    if (dailyTotals[item.date]) {
      dailyTotals[item.date].total += item.total;
      dailyTotals[item.date].resolved += item.resolved;
    }
  });

  return [
    {
      name: "Total",
      data: weekDates.value.map((date) => dailyTotals[date].total),
    },
    {
      name: "Resolvidas",
      data: weekDates.value.map((date) => dailyTotals[date].resolved),
    },
  ];
});

const chartOptions = computed(() => ({
  chart: {
    type: "area",
    height: 350,
    toolbar: {
      show: true,
      tools: {
        download: true,
        selection: true,
        zoom: true,
        zoomin: true,
        zoomout: true,
        pan: true,
      },
    },
  },
  stroke: { curve: "smooth" },
  xaxis: {
    categories: weekDates.value,
    labels: {
      formatter: function (value) {
        // Formatação para exibir data como DD/MM
        const date = new Date(value);
        const day = date.getDate().toString().padStart(2, "0");
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        return `${day}/${month}`;
      },
    },
  },
  dataLabels: { enabled: false },
  legend: { position: "top" },
  tooltip: {
    x: { format: "dd/MM" },
    y: {
      formatter: function (value) {
        return value || "0";
      },
    },
  },
  colors: ["#33b2df", "#546E7A"],
  fill: {
    type: "gradient",
    gradient: {
      shade: "light",
      type: "vertical",
      shadeIntensity: 0.25,
      gradientToColors: undefined,
      inverseColors: true,
      opacityFrom: 0.85,
      opacityTo: 0.55,
    },
  },
}));

// Funções auxiliares para localStorage
function salvarDadosLocal() {
  try {
    // Estrutura de dados para salvar
    const dadosParaSalvar = {
      rawData: rawData.value,
      cacheRegiao: cacheRegiao,
      timestamp: Date.now(),
    };

    // Salvar no localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dadosParaSalvar));
    localStorage.setItem(TIMESTAMP_KEY, Date.now().toString());

    console.log("Dados de ocorrências salvos no localStorage com sucesso");
    ultimaAtualizacao.value = new Date();
  } catch (error) {
    console.error(
      "Erro ao salvar dados de ocorrências no localStorage:",
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
      console.log("Nenhum dado de ocorrências encontrado no localStorage");
      return false;
    }

    // Verificar se os dados estão vencidos
    const agora = Date.now();
    const dataUltimaAtualizacao = parseInt(timestampSalvo);

    if (agora - dataUltimaAtualizacao > UPDATE_INTERVAL) {
      console.log(
        "Dados de ocorrências do localStorage estão vencidos, buscando novos dados"
      );
      return false;
    }

    // Carregar dados do localStorage
    const dados = JSON.parse(dadosSalvos);
    rawData.value = dados.rawData;

    // Restaurar o cache de geocodificação
    Object.assign(cacheRegiao, dados.cacheRegiao);

    ultimaAtualizacao.value = new Date(dataUltimaAtualizacao);
    dataCarregado.value = true;

    console.log("Dados de ocorrências carregados do localStorage com sucesso");
    return true;
  } catch (error) {
    console.error(
      "Erro ao carregar dados de ocorrências do localStorage:",
      error
    );
    return false;
  }
}

// Função para forçar a atualização dos dados
async function forcarAtualizacao() {
  console.log("Forçando atualização dos dados de ocorrências...");

  try {
    // Limpar os dados atuais
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(TIMESTAMP_KEY);

    // Buscar novos dados do Firestore
    await carregarDadosFirestore();

    // Salvar os novos dados no localStorage
    salvarDadosLocal();

    console.log("Dados de ocorrências atualizados com sucesso!");
  } catch (error) {
    console.error(
      "Erro ao forçar atualização dos dados de ocorrências:",
      error
    );
  }
}

// Função para carregar dados do Firestore - CORRIGIDA para garantir contagem precisa
async function carregarDadosFirestore() {
  const snap = await getDocs(collection(db, "ocorrencias"));
  console.log(`Carregadas ${snap.docs.length} ocorrências do Firestore`);
  const items = [];

  for (const doc of snap.docs) {
    const d = doc.data();
    const stamp = d.dataSubmissao ?? doc.createTime;
    const tsDate = stamp.toDate();
    const dateStr = tsDate.toISOString().slice(0, 10);

    // Verificar se temos coordenadas
    if (!d.coordenadas || !d.coordenadas.latitude || !d.coordenadas.longitude) {
      console.warn(`Ocorrência ${doc.id} sem coordenadas válidas, ignorando.`);
      continue;
    }

    const lat = d.coordenadas.latitude;
    const lon = d.coordenadas.longitude;
    const region = await buscarRegiaoComCache(lat, lon);

    const resolved = d.status === "Resolvido" ? 1 : 0;

    items.push({
      date: dateStr,
      region,
      total: 1, // Cada documento conta como 1 ocorrência
      resolved,
    });
  }

  // Aplicar agregação por data e região
  rawData.value = aggregate(items);
  dataCarregado.value = true;
}

// Configurar observadores para mudanças em dados importantes
watch(
  rawData,
  () => {
    if (dataCarregado.value) {
      salvarDadosLocal();
    }
  },
  { deep: true }
);

onMounted(async () => {
  // Tentar carregar dados do localStorage primeiro
  const dadosCarregados = carregarDadosLocal();

  if (!dadosCarregados) {
    // Se não houver dados no localStorage ou estiverem vencidos, buscar do Firestore
    await carregarDadosFirestore();

    // Salvar os novos dados no localStorage
    salvarDadosLocal();
  }
});

onUnmounted(() => {
  // Salvar os dados atuais no localStorage antes de sair
  if (dataCarregado.value) {
    salvarDadosLocal();
  }
});
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

/* Estilos para a navegação */
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

/* Estilos para área de filtros */
.filters-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.spacer {
  flex: 1;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #13c2c2;
  border-radius: 4px;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-select:hover,
.filter-select:focus {
  border-color: #1890ff;
  outline: none;
}

.filter-week-wrapper {
  display: flex;
  flex-direction: column;
}

.filter-week-label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 4px;
}

.filter-week {
  padding: 8px 12px;
  border: 1px solid #13c2c2;
  border-radius: 4px;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s;
  width: 160px;
}

.filter-week:hover,
.filter-week:focus {
  border-color: #1890ff;
  outline: none;
}

select,
input[type="week"] {
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* Estilos para o botão de atualização e info */
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

/* Estilo para o gráfico */
#chart {
  margin-top: 24px;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  background-color: #fff;
}
</style>
