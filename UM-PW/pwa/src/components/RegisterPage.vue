<template>
  <main class="register-page painel">
    <form class="auth-form" @submit.prevent="handleRegister" novalidate>
      <h2>Registar Conta</h2>
      <div class="form-group">
        <input v-model.trim="displayName" type="text" placeholder="Nome" required />
      </div>
      <div class="form-group">
        <input v-model.trim="email" type="email" placeholder="Email" required />
      </div>
      <div class="form-group">
        <input v-model="password" type="password" placeholder="Palavra‑passe (min. 6)" required />
      </div>
      <div class="form-group">
        <input v-model="confirm" type="password" placeholder="Confirmar palavra‑passe" required />
      </div>
      <p v-if="errorMsg">{{ errorMsg }}</p>
      <button :disabled="!canSubmit" type="submit">
        Registar
      </button>
      <p>
        Já tens conta?
        <router-link class="p-1" to="/">Entrar</router-link>
      </p>
    </form>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { registerWithEmail } from '@/firebase/firebase.js';

const displayName = ref('');
const email = ref('');
const password = ref('');
const confirm = ref('');
const errorMsg = ref('');
const router = useRouter();

const canSubmit = computed(() =>
  displayName.value && email.value && password.value.length >= 6 && password.value === confirm.value
);

const handleRegister = async () => {
  if (!canSubmit.value) {
    errorMsg.value = 'Preenche todos os campos correctamente.';
    return;
  }
  try {
    await registerWithEmail(email.value, password.value, displayName.value);
    router.push('/');
  } catch (err) {
    if (err.code === 'auth/email-already-in-use') {
      errorMsg.value = 'Esse e‑mail já está registado.';
    } else if (err.code === 'auth/weak-password') {
      errorMsg.value = 'Palavra‑passe deve ter pelo menos 6 caracteres.';
    } else {
      errorMsg.value = 'Erro: ' + err.message;
    }
  }
};
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #F5F5F5 0%, #e3f2fd 100%);
}

.auth-form {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 360px;
  text-align: center;
}

.auth-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #204C6D;
}

.form-group {
  width: 100%;
  margin-bottom: 1rem;
  margin-right: 1.6rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #204C6D;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #bbb;
  border-radius: 8px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background: #204C6D;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background: #1565c0;
}

.p-1 {
  color: #204C6D;
}

.p-1:hover {
  color: #1565c0;
}
</style>