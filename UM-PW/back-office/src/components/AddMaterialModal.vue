<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <h3>{{ materialProp ? "Editar Material" : "Adicionar Material" }}</h3>
      <form @submit.prevent="saveMaterial">
        <div class="form-group">
          <label>Nome</label>
          <input v-model="form.nome" type="text" required />
        </div>

        <div class="form-group">
          <label>Categoria</label>
          <input v-model="form.categoria" type="text" required />
        </div>

        <div class="form-group">
          <label>Preço/Unidade (€)</label>
          <input
            v-model.number="form.preco"
            type="number"
            step="0.01"
            required
          />
        </div>

        <div v-if="!materialProp" class="form-group">
          <label>Quantidade</label>
          <input v-model.number="form.quantidade" type="number" required />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="closeModal">
            Cancelar
          </button>
          <button type="submit" class="btn-primary">
            {{ materialProp ? "Guardar Alterações" : "Adicionar" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
// eslint-env vue/setup-compiler-macros
/* eslint-disable no-undef */
const props = defineProps({
  material: { type: Object, default: null },
});
const emits = defineEmits(["close", "saved"]);

import { ref, watch, toRef } from "vue";
import { db } from "@/firebase.js";
import { addDoc, collection, doc, updateDoc } from "firebase/firestore";

// alias para usar no template
const materialProp = toRef(props, "material");

// inicializa o form, ou com os valores existentes (edit), ou vazio (add)
const form = ref({
  nome: "",
  categoria: "",
  preco: 0,
  quantidade: 0,
});

// se o prop mudar (reaberturas), sincroniza o form
watch(
  materialProp,
  (novo) => {
    if (novo) {
      form.value = {
        nome: novo.nome,
        categoria: novo.categoria,
        preco: novo.preco,
        quantidade: novo.quantidade,
      };
    } else {
      form.value = { nome: "", categoria: "", preco: 0, quantidade: 0 };
    }
  },
  { immediate: true }
);

function closeModal() {
  emits("close");
}

async function saveMaterial() {
  try {
    if (materialProp.value) {
      const refDoc = doc(db, "materiais", materialProp.value.id);
      await updateDoc(refDoc, { ...form.value });
    } else {
      await addDoc(collection(db, "materiais"), { ...form.value });
    }
    emits("saved");
  } catch (e) {
    console.error("Erro ao guardar material:", e);
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
  max-width: 480px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-container h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.form-group {
  margin-bottom: 0.75rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-primary {
  background: #204c6d;
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
</style>
