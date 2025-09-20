<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <h3>Adicionar Perito</h3>
      <form @submit.prevent="savePerito">
        <!-- Nome (não editável) -->
        <div class="form-group">
          <label>Nome</label>
          <input v-model="form.displayName" disabled />
        </div>

        <!-- Especialidade -->
        <div class="form-group">
          <label>Especialidade</label>
          <input v-model="form.specialty" type="text" required />
        </div>

        <!-- E-mail -->
        <div class="form-group">
          <label>E-mail</label>
          <input v-model="form.email" type="email" required />
        </div>

        <!-- Telemóvel -->
        <div class="form-group">
          <label>Telemóvel</label>
          <input v-model="form.phone" type="tel" required />
        </div>

        <!-- Morada -->
        <div class="form-group">
          <label>Morada</label>
          <input v-model="form.address" type="text" required />
        </div>

        <!-- Data de Nascimento -->
        <div class="form-group">
          <label>Data de Nascimento</label>
          <input v-model="form.birthDate" type="date" required />
        </div>

        <!-- Status -->
        <div class="form-group">
          <label>Status</label>
          <select v-model="form.status" required>
            <option value="">Selecionar...</option>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
          </select>
        </div>

        <!-- Localidades -->
        <div class="form-group">
          <label>Localidades</label>
          <div class="region-buttons">
            <div
              v-for="region in regions"
              :key="region.value"
              class="region-item"
            >
              <span class="region-name">{{ region.value }}</span>
              <button
                type="button"
                class="select-button"
                :class="{ selected: form.localidades.includes(region.value) }"
                @click="toggleRegion(region.value)"
              >
                {{
                  form.localidades.includes(region.value)
                    ? "Remover"
                    : "Selecionar"
                }}
              </button>
            </div>
          </div>
        </div>

        <!-- Botões -->
        <div class="modal-buttons">
          <button type="button" class="cancel-button" @click="closeModal">
            Cancelar
          </button>
          <button type="submit" class="save-button">Guardar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
// eslint-env vue/setup-compiler-macros
/* eslint-disable no-undef */
import { ref, watch } from "vue";
import { addPeritoProfile } from "@/firebase";

const props = defineProps({
  user: { type: Object, required: true },
});

const emits = defineEmits(["close", "saved"]);

const regions = [
  {
    value: "Norte",
  },
  {
    value: "Centro",
  },
  {
    value: "Lisboa e Vale do Tejo",
  },
  {
    value: "Alentejo",
  },
  {
    value: "Algarve",
  },
];

// Estado do formulário
const form = ref({
  displayName: props.user.displayName || "",
  specialty: props.user.specialty || "",
  status: props.user.status || "",
  localidades: props.user.localidades || [],
  email: props.user.email || "",
  phone: props.user.phone || "",
  address: props.user.address || "",
  birthDate: props.user.birthDate || "",
});

function toggleRegion(region) {
  const idx = form.value.localidades.indexOf(region);
  if (idx === -1) {
    form.value.localidades.push(region);
  } else {
    form.value.localidades.splice(idx, 1);
  }
}

// Sincroniza quando props.user muda
watch(
  () => props.user,
  (newUser) => {
    form.value.displayName = newUser.displayName || "";
    form.value.specialty = newUser.specialty || "";
    form.value.status = newUser.status || "";
    form.value.localidades = newUser.localidades || [];
    form.value.localidades = newUser.localidades || "";
    form.value.email = newUser.email || "";
    form.value.phone = newUser.phone || "";
    form.value.address = newUser.address || "";
    form.value.birthDate = newUser.birthDate || "";
  }
);

function closeModal() {
  emits("close");
}

async function savePerito() {
  try {
    await addPeritoProfile(props.user.uid, {
      displayName: form.value.displayName,
      specialty: form.value.specialty,
      status: form.value.status,
      localidades: form.value.localidades,
      email: form.value.email,
      phone: form.value.phone,
      address: form.value.address,
      birthDate: form.value.birthDate,
    });
    emits("saved");
  } catch (error) {
    console.error("Erro ao guardar perito:", error);
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-container h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.cancel-button {
  background: none;
  border: 1px solid #ccc;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
}

.save-button {
  background: #204c6d;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
}

.save-button:hover {
  background: #167ac6;
}

.region-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.region-item {
  display: flex;
  align-items: start;
  gap: 0.5rem;
}

.region-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.region-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.region-name {
  font-weight: 500;
}

.select-button {
  padding: 0.25rem 0.5rem;
  border: 1px solid #204c6d;
  border-radius: 0.25rem;
  background: transparent;
  cursor: pointer;
}

.select-button.selected {
  background: #1890ff;
  color: #fff;
}
</style>
