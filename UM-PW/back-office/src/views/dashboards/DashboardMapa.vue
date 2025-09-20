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

          <!-- Conteúdo do Mapa -->
          <div v-if="activeTab === 'mapa'" class="map-container">
            <div class="map-controls">
              <div class="map-legend">
                <div class="legend-item">
                  <span class="legend-marker pendente-marker"></span>
                  <span>Ocorrências Pendentes</span>
                </div>
                <div class="legend-item">
                  <span class="legend-marker analise-marker"></span>
                  <span>Auditorias a decorrer</span>
                </div>
                <div class="legend-item">
                  <span class="legend-marker resolvido-marker"></span>
                  <span>Auditorias finalizadas</span>
                </div>
                <div class="legend-item">
                  <span class="legend-marker rejeitado-marker"></span>
                  <span>Ocorrências Rejeitadas</span>
                </div>
              </div>
              <div class="map-filters">
                <label class="filter-checkbox">
                  <input
                    type="checkbox"
                    v-model="filtros.mostrarPendentes"
                    @change="
                      limparMarcadores();
                      adicionarMarcadores();
                    "
                  />
                  <span>Pendentes</span>
                </label>
                <label class="filter-checkbox">
                  <input
                    type="checkbox"
                    v-model="filtros.mostrarAnalise"
                    @change="
                      limparMarcadores();
                      adicionarMarcadores();
                    "
                  />
                  <span>Em Análise</span>
                </label>
                <label class="filter-checkbox">
                  <input
                    type="checkbox"
                    v-model="filtros.mostrarResolvidos"
                    @change="
                      limparMarcadores();
                      adicionarMarcadores();
                    "
                  />
                  <span>Resolvidas</span>
                </label>
                <label class="filter-checkbox">
                  <input
                    type="checkbox"
                    v-model="filtros.mostrarRejeitados"
                    @change="
                      limparMarcadores();
                      adicionarMarcadores();
                    "
                  />
                  <span>Rejeitadas</span>
                </label>
              </div>
            </div>
            <div id="google-map" ref="googleMap" class="google-map"></div>
          </div>
        </div>
      </main>
    </div>
  </div>

  <!-- Modal para detalhes -->
  <div v-if="modalVisible" class="modal-overlay" @click.self="fecharModal">
    <div class="modal-content">
      <div class="modal-body">
        <DetailModal
          v-if="ocorrenciaSelecionada"
          :ocorrencia="ocorrenciaSelecionada"
          :auditoria="auditoriaSelecionada"
          @fechar="fecharModal"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import NavigationList from "@/components/NavigationList.vue";
import DetailModal from "@/components/DetailModal.vue";
import { db } from "@/firebase.js";
import { collection, getDocs } from "firebase/firestore";

const activeTab = ref("mapa");
const googleMap = ref(null);
const map = ref(null);
const markers = ref([]);
const dados = ref([]);
const auditorias = ref([]); // Nova ref para armazenar auditorias
const filtros = ref({
  mostrarPendentes: true,
  mostrarAnalise: true,
  mostrarResolvidos: true,
  mostrarRejeitados: true,
});

// Estado para controle da modal
const modalVisible = ref(false);
const modalTitulo = ref("");
const ocorrenciaSelecionada = ref(null);
const auditoriaSelecionada = ref(null); // Nova ref para auditoria selecionada

// Ícones para os diferentes status
const STATUS_ICONS = {
  Pendente: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
  Analise: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
  Resolvido: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
  Rejeitado: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
};

