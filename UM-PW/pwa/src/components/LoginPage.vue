<template>
  <main class="login-page painel">
    <form class="auth-form" @submit.prevent="handleEmailLogin" novalidate>
      <h2>Iniciar Sessão</h2>
      <div class="form-group">
        <input v-model.trim="email" type="email" placeholder="Email" required />
      </div>
      <div class="form-group">
        <input v-model="password" type="password" placeholder="Palavra‑passe" required />
      </div>
      <p v-if="errorMsg">{{ errorMsg }}</p>
      <button :disabled="!canSubmit || emailLoading" type="submit">
        {{ emailLoading ? 'A aguardar...' : 'Login' }}
      </button>
      <hr />
      <button @click="handleGoogleLogin" :disabled="googleLoading">
        <img class="google" src="@/assets/google.png" alt="google">
        <span v-if="googleLoading">Abrindo Google...</span>
        <span v-else>Entrar com Google</span>
      </button>
      <p>
        Não tem conta?
        <router-link class="p-1" to="/register">Registar</router-link>
      </p>
    </form>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { loginWithEmail, loginWithGoogle, auth } from '@/firebase/firebase.js'

// Estados
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const emailLoading = ref(false)
const googleLoading = ref(false)
const router = useRouter()

// Redireciona se já existir sessão guardada
onMounted(() => {
  const savedUID = localStorage.getItem('userUID')
  if (savedUID) {
    router.replace('/ListaAuditorias')
  }
})

// Validação do formulário de email
const canSubmit = computed(() => email.value && password.value.length)

// Login por email
const handleEmailLogin = async () => {
  if (emailLoading.value) return
  emailLoading.value = true
  errorMsg.value = ''
  if (!canSubmit.value) {
    errorMsg.value = 'Preenche e‑mail e palavra‑passe.'
    emailLoading.value = false
    return
  }
  try {
    await loginWithEmail(email.value, password.value)
    localStorage.setItem('userUID', auth.currentUser.uid)
    router.push('/ListaAuditorias')
  } catch (err) {
    switch (err.code) {
      case 'auth/missing-password':
        errorMsg.value = 'Introduz a palavra‑passe.'
        break
      case 'auth/invalid-email':
        errorMsg.value = 'E‑mail inválido.'
        break
      case 'auth/wrong-password':
        errorMsg.value = 'Palavra‑passe incorrecta.'
        break
      case 'auth/user-not-found':
        errorMsg.value = 'Utilizador não encontrado.'
        break
      default:
        errorMsg.value = 'Erro: ' + err.message
    }
  } finally {
    emailLoading.value = false
  }
}

const handleGoogleLogin = async () => {
  if (googleLoading.value) return
  googleLoading.value = true
  errorMsg.value = ''
  try {
    const user = await loginWithGoogle()
    localStorage.setItem('userUID', user.uid)
    router.push('/ListaAuditorias')
  } catch (err) {
    const ignoreCodes = [
      'auth/cancelled-popup-request',
      'auth/popup-closed-by-user',
      'auth/popup-blocked'
    ]
    if (!ignoreCodes.includes(err.code)) {
      errorMsg.value = 'Erro: ' + err.message
    }
  } finally {
    googleLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #F5F5F5 0%, #e3f2fd 100%);
}

.auth-form {
  background: white;
  padding: 2rem;
  border-radius: 15px;
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

.google {
  margin-right: 10px;
}

.p-1 {
  color: #204C6D;
}

.p-1:hover {
  color: #1565c0;
}
</style>
