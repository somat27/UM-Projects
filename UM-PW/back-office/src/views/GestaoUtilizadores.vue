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
            <h2>Gestão de Utilizadores</h2>
          </div>
          <div class="table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.uid">
                  <td>{{ user.displayName }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <select
                      v-model="user.newRole"
                      class="select-field"
                      :disabled="isOtherAdmin(user)"
                    >
                      <option value="usuario">Usuário</option>
                      <option value="perito">Perito</option>
                      <option value="gestor">Gestor</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td>
                    <button
                      class="btn-apply"
                      @click="changeRole(user)"
                      :disabled="isOtherAdmin(user)"
                    >
                      Aplicar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import NavigationList from "../components/NavigationList.vue";
import { auth, db } from "@/firebase";
import { onAuthStateChanged } from "firebase/auth";
import {
  collection,
  getDocs,
  doc,
  updateDoc,
  getDoc,
} from "firebase/firestore";

const users = ref([]);
const currentUser = ref(null);
const router = useRouter();

onMounted(() => {
  onAuthStateChanged(auth, async (user) => {
    if (!user) return router.push("/");

    const snapAdmin = await getDoc(doc(db, "users", user.uid));
    if (!(snapAdmin.exists() && snapAdmin.data().role === "admin")) {
      return router.push("/");
    }

    // Guarda o utilizador atual
    currentUser.value = {
      uid: user.uid,
      role: snapAdmin.data().role,
    };

    // Carrega todos os utilizadores e inicializa newRole
    const qs = await getDocs(collection(db, "users"));
    users.value = qs.docs.map((d) => ({
      uid: d.id,
      displayName: d.data().displayName,
      email: d.data().email,
      role: d.data().role,
      newRole: d.data().role,
    }));
  });
});

function isOtherAdmin(user) {
  return user.role === "admin" && user.uid !== currentUser.value.uid;
}

async function changeRole(user) {
  try {
    const isSelfDemoting =
      user.uid === currentUser.value.uid && user.newRole !== "admin";

    await updateDoc(doc(db, "users", user.uid), { role: user.newRole });
    alert(`Role atualizada para ${user.newRole}`);
    user.role = user.newRole;

    if (isSelfDemoting) {
      router.push("/");
    }
  } catch (err) {
    console.error("Erro ao atualizar role:", err);
    alert("Falha ao atualizar role");
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
  font-size: 1.75rem;
  margin-bottom: 1rem;
}

.navigation-tabs {
  margin-top: -15px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "Public Sans", -apple-system, Roboto, Helvetica, sans-serif;
  padding: 8px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.table th,
.table td {
  border: 1px solid #e0e0e0;
  padding: 12px 16px;
  text-align: left;
}

.table th {
  background-color: #f9fafb;
  font-weight: 600;
}

.table tbody tr:nth-child(even) {
  background-color: #fcfcfc;
}

.select-field {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background-color: #ffffff;
  font-size: 14px;
}

.select-field:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.btn-apply {
  padding: 8px 16px;
  background-color: #204c6d;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-apply:hover {
  background-color: #1e40af;
}
</style>
