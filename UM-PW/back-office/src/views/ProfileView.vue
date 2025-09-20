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
            <h2>Meu Perfil</h2>
          </div>

          <!-- Seção de Avatar com Preview -->
          <div class="profile-photo-section">
            <img
              :src="previewUrl || profile.photoURL || defaultAvatar"
              alt="Foto de Perfil"
              class="avatar"
            />
            <input
              type="file"
              accept="image/*"
              @change="onFileChange"
              class="file-input"
            />
            <button
              class="btn-primary"
              @click="uploadPhoto"
              :disabled="!selectedFile || loading"
            >
              {{ loading ? "Enviando..." : "Atualizar Foto" }}
            </button>
          </div>

          <!-- Dados do Perfil -->
          <div class="profile-info">
            <p><strong>Nome:</strong> {{ profile.displayName }}</p>
            <p><strong>Email:</strong> {{ profile.email }}</p>
          </div>

          <!-- Botão de Editar -->
          <button class="btn-primary edit-btn" @click="goToEdit">
            Editar Perfil
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { auth, db } from "@/firebase";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import NavigationList from "@/components/NavigationList.vue";

const CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/do5hfydb2/upload";
const CLOUDINARY_UPLOAD_PRESET = "EyesEveryWhere";

const profile = ref({ displayName: "", email: "", photoURL: "" });
const selectedFile = ref(null);
const loading = ref(false);
const router = useRouter();
const defaultAvatar = "/default-avatar.png";

onMounted(async () => {
  const user = auth.currentUser;
  if (!user) return router.push("/");
  const snap = await getDoc(doc(db, "users", user.uid));
  if (snap.exists()) profile.value = snap.data();
});

function goToEdit() {
  router.push({ name: "EditProfile" });
}

function onFileChange(event) {
  const file = event.target.files[0];
  if (file) selectedFile.value = file;
}

async function uploadPhoto() {
  if (!selectedFile.value) return;
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append("file", selectedFile.value);
    formData.append("upload_preset", CLOUDINARY_UPLOAD_PRESET);

    const response = await fetch(CLOUDINARY_URL, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    const photoURL = data.secure_url;

    const user = auth.currentUser;
    await updateDoc(doc(db, "users", user.uid), { photoURL });

    profile.value.photoURL = photoURL;
    alert("Foto de perfil atualizada com sucesso!");
  } catch (error) {
    console.error("Erro ao enviar foto:", error);
    alert("Falha ao atualizar foto de perfil.");
  } finally {
    loading.value = false;
    selectedFile.value = null;
  }
}
</script>

<style scoped>
.profile-photo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding: 16px;
  background-color: #f3f4f6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Avatar circular com borda azul */
.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #204c6d;
}

/* Input de arquivo estilizado */
.file-input {
  font-size: 14px;
  color: #374151;
}

/* Botão principal */
.btn-primary {
  padding: 10px 20px;
  background-color: #204c6d;
  color: #ffffff;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #1e40af;
}

/* Botão de editar perfil */
.edit-btn {
  margin-top: 24px;
}

/* Seção de informações pessoais */
.profile-info {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.profile-info p {
  margin: 8px 0;
  font-size: 16px;
  color: #1f2937;
}

.profile-info p {
  margin: 4px 0;
}

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

.profile-card {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.profile-field {
  display: flex;
  margin-bottom: 16px;
}

.profile-field label {
  width: 120px;
  font-weight: 600;
}

.profile-field span {
  flex: 1;
}
</style>
