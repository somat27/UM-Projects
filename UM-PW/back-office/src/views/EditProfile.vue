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
                        <h2>Editar Perfil</h2>
                    </div>

                    <form class="edit-form" @submit.prevent="saveProfile">
                        <div class="form-field">
                            <label for="displayName">Nome</label>
                            <input id="displayName" v-model="form.displayName" required />
                        </div>

                        <div class="form-field">
                            <label for="email">Email</label>
                            <input id="email" type="email" v-model="form.email" disabled />
                        </div>

                        <div class="form-actions">
                            <button class="btn btn-primary" type="submit" :disabled="saving">
                                {{ saving ? 'A gravar...' : 'Salvar' }}
                            </button>
                            <button class="btn btn-secondary" @click.prevent="cancelEdit">
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { doc, getDoc, updateDoc } from 'firebase/firestore'
import { auth, db } from '@/firebase'
import NavigationList from '@/components/NavigationList.vue'

const form = reactive({ displayName: '', email: '' })
const saving = ref(false)
const router = useRouter()
const uid = auth.currentUser?.uid

onMounted(async () => {
    if (!uid) return router.push('/')
    const snap = await getDoc(doc(db, 'users', uid))
    if (snap.exists()) Object.assign(form, snap.data())
})

const saveProfile = async () => {
    saving.value = true
    try {
        await updateDoc(doc(db, 'users', uid), {
            displayName: form.displayName
        })
        alert('Perfil atualizado com sucesso!')
        router.push({ name: 'ProfileView' })
    } catch (err) {
        console.error(err)
        alert('Erro ao salvar perfil.')
    } finally {
        saving.value = false
    }
}

const cancelEdit = () => {
    router.push({ name: 'ProfileView' })
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

.icon-btn {
    background: none;
    border: none;
    cursor: pointer;
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

.edit-form {
    background: #fff;
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.form-field {
    display: flex;
    flex-direction: column;
    margin-bottom: 16px;
}

.form-field label {
    font-weight: 600;
    margin-bottom: 4px;
}

.form-field input {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.form-actions {
    display: flex;
    gap: 12px;
    margin-top: 24px;
}

.btn-secondary {
    background: #f0f0f0;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.btn-secondary:hover {
    background: #e2e2e2;
}
</style>