<template>
  <div class="controls">
    <input
      v-model="searchQuery"
      type="text"
      :placeholder="searchPlaceholder"
      class="search-input"
    />

    <select v-model="sortKey" class="sort-select">
      <option value="">{{ sortPlaceholder }}</option>
      <option v-for="col in sortColumns" :key="col.key" :value="col.key">
        {{ col.label }}
      </option>
    </select>

    <button @click="toggleSortOrder" class="sort-button">
      {{ sortOrder === "asc" ? "↑" : "↓" }}
    </button>

    <button v-if="showAdd" @click="$emit('add')" class="add-button">
      Adicionar
    </button>

    <button @click="showFilterModal = true" class="filter-button">
      Filtrar
    </button>
  </div>

  <!-- Modal de Filtro -->
  <transition name="modal">
    <div v-if="showFilterModal" class="modal-overlay" @click.self="closeFilter">
      <div class="modal-container">
        <header class="modal-header">
          <h3>Filtrar</h3>
          <button class="modal-close" @click="closeFilter" aria-label="Fechar">
            ×
          </button>
        </header>

        <div class="modal-body">
          <div
            v-for="(values, key) in filterOptions"
            :key="key"
            class="filter-group"
          >
            <p class="filter-label">{{ getColumnLabel(key) }}</p>
            <div class="filter-items">
              <label v-for="value in values" :key="value" class="filter-item">
                <input
                  type="checkbox"
                  :value="value"
                  v-model="internalFilters[key]"
                />
                {{ value }}
              </label>
            </div>
          </div>
        </div>

        <footer class="modal-footer">
          <button @click="resetFilters" class="modal-btn">Limpar</button>
          <button @click="applyFilters" class="modal-btn">Aplicar</button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from "vue";

const props = defineProps({
  searchPlaceholder: { type: String, default: "Procurar..." },
  sortPlaceholder: { type: String, default: "Ordenar por" },
  sortColumns: { type: Array, default: () => [] },
  showAdd: { type: Boolean, default: false },
  filterOptions: { type: Object, default: () => ({}) },
  modelSearch: { type: String, default: "" },
  modelSort: { type: String, default: "" },
  modelOrder: { type: String, default: "asc" },
});

const emit = defineEmits([
  "update:modelSearch",
  "update:modelSort",
  "update:modelOrder",
  "add",
  "filter-applied",
]);

// Estados internos
const searchQuery = ref(props.modelSearch);
watch(
  () => props.modelSearch,
  (val) => (searchQuery.value = val)
);
watch(searchQuery, (val) => emit("update:modelSearch", val));

const sortKey = ref(props.modelSort);
watch(
  () => props.modelSort,
  (val) => (sortKey.value = val)
);
watch(sortKey, (val) => emit("update:modelSort", val));

const sortOrder = ref(props.modelOrder);
watch(
  () => props.modelOrder,
  (val) => (sortOrder.value = val)
);
watch(sortOrder, (val) => emit("update:modelOrder", val));

const showFilterModal = ref(false);
const internalFilters = ref({});

// Inicializar filtros vazios
Object.keys(props.filterOptions).forEach((key) => {
  internalFilters.value[key] = [];
});

function toggleSortOrder() {
  sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
}

function closeFilter() {
  showFilterModal.value = false;
}

function resetFilters() {
  Object.keys(internalFilters.value).forEach((key) => {
    internalFilters.value[key] = [];
  });
}

function applyFilters() {
  emit("filter-applied", internalFilters.value);
  closeFilter();
}

function getColumnLabel(key) {
  const col = props.sortColumns.find((c) => c.key === key);
  return col ? col.label : key;
}
</script>

<style scoped>
.controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

/* Ajusta os estilos abaixo conforme necessário */
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

.add-button {
  background-color: #204c6d;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.add-button:hover {
  background-color: #167ac6;
}

.filter-button {
  background-color: #204c6d;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.filter-button:hover {
  background-color: #167ac6;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-container {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal-header,
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.filter-group {
  margin-bottom: 12px;
}

.filter-label {
  font-weight: bold;
  margin-bottom: 4px;
}

.filter-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-item input {
  margin-right: 4px;
}

.modal-btn {
  padding: 6px 12px;
  border: none;
  background: #204c6d;
  color: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 1em;
}

.input {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
