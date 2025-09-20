<template>
    <div class="dashboard-container">
        <div class="dashboard-layout">
            <main class="main-content">
                <div class="content-wrapper centered">
                    <div class="card">
                        <h2>Conta Pendente</h2>
                        <p>
                            A sua conta ainda não foi validada por um Admin.<br />
                            Por favor, aguarde até receber a validação.
                        </p>
                        <button class="change-account-button" @click="handleLogout">
                            Mudar de Conta
                        </button>
                    </div>
                </div>
            </main>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { logout } from '@/firebase'

const router = useRouter()

async function handleLogout() {
    await logout()
    localStorage.removeItem('userUID')
    router.push('/')
}
</script>

<style scoped>
.centered {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 60vh;
}

.card {
    background: #fff;
    padding: 32px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.card h2 {
    margin-bottom: 16px;
}

.change-account-button {
    margin-top: 16px;
    padding: 8px 16px;
    background: #1890ff;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.change-account-button:hover {
    background: #167ac6;
}

.help-text {
    margin-top: 8px;
    font-size: 0.9rem;
    color: #555;
}
</style>