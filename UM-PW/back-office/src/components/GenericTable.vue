<template>
  <div class="table-wrapper">
    <div v-if="title" class="table-header">
      <h3 class="table-title">{{ title }}</h3>
      <p v-if="subTitle" class="table-subtitle">{{ subTitle }}</p>
    </div>

    <div class="table-responsive">
      <table class="generic-table" :class="tableClass">
        <div v-if="loading" class="loading-message">
          A Carregar Informações ...
        </div>
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key">
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, rowIndex) in data"
            :key="item.id || item.uid || rowIndex"
          >
            <td v-for="column in columns" :key="column.key">
              <!-- Scoped slot for custom cell -->
              <template v-if="$slots['cell-' + column.key]">
                <slot :name="'cell-' + column.key" :row="item" />
              </template>

              <!-- Nome & Email cell -->
              <template v-if="column.key === 'nameEmail'">
                <div class="name-email-cell">
                  <div class="name">{{ item.displayName }}</div>
                  <div class="email">{{ item.email }}</div>
                </div>
              </template>

              <template v-if="$slots['column-' + column.key]">
                <slot :name="'column-' + column.key" :item="item" />
              </template>

              <!-- Status badge -->
              <template v-else-if="column.key === 'status'">
                <span
                  class="status-badge"
                  :data-status="item.status.toLowerCase()"
                >
                  {{ item.status }}
                </span>
              </template>

              <!-- Action buttons -->
              <template v-else-if="column.key === 'actions'">
                <div class="action-btn-group">
                  <button class="icon-btn" @click="$emit('view', item)">
                    <img
                      src="@/assets/icons8-eye-forma-light/icons8-eye-24.png"
                      alt="Ver"
                    />
                  </button>
                </div>
              </template>

              <template v-else-if="column.key === 'edit'">
                <div class="action-btn-group">
                  <button class="icon-btn" @click="$emit('edit', item)">
                    <img
                      src="@/assets/icons8-pencil-pastel-glyph/icons8-pencil-24.png"
                      alt="Editar"
                    />
                  </button>
                </div>
              </template>

              <template v-else-if="column.key === 'edit-profissionais'">
                <div class="action-btn-group">
                  <button class="icon-btn" @click="$emit('edit', item)">
                    <img
                      src="@/assets/icons8-pencil-pastel-glyph/icons8-pencil-24.png"
                      alt="Editar"
                    />
                  </button>
                  <button class="icon-btn" @click="$emit('add', item)">
                    <img
                      src="@/assets/icons8-plus/icons8-plus.png"
                      alt="Adicionar"
                    />
                  </button>
                </div>
              </template>

              <template v-else-if="column.key === 'edit-materiais'">
                <div class="action-btn-group">
                  <button class="icon-btn" @click="$emit('edit', item)">
                    <img
                      src="@/assets/icons8-pencil-pastel-glyph/icons8-pencil-24.png"
                      alt="Editar"
                    />
                  </button>
                  <button class="icon-btn" @click="$emit('add', item)">
                    <img
                      src="@/assets/icons8-plus/icons8-plus.png"
                      alt="Adicionar"
                    />
                  </button>
                </div>
              </template>

              <!-- Add Perito action -->
              <template v-else-if="column.key === 'add'">
                <div class="action-btn-group">
                  <button class="icon-btn" @click="$emit('add', item)">
                    <img
                      src="@/assets/icons8-plus/icons8-plus.png"
                      alt="Adicionar"
                    />
                    <div class="registar-perito">Registar Perito</div>
                  </button>
                </div>
              </template>

              <!-- Lista de localidades como botões -->
              <template v-else-if="column.key === 'localidades'">
                <div class="localidades-list">
                  <button
                    v-for="loc in item.localidades"
                    :key="loc"
                    class="localidade-btn"
                  >
                    {{ loc }}
                  </button>
                </div>
              </template>

              <!-- Default cell -->
              <template v-else-if="column.key !== 'qtd'">
                {{ item[column.key] }}
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { computed } from "vue";

const props = defineProps({
  title: String,
  subTitle: String,
  data: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  columns: {
    type: Array,
    required: true,
  },
  type: {
    type: String,
    default: "striped",
    validator: (val) => ["striped", "hover", "plain"].includes(val),
  },
});

const tableClass = computed(() => ({
  striped: props.type === "striped",
  hover: props.type === "hover",
  plain: props.type === "plain",
}));
</script>

<style scoped>
.table-header {
  padding: 1rem 1.5rem 0;
}

.table-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.table-subtitle {
  color: #6c757d;
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
}

.table-responsive {
  overflow-x: auto;
}

.generic-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.generic-table th {
  background-color: #f8f9fa;
  padding: 12px 16px;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #e9ecef;
  text-align: left;
}

.generic-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
  text-align: left;
}

.name-email-cell {
  display: flex;
  flex-direction: column;
}

/* Exemplo de estilos para status */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: capitalize;
}

.status-badge[data-status="resolvido"] {
  background: #4caf50;
  color: white;
}

.status-badge[data-status="analise"] {
  background: #36bef4;
  color: white;
}

.status-badge[data-status="pendente"] {
  background: goldenrod;
  color: white;
}

.status-badge[data-status="concluido"] {
  background: #4caf50;
  color: white;
}

.status-badge[data-status="resolvido"] {
  background: #4caf50;
  color: white;
}

.status-badge[data-status="rejeitado"] {
  background: #f44336;
  color: white;
}

.status-badge[data-status="incompleto"] {
  background: #f44336;
  color: white;
}

.status-badge[data-status="ativo"] {
  background: #4caf50;
  color: white;
}

.status-badge[data-status="inativo"] {
  background: #f44336;
  color: white;
}

.action-btn-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.icon-btn img {
  width: 20px;
  height: 20px;
}

/* Novos estilos para localidades */
.localidades-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.localidade-btn {
  background: #e9ecef;
  border: 1px solid #ced4da;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: default;
}

.localidade-btn:hover {
  background: #dee2e6;
}

.loading-message {
  padding: 1rem;
  text-align: center;
}

.registar-perito {
  margin-left: 2px;
}
</style>
