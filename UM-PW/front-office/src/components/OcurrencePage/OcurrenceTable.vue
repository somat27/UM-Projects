<template>
  <div class="occurrences-container">
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

    <!-- Tabela de ocorrências -->
    <div class="occurrences-table-wrapper">
      <div class="occurrences-table">
        <div class="table-header">
          <div class="header-cell">Data</div>
          <div class="header-cell location-cell">Localização</div>
          <div class="header-cell type-cell">Tipo</div>
          <div class="header-cell status-cell">Estado</div>
        </div>

        <div v-if="loading" class="loading-container">
          <div class="loader"></div>
          <p>Carregando ocorrências...</p>
        </div>

        <div
          v-else-if="ocorrenciasFiltradas.length === 0"
          class="empty-message"
        >
          <p>Nenhuma ocorrência encontrada.</p>
        </div>

        <template v-else>
          <transition-group name="list" tag="div">
            <div
              v-for="ocorrencia in ocorrenciasFiltradas"
              :key="ocorrencia.id"
              class="row-container"
            >
              <div
                class="table-row"
                :class="{ active: selectedOcorrenciaId === ocorrencia.id }"
                @click="toggleDetails(ocorrencia.id)"
              >
                <div class="table-cell">
                  {{ formatarData(ocorrencia.dataSubmissao) }}
                </div>
                <div class="table-cell location-cell">
                  {{ ocorrencia.endereco || "Endereço não disponível" }}
                </div>
                <div class="table-cell type-cell">
                  {{ mapearTipoOcorrencia(ocorrencia.tipoOcorrencia) }}
                </div>
                <div class="table-cell status-cell">
                  <StatusBadge :status="mapearStatus(ocorrencia.status)" />
                </div>
              </div>

              <!-- Dropdown com detalhes da ocorrência -->
              <transition name="slide">
                <div
                  v-if="selectedOcorrenciaId === ocorrencia.id"
                  class="details-dropdown"
                >
                  <div class="details-content">
                    <div class="details-section">
                      <h4>Descrição</h4>
                      <div class="description-box">
                        <p>
                          {{
                            ocorrencia.descricao || "Sem descrição disponível."
                          }}
                        </p>
                      </div>
                    </div>

                    <div
                      v-if="
                        ocorrencia.imagemVideo &&
                        ocorrencia.imagemVideo.length > 0
                      "
                      class="details-section images-section"
                    >
                      <h4>Imagens</h4>
                      <transition-group
                        name="gallery"
                        tag="div"
                        class="images-grid"
                      >
                        <div
                          v-for="(media, index) in ocorrencia.imagemVideo"
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
                      </transition-group>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </transition-group>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import StatusBadge from "./StatusBadge.vue";
import { getOcorrencias } from "@/services/firebase";

