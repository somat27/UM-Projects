<template>
  <div class="occurrences-map-container">
    <!-- Seção de filtros sem título -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="filter-group">
          <label for="statusFilter">Status:</label>
          <select
            id="statusFilter"
            v-model="filtros.status"
            @change="aplicarFiltros"
            class="filter-select"
          >
            <option value="">Todos</option>
            <option value="Pendente">Pendente</option>
            <option value="Analise">Em Análise</option>
            <option value="Resolvido">Resolvido</option>
            <option value="Rejeitado">Rejeitado</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="tipoFilter">Tipo de Ocorrência:</label>
          <select
            id="tipoFilter"
            v-model="filtros.tipoOcorrencia"
            @change="aplicarFiltros"
            class="filter-select"
          >
            <option value="">Todos</option>
            <option v-for="tipo in tiposOcorrencia" :key="tipo" :value="tipo">
              {{ mapearTipoOcorrencia(tipo) }}
            </option>
          </select>
        </div>

        <button @click="limparFiltros" class="filter-button">
          Limpar Filtros
        </button>
      </div>
    </div>

    <!-- Container do mapa -->
    <div class="map-container">
      <div v-if="loading" class="loading-container">
        <div class="loader"></div>
        <p>Carregando ocorrências...</p>
      </div>

      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="tentarNovamente" class="retry-button">
          <i class="bi bi-arrow-repeat"></i> Tentar novamente
        </button>
      </div>

      <div v-else-if="ocorrenciasFiltradas.length === 0" class="empty-message">
        <p>Nenhuma ocorrência encontrada.</p>
      </div>

      <div v-else id="map" class="google-map"></div>
    </div>

    <div v-if="selectedOcorrencia" class="modal-overlay">
      <transition name="fade">
        <div class="occurrence-details-modal">
          <div class="details-header">
            <h3>Detalhes da Ocorrência</h3>
            <button @click="closeDetails" class="close-button">✕</button>
          </div>

          <div class="details-content">
            <div class="details-info">
              <div class="detail-item">
                <span class="detail-label">Data:</span>
                <span class="detail-value">{{
                  formatarData(selectedOcorrencia.dataSubmissao)
                }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Localização:</span>
                <span class="detail-value">{{
                  selectedOcorrencia.endereco || "Endereço não disponível"
                }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Tipo:</span>
                <span class="detail-value">{{
                  mapearTipoOcorrencia(selectedOcorrencia.tipoOcorrencia)
                }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Status:</span>
                <span class="detail-value">
                  <StatusBadge
                    :status="mapearStatus(selectedOcorrencia.status)"
                  />
                </span>
              </div>
            </div>

            <div class="details-section">
              <h4>Descrição</h4>
              <div class="description-box">
                <p>
                  {{
                    selectedOcorrencia.descricao || "Sem descrição disponível."
                  }}
                </p>
              </div>
            </div>

            <div
              v-if="
                selectedOcorrencia.imagemVideo &&
                selectedOcorrencia.imagemVideo.length > 0
              "
              class="details-section images-section"
            >
              <h4>Imagens e Videos</h4>
              <div class="images-grid">
                <div
                  v-for="(media, index) in selectedOcorrencia.imagemVideo"
                  :key="index"
                  class="image-item"
                >
                  <template v-if="isVideo(media)">
                    <!-- Exibe o vídeo -->
                    <div class="play-container">
                      <img
                        src="../../assets/play-icon.png"
                        alt="Play"
                        class="play-icon"
                        @click="ampliarImagem(media)"
                      />
                    </div>
                  </template>
                  <template v-else>
                    <!-- Exibe a imagem -->
                    <img
                      :src="media"
                      alt="Imagem da ocorrência"
                      @click="ampliarImagem(media)"
                    />
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import StatusBadge from "../OcurrencePage/StatusBadge.vue";
import { getOcorrencias } from "@/services/firebase";

export default {
  name: "OccurrencesMap",
  components: {
    StatusBadge,
  },
  data() {
    return {
      ocorrencias: [],
      tiposOcorrencia: [],
      loading: true,
      error: null,
      selectedOcorrencia: null,
      map: null,
      markers: [],
      infoWindow: null,
      filtros: {
        status: "",
        tipoOcorrencia: "",
      },
      tiposMapeados: {
        lights: "Iluminação Pública",
        roads: "Vias e Estradas",
        sinals: "Sinalização",
      },
      isRetrying: false,
      retryCount: 0,
      maxRetries: 3,
      googleMapsLoaded: false,
      ocorrenciasCarregadas: false,
      mapsInitCallback: null,

      statusMarkerIcons: {
        Rejeitado: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
        Pendente: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
        Analise: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        Resolvido: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
      },
    };
  },
  computed: {
    ocorrenciasFiltradas() {
      let resultado = [...this.ocorrencias];

      if (this.filtros.status) {
        resultado = resultado.filter((o) => o.status === this.filtros.status);
      }

      if (this.filtros.tipoOcorrencia) {
        resultado = resultado.filter(
          (o) => o.tipoOcorrencia === this.filtros.tipoOcorrencia
        );
      }

      return resultado;
    },
  },
  watch: {
    $route: {
      handler() {
        this.iniciarCarregamentoCompleto();
      },
      immediate: true,
    },
  },
  created() {
    this.iniciarCarregamentoCompleto();
  },
  methods: {
    isVideo(media) {
      // Verifica a extensão do arquivo para identificar se é um vídeo
      const videoExtensions = ["mp4", "webm", "ogg"];
      const extension = media.split(".").pop().toLowerCase();
      return videoExtensions.includes(extension);
    },
    async iniciarCarregamentoCompleto() {
      try {
        await this.carregarOcorrencias();
        await this.carregarGoogleMapsAPI();

        if (this.ocorrenciasCarregadas && this.googleMapsLoaded && this.map) {
          this.reinicializarMapa();
        }
      } catch (error) {
        console.error("Erro ao inicializar componente:", error);
        this.error = "Erro ao carregar o mapa e ocorrências.";
      }
    },

    async carregarOcorrencias() {
      try {
        this.loading = true;
        this.error = null;
        this.ocorrenciasCarregadas = false;

        const timeout = new Promise((_, reject) =>
          setTimeout(() => reject(new Error("Timeout")), 15000)
        );

        const ocorrencias = await Promise.race([getOcorrencias(), timeout]);

        if (!Array.isArray(ocorrencias)) {
          throw new Error("Formato de dados inválido");
        }

        this.ocorrencias = [...ocorrencias];
        this.tiposOcorrencia = [
          ...new Set(
            ocorrencias
              .filter((o) => o && o.tipoOcorrencia)
              .map((o) => o.tipoOcorrencia)
          ),
        ];
        this.ocorrenciasCarregadas = true;

        this.retryCount = 0;
        this.isRetrying = false;
      } catch (error) {
        console.error("Erro ao carregar ocorrências:", error);

        if (this.retryCount < this.maxRetries && !this.isRetrying) {
          this.retryCount++;
          this.isRetrying = true;
          setTimeout(() => {
            this.isRetrying = false;
            this.carregarOcorrencias();
          }, 3000);
        } else {
          this.error = "Erro ao carregar ocorrências.";
        }
      } finally {
        this.loading = false;
      }
    },

    async carregarGoogleMapsAPI() {
      return new Promise((resolve, reject) => {
        if (window.google && window.google.maps) {
          this.googleMapsLoaded = true;
          this.inicializarMapa();
          resolve();
          return;
        }

        const apiKey = process.env.VUE_APP_API_KEY;
        if (!apiKey) {
          this.error = "API Key do Google Maps não encontrada.";
          reject(new Error("API Key não disponível"));
          return;
        }

        const callbackName = `initMapCallback_${Date.now()}`;
        this.mapsInitCallback = callbackName;

        window[callbackName] = () => {
          this.googleMapsLoaded = true;
          this.inicializarMapa();
          delete window[callbackName];
          resolve();
        };

        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=${callbackName}`;
        script.async = true;
        script.onerror = () => {
          this.error = "Erro ao carregar Google Maps.";
          delete window[callbackName];
          reject(new Error("Erro no carregamento do script"));
        };
        document.head.appendChild(script);
      });
    },

    inicializarMapa() {
      const mapDiv = document.getElementById("map");
      if (!mapDiv) {
        console.error("Elemento do mapa não encontrado");
        this.error = "Elemento do mapa não encontrado.";
        return;
      }

      const center = { lat: 38.7223, lng: -9.1393 };

      this.map = new window.google.maps.Map(mapDiv, {
        center,
        zoom: 12,
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true,
      });

      this.infoWindow = new window.google.maps.InfoWindow();

      if (this.ocorrenciasCarregadas) {
        this.renderizarMarcadores();
      }
    },

    reinicializarMapa() {
      const mapDiv = document.getElementById("map");

      if (!mapDiv) {
        console.error("Elemento do mapa não encontrado");
        this.error = "Elemento do mapa não encontrado.";
        return;
      }

      if (this.map && window.google?.maps) {
        window.google.maps.event.clearInstanceListeners(this.map);
        this.map = null;
      }

      const center = { lat: 38.7223, lng: -9.1393 };

      this.map = new window.google.maps.Map(mapDiv, {
        center,
        zoom: 12,
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true,
      });

      this.infoWindow = new window.google.maps.InfoWindow();

      this.renderizarMarcadores();
    },

    renderizarMarcadores() {
      this.markers = [];
      this.adicionarMarcadores();
    },

    adicionarMarcadores() {
      if (!this.map || !this.googleMapsLoaded || !this.ocorrenciasCarregadas) {
        return;
      }

      const ocorrencias = this.ocorrenciasFiltradas;
      const bounds = new window.google.maps.LatLngBounds();
      let temCoordenadasValidas = false;

      ocorrencias.forEach((o) => {
        if (
          !o?.coordenadas ||
          isNaN(o.coordenadas.latitude) ||
          isNaN(o.coordenadas.longitude)
        ) {
          return;
        }

        const pos = {
          lat: parseFloat(o.coordenadas.latitude),
          lng: parseFloat(o.coordenadas.longitude),
        };

        temCoordenadasValidas = true;

        // Usar o ícone correspondente ao status ou um ícone padrão se não encontrado
        const markerIcon =
          this.statusMarkerIcons[o.status] ||
          "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png"; // Ícone padrão

        const marker = new window.google.maps.Marker({
          position: pos,
          map: this.map,
          title: this.mapearTipoOcorrencia(o.tipoOcorrencia),
          animation: window.google.maps.Animation.DROP,
          icon: markerIcon,
        });

        marker.addListener("click", () => {
          this.infoWindow.open(this.map, marker);
          this.selectedOcorrencia = o;
        });

        this.markers.push(marker);
        bounds.extend(pos);
      });

      if (temCoordenadasValidas) {
        this.map.fitBounds(bounds);
        if (this.markers.length === 1) {
          this.map.setZoom(15);
        }
      } else {
        this.map.setCenter({ lat: 38.7223, lng: -9.1393 });
        this.map.setZoom(12);
      }
    },

    mapearTipoOcorrencia(tipo) {
      return this.tiposMapeados[tipo] || tipo || "Tipo não especificado";
    },

    aplicarFiltros() {
      this.selectedOcorrencia = null;
      if (this.infoWindow) this.infoWindow.close();
      this.reinicializarMapa();
    },

    limparFiltros() {
      this.filtros = {
        status: "",
        tipoOcorrencia: "",
      };
      this.aplicarFiltros();
    },

    formatarData(timestamp) {
      try {
        let data;
        if (timestamp instanceof Date) data = timestamp;
        else if (timestamp?.toDate) data = timestamp.toDate();
        else data = new Date(timestamp);

        return isNaN(data.getTime())
          ? "Data inválida"
          : data.toLocaleDateString("pt-PT");
      } catch {
        return "Data inválida";
      }
    },

    mapearStatus(status) {
      const m = {
        Pendente: "pending",
        Analise: "analyzing",
        Resolvido: "resolved",
        Rejeitado: "rejected",
      };
      return m[status] || "pending";
    },

    closeDetails() {
      this.selectedOcorrencia = null;
      if (this.infoWindow) this.infoWindow.close();
    },

    ampliarImagem(url) {
      if (url) window.open(url, "_blank", "noopener,noreferrer");
    },

    tentarNovamente() {
      this.error = null;
      this.iniciarCarregamentoCompleto();
    },
  },
  beforeUnmount() {
    this.markers.forEach((m) =>
      window.google?.maps?.event.clearInstanceListeners(m)
    );

    if (this.map && window.google?.maps) {
      window.google.maps.event.clearInstanceListeners(this.map);
    }

    this.map = null;
    this.infoWindow = null;
  },
};
</script>

<style scoped>
.occurrences-map-container {
  width: 100%;
  position: relative;
}

/* Estilos para a seção de filtros */
.filters-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.6s ease-in-out;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 200px;
}

.filter-group label {
  margin-bottom: 5px;
  font-weight: 500;
}

.filter-select {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

.filter-select:focus {
  border-color: #204c6d;
  box-shadow: 0 0 0 3px rgba(32, 76, 109, 0.2);
  outline: none;
}

.filter-button {
  padding: 8px 15px;
  background-color: #204c6d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.filter-button:hover {
  background-color: #173a54;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.filter-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Efeito de ondulação para o botão */
.filter-button::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%, -50%);
  transform-origin: 50% 50%;
}

.filter-button:active::after {
  animation: ripple 0.6s ease-out;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  20% {
    transform: scale(25, 25);
    opacity: 0.5;
  }
  100% {
    opacity: 0;
    transform: scale(40, 40);
  }
}

.map-container {
  width: 100%;
  height: 400px;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  animation: slideInUp 0.5s ease-out;
}

.google-map {
  width: 100%;
  height: 100%;
}

.loading-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 5;
  animation: pulse 1.5s infinite;
}

.loader {
  border: 5px solid #f3f3f3;
  border-top: 5px solid #204c6d;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

.empty-message {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  z-index: 5;
  animation: fadeIn 0.5s ease-in-out;
}

.empty-message p {
  padding: 30px;
  text-align: center;
  color: #666;
  font-weight: 500;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.occurrence-details-modal {
  width: 75%;
  max-height: 85vh;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
  animation: zoomIn 0.3s ease-out;
}

@keyframes zoomIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eaeaea;
  background-color: #204c6d;
  color: white;
  border-radius: 8px 8px 0 0;
  position: sticky;
  top: 0;
  z-index: 5;
}

.details-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  color: white;
  font-size: 22px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  border-radius: 50%;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.details-content {
  padding: 25px;
}

.details-info {
  margin-bottom: 25px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.detail-item {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 600;
  color: #555;
  font-size: 15px;
  margin-bottom: 5px;
}

.detail-value {
  color: #333;
  font-size: 16px;
}

.details-section {
  margin-bottom: 25px;
  animation: fadeIn 0.5s ease-in-out;
}

.details-section:last-child {
  margin-bottom: 0;
}

.details-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #204c6d;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 10px;
  position: relative;
}

.details-section h4::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -1px;
  width: 60px;
  height: 3px;
  background-color: #204c6d;
  transition: width 0.3s ease-in-out;
}

.details-section:hover h4::after {
  width: 120px;
}

.description-box {
  background-color: white;
  border-radius: 5px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #eaeaea;
  transition: box-shadow 0.3s ease;
}

.description-box:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.description-box p {
  margin: 0;
  line-height: 1.6;
  font-size: 15px;
}

.images-section {
  margin-top: 25px;
}

.images-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.image-item {
  width: 120px;
  height: 120px;
  overflow: hidden;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  border: 2px solid white;
  transition: all 0.3s ease;
}

.image-item:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
  border-color: #204c6d;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.image-item:hover img {
  transform: scale(1.1);
}

@media (max-width: 991px) {
  .filters-row {
    flex-direction: column;
    gap: 10px;
  }

  .filter-group {
    width: 100%;
  }

  .occurrence-details-modal {
    width: 85%;
  }
}

@media (max-width: 640px) {
  .map-container {
    height: 400px;
  }

  .occurrence-details-modal {
    width: 95%;
    max-height: 80vh;
  }

  .details-content {
    padding: 15px;
  }

  .images-grid {
    gap: 10px;
  }

  .image-item {
    width: 80px;
    height: 80px;
  }
}

.play-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  scale: 0.2;
}
</style>
