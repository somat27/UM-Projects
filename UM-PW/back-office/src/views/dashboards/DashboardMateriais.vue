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

          <StatisticsGridMateriais :cards="materialCards" />

          <div class="single-chart">
            <apexchart
              type="radialBar"
              :options="chartOptions"
              :series="chartSeries"
              height="350"
            />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed } from "vue";
import NavigationList from "@/components/NavigationList.vue";
import StatisticsGridMateriais from "@/components/StatisticsGridMateriais.vue";
import { collection, onSnapshot } from "firebase/firestore";
import { db } from "@/firebase.js";

const activeTab = ref("materiais");

const totalUtilizado = ref({});
const totalDisponivel = ref({});

const unsubAud = onSnapshot(collection(db, "auditorias"), (snap) => {
  let soma = 0;
  snap.forEach((doc) =>
    doc.data().materiais.forEach((item) => (soma += item.quantidade))
  );
  totalUtilizado.value = soma;
});

const unsubMat = onSnapshot(collection(db, "materiais"), (snap) => {
  let soma = 0;
  snap.forEach((doc) => (soma += doc.data().quantidade));
  totalDisponivel.value = soma;
});

onUnmounted(() => {
  unsubAud();
  unsubMat();
});

const materialCards = computed(() => [
  { title: "Materiais usados", value: totalUtilizado.value },
  { title: "Materiais por usar", value: totalDisponivel.value },
]);

const totalGeral = computed(() => totalUtilizado.value + totalDisponivel.value);

const pctUsados = computed(() =>
  totalGeral.value
    ? Math.round((totalUtilizado.value / totalGeral.value) * 100)
    : 0
);

// Configuração do gráfico com apenas uma série (materiais usados)
const chartOptions = computed(() => ({
  chart: {
    id: "materiais-grafico",
    foreColor: "#333",
  },
  labels: ["Materiais Usados"],
  title: {
    text: "Materiais Usados & Por Usar",
    align: "center",
    style: {
      fontSize: "18px",
      fontWeight: 600,
    },
  },
  plotOptions: {
    radialBar: {
      startAngle: 0,
      endAngle: 360,
      hollow: {
        size: "65%",
      },
      track: {
        background: "#e7e7e7",
        strokeWidth: "97%",
        margin: 5,
        dropShadow: {
          enabled: false,
        },
      },
      dataLabels: {
        name: {
          fontSize: "16px",
          color: "##204C6D",
          offsetY: -10,
        },
        value: {
          fontSize: "24px",
          color: "#111",
          formatter: function (val) {
            return val + "%";
          },
        },
        total: {
          show: true,
          label: "Por Usar",
          color: "#204C6D",
          formatter: function () {
            return pctUsados.value > 0 ? 100 - pctUsados.value + "%" : "100%";
          },
        },
      },
    },
  },
  fill: {
    type: "gradient",
    gradient: {
      shade: "dark",
      type: "horizontal",
      shadeIntensity: 0.5,
      color: ["#204C6D"],
      inverseColors: true,
      opacityFrom: 1,
      opacityTo: 1,
      stops: [0, 100],
    },
  },
  stroke: {
    lineCap: "round",
  },
  tooltip: {
    enabled: true,
    y: {
      formatter: function (val) {
        return val + "% Usados / " + (100 - val) + "% Por Usar";
      },
    },
  },
}));

// Apenas uma série com a porcentagem de materiais usados
const chartSeries = computed(() => [pctUsados.value]);
</script>

<style scoped>
.dashboard-container {
  background: #fff;
}

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

.stats-only-grid {
  margin-top: 16px;
}

.single-chart {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}
</style>
