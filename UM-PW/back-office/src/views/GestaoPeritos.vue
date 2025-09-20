<template>
  <div class="dashboard-container" :space="23">
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
          <div class="page-header">
            <h2>Gestão de Peritos</h2>
          </div>

          <FiltroTabela v-model:modelSearch="searchQuery" v-model:modelSort="sortKey" v-model:modelOrder="sortOrder"
            :sortColumns="sortColumns" :filterOptions="filterOptions" @filter-applied="handleFilterApplied"
            search-placeholder="Procurar Peritos..." sort-placeholder="Ordenar por…" />


          <template v-if="faltaPerfil.length > 0">
            <div class="table-section">
              <h3 class="table-section-title">Peritos não Registados</h3>
              <GenericTable :data="filteredFaltaPerfil" :loading="aCarregar" :columns="missingColumns" type="striped"
                @add="openAddPeritoModal" />
            </div>
          </template>

          <div class="table-section">
            <h3 class="table-section-title">Peritos Registados</h3>
            <GenericTable :data="filteredComPerfil" :loading="aCarregar" :columns="completeColumns" type="striped"
              @edit="handleEdit" />
          </div>

          <AddPeritoModal v-if="showAddModal" :user="selectedUser" @close="showAddModal = false"
            @saved="handlePeritoSaved" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import NavigationList from '@/components/NavigationList.vue'
import { ref, onMounted, computed } from 'vue';
import GenericTable from '@/components/GenericTable.vue';
import AddPeritoModal from '@/components/AddPeritoModal.vue';
import { getPeritosWithoutProfile, getPeritosWithProfile } from '@/firebase';
import FiltroTabela from '@/components/FiltroTabela.vue';

const faltaPerfil = ref([]);
const comPerfil = ref([]);
const aCarregar = ref(true);

const searchQuery = ref('');
const sortKey = ref('');
const sortOrder = ref('asc');

// 1) onde vamos guardar os filtros seleccionados
const appliedFilters = ref({});

// 2) opções para preencher o modal de filtros
const filterOptions = computed(() => {
  const campos = ['specialty', 'localidades', 'status'];
  const opts = {};

  campos.forEach(key => {
    // recolhe todos os valores desse campo
    let valores = comPerfil.value.map(u => u[key] ?? []);

    // se for localidades, achata os arrays num único array
    if (key === 'localidades') {
      valores = valores.flat();
    }

    // tira duplicados e valores vazios
    opts[key] = Array.from(new Set(valores))
      .filter(v => v !== '');
  });

  return opts;
});


// 3) função a disparar quando clicas em “Aplicar” no modal
function handleFilterApplied(filters) {
  appliedFilters.value = filters;
}

const showAddModal = ref(false);
const selectedUser = ref(null);

const missingColumns = [
  { key: 'displayName', label: 'Nome' },
  { key: 'email', label: 'Email' },
  { key: 'add', label: 'Ações' }
];

const completeColumns = [
  { key: 'displayName', label: 'Nome' },
  { key: 'specialty', label: 'Especialidade' },
  { key: 'localidades', label: 'Localidades' },
  { key: 'status', label: 'Status' },
  { key: 'edit', label: 'Ações' }
];

// pega todos os elementos até ao penúltimo
const sortColumns = completeColumns.slice(0, -1);

async function loadData() {
  aCarregar.value = true;
  try {
    faltaPerfil.value = await getPeritosWithoutProfile();
    comPerfil.value = await getPeritosWithProfile();
  } catch (error) {
    console.error('Erro ao carregar peritos:', error);
  } finally {
    aCarregar.value = false;
  }
}

onMounted(loadData);

function openAddPeritoModal(user) {
  selectedUser.value = user;
  showAddModal.value = true;
}

function handlePeritoSaved() {
  showAddModal.value = false;
  loadData();
}

function handleEdit(user) {
  selectedUser.value = user;
  console.log(selectedUser.value);
  showAddModal.value = true;
}

function sortData(arr) {
  if (!sortKey.value) return arr;
  return [...arr].sort((a, b) => {
    const aVal = a[sortKey.value];
    const bVal = b[sortKey.value];
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal;
    }
    const aStr = Array.isArray(aVal) ? aVal.join(', ') : String(aVal);
    const bStr = Array.isArray(bVal) ? bVal.join(', ') : String(bVal);
    return sortOrder.value === 'asc'
      ? aStr.localeCompare(bStr)
      : bStr.localeCompare(aStr);
  });
}

const filteredFaltaPerfil = computed(() => {
  let data = faltaPerfil.value.filter(u =>
    u.displayName.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
  return sortData(data);
});

const filteredComPerfil = computed(() => {
  let data = comPerfil.value;

  // pesquisa por texto
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    data = data.filter(u =>
      (u.displayName ?? '').toLowerCase().includes(q)
    );
  }

  // aplicação dos filtros do modal
  Object.entries(appliedFilters.value).forEach(([key, vals]) => {
    if (!vals.length) return;

    // campo localidades é um array: verifica se alguma das localidades do perito está nas vals
    if (key === 'localidades') {
      data = data.filter(u =>
        Array.isArray(u.localidades) &&
        u.localidades.some(loc => vals.includes(loc))
      );
    }
    else {
      // campos simples (specialty, status, etc.)
      data = data.filter(u => vals.includes(u[key]));
    }
  });


  // ordenação
  return sortData(data);
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

.page-header {
  margin-bottom: 16px;
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

.add-button {
  padding: 0.5rem 1rem;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 1rem;
  cursor: pointer;
}

.add-button:hover {
  background-color: #167ac6;
}
</style>