// Função para buscar todas as ocorrências e auditorias
async function getDados() {
  try {
    // Buscar ocorrências
    const ocorrenciasRef = collection(db, "ocorrencias");
    const ocorrenciasSnapshot = await getDocs(ocorrenciasRef);

    const ocorrencias = [];
    for (const doc of ocorrenciasSnapshot.docs) {
      const ocorrencia = { id: doc.id, ...doc.data() };
      if (
        ocorrencia.coordenadas &&
        ocorrencia.coordenadas.latitude &&
        ocorrencia.coordenadas.longitude
      ) {
        ocorrencias.push(ocorrencia);
      }
    }

    // Buscar auditorias
    const auditoriasRef = collection(db, "auditorias");
    const auditoriasSnapshot = await getDocs(auditoriasRef);

    const auditoriasData = [];
    for (const doc of auditoriasSnapshot.docs) {
      const auditoria = { id: doc.id, ...doc.data() };
      auditoriasData.push(auditoria);
    }

    // Armazenar auditorias na ref
    auditorias.value = auditoriasData;

    console.log(
      "Dados carregados:",
      ocorrencias.length,
      "ocorrências,",
      auditoriasData.length,
      "auditorias"
    );
    return ocorrencias;
  } catch (error) {
    console.error("Erro ao buscar dados:", error);
    throw error;
  }
}

// Função para inicializar o mapa
function inicializarMapa() {
  const mapElement = document.getElementById("google-map");
  if (!mapElement || !window.google) {
    console.error(
      "Elemento do mapa não encontrado ou API do Google não carregada"
    );
    return;
  }

  console.log("Inicializando mapa com elemento:", mapElement);

  const centroInicial = { lat: 38.7223, lng: -9.1393 }; //incio

  try {
    map.value = new window.google.maps.Map(mapElement, {
      center: centroInicial,
      zoom: 7,
      mapTypeControl: true,
      streetViewControl: false,
      fullscreenControl: true,
      zoomControl: true,
      styles: [
        {
          featureType: "poi",
          elementType: "labels",
          stylers: [{ visibility: "off" }],
        },
      ],
    });

    console.log("Mapa inicializado com sucesso");
  } catch (error) {
    console.error("Erro ao inicializar o mapa:", error);
  }
}

async function carregarDados() {
  try {
    limparMarcadores();

    if (dados.value.length === 0) {
      const ocorrencias = await getDados();
      dados.value = ocorrencias;
      console.log("Dados iniciais carregados:", dados.value.length);
    }

    adicionarMarcadores();
  } catch (error) {
    console.error("Erro ao carregar dados:", error);
  }
}
function determinarCategoria(ocorrencia) {
  if (!ocorrencia || !ocorrencia.status) {
    console.error("ocorrencia ou status não encontrado", ocorrencia);
    return "Pendente";
  }

  // Categorizar com base no status
  if (ocorrencia.status === "Pendente") {
    return "Pendente";
  } else if (ocorrencia.status === "Analise") {
    return "Analise";
  } else if (ocorrencia.status === "Resolvido") {
    return "Resolvido";
  } else if (ocorrencia.status === "Rejeitado") {
    return "Rejeitado";
  }

  return "Pendente";
}

// Função para encontrar a auditoria correspondente à ocorrência
function encontrarAuditoria(ocorrenciaId) {
  return auditorias.value.find((auditoria) => auditoria.id === ocorrenciaId);
}

// Função para abrir a modal com detalhes da ocorrência selecionada
function abrirModal(ocorrencia) {
  // Definir o ocorrencia selecionado
  ocorrenciaSelecionada.value = ocorrencia;

  // Encontrar a auditoria correspondente
  const auditoria = encontrarAuditoria(ocorrencia.id);
  auditoriaSelecionada.value = auditoria;

  // Definir o título da modal
  modalTitulo.value = `Ocorrência: ${ocorrencia.titulo || "Sem título"}`;

  // Exibir a modal
  modalVisible.value = true;

  console.log("Modal aberta com ocorrência:", ocorrencia);
  console.log("Auditoria relacionada:", auditoria || "Não encontrada");
}

// Função para fechar a modal
function fecharModal() {
  modalVisible.value = false;
  ocorrenciaSelecionada.value = null;
  auditoriaSelecionada.value = null;
}

