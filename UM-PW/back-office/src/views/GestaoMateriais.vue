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

          <AddMaterialModal v-if="showAddModal" :material="materialParaEditar" @close="showAddModal = false"
            @saved="handleMaterialSaved" />

          <div v-if="showAddQuantidadeModal" class="modal-overlay">
            <div class="modal-content">
              <h3>Adicionar {{ materialParaAdicionarQtd.nome }}</h3>
              <input type="number" v-model.number="quantidadeParaAdicionar" min="1" class="input-quantidade" />
              <div class="modal-actions">
                <button @click="showAddQuantidadeModal = false" class="btn-secondary">Cancelar</button>
                <button @click="confirmarAdicionarQuantidade" class="btn-primary">Confirmar</button>
              </div>
            </div>
          </div>

          <div v-if="loading">A carregar…</div>
          <div v-else>
            <div v-if="erro" class="error">{{ erro }}</div>

            <!-- Cabeçalho -->
            <div class="page-header">
              <h2>Gestão de Materiais</h2>
            </div>

            <FiltroTabela v-model:modelSearch="searchQuery" v-model:modelSort="sortKey" v-model:modelOrder="sortOrder"
              :sortColumns="materialColumns" :filterOptions="filterOptions" @filter-applied="handleFilterApplied"
              :showAdd="true" @add="openAddMaterialModal" search-placeholder="Procurar Materiais..."
              sort-placeholder="Ordenar por…" />


            <!-- Tabela genérica com colunas e ações -->
            <GenericTable :data="filteredMateriais" :columns="[...materialColumns, editColumn]" :loading="loading"
              type="striped" @edit="openEditModal" @add="openAddQuantidadeModal" />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import NavigationList from '@/components/NavigationList.vue'
import GenericTable from '@/components/GenericTable.vue'
import AddMaterialModal from '@/components/AddMaterialModal.vue'
import { db } from '@/firebase.js'
import { collection, getDocs, updateDoc, doc } from 'firebase/firestore'
import FiltroTabela from '@/components/FiltroTabela.vue';

// estados
const materiais = ref([])
const loading = ref(false)
const erro = ref(null)
const searchQuery = ref('')       // pesquisa por nome apenas
const sortKey = ref('')
const sortOrder = ref('asc')
const sortColumns = [
  { key: 'nome', label: 'Nome' },
  { key: 'categoria', label: 'Categoria' },
  { key: 'preco', label: 'Preço/Unidade' },
  { key: 'quantidade', label: 'Quantidade' }
]
const materialColumns = [...sortColumns]
const editColumn = { key: 'edit-materiais', label: 'Ações' }
const showAddModal = ref(false)
const materialParaEditar = ref(null)
const showAddQuantidadeModal = ref(false)
const materialParaAdicionarQtd = ref(null)
const quantidadeParaAdicionar = ref(1)

// 1) onde vamos guardar a seleção de filtros
const appliedFilters = ref({});

// 2) gera as opções para o modal de filtros
//    ajusta ‘categoria’ e ‘estado’ aos campos reais do teu data model
const filterOptions = computed(() => {
  const campos = ['categoria'];
  const opts = {};
  campos.forEach(key => {
    // ‘materiais’ é o teu ref com todos os registos
    let vals = materiais.value.map(m => m[key] ?? '');
    opts[key] = Array.from(new Set(vals))
      .filter(v => v !== '');
  });
  return opts;
});

// 3) função chamada quando clicas em “Aplicar” no modal
function handleFilterApplied(filters) {
  appliedFilters.value = filters;
}

// 4) computed que junta pesquisa, filtros e ordenação
const filteredMateriais = computed(() => {
  let arr = materiais.value;

  // 4.1 pesquisa por texto
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    arr = arr.filter(m =>
      (m.nome ?? '').toString().toLowerCase().includes(q)
    );
  }

  // 4.2 filtros por checkbox
  Object.entries(appliedFilters.value).forEach(([key, vals]) => {
    if (!vals.length) return;
    arr = arr.filter(m => vals.includes(m[key]));
  });

  // 4.3 ordenação
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


// métodos
async function fetchMateriais() {
  loading.value = true
  erro.value = null
  try {
    const snap = await getDocs(collection(db, 'materiais'))
    materiais.value = snap.docs.map(d => ({ id: d.id, ...d.data() }))
  } catch (e) {
    erro.value = 'Não foi possível carregar os materiais.'
    console.error(e)
  } finally {
    loading.value = false
  }
}


function openAddMaterialModal() {
  materialParaEditar.value = null
  showAddModal.value = true
}

function openEditModal(item) {
  materialParaEditar.value = item
  showAddModal.value = true
}

function openAddQuantidadeModal(item) {
  materialParaAdicionarQtd.value = item
  quantidadeParaAdicionar.value = 1
  showAddQuantidadeModal.value = true
}

async function confirmarAdicionarQuantidade() {
  const novaQtd = materialParaAdicionarQtd.value.quantidade + quantidadeParaAdicionar.value
  await atualizarQuantidade(materialParaAdicionarQtd.value.id, novaQtd)
  showAddQuantidadeModal.value = false
  fetchMateriais()
}

async function handleMaterialSaved() {
  showAddModal.value = false
  fetchMateriais()
}

async function atualizarQuantidade(id, novaQtd) {
  try {
    const refDoc = doc(db, 'materiais', id)
    await updateDoc(refDoc, { quantidade: novaQtd })
    const item = materiais.value.find(m => m.id === id)
    if (item) item.quantidade = novaQtd
  } catch (e) {
    console.error('Erro ao atualizar quantidade:', e)
  }
}

// life-cycle
onMounted(fetchMateriais)
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
  color: #1890ff;
  background-color: rgba(24, 144, 255, 0.08);
  font-weight: 600;
}

.tab-link.active::after {
  content: '';
  position: absolute;
  bottom: -9px;
  left: 16px;
  right: 16px;
  height: 2px;
  background-color: #1890ff;
  border-radius: 2px 2px 0 0;
}

.tab-link::after {
  content: '';
  position: absolute;
  bottom: -9px;
  left: 50%;
  right: 50%;
  height: 2px;
  background-color: #1890ff;
  transition: all 0.3s ease;
  border-radius: 2px 2px 0 0;
}

.filters-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto;
  max-width: fit-content;
}

.page-header h2 {
  font-size: 1.75rem;
  margin-bottom: 1rem;
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
  font-size: 1rem;
}

.sort-button {
  padding: 0.4rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
  background: white;
  font-size: 1rem;
  cursor: pointer;
}

.sort-button:hover {
  background: #f0f0f0;
}

.quant-input {
  width: 4rem;
  padding: 0.25rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  text-align: right;
}

.btn-add-material {
  background-color: #1890ff;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-add-material:hover {
  background-color: #167ac6;
}

.btn-primary {
  background: #1890ff;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
}

.btn-primary:hover {
  background: #167ac6;
}

.btn-secondary {
  background: transparent;
  border: 1px solid #ccc;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #f5f5f5;
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
  width: 300px;
}

.modal-content h3 {
  margin-top: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}
</style>