import { createRouter, createWebHistory } from "vue-router";
import { auth, db } from "@/firebase/firebase.js";
import ListaAuditorias from "@/components/Paginas/ListaAuditorias.vue";
import InfoAuditoria from "@/components/Paginas/InfoAuditoria.vue";
import UserPerfil from "@/components/UserPerfil.vue";
import RegistoAuditoria from "@/components/Paginas/RegistoAuditoria.vue";
import LoginPage from "@/components/LoginPage.vue";
import RegisterPage from "@/components/RegisterPage.vue";
import PendingValidation from "@/components/PendingValidation.vue";

import { onAuthStateChanged } from 'firebase/auth'
import { doc, getDoc, collection, query, where, getDocs } from 'firebase/firestore'

const routes = [
  {
    path: "/ListaAuditorias",
    name: "ListaAuditorias",
    component: ListaAuditorias,
    meta: { requiresAuth: true, requiresPerito: true },
  },

  {
    path: "/InfoAuditoria/:id",
    name: "InfoAuditoria",
    component: InfoAuditoria,
    meta: { requiresAuth: true, requiresPerito: true, requiresAcesso: true },
  },

  {
    path: "/RegistoAuditoria/:id",
    name: "RegistoAuditoria",
    component: RegistoAuditoria,
    meta: { requiresAuth: true, requiresPerito: true, requiresAcesso: true, porCompletar: true },
  },

  {
    path: "/Perfil",
    name: "UserPerfil",
    component: UserPerfil,
    meta: { requiresAuth: true, requiresPerito: true },
  },

  {
    path: "/",
    name: "LoginPage",
    component: LoginPage,
  },

  {
    path: "/register",
    name: "RegisterPage",
    component: RegisterPage,
  },

  {
    path: "/PendingValidation",
    name: "PendingValidation",
    component: PendingValidation,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


function getCurrentUser() {
  return new Promise((resolve, reject) => {
    const unsubscribe = onAuthStateChanged(
      auth,
      user => {
        unsubscribe()
        resolve(user)
      },
      err => {
        unsubscribe()
        reject(err)
      }
    )
  })
}

router.beforeEach(async (to, from, next) => {
  if (!to.meta.requiresAuth) {
    return next();
  }

  const savedUID = localStorage.getItem('userUID');
  if (!savedUID) {
    return next({ name: 'LoginPage' });
  }

  const user = await getCurrentUser();
  if (!user) {
    localStorage.removeItem('userUID');
    return next({ name: 'LoginPage' });
  }

  const snap = await getDoc(doc(db, 'users', user.uid));
  const role = snap.exists() ? snap.data().role : null;

  const peritosQuery = query(
    collection(db, 'peritos'),
    where('uid', '==', user.uid)
  )
  const peritosSnap = await getDocs(peritosQuery)
  const isPeritoNaColecao = !peritosSnap.empty

  if (to.meta.requiresPerito) {
    if (role !== 'perito' || !isPeritoNaColecao) {
      return next({ name: 'PendingValidation' });
    }
  }

  if (to.meta.requiresAcesso && to.params.id) {
    const auditoriaId = to.params.id
    const auditoriaRef = doc(db, 'auditorias', auditoriaId)
    const auditoriaSnap = await getDoc(auditoriaRef)

    if (!auditoriaSnap.exists()) {
      return next({ name: 'ListaAuditorias' })
    }

    const auditoria = auditoriaSnap.data()
    if (auditoria.perito !== user.uid) {
      return next({ name: 'PendingValidation' })
    }

    if (to.meta.porCompletar && auditoria.status === 'Concluido') {
      return next({ name: 'InfoAuditoria', params: { id: auditoriaId } })
    }
  }

  return next();
});


export default router;