// Função para adicionar marcadores no mapa
function adicionarMarcadores() {
  // Garantir que o mapa está inicializado
  if (!map.value || !window.google) {
    console.error("Mapa não inicializado");
    return;
  }

  console.log("Adicionando marcadores...");
  console.log("Filtros atuais:", filtros.value);

  // Limpar marcadores existentes
  limparMarcadores();

  // Contador para verificar quantos marcadores foram adicionados
  let marcadoresAdicionados = 0;

  dados.value.forEach((ocorrencia) => {
    // Determinar a categoria da ocorrência
    const categoria = determinarCategoria(ocorrencia);

    // Verificar se esta categoria deve ser mostrada com base nos filtros
    if (
      (categoria === "Pendente" && filtros.value.mostrarPendentes) ||
      (categoria === "Analise" && filtros.value.mostrarAnalise) ||
      (categoria === "Resolvido" && filtros.value.mostrarResolvidos) ||
      (categoria === "Rejeitado" && filtros.value.mostrarRejeitados)
    ) {
      // Verifica se tem coordenadas válidas
      if (
        ocorrencia.coordenadas &&
        ocorrencia.coordenadas.latitude &&
        ocorrencia.coordenadas.longitude
      ) {
        const titulo = ocorrencia.titulo || "Ocorrência";

        const marker = criarMarcador(
          ocorrencia.coordenadas.latitude,
          ocorrencia.coordenadas.longitude,
          titulo,
          categoria,
          ocorrencia
        );

        if (marker) {
          markers.value.push(marker);
          marcadoresAdicionados++;
        }
      }
    }
  });

  console.log(`Adicionados ${marcadoresAdicionados} marcadores`);

  // Só ajustar o zoom se houver marcadores
  if (marcadoresAdicionados > 0) {
    // Ajustar o zoom para mostrar todos os marcadores
    ajustarZoom();
  }
}

// Função para criar um marcador
function criarMarcador(lat, lng, titulo, categoria, ocorrencia) {
  if (!window.google || !map.value) return null;

  const position = { lat: parseFloat(lat), lng: parseFloat(lng) };

  // Validar posição
  if (isNaN(position.lat) || isNaN(position.lng)) {
    console.error("Coordenadas inválidas:", lat, lng);
    return null;
  }

  // Configuração do ícone com base na categoria
  const icone = {
    url: STATUS_ICONS[categoria],
    scaledSize: new window.google.maps.Size(30, 30),
  };

  // Criar marcador
  const marker = new window.google.maps.Marker({
    position,
    map: map.value,
    title: titulo,
    icon: icone,
    animation: window.google.maps.Animation.DROP,
  });

  // Adicionar evento de clique para abrir a modal
  marker.addListener("click", () => {
    abrirModal(ocorrencia);
  });

  return marker;
}

function limparMarcadores() {
  console.log("Limpando", markers.value.length, "marcadores");

  // 1. Remover todos os marcadores do mapa
  for (const marker of markers.value) {
    marker.setMap(null);
  }

  // 2. Limpar array de marcadores
  markers.value = [];

  // 3. Recriar o mapa a partir do elemento DOM
  const mapElement = document.getElementById("google-map");
  if (!mapElement) {
    console.warn("Elemento #google-map não encontrado");
    return;
  }

  const centroInicial = { lat: 38.7223, lng: -9.1393 }; // Lisboa

  map.value = new window.google.maps.Map(mapElement, {
    center: centroInicial,
    zoom: 7,
    mapTypeControl: true,
    streetViewControl: false,
    fullscreenControl: true,
    zoomControl: true,
    styles: [
      {
        featureType: "poi",
        elementType: "labels",
        stylers: [{ visibility: "off" }],
      },
    ],
  });

  console.log("Mapa reiniciado com sucesso");
}

// Função para ajustar o zoom para mostrar todos os marcadores
function ajustarZoom() {
  if (!markers.value.length || !window.google || !map.value) return;

  const bounds = new window.google.maps.LatLngBounds();
  let marcadoresValidos = 0;

  markers.value.forEach((marker) => {
    if (marker && marker.getPosition()) {
      bounds.extend(marker.getPosition());
      marcadoresValidos++;
    }
  });

  if (marcadoresValidos > 0) {
    map.value.fitBounds(bounds);

    // Se houver apenas um marcador, ajustar o zoom
    if (marcadoresValidos === 1) {
      map.value.setZoom(12);
    }
  }
}