export default {
  name: "OccurrencesTable",
  components: {
    StatusBadge,
  },
  data() {
    return {
      ocorrencias: [],
      tiposOcorrencia: [],
      loading: true,
      error: null,
      selectedOcorrenciaId: null,
      filtros: {
        status: "",
        tipoOcorrencia: "",
      },
      tiposMapeados: {
        lights: "Iluminação Pública",
        roads: "Vias e Estradas",
        sinals: "Sinalização",
      },
    };
  },
  computed: {
    ocorrenciasFiltradas() {
      let resultado = [...this.ocorrencias];

      // Aplicar filtro de status
      if (this.filtros.status) {
        resultado = resultado.filter(
          (ocorrencia) => ocorrencia.status === this.filtros.status
        );
      }

      // Aplicar filtro de tipo de ocorrência
      if (this.filtros.tipoOcorrencia) {
        resultado = resultado.filter(
          (ocorrencia) =>
            ocorrencia.tipoOcorrencia === this.filtros.tipoOcorrencia
        );
      }

      return resultado;
    },
  },
  async created() {
    await this.carregarOcorrencias();
  },
  methods: {
    isVideo(media) {
      // Verifica a extensão do arquivo para identificar se é um vídeo
      const videoExtensions = ["mp4", "webm", "ogg"];
      const extension = media.split(".").pop().toLowerCase();
      return videoExtensions.includes(extension);
    },
    async carregarOcorrencias() {
      try {
        this.loading = true;
        this.ocorrencias = await getOcorrencias();

        this.tiposOcorrencia = [
          ...new Set(this.ocorrencias.map((o) => o.tipoOcorrencia)),
        ];

        this.error = null;
      } catch (error) {
        console.error("Erro ao carregar ocorrências:", error);
        this.error =
          "Falha ao carregar as ocorrências. Por favor, tente novamente.";
      } finally {
        this.loading = false;
      }
    },

    mapearTipoOcorrencia(tipo) {
      return this.tiposMapeados[tipo] || tipo;
    },
    aplicarFiltros() {
      this.selectedOcorrenciaId = null; // Fecha qualquer dropdown aberto ao filtrar
    },
    limparFiltros() {
      this.filtros = {
        status: "",
        tipoOcorrencia: "",
      };
      this.selectedOcorrenciaId = null;
    },
    formatarData(timestamp) {
      if (!timestamp) return "Data não disponível";

      const data = timestamp instanceof Date ? timestamp : timestamp.toDate();

      return data.toLocaleDateString("pt-PT", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    },
    mapearStatus(status) {
      //mapeamento com a firebase
      const mapeamentoStatus = {
        Pendente: "pending",
        Analise: "analyzing",
        Resolvido: "resolved",
        Rejeitado: "rejected",
      };

      return mapeamentoStatus[status];
    },
    toggleDetails(ocorrenciaId) {
      if (this.selectedOcorrenciaId === ocorrenciaId) {
        this.selectedOcorrenciaId = null;
      } else {
        this.selectedOcorrenciaId = ocorrenciaId;
      }
    },
    ampliarImagem(imagemUrl) {
      window.open(imagemUrl, "_blank");
    },
  },
};
</script>

<style scoped>
.occurrences-container {
  width: 100%;
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
  flex: 1;
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
  width: 100%;
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
  min-height: 38px;
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

/* Estilos para a tabela */
.occurrences-table-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.occurrences-table {
  width: 100%;
  min-width: 500px;
  border-collapse: collapse;
  animation: slideInUp 0.5s ease-out;
}

.table-header {
  display: flex;
  color: #fff;
  padding: 12px 0;
  background-color: #204c6d;
  border-radius: 5px 5px 0 0;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.header-cell {
  flex: 1;
  padding: 10px;
  text-align: left;
  font-weight: 700;
}

.row-container {
  position: relative;
}

.table-row {
  display: flex;
  border-bottom: 1px solid #ddd;
  padding: 12px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.table-row:hover {
  background-color: #f5f5f5;
  transform: translateX(5px);
}

.table-row.active {
  background-color: #e6f7ff;
  border-left: 4px solid #1890ff;
}

.table-cell {
  flex: 1;
  padding: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Ajustes específicos para colunas em dispositivos móveis */
.location-cell {
  flex: 1.5;
}

.type-cell {
  flex: 1;
}

.status-cell {
  flex: 0.8;
  min-width: 90px;
}

.loading-container {
  padding: 30px;
  text-align: center;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
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
  padding: 25px;
  text-align: center;
  width: 100%;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 5px;
  animation: fadeIn 0.5s ease-in-out;
}

/* Estilos para o dropdown e detalhes */
.details-dropdown {
  width: 100%;
  background-color: #f9f9f9;
  overflow: hidden;
  border-bottom: 1px solid #ddd;
}

.details-content {
  padding: 15px;
}

.details-section {
  margin-bottom: 15px;
  animation: fadeIn 0.5s ease-in-out;
}

.details-section:last-child {
  margin-bottom: 0;
}

.details-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #204c6d;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 8px;
  position: relative;
}

.details-section h4::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -1px;
  width: 50px;
  height: 3px;
  background-color: #204c6d;
  transition: width 0.3s ease-in-out;
}

.details-section:hover h4::after {
  width: 100px;
}

.description-box {
  background-color: white;
  border-radius: 4px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #eaeaea;
  transition: box-shadow 0.3s ease;
}

.description-box:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.description-box p {
  margin: 0;
  line-height: 1.5;
}

.images-section {
  margin-top: 15px;
}

.images-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-item {
  width: 100px;
  height: 100px;
  overflow: hidden;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 2px solid white;
  transition: all 0.3s ease;
}

.image-item:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
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

/* Animações para transições entre estados */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease-out;
  max-height: 800px; /* ajuste conforme necessário */
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

.gallery-enter-active,
.gallery-leave-active {
  transition: all 0.4s ease;
}

.gallery-enter-from,
.gallery-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* Animações de entrada */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
    gap: 12px;
  }

  .filter-group {
    width: 100%;
    min-width: 100%;
  }

  .filter-button {
    width: 100%;
  }

  .table-header {
    padding: 8px 0;
  }

  .header-cell,
  .table-cell {
    padding: 8px 5px;
    font-size: 14px;
  }

  .location-cell {
    flex: 1;
  }

  .type-cell {
    min-width: 80px;
  }

  .status-cell {
    min-width: 80px;
  }

  .image-item {
    width: 80px;
    height: 80px;
  }
}

@media (max-width: 480px) {
  .header-cell,
  .table-cell {
    font-size: 13px;
    padding: 6px 3px;
  }

  .details-content {
    padding: 10px;
  }

  .description-box {
    padding: 10px;
  }

  .image-item {
    width: 70px;
    height: 70px;
  }

  .details-section h4 {
    font-size: 15px;
  }
}

@supports (-webkit-touch-callout: none) {
  .occurrences-table-wrapper {
    -webkit-overflow-scrolling: touch;
  }

  .filter-select {
    font-size: 16px;
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
