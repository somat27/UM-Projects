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
          <div class="page-header">
            <h2>Gestão de Auditorias</h2>
          </div>

          <FiltroTabela
            v-model:modelSearch="searchQuery"
            v-model:modelSort="sortKey"
            v-model:modelOrder="sortOrder"
            :sortColumns="columns"
            :showAdd="false"
            :filterOptions="filterOptions"
            @filter-applied="handleFilterApplied"
            search-placeholder="Procurar Auditorias..."
            sort-placeholder="Ordenar por…"
          />

          <GenericTable
            :columns="[...columns, editColumn]"
            :data="filteredData"
            class="table-scroll"
          >
            <template #cell-acoes="{ row }">
              <button
                @click="viewAuditoria(row)"
                class="icon-btn"
                title="Ver detalhes"
              >
                <img
                  src="@/assets/icons8-eye-forma-light/icons8-eye-24.png"
                  alt="Ver detalhes"
                />
              </button>
            </template>
          </GenericTable>

          <!-- Modal de detalhes -->
          <transition name="modal">
            <div
              v-if="selectedAuditoria"
              class="modal-overlay"
              @click.self="closeModal"
            >
              <div class="modal-container" role="dialog" aria-modal="true">
                <!-- Header -->
                <header class="modal-header">
                  <h3>Auditoria: {{ selectedAuditoria.id }}</h3>
                  <button
                    class="modal-close"
                    @click="closeModal"
                    aria-label="Fechar"
                  >
                    ×
                  </button>
                </header>

                <!-- Body (scroll se exceder altura) -->
                <div class="modal-body">
                  <!-- Mapa -->
                  <div v-if="selectedAuditoria.coordenadas" class="map-wrapper">
                    <iframe
                      :src="`
                https://www.google.com/maps?q=
                ${selectedAuditoria.coordenadas.latitude},
                ${selectedAuditoria.coordenadas.longitude}
                &hl=pt&z=15&output=embed
              `"
                      class="map-iframe"
                      allowfullscreen
                      loading="lazy"
                    ></iframe>
                  </div>

                  <!-- Dados principais em grid -->
                  <div class="info-grid">
                    <div v-if="selectedAuditoria.dataInicio" class="info-item">
                      <span>Data Início:</span>
                      {{ formatDate(selectedAuditoria.dataInicio) }}
                    </div>
                    <div v-if="selectedAuditoria.dataFim" class="info-item">
                      <span>Data Fim:</span>
                      {{ formatDate(selectedAuditoria.dataFim) }}
                    </div>
                    <div class="info-item">
                      <span>Tipo:</span> {{ selectedAuditoria.tipo }}
                    </div>
                    <div class="info-item">
                      <span>Estado:</span> {{ selectedAuditoria.status }}
                    </div>
                  </div>

                  <!-- Descrição -->
                  <div v-if="selectedAuditoria.descricao" class="section">
                    <p class="section-title">Descrição:</p>
                    <p class="description-text">
                      {{ selectedAuditoria.descricao }}
                    </p>
                  </div>

                  <!-- Mostra imagens/vídeos -->
                  <div
                    v-if="selectedAuditoria.imagemVideo?.length"
                    class="imagem-video-container"
                  >
                    <p class="section-title">Imagens/Videos:</p>
                    <div
                      v-for="(item, idx) in selectedAuditoria.imagemVideo"
                      :key="idx"
                      class="imagem-video-item"
                    >
                      <!-- se for imagem -->
                      <img
                        v-if="item.tipo.startsWith('image')"
                        :src="item.url"
                        alt="imagem da auditoria"
                        class="max-w-full rounded shadow"
                      />
                      <!-- se for vídeo -->
                      <video
                        v-else-if="item.tipo.startsWith('video')"
                        :src="item.url"
                        controls
                        class="max-w-full rounded shadow"
                      />
                      <!-- caso tenhas outros tipos -->
                      <p v-else class="text-sm text-gray-600">
                        Tipo desconhecido: {{ item.tipo }}
                      </p>
                    </div>
                  </div>

                  <!-- === TABELA DE MATERIAIS === -->
                  <div v-if="selectedAuditoria.materiais" class="section">
                    <div class="section-header">
                      <p class="section-title">Materiais</p>
                      <div v-if="isEditable">
                        <button class="add-button" @click="openMaterialsModal">
                          + Novo
                        </button>
                        <button
                          class="save-button"
                          :disabled="saving"
                          @click="saveAll"
                        >
                          {{ saving ? "A guardar…" : "Salvar" }}
                        </button>
                      </div>
                    </div>

                    <table class="materials-table">
                      <thead>
                        <tr>
                          <th>Nome</th>
                          <th class="text-center">Qtd</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="m in selectedAuditoria.materiais"
                          :key="m.id"
                        >
                          <td>{{ m.nome }}</td>
                          <td class="text-center">
                            <input
                              type="number"
                              min="0"
                              v-model.number="m.quantidade"
                              :disabled="!isEditable"
                              class="qty-input"
                            />
                          </td>
                        </tr>
                      </tbody>
                    </table>

                    <!-- Erros de stock por material -->
                    <p
                      v-for="(err, mid) in materialErrors"
                      :key="mid"
                      class="error-text"
                    >
                      {{ err }}
                    </p>
                  </div>

                  <!-- === TABELA DE PROFISSIONAIS === -->
                  <div v-if="selectedAuditoria.profissionais" class="section">
                    <div class="section-header">
                      <p class="section-title">Profissionais</p>
                      <div v-if="isEditable">
                        <button class="add-button" @click="openProfsModal">
                          + Novo
                        </button>
                        <button
                          class="save-button"
                          :disabled="saving"
                          @click="saveAll"
                        >
                          {{ saving ? "A guardar…" : "Salvar" }}
                        </button>
                      </div>
                    </div>

                    <table class="professionals-table">
                      <thead>
                        <tr>
                          <th>Nome</th>
                          <th class="text-center">Qtd</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="p in selectedAuditoria.profissionais"
                          :key="p.id"
                        >
                          <td>{{ p.nome }}</td>
                          <td class="text-center">
                            <input
                              type="number"
                              min="0"
                              v-model.number="p.quantidade"
                              :disabled="!isEditable"
                              class="qty-input"
                            />
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <Modal
                  v-if="showMaterialsModal"
                  @close="showMaterialsModal = false"
                >
                  <h3>Seleciona Materiais</h3>
                  <table class="w-full table-auto">
                    <thead>
                      <tr>
                        <th class="text-left p-2">Nome</th>
                        <th class="text-left p-2">Stock</th>
                        <th class="text-left p-2">Quantidade Desejada</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="mat in filteredMaterials"
                        :key="mat.id"
                        class="border-t"
                      >
                        <td class="p-2">
                          <label class="inline-flex items-center">
                            <input
                              type="checkbox"
                              :value="mat.id"
                              v-model="selectedItemsMap.material"
                              class="mr-2"
                            />
                            {{ mat.nome }}
                          </label>
                        </td>
                        <td class="p-2">{{ mat.quantidade }}</td>
                        <td class="p-2">
                          <input
                            type="number"
                            v-model.number="selectedItemsQuantities[mat.id]"
                            :min="1"
                            :max="mat.quantidade"
                            :disabled="
                              !selectedItemsMap.material.includes(mat.id)
                            "
                            class="w-20 border rounded p-1"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="mt-4 text-right">
                    <button
                      @click="showMaterialsModal = false"
                      class="px-4 py-2 rounded bg-gray-200"
                    >
                      Fechar
                    </button>
                  </div>
                </Modal>

                <Modal v-if="showProfsModal" @close="showProfsModal = false">
                  <h3>Seleciona Profissionais</h3>
                  <table class="w-full table-auto">
                    <thead>
                      <tr>
                        <th class="text-left p-2">Nome</th>
                        <th class="text-left p-2">Disponível</th>
                        <th class="text-left p-2">Quantidade Desejada</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="prof in filteredProfs"
                        :key="prof.id"
                        class="border-t"
                      >
                        <td class="p-2">
                          <label class="inline-flex items-center">
                            <input
                              type="checkbox"
                              :value="prof.id"
                              v-model="selectedItemsMap.profissional"
                              class="mr-2"
                            />
                            {{ prof.nome }}
                          </label>
                        </td>
                        <td class="p-2">{{ prof.quantidade }}</td>
                        <td class="p-2">
                          <input
                            type="number"
                            v-model.number="selectedItemsQuantities[prof.id]"
                            :min="1"
                            :max="prof.quantidade"
                            :disabled="
                              !selectedItemsMap.profissional.includes(prof.id)
                            "
                            class="w-20 border rounded p-1"
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="mt-4 text-right">
                    <button
                      @click="showProfsModal = false"
                      class="px-4 py-2 rounded bg-gray-200"
                    >
                      Fechar
                    </button>
                  </div>
                </Modal>
              </div>
            </div>
          </transition>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import NavigationList from "@/components/NavigationList.vue";
import GenericTable from "@/components/GenericTable.vue";
import { collection, getDocs } from "firebase/firestore";
import { doc, updateDoc, getDoc } from "firebase/firestore";
import { db } from "@/firebase";
import FiltroTabela from "@/components/FiltroTabela.vue";

// mapeamento de tipo → label
const tipoLabels = {
  sinals: "Sinalização em Falta",
  roads: "Vias e Passeios",
  lights: "Iluminação Pública",
};

const tableData = ref([]);
const searchQuery = ref("");
const sortKey = ref(""); // coluna por onde ordenar
const sortOrder = ref("asc"); // 'asc' ou 'desc'
const selectedAuditoria = ref(null);

const showMaterialsModal = ref(false);
const showProfsModal = ref(false);

const allMaterials = ref([]); // vai trazer todos os docs de “materiais”
const allProfissionais = ref([]); // idem para “profissionais”

const isEditable = computed(
  () => selectedAuditoria.value.status.toLowerCase() === "pendente"
);

const filteredMaterials = computed(() => {
  const usados = selectedAuditoria.value.materiais.map((i) => i.id);
  return allMaterials.value.filter(
    (mat) => !usados.includes(mat.id) && mat.quantidade > 0
  );
});

const filteredProfs = computed(() => {
  const usados = selectedAuditoria.value.profissionais.map((i) => i.id);
  return allProfissionais.value.filter(
    (prof) => !usados.includes(prof.id) && prof.quantidade > 0
  );
});

const appliedFilters = ref({});
const filterOptions = computed(() => {
  // para cada campo que queiras filtrar
  const campos = ["status", "tipo"];
  const opts = {};
  campos.forEach((key) => {
    opts[key] = [
      ...new Set(tableData.value.map((item) => item[key] ?? "")), // retira undefined
    ].filter((v) => v !== ""); // opcional: tira valores vazios
  });
  return opts;
});

// 3. lidar com o evento do modal
function handleFilterApplied(filters) {
  appliedFilters.value = filters;
}

// 4. computed que junta pesquisa + filtros + ordenação
const filteredData = computed(() => {
  let data = tableData.value;

  // pesquisa por texto
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    data = data.filter((item) => {
      const valores = [item.id];
      return valores.some((v) =>
        (v ?? "").toString().toLowerCase().includes(q)
      );
    });
  }

  // filtros por checkbox
  Object.entries(appliedFilters.value).forEach(([key, vals]) => {
    if (vals.length) {
      data = data.filter((item) => vals.includes(item[key]));
    }
  });

  // ordenação (igual ao que já tinhas)
  if (sortKey.value) {
    data = [...data].sort((a, b) => {
      const A = a[sortKey.value];
      const B = b[sortKey.value];
      if (A < B) return sortOrder.value === "asc" ? -1 : 1;
      if (A > B) return sortOrder.value === "asc" ? 1 : -1;
      return 0;
    });
  }

  return data;
});

// colunas: só ID, Tipo, Estado + ações
const columns = [
  { key: "id", label: "ID", sortable: true, headerClass: "col-id" },
  { key: "tipo", label: "Tipo", sortable: true },
  { key: "status", label: "Estado", sortable: true },
];
const editColumn = { key: "acoes", label: "Ações" };

// carrega auditorias da Firestore
async function loadAuditorias() {
  const snap = await getDocs(collection(db, "auditorias"));
  tableData.value = snap.docs.map((doc) => {
    const d = doc.data();
    return {
      id: doc.id,
      tipo: tipoLabels[d.tipo] || d.tipo,
      status: d.status || "",
      coordenadas: d.coordenadas || { latitude: 0, longitude: 0 },
      dataInicio: d.dataInicio || null,
      dataFim: d.dataFim || null,
      descricao: d.descricao || "",
      endereco: d.endereco || "",
      imagemVideo: Array.isArray(d.imagemVideo) ? d.imagemVideo : [],
      materiais: Array.isArray(d.materiais) ? d.materiais : [],
      profissionais: Array.isArray(d.profissionais) ? d.profissionais : [],
      perito: d.perito || "",
      tempoEstimado: d.tempoEstimado || 0,
    };
  });
}

onMounted(loadAuditorias);

// abre modal
function viewAuditoria(row) {
  selectedAuditoria.value = row;
}

// fecha modal
function closeModal() {
  selectedAuditoria.value = null;
}

// formata timestamp Firestore para string PT-PT
function formatDate(ts) {
  const date = ts.toDate ? ts.toDate() : ts;
  return (
    new Intl.DateTimeFormat("pt-PT", {
      dateStyle: "long",
      timeStyle: "medium",
    }).format(date) + ` UTC${date.toString().match(/GMT([+-]\d+)/)[1]}`
  );
}

// para facilitar o v-model de checkboxes + quantidades
const selectedItemsMap = ref({
  material: [],
  profissional: [],
});
const selectedItemsQuantities = ref({});

async function fetchAll() {
  // materiais
  const matsSnap = await getDocs(collection(db, "materiais"));
  allMaterials.value = matsSnap.docs.map((d) => ({ id: d.id, ...d.data() }));
  // profissionais
  const profsSnap = await getDocs(collection(db, "profissionais"));
  allProfissionais.value = profsSnap.docs.map((d) => ({
    id: d.id,
    ...d.data(),
  }));
}

onMounted(fetchAll);

function openMaterialsModal() {
  showMaterialsModal.value = true;
}

function openProfsModal() {
  showProfsModal.value = true;
}

const saving = ref(false);

async function saveAll() {
  if (!selectedAuditoria.value?.id) {
    alert("Nenhuma auditoria seleccionada");
    return;
  }

  saving.value = true;
  const auditRef = doc(db, "auditorias", selectedAuditoria.value.id);

  try {
    // 1) Buscar auditoria original
    const auditSnap = await getDoc(auditRef);
    const origData = auditSnap.data() || {};
    const origMats = origData.materiais || [];
    const origProfs = origData.profissionais || [];

    // 2) Construir arrays actualizados
    const updatedMats = origMats.map((item) => ({
      id: item.id,
      nome: item.nome,
      quantidade:
        selectedAuditoria.value.materiais.find((i) => i.id === item.id)
          ?.quantidade ?? item.quantidade,
    }));
    for (const matId of selectedItemsMap.value.material) {
      const qtd = selectedItemsQuantities.value[matId] || 0;
      if (qtd > 0) {
        const mat = allMaterials.value.find((m) => m.id === matId);
        updatedMats.push({ id: matId, nome: mat.nome, quantidade: qtd });
      }
    }

    const updatedProfs = origProfs.map((item) => ({
      id: item.id,
      nome: item.nome,
      quantidade:
        selectedAuditoria.value.profissionais.find((i) => i.id === item.id)
          ?.quantidade ?? item.quantidade,
    }));
    for (const profId of selectedItemsMap.value.profissional) {
      const qtd = selectedItemsQuantities.value[profId] || 0;
      if (qtd > 0) {
        const prof = allProfissionais.value.find((p) => p.id === profId);
        updatedProfs.push({ id: profId, nome: prof.nome, quantidade: qtd });
      }
    }

    // 3) Validação de stock — não permitir diffs maiores que o disponível
    for (const item of updatedMats) {
      const orig = origMats.find((o) => o.id === item.id);
      const origQ = orig?.quantidade || 0;
      const diff = item.quantidade - origQ;
      if (diff > 0) {
        // fetch stock actual
        const mSnap = await getDoc(doc(db, "materiais", item.id));
        const stock = mSnap.data().quantidade;
        if (diff > stock) {
          alert(
            `Não podes adicionar mais do que ${stock} unidades do material "${item.nome}".`
          );
          saving.value = false;
          return;
        }
      }
    }
    for (const item of updatedProfs) {
      const orig = origProfs.find((o) => o.id === item.id);
      const origQ = orig?.quantidade || 0;
      const diff = item.quantidade - origQ;
      if (diff > 0) {
        const pSnap = await getDoc(doc(db, "profissionais", item.id));
        const stock = pSnap.data().quantidade;
        if (diff > stock) {
          alert(
            `Não podes adicionar mais do que ${stock} unidades do profissional "${item.nome}".`
          );
          saving.value = false;
          return;
        }
      }
    }

    // 4) Ajustar stocks na Firebase
    for (const item of updatedMats) {
      const orig = origMats.find((o) => o.id === item.id);
      const origQ = orig?.quantidade || 0;
      const diff = item.quantidade - origQ;
      if (diff !== 0) {
        const mRef = doc(db, "materiais", item.id);
        const mSnap = await getDoc(mRef);
        const atual = mSnap.data().quantidade;
        await updateDoc(mRef, { quantidade: atual - diff });
      }
    }
    for (const item of updatedProfs) {
      const orig = origProfs.find((o) => o.id === item.id);
      const origQ = orig?.quantidade || 0;
      const diff = item.quantidade - origQ;
      if (diff !== 0) {
        const pRef = doc(db, "profissionais", item.id);
        const pSnap = await getDoc(pRef);
        const atual = pSnap.data().quantidade;
        await updateDoc(pRef, { quantidade: atual - diff });
      }
    }

    // 5) Gravar auditoria actualizada
    await updateDoc(auditRef, {
      materiais: updatedMats,
      profissionais: updatedProfs,
    });

    // 6) Actualizar estado local
    selectedAuditoria.value.materiais = updatedMats;
    selectedAuditoria.value.profissionais = updatedProfs;

    // 7) Limpar selecções e fechar modais
    selectedItemsMap.value.material = [];
    selectedItemsMap.value.profissional = [];
    selectedItemsQuantities.value = {};
    showMaterialsModal.value = false;
    showProfsModal.value = false;

    console.log("saveAll concluído com sucesso");
  } catch (erro) {
    console.error("Erro ao guardar auditoria:", erro);
    alert("Ocorreu um erro ao gravar. Vê o console para mais detalhes.");
  } finally {
    saving.value = false;
  }
}
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

.page-header h2 {
  margin: 0 0 1em;
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

.table-scroll {
  margin-top: 1em;
}

.table-scroll .generic-table-wrapper {
  max-height: 400px;
  overflow-y: auto;
}

.icon-btn {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.icon-btn:hover {
  background-color: #f0f0f0;
}

.icon-btn img {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

/* fade-in do overlay */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

/* slide + fade do box */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-box {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  padding: 1.5em 2em;
  animation: slideIn 0.3s ease-out forwards;
}

.modal-box h3 {
  margin: 0 0 0.75em;
  font-size: 1.5em;
  font-weight: 600;
}

.btn-close {
  display: inline-block;
  margin-top: 1.5em;
  padding: 0.6em 1.2em;
  font-size: 1em;
  background: #204c6d;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
}

.btn-close:hover {
  background: #0056b3;
  transform: translateY(-2px);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 600px;
  margin: 0 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  overflow: hidden;
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

.modal-close:hover {
  color: #000;
}

.modal-body {
  overflow-y: auto;
  flex: 1;
  margin-bottom: 16px;
}

.map-wrapper {
  margin-bottom: 16px;
}

.map-iframe {
  width: 100%;
  height: 200px;
  border: 0;
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.info-item {
  font-size: 0.9rem;
  color: #333;
}

.info-item span {
  font-weight: 600;
}

.section-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.materials-list,
.profissionais-list {
  list-style: disc inside;
  margin: 0;
  padding: 0;
}

.materials-list li,
.profissionais-list li {
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #333;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.primary-button {
  background: #204c6d;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.primary-button:hover {
  background: #0053ba;
}

/* Transições suaves */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.description-text {
  font-size: 0.9rem;
  color: #333;
  line-height: 1.4;
  margin: 0 0 8px;
}

.materials-table,
.professionals-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
  font-size: 0.9rem;
}

.materials-table th,
.materials-table td,
.professionals-table th,
.professionals-table td {
  border: 1px solid #ddd;
  padding: 8px;
}

.materials-table th,
.professionals-table th {
  background: #f5f5f5;
  font-weight: 600;
  text-align: left;
}

.materials-table td.text-center,
.professionals-table td.text-center {
  text-align: center;
}

.section-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

@media (max-width: 480px) {
  .materials-table th,
  .materials-table td,
  .professionals-table th,
  .professionals-table td {
    padding: 6px;
    font-size: 0.8rem;
  }
}

.qty-input {
  width: 60px;
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.add-button {
  background: transparent;
  border: none;
  font-size: 1rem;
  color: #204c6d;
  cursor: pointer;
  transition: color 0.2s;
}

.add-button:hover {
  color: #0053ba;
}

.imagem-video-container {
  margin-bottom: 24px;
  /* mb-6 */
}

.imagem-video-item {
  margin-bottom: 16px;
  /* mb-4 */
}

.imagem-video-item img,
.imagem-video-item video {
  max-width: 100%;
  /* max-w-full */
  border-radius: 4px;
  /* rounded */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  /* shadow */
}

/* Tabelas de seleção */
.table {
  width: 100%;
  /* w-full */
  table-layout: auto;
  /* table-auto */
  border-collapse: collapse;
}

.table th,
.table td {
  text-align: left;
  /* text-left */
  padding: 8px;
  /* p-2 */
}

.border-t {
  border-top: 1px solid #ccc;
  /* border-t */
}

/* Checkbox + label */
.inline-flex {
  display: inline-flex;
  /* inline-flex */
  align-items: center;
  /* items-center */
}

.mr-2 {
  margin-right: 8px;
  /* mr-2 */
}

/* Input de quantidade */
.quantity-input {
  width: 80px;
  /* w-20 (5rem = 80px) */
  border: 1px solid #ccc;
  /* border */
  border-radius: 4px;
  /* rounded */
  padding: 4px;
  /* p-1 */
}

/* Footer do modal */
.modal-footer {
  margin-top: 16px;
  /* mt-4 */
  text-align: right;
  /* text-right */
}

.modal-footer button {
  padding: 8px 16px;
  /* py-2 px-4 */
  border-radius: 4px;
  /* rounded */
  background-color: #e5e7eb;
  /* bg-gray-200 */
  border: none;
  cursor: pointer;
}
</style>
