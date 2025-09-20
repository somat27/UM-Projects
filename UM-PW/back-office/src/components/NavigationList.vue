<template>
  <nav class="navigation-list">
    <img
      src="https://cdn.builder.io/api/v1/image/assets/TEMP/9cae2c5a44e739bfd2edc79e5215ab61eb4c5ee8?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
      alt="Logo"
      class="logo"
    />
    <div class="menu-header"></div>
    <router-link
      to="/dashboards/auditorias"
      class="nav-item"
      :class="{ 'nav-item-active': isDashboardActive }"
    >
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/bd9d82f1effb8381bb1929299adeb4fb409cd704?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
        alt="Dashboard"
        class="nav-icon"
      />
      <span class="nav-text">DASHBOARDS</span>
    </router-link>

    <router-link to="/GestaoAuditorias" class="nav-item">
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/b414ddc8a44a7865af46891e60f33ca4a0160885?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
        alt="Auditorias"
        class="nav-icon"
      />
      <span class="nav-text">GESTÃO DE AUDITORIAS</span>
    </router-link>

    <router-link
      to="/GestaoOcorrencias"
      class="nav-item"
      :class="{ 'nav-item-active': isGAActive }"
    >
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/32555fc51897e2a6d661a8bff00a21a07bb15d13?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
        alt="Notification"
        class="nav-icon"
      />
      <span class="nav-text">GESTÃO DE OCORRÊNCIAS</span>
    </router-link>

    <router-link to="/GestaoPeritos" class="nav-item">
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/08fd61f8d2974d973bc8956784b3929b25f9988a?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
        alt="Alert"
        class="nav-icon"
      />
      <span class="nav-text">GESTÃO DE PERITOS</span>
    </router-link>

    <router-link to="/GestaoMateriais" class="nav-item">
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/890255b1fe5b0074d3223ecb23bf8221887fb032?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
        alt="Materiais"
        class="nav-icon"
      />
      <span class="nav-text">GESTÃO DE MATERIAIS</span>
    </router-link>

    <router-link to="/GestaoProfissionais" class="nav-item">
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/2130c19d7d5c87c243ec6c2559e349da836493a5?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
        alt="Profissionais"
        class="nav-icon"
      />
      <span class="nav-text">GESTÃO DE PROFISSIONAIS</span>
    </router-link>

    <router-link to="/GestaoUtilizadores" class="nav-item" v-if="isAdmin">
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/2130c19d7d5c87c243ec6c2559e349da836493a5?placeholderIfAbsent=true&apiKey=98100b9ac2c544efa71903dc3e1eda07"
        alt="Profissionais"
        class="nav-icon"
      />
      <span class="nav-text">GESTÃO DE UTILIZADORES</span>
    </router-link>

    <router-link
      to="/profile"
      class="user-panel text-decoration-none"
      v-if="currentUser"
    >
      <img :src="currentUser.photoURL || defaultAvatar" class="avatar" />
      <span class="user-name">
        {{ currentUser.displayName || currentUser.email }}
      </span>
    </router-link>

    <button class="logout-button" @click="handleLogout">
      <span class="logout-text">LOG OUT</span>
      <div class="lock-icon">⏻</div>
    </button>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useCurrentUser } from "@/composables/useCurrentUser";
import { auth, db, logout } from "@/firebase";
import { onAuthStateChanged } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";

const isAdmin = ref(false);
const router = useRouter();
const route = useRoute();

const { currentUser } = useCurrentUser();
const defaultAvatar = "https://i.pravatar.cc/40?u=placeholder";

async function handleLogout() {
  await logout();
  localStorage.removeItem("userUID");
  router.push("/");
}

const isDashboardActive = computed(() => route.path.startsWith("/dashboards/"));

const isGAActive = computed(() => route.path.startsWith("/GestaoOcorrencias/"));

onMounted(() => {
  onAuthStateChanged(auth, async (user) => {
    if (!user) return;
    const snap = await getDoc(doc(db, "users", user.uid));
    isAdmin.value = snap.exists() && snap.data().role === "admin";
  });
});
</script>

<style scoped>
.navigation-list {
  width: 100%;
  font-family: "Public Sans", -apple-system, Roboto, Helvetica, sans-serif;
  font-size: 14px;
  color: #141414;
  background-color: #fff;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-title {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  gap: 10px;
  background-color: #fff;
  width: 100%;
  box-sizing: border-box;
  margin: 0;
  border-bottom: 1px solid #e0e0e0;
}

.logo-icon {
  width: 24px;
  height: 24px;
}

.app-name {
  font-size: 20px;
  font-weight: 500;
}

.nav-item {
  position: relative;
  display: flex;
  width: 100%;
  padding: 16px 24px;
  align-items: center;
  gap: 18px;
  color: #4d4d4d;
  text-decoration: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
  margin: 0;
  background-color: #fff;
  transition: background-color 0.3s ease, transform 0.2s ease,
    box-shadow 0.3s ease;
  transform-origin: left center;
}

.nav-item:hover {
  color: #204c6d;
  background-color: #f0f7ff;
}

.nav-item-active,
.nav-item.router-link-active {
  color: #204c6d;
  background-color: #f0f7ff;
  font-weight: 500;
  position: relative;
  border-left: 3px solid #204c6d;
}

.nav-item-active::after,
.nav-item.router-link-active::after {
  display: none;
}

.nav-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  filter: grayscale(100%);
  transition: filter 0.3s ease, transform 0.3s ease;
}

.nav-item:hover .nav-icon {
  filter: grayscale(0%);
  transform: scale(1.1) rotate(-5deg);
}
.nav-item-active .nav-icon,
.nav-item.router-link-active .nav-icon {
  filter: brightness(0) saturate(100%) invert(26%) sepia(51%) saturate(679%)
    hue-rotate(161deg) brightness(95%) contrast(97%);
  transform: scale(1.15) rotate(0deg);
  animation: iconPulse 1.5s infinite alternate;
}

.nav-text {
  line-height: 21px;
  font-size: 13px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  transition: letter-spacing 0.3s ease, transform 0.3s ease;
}

.user-profile {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 20px 24px;
  color: #666;
  font-weight: 400;
  background-color: #fff;
}

.user-avatar {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 50%;
  display: block;
  background-color: #f0f0f0;
}

.logout-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #204c6d;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 20px;
  margin: 15px 24px 30px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.logout-button:hover {
  background-color: #e74c3c;
}

.logout-text {
  letter-spacing: 1px;
  margin-right: 5px;
}

@media (max-width: 991px) {
  .nav-item,
  .app-title {
    padding-left: 16px;
    padding-right: 16px;
  }

  .nav-item-active::after,
  .nav-item.router-link-active::after {
    border-top: 20px solid transparent;
    border-bottom: 20px solid transparent;
    border-right: 20px solid #fff;
  }
}

.user-panel {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
}

.avatar {
  margin-left: 10px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  line-height: 21px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #666;
  font-size: 15px;
}

.logo {
  margin-top: 24px;
}

.menu-header {
  height: 1px;
  margin: 12px 0 20px;
}
</style>
