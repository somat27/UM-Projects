<template>
  <div class="detail-modal">
    <!-- Informações para Ocorrências Pendentes -->
    <div
      v-if="ocorrencia && ocorrencia.status === 'Pendente'"
      class="status-pendente"
    >
      <div class="status-badge pendente">
        <span class="status-icon">⚠️</span>
        <span class="status-text">Pendente</span>
      </div>

      <div class="info-section">
        <div class="info-row">
          <div class="info-label">Data de Submissão:</div>
          <div class="info-value">
            {{ formatarData(ocorrencia.dataSubmissao) }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Tipo:</div>
          <div class="info-value">
            {{ mapearTipo(ocorrencia.tipoOcorrencia) }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Endereço:</div>
          <div class="info-value">
            {{ ocorrencia.endereco || "Endereço não especificado" }}
          </div>
        </div>

        <div class="info-row description">
          <div class="info-label">Descrição:</div>
          <div class="info-value">
            {{ ocorrencia.descricao || "Sem descrição disponível" }}
          </div>
        </div>

        <!-- Galeria de Imagens/Vídeos -->
        <div
          v-if="ocorrencia.imagemVideo && ocorrencia.imagemVideo.length > 0"
          class="info-row"
        >
          <div class="info-label">Imagens/Vídeos:</div>
          <div class="info-value">
            <div class="media-gallery">
              <div
                v-for="(media, index) in ocorrencia.imagemVideo"
                :key="index"
                class="media-item"
                @click="abrirMidiaEmNovaJanela(media)"
              >
                <template v-if="isVideoUrl(media)">
                  <!-- Exibindo um vídeo -->
                  <div class="play-container">
                    <img
                      src="../assets/play-icon.png"
                      alt="Play"
                      class="play-icon"
                    />
                  </div>
                </template>
                <template v-else>
                  <!-- Exibindo uma imagem -->
                  <img
                    :src="media"
                    :alt="'Mídia ' + (index + 1)"
                    class="media-thumbnail"
                  />
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="actions-footer">
        <button class="action-button secondary" @click="$emit('fechar')">
          Fechar
        </button>
      </div>
    </div>

    <!-- Informações para Ocorrências Rejeitadas -->
    <div
      v-else-if="ocorrencia && ocorrencia.status === 'Rejeitado'"
      class="status-pendente"
    >
      <div class="status-badge rejeitado">
        <span class="status-icon">❌</span>
        <span class="status-text">Rejeitado</span>
      </div>

      <div class="info-section">
        <div class="info-row">
          <div class="info-label">Data de Submissão:</div>
          <div class="info-value">
            {{ formatarData(ocorrencia.dataSubmissao) }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Tipo:</div>
          <div class="info-value">
            {{ mapearTipo(ocorrencia.tipoOcorrencia) }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Endereço:</div>
          <div class="info-value">
            {{ ocorrencia.endereco || "Endereço não especificado" }}
          </div>
        </div>

        <div class="info-row description">
          <div class="info-label">Descrição:</div>
          <div class="info-value">
            {{ ocorrencia.descricao || "Sem descrição disponível" }}
          </div>
        </div>

        <!-- Galeria de Imagens/Vídeos -->
        <div
          v-if="ocorrencia.imagemVideo && ocorrencia.imagemVideo.length > 0"
          class="info-row"
        >
          <div class="info-label">Imagens/Vídeos:</div>
          <div class="info-value">
            <div class="media-gallery">
              <div
                v-for="(media, index) in ocorrencia.imagemVideo"
                :key="index"
                class="media-item"
                @click="abrirMidiaEmNovaJanela(media)"
              >
                <template v-if="isVideoUrl(media)">
                  <!-- Exibindo um vídeo -->
                  <div class="play-container">
                    <img
                      src="../assets/play-icon.png"
                      alt="Play"
                      class="play-icon"
                    />
                  </div>
                </template>
                <template v-else>
                  <!-- Exibindo uma imagem -->
                  <img
                    :src="media"
                    :alt="'Mídia ' + (index + 1)"
                    class="media-thumbnail"
                  />
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="actions-footer">
        <button class="action-button secondary" @click="$emit('fechar')">
          Fechar
        </button>
      </div>
    </div>

    <!-- Informações para Ocorrências em Análise -->
    <div
      v-else-if="ocorrencia && ocorrencia.status === 'Analise' && auditoria"
      class="status-analise"
    >
      <div class="status-badge analise">
        <span class="status-icon">🔍</span>
        <span class="status-text">Em Análise</span>
      </div>

      <div class="info-section">
        <div class="info-row">
          <div class="info-label">Data de Início:</div>
          <div class="info-value">{{ formatarData(auditoria.dataInicio) }}</div>
        </div>

        <div class="info-row">
          <div class="info-label">Tipo:</div>
          <div class="info-value">
            {{ mapearTipo(auditoria.tipo) }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Endereço:</div>
          <div class="info-value">
            {{ auditoria.endereco || "Endereço não especificado" }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Perito Responsável:</div>
          <div class="info-value">
            <span v-if="peritoCarregando" class="loading-indicator"
              >Carregando...</span
            >
            <span v-else>{{ nomePerito || "Não atribuído" }}</span>
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Tempo Estimado:</div>
          <div class="info-value">
            {{ auditoria.tempoEstimado || "Não especificado" }}
          </div>
        </div>

        <div class="info-row description">
          <div class="info-label">Descrição:</div>
          <div class="info-value">
            {{ auditoria.descricao || "Sem descrição disponível" }}
          </div>
        </div>

        <!-- Lista de Materiais -->
        <div
          v-if="auditoria.materiais && auditoria.materiais.length > 0"
          class="info-row"
        >
          <div class="info-label">Materiais:</div>
          <div class="info-value">
            <div class="resources-list">
              <div
                v-for="(material, index) in auditoria.materiais"
                :key="'mat-' + index"
                class="resource-item"
              >
                <span class="resource-name">{{ material.nome }}</span>
                <span class="resource-quantity">{{ material.quantidade }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Lista de Profissionais -->
        <div
          v-if="auditoria.profissionais && auditoria.profissionais.length > 0"
          class="info-row"
        >
          <div class="info-label">Profissionais:</div>
          <div class="info-value">
            <div class="resources-list">
              <div
                v-for="(profissional, index) in auditoria.profissionais"
                :key="'prof-' + index"
                class="resource-item"
              >
                <span class="resource-name">{{ profissional.nome }}</span>
                <span class="resource-quantity">{{
                  profissional.quantidade
                }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Galeria de Imagens/Vídeos -->
        <div
          v-if="auditoria.imagemVideo && auditoria.imagemVideo.length > 0"
          class="info-row"
        >
          <div class="info-label">Imagens/Vídeos:</div>
          <div class="info-value">
            <div class="media-gallery">
              <div
                v-for="(media, index) in auditoria.imagemVideo"
                :key="index"
                class="media-item"
                @click="abrirMidiaEmNovaJanela(media.url)"
              >
                <template v-if="isVideoUrl(media.url)">
                  <!-- Exibindo um vídeo -->
                  <div class="play-container">
                    <img
                      src="../assets/play-icon.png"
                      alt="Play"
                      class="play-icon"
                    />
                  </div>
                </template>
                <template v-else>
                  <!-- Exibindo uma imagem -->
                  <img
                    :src="media.url"
                    :alt="'Mídia ' + (index + 1)"
                    class="media-thumbnail"
                  />
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="actions-footer">
        <button class="action-button secondary" @click="$emit('fechar')">
          Fechar
        </button>
      </div>
    </div>

    <!-- Informações para Ocorrências Resolvidas -->
    <div
      v-else-if="ocorrencia && ocorrencia.status === 'Resolvido' && auditoria"
      class="status-resolvido"
    >
      <div class="status-badge resolvido">
        <span class="status-icon">✅</span>
        <span class="status-text">Resolvido</span>
      </div>

      <div class="info-section">
        <!-- Datas e duração -->
        <div class="info-row">
          <div class="info-label">Data de Submissão:</div>
          <div class="info-value">
            {{ formatarData(ocorrencia.dataSubmissao) }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Data de Início da Auditoria:</div>
          <div class="info-value">{{ formatarData(auditoria.dataInicio) }}</div>
        </div>

        <div class="info-row">
          <div class="info-label">Data de Conclusão:</div>
          <div class="info-value">{{ formatarData(auditoria.dataFim) }}</div>
        </div>

        <div class="info-row">
          <div class="info-label">Dias Totais de Resolução:</div>
          <div class="info-value">
            {{
              calcularDiasTotais(ocorrencia.dataSubmissao, auditoria.dataFim)
            }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Dias de Auditoria:</div>
          <div class="info-value">
            {{ calcularDiasTotais(auditoria.dataInicio, auditoria.dataFim) }}
          </div>
        </div>

        <!-- Informações da auditoria -->
        <div class="info-row">
          <div class="info-label">Tipo:</div>
          <div class="info-value">
            {{ mapearTipo(auditoria.tipo) }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Endereço:</div>
          <div class="info-value">
            {{ auditoria.endereco || "Endereço não especificado" }}
          </div>
        </div>

        <div class="info-row">
          <div class="info-label">Perito Responsável:</div>
          <div class="info-value">
            <span v-if="peritoCarregando" class="loading-indicator"
              >Carregando...</span
            >
            <span v-else>{{ nomePerito || "Não especificado" }}</span>
          </div>
        </div>

        <div class="info-row description">
          <div class="info-label">Descrição:</div>
          <div class="info-value">
            {{ auditoria.descricao || "Sem descrição disponível" }}
          </div>
        </div>

        <!-- Lista de Materiais -->
        <div
          v-if="auditoria.materiais && auditoria.materiais.length > 0"
          class="info-row"
        >
          <div class="info-label">Materiais:</div>
          <div class="info-value">
            <div class="resources-list">
              <div
                v-for="(material, index) in auditoria.materiais"
                :key="'mat-' + index"
                class="resource-item"
              >
                <span class="resource-name">{{ material.nome }}</span>
                <span class="resource-quantity">{{ material.quantidade }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Lista de Profissionais -->
        <div
          v-if="auditoria.profissionais && auditoria.profissionais.length > 0"
          class="info-row"
        >
          <div class="info-label">Profissionais:</div>
          <div class="info-value">
            <div class="resources-list">
              <div
                v-for="(profissional, index) in auditoria.profissionais"
                :key="'prof-' + index"
                class="resource-item"
              >
                <span class="resource-name">{{ profissional.nome }}</span>
                <span class="resource-quantity">{{
                  profissional.quantidade
                }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Galeria de Imagens/Vídeos -->
        <div
          v-if="auditoria.imagemVideo && auditoria.imagemVideo.length > 0"
          class="info-row"
        >
          <div class="info-label">Imagens/Vídeos:</div>
          <div class="info-value">
            <div class="media-gallery">
              <div
                v-for="(media, index) in auditoria.imagemVideo"
                :key="index"
                class="media-item"
                @click="abrirMidiaEmNovaJanela(media.url)"
              >
                <template v-if="isVideoUrl(media.url)">
                  <!-- Exibindo um vídeo -->
                  <div class="play-container">
                    <img
                      src="../assets/play-icon.png"
                      alt="Play"
                      class="play-icon"
                    />
                  </div>
                </template>
                <template v-else>
                  <!-- Exibindo uma imagem -->
                  <img
                    :src="media.url"
                    :alt="'Mídia ' + (index + 1)"
                    class="media-thumbnail"
                  />
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="actions-footer">
        <button class="action-button secondary" @click="$emit('fechar')">
          Fechar
        </button>
      </div>
    </div>

    <!-- Mensagem de erro caso não haja dados -->
    <div v-else class="error-message">
      <p>Não foi possível carregar os detalhes. Tente novamente mais tarde.</p>
      <button class="action-button secondary" @click="$emit('fechar')">
        Fechar
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import { db } from "@/firebase.js";
import { doc, getDoc } from "firebase/firestore";

export default {
  props: {
    ocorrencia: {
      type: Object,
      required: false,
      default: null,
    },
    auditoria: {
      type: Object,
      required: false,
      default: null,
    },
  },
  setup(props) {
    const nomePerito = ref("");
    const peritoCarregando = ref(false);

    // Função para mapear tipos de ocorrência
    function mapearTipo(codigo) {
      const mapeamento = {
        roads: "Vias e Passeios",
        sinals: "Sinalização",
        lights: "Iluminação Pública",
        others: "Outro",
      };

      return mapeamento[codigo] || "Não especificado";
    }

    async function buscarNomePerito(id) {
      if (!id) {
        nomePerito.value = "Perito não especificado";
        peritoCarregando.value = false;
        return;
      }

      peritoCarregando.value = true;

      try {
        const peritoRef = doc(db, "peritos", id);
        const peritoSnap = await getDoc(peritoRef);

        if (peritoSnap.exists()) {
          // Usar o displayName do perito ou buscar outro campo apropriado
          // Verificamos se o uid coincide com o id passado
          const peritoData = peritoSnap.data();
          if (peritoData.uid === id) {
            nomePerito.value = peritoData.displayName || "Nome não disponível";
          } else {
            console.warn("UID do perito não corresponde ao ID fornecido");
            nomePerito.value = "Inconsistência nos dados do perito";
          }
        } else {
          nomePerito.value = "Perito não encontrado";
          console.warn(`Perito com ID ${id} não encontrado na coleção`);
        }
      } catch (error) {
        console.error("Erro ao buscar perito:", error);
        nomePerito.value = "Erro ao carregar nome do perito";
      } finally {
        peritoCarregando.value = false;
      }
    }

    // Extrair peritoId da ocorrência ou da auditoria
    function atualizarPeritoId() {
      const idFromOcorrencia = props.ocorrencia?.perito;
      const idFromAuditoria = props.auditoria?.perito;

      const id = idFromOcorrencia || idFromAuditoria || null;

      if (id) {
        buscarNomePerito(id);
      } else {
        nomePerito.value = "Perito não especificado";
        peritoCarregando.value = false;
      }
    }

    // Buscar nome assim que o componente montar e os dados estiverem disponíveis
    onMounted(() => {
      atualizarPeritoId();
    });

    // Observar mudanças nos props para atualizar o peritoId
    watch(
      () => [props.ocorrencia, props.auditoria],
      () => {
        atualizarPeritoId();
      },
      { deep: true }
    );

    function formatarData(data) {
      if (!data) return "Data não disponível";

      try {
        const dataObj =
          data.seconds && data.nanoseconds
            ? new Date(data.seconds * 1000)
            : new Date(data);
        return new Intl.DateTimeFormat("pt-PT", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }).format(dataObj);
      } catch (error) {
        console.error("Erro ao formatar data:", error);
        return "Data inválida";
      }
    }

    function calcularDuracao(dataInicio, dataFim) {
      if (!dataInicio || !dataFim) return "Duração indisponível";

      try {
        const inicio = dataInicio.seconds
          ? new Date(dataInicio.seconds * 1000)
          : new Date(dataInicio);
        const fim = dataFim.seconds
          ? new Date(dataFim.seconds * 1000)
          : new Date(dataFim);

        const diferencaMs = fim - inicio;
        const dias = Math.floor(diferencaMs / (1000 * 60 * 60 * 24));
        const horas = Math.floor(
          (diferencaMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
        );
        const minutos = Math.floor(
          (diferencaMs % (1000 * 60 * 60)) / (1000 * 60)
        );

        let duracao = "";
        if (dias > 0) duracao += `${dias} dia${dias > 1 ? "s" : ""} `;
        if (horas > 0 || dias > 0)
          duracao += `${horas} hora${horas > 1 ? "s" : ""} `;
        duracao += `${minutos} minuto${minutos > 1 ? "s" : ""}`;

        return duracao.trim();
      } catch (error) {
        console.error("Erro ao calcular duração:", error);
        return "Cálculo indisponível";
      }
    }

    function calcularDiasTotais(dataInicio, dataFim) {
      if (!dataInicio || !dataFim) return "Não disponível";

      try {
        const inicio = dataInicio.seconds
          ? new Date(dataInicio.seconds * 1000)
          : new Date(dataInicio);
        const fim = dataFim.seconds
          ? new Date(dataFim.seconds * 1000)
          : new Date(dataFim);

        const diferencaMs = fim - inicio;
        const dias = Math.floor(diferencaMs / (1000 * 60 * 60 * 24));

        return `${dias} dia${dias !== 1 ? "s" : ""}`;
      } catch (error) {
        console.error("Erro ao calcular dias totais:", error);
        return "Cálculo indisponível";
      }
    }

    function abrirMidiaEmNovaJanela(url) {
      if (url) {
        window.open(url, "_blank");
      }
    }

    function isVideoUrl(url) {
      const videoPattern = /\.(mp4|webm|avi|mov|mkv|flv|wmv|mpg|mpeg)$/i;
      return videoPattern.test(url);
    }

    return {
      formatarData,
      calcularDuracao,
      calcularDiasTotais,
      abrirMidiaEmNovaJanela,
      nomePerito,
      peritoCarregando,
      mapearTipo,
      isVideoUrl,
    };
  },
};
</script>

<style scoped>
.detail-modal {
  font-family: "Public Sans", -apple-system, Roboto, Helvetica, sans-serif;
  color: #262626;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 20px;
}

.status-badge .status-icon {
  margin-right: 6px;
}

.status-badge.pendente {
  background-color: rgba(85, 138, 253, 0.1);
  color: #1e90ff;
}

.status-badge.analise {
  background-color: rgba(250, 173, 20, 0.1);
  color: #faad14;
}

.status-badge.resolvido {
  background-color: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.status-badge.rejeitado {
  background-color: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-weight: 600;
  font-size: 14px;
  color: #595959;
  margin-bottom: 4px;
}

.info-value {
  font-size: 15px;
  color: #262626;
  line-height: 1.5;
}

.loading-indicator {
  font-style: italic;
  color: #8c8c8c;
}

.description .info-value {
  white-space: pre-line;
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #d9d9d9;
}

.actions-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.action-button.primary {
  background-color: #1890ff;
  color: white;
}

.action-button.primary:hover {
  background-color: #40a9ff;
}

.action-button.secondary {
  background-color: #f0f0f0;
  color: #595959;
}

.action-button.secondary:hover {
  background-color: #d9d9d9;
}

.error-message {
  text-align: center;
  padding: 24px;
  color: #595959;
}

/* Estilos para a galeria de imagens */
.media-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.media-item {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #e8e8e8;
  transition: transform 0.2s;
}

.media-item:hover {
  transform: scale(1.05);
}

.media-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Estilos para listas de recursos (materiais/profissionais) */
.resources-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.resource-name {
  font-weight: 500;
}

.resource-quantity {
  background-color: #e6f7ff;
  color: #1890ff;
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
}

/* Estilos responsivos */
@media (min-width: 768px) {
  .info-row {
    flex-direction: row;
    align-items: flex-start;
  }

  .info-label {
    width: 180px;
    flex-shrink: 0;
    margin-bottom: 0;
  }

  .info-value {
    flex: 1;
  }

  .media-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
}

@media (max-width: 767px) {
  .status-badge {
    margin-bottom: 16px;
  }

  .info-section {
    gap: 12px;
  }

  .actions-footer {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }

  .media-gallery {
    grid-template-columns: repeat(3, 1fr);
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