// Carregar script da Google Maps API
function carregarGoogleMapsAPI() {
  return new Promise((resolve, reject) => {
    // Verificar se o script já foi carregado
    if (window.google && window.google.maps) {
      console.log("Google Maps API já está carregada");
      resolve();
      return;
    }

    // Obter API Key do ambiente
    const apiKey = process.env.VUE_APP_API_KEY;

    if (!apiKey) {
      console.error(
        "API Key do Google Maps não encontrada nas variáveis de ambiente"
      );
      reject(new Error("API Key não encontrada"));
      return;
    }

    // Definir callback global para quando a API estiver carregada
    window.initMap = () => {
      console.log("Google Maps API carregada com sucesso");
      resolve();
    };

    // Criar elemento de script
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initMap`;
    script.async = true;
    script.defer = true;

    script.onerror = () => {
      console.error("Falha ao carregar Google Maps API");
      reject(new Error("Falha ao carregar Google Maps API"));
    };

    // Adicionar script ao documento
    document.head.appendChild(script);
  });
}

// Setup do componente ao montar
onMounted(async () => {
  console.log("Componente montado, aba ativa:", activeTab.value);

  // Apenas inicializar o mapa se estiver na aba correta
  if (activeTab.value === "mapa") {
    try {
      console.log("Iniciando carregamento do mapa");
      await carregarGoogleMapsAPI();
      console.log("API carregada, inicializando mapa");

      // Usar setTimeout para garantir que o DOM esteja pronto
      setTimeout(() => {
        inicializarMapa();
        carregarDados();
      }, 200);
    } catch (error) {
      console.error("Erro ao configurar o mapa:", error);
    }
  }
});

// Observar alterações na aba ativa
watch(activeTab, async (novoValor) => {
  console.log("Aba alterada para:", novoValor);

  if (novoValor === "mapa") {
    try {
      console.log("Carregando mapa após troca de aba");

      // Verificar se a API já está carregada
      if (!window.google || !window.google.maps) {
        await carregarGoogleMapsAPI();
      }

      // Verificar se o mapa já está inicializado
      if (!map.value) {
        inicializarMapa();
      }

      // Carregar dados e aplicar os filtros
      setTimeout(() => {
        carregarDados();
      }, 200);
    } catch (error) {
      console.error("Erro ao configurar o mapa após troca de aba:", error);
    }
  }
});

// Observar alterações nos filtros
watch(
  filtros,
  (novoValor) => {
    console.log("Filtros alterados:", novoValor);
    // Apenas recarregar marcadores se o componente estiver na aba mapa
    if (activeTab.value === "mapa") {
      limparMarcadores();
      adicionarMarcadores();
    }
  },
  { deep: true }
);
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
  align-ocorrencias: center;
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
  color: #204c6d;
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
  color: #204c6d;
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

/* Estilos específicos do mapa */
.map-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  min-height: 500px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
}

.google-map {
  flex: 1;
  width: 100%;
  border-radius: 0 0 8px 8px;
}

.map-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
}

.map-legend {
  display: flex;
  align-items: center;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #495057;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.pendente-marker {
  background-color: #faad14; /* Amarelo */
}

.analise-marker {
  background-color: #1e90ff; /* Azul*/
}

.resolvido-marker {
  background-color: #52c41a; /* Verde */
}

.rejeitado-marker {
  background-color: #ff4d4f; /* Vermelho */
}

.map-filters {
  display: flex;
  gap: 16px;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #495057;
  cursor: pointer;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
  border-radius: 8px 8px 0 0;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #262626;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #8c8c8c;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: #f5f5f5;
  color: #262626;
}

.modal-body {
  padding: 20px 24px;
}

/* Estilos responsivos */
@media (max-width: 768px) {
  .map-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .map-container {
    height: calc(100vh - 160px);
  }

  .map-legend {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .map-filters {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .modal-content {
    width: 95%;
    max-height: 85vh;
  }
}
</style>
