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

          <!-- Cabeçalho -->
          <div class="page-header">
            <h2>Gestão de Ocorrências</h2>
          </div>

          <!-- Controles de pesquisa e ordenação -->
          <FiltroTabela v-model:modelSearch="searchQuery" v-model:modelSort="sortKey" v-model:modelOrder="sortOrder"
            :sortColumns="sortColumns" :filterOptions="filterOptions" @filter-applied="handleFilterApplied"
            search-placeholder="Procurar por ID..." sort-placeholder="Ordenar por…" />

          <!-- Tabela de Ocorrências -->
          <div class="table-section">
            <GenericTable :columns="columns" :data="filteredOccurrences" :loading="loading" @view="openDetail" />
          </div>

          <!-- Modal de Detalhes -->
          <div v-if="showDetailModal" @click.self="closeModals" class="modal-overlay large">
            <div class="modal-content">
              <header class="modal-header">
                <h3>Ocorrência: {{ selected.id }}</h3>
                <button class="modal-close" @click="closeModals" aria-label="Fechar">×</button>
              </header>
              <!-- Mapa -->
              <iframe v-if="selected.coordenadas"
                :src="`https://www.google.com/maps?q=${selected.coordenadas.latitude},${selected.coordenadas.longitude}&output=embed`"
                width="100%" height="300" frameborder="0" style="border:0; margin-top:10px;"></iframe>

              <ul class="detail-list">
                <li><strong>Tipo:</strong> {{ selected.tipoOcorrencia }}</li>
                <li><strong>Estado:</strong> {{ selected.status }}</li>
                <li><strong>Submetido em:</strong> {{ selected.dataSubmissao }}</li>
                <li><strong>Endereço:</strong> {{ selected.endereco }}</li>
                <li><strong>Descrição:</strong> {{ selected.descricao }}</li>
                <li v-if="selected.motivoRejeicao"><strong>Motivo da Rejeição:</strong> {{ selected.motivoRejeicao }}
                </li>
              </ul>

              <!-- Carrossel de mídia -->
              <div v-if="selected.imagemVideo?.length" class="media-carousel">
                <button @click="prevMedia">‹</button>
                <div class="media-item">
                  <img v-if="selected.imagemVideo[mediaIndex].includes('/image/')"
                    :src="selected.imagemVideo[mediaIndex]" />
                  <video v-else controls :src="selected.imagemVideo[mediaIndex]"></video>
                </div>
                <button @click="nextMedia">›</button>
              </div>

              <div class="modal-actions">
                <router-link v-if="selected.status.toLowerCase() === 'pendente'"
                  :to="{ name: 'AprovacaoOcorrencia', params: { id: selected.id } }" class="btn-approve">
                  Aprovar
                </router-link>
                <button v-if="selected.status.toLowerCase() === 'pendente'" class="btn-reject"
                  @click="handleReject(selected)">
                  Rejeitar
                </button>
              </div>
            </div>
          </div>

          <!-- Modal de Motivo de Rejeição -->
          <div v-if="showRejectModal" class="modal-overlay">
            <div class="modal-content">
              <h3>Motivo da Rejeição</h3>
              <textarea v-model="rejectReason" rows="4" placeholder="Insira a razão..."></textarea>
              <div class="modal-actions">
                <button class="btn-submit" @click="submitReject">Enviar</button>
                <button class="btn-cancel" @click="closeModals">Cancelar</button>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import NavigationList from '@/components/NavigationList.vue';
import GenericTable from '@/components/GenericTable.vue';
import { db } from '@/firebase.js';
import { collection, getDocs, updateDoc, doc } from 'firebase/firestore';
import FiltroTabela from '@/components/FiltroTabela.vue';

// Estado
const occurrences = ref([]);
const loading = ref(false);
const selected = ref(null);
const showDetailModal = ref(false);
const showRejectModal = ref(false);
const rejectReason = ref('');
const mediaIndex = ref(0);
const searchQuery = ref('');
const sortKey = ref('');
const sortOrder = ref('asc');

const appliedFilters = ref({});

const filterOptions = computed(() => {
  const campos = ['tipoOcorrencia', 'status'];
  const opts = {};
  campos.forEach(key => {
    opts[key] = Array.from(
      new Set(
        occurrences.value.map(item => item[key] ?? '')
      )
    ).filter(v => v !== '');
  });
  return opts;
});

function handleFilterApplied(filters) {
  appliedFilters.value = filters;
}

// Rótulos e opções de ordenação
const tipoLabels = { sinals: 'Sinalização em Falta', roads: 'Vias e Passeios', lights: 'Iluminação Pública' };
const sortColumns = [
  { key: 'id', label: 'ID' },
  { key: 'tipoOcorrencia', label: 'Tipo' },
  { key: 'status', label: 'Estado' }
];

// Colunas para a tabela única
const columns = [
  { key: 'id', label: 'ID' },
  { key: 'tipoOcorrencia', label: 'Tipo' },
  { key: 'status', label: 'Estado' },
  { key: 'actions', label: 'Ações' }
];

// Filtrar e ordenar apenas por ID
const filteredOccurrences = computed(() => {
  let arr = occurrences.value;

  // 1) pesquisa por texto
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    arr = arr.filter(item =>
      (item.id ?? '').toString().toLowerCase().includes(q)
    );
  }

  // 2) filtros por checkbox
  Object.entries(appliedFilters.value).forEach(([key, vals]) => {
    if (vals.length) {
      arr = arr.filter(item => vals.includes(item[key]));
    }
  });

  // 3) ordenação
  if (sortKey.value) {
    arr = [...arr].sort((a, b) => {
      const A = a[sortKey.value], B = b[sortKey.value];
      if (typeof A === 'string') {
        return sortOrder.value === 'asc'
          ? A.localeCompare(B)
          : B.localeCompare(A);
      }
      return sortOrder.value === 'asc' ? A - B : B - A;
    });
  }

  return arr;
});



// Carregar dados
async function loadOccurrences() {
  loading.value = true;
  try {
    const snap = await getDocs(collection(db, 'ocorrencias'));
    occurrences.value = snap.docs.map(d => {
      const data = d.data();
      const raw = data.dataSubmissao;
      const formatted = raw?.toDate ? raw.toDate().toLocaleString('pt-PT') : (raw || '');
      return { id: d.id, ...data, dataSubmissao: formatted, tipoOcorrencia: tipoLabels[data.tipoOcorrencia] || data.tipoOcorrencia };
    });
  } catch (e) { console.error('Erro ao carregar ocorrências:', e); } finally { loading.value = false; }
}

// Ações de modal
function openDetail(item) {
  selected.value = item;
  mediaIndex.value = 0;
  showDetailModal.value = true;
}
function handleReject() {
  showRejectModal.value = true;
}
function closeModals() {
  showDetailModal.value = false;
  showRejectModal.value = false;
  rejectReason.value = '';
}
async function submitReject() {
  if (selected.value) {
    await updateDoc(doc(db, 'ocorrencias', selected.value.id), { status: 'Rejeitado', motivoRejeicao: rejectReason.value });
    closeModals(); loadOccurrences();
  }
}
function nextMedia() {
  if (!selected.value?.imagemVideo) return;
  mediaIndex.value = (mediaIndex.value + 1) % selected.value.imagemVideo.length;
}
function prevMedia() {
  if (!selected.value?.imagemVideo) return;
  mediaIndex.value = (mediaIndex.value - 1 + selected.value.imagemVideo.length) % selected.value.imagemVideo.length;
}

onMounted(loadOccurrences);
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

.controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.sort-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
  background: #fff;
  font-size: 0.875rem;
}

.sort-button {
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  border: none;
  background: none;
  cursor: pointer;
}

.table-section {
  margin-bottom: 30px;
}

.modal-overlay.large .modal-content {
  width: 800px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 600px;
  max-width: 95%;
  max-height: 95%;
  overflow-y: auto;
}

.detail-list {
  list-style: none;
  padding: 0;
}

.detail-list li {
  margin-bottom: 8px;
}

.media-carousel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 15px 0;
}

.media-carousel button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.media-item img,
.media-item video {
  max-width: 600px;
  max-height: 300px;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

textarea {
  width: 100%;
  padding: 8px;
  resize: vertical;
}

.btn-approve {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-reject {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-cancel {
  background-color: #ccc;
  color: #333;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-submit {
  background-color: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 4px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}
</style>
