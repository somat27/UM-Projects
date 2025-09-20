// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { auth, db } from '@/firebase'
import { onAuthStateChanged } from 'firebase/auth'
import { doc, getDoc } from 'firebase/firestore'

import LoginPage from '@/views/LoginPage.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import DashboardAuditorias from '@/views/dashboards/DashboardAuditorias.vue'
import DashboardOcorrencia from '@/views/dashboards/DashboardOcorrencia.vue'
import DashboardPeritos from '@/views/dashboards/DashboardPeritos.vue'
import DashboardMateriais from '@/views/dashboards/DashboardMateriais.vue'
import DashboardMapa from '@/views/dashboards/DashboardMapa.vue'
import GestaoAuditorias from '@/views/GestaoAuditorias.vue'
import GestaoOcorrencias from '@/views/GestaoOcorrencias.vue'
import AprovacaoOcorrencia from '@/views/AprovacaoOcorrencia.vue'
import GestaoPeritos from '@/views/GestaoPeritos.vue'
import GestaoMateriais from '@/views/GestaoMateriais.vue'
import GestaoProfissionais from '@/views/GestaoProfissionais.vue'
import ProfileView from '@/views/ProfileView.vue'
import EditProfile from '@/views/EditProfile.vue'
import GestaoUtilizadores from '@/views/GestaoUtilizadores.vue'
import PendingValidation from '@/views/PendingValidation.vue'

const routes = [
  {
    path: '/',
    name: 'LoginPage',
    component: LoginPage
  },
  {
    path: '/register',
    name: 'RegisterPage',
    component: RegisterPage
  },
  {
    path: '/pendente',
    name: 'PendingValidation',
    component: PendingValidation,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'ProfileView',
        component: ProfileView
      },
      {
        path: 'edit',
        name: 'EditProfile',
        component: EditProfile
      }
    ]
  },
  {
    path: '/dashboards',
    meta: { requiresAuth: true, requiresGestorOrAdmin: true },
    children: [
      { path: 'auditorias', component: DashboardAuditorias, name: 'auditorias' },
      { path: 'ocorrencias', component: DashboardOcorrencia, name: 'ocorrencias' },
      { path: 'peritos', component: DashboardPeritos, name: 'peritos' },
      { path: 'materiais', component: DashboardMateriais, name: 'materiais' },
      { path: 'mapa', component: DashboardMapa, name: 'mapa' }
    ]
  },
  {
    path: '/GestaoAuditorias',
    name: 'GestaoAuditorias',
    component: GestaoAuditorias,
    meta: {
      requiresAuth: true,
      requiresGestorOrAdmin: true
    }
  },
  {
    path: '/GestaoOcorrencias',
    name: 'GestaoOcorrencias',
    component: GestaoOcorrencias,
    meta: {
      requiresAuth: true,
      requiresGestorOrAdmin: true
    }
  },
  {
    path: '/GestaoOcorrencias/AprovacaoOcorrencia/:id',
    name: 'AprovacaoOcorrencia',
    component: AprovacaoOcorrencia,
    props: true,
    meta: { requiresAuth: true, requiresGestorOrAdmin: true }
  },
  {
    path: '/GestaoPeritos',
    name: 'GestaoPeritos',
    component: GestaoPeritos,
    meta: {
      requiresAuth: true,
      requiresGestorOrAdmin: true
    }
  },
  {
    path: '/GestaoMateriais',
    name: 'GestaoMateriais',
    component: GestaoMateriais,
    meta: {
      requiresAuth: true,
      requiresGestorOrAdmin: true
    }
  },
  {
    path: '/GestaoProfissionais',
    name: 'GestaoProfissionais',
    component: GestaoProfissionais,
    meta: {
      requiresAuth: true,
      requiresGestorOrAdmin: true
    }
  },
  {
    path: '/GestaoUtilizadores',
    name: 'GestaoUtilizadores',
    component: GestaoUtilizadores,
    meta: { requiresAuth: true, requiresGestorOrAdmin: true }
  }
]

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

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (!to.meta.requiresAuth) {
    return next()
  }

  const savedUID = localStorage.getItem('userUID')
  if (!savedUID) {
    return next({ name: 'LoginPage' })
  }

  const user = await getCurrentUser()
  if (!user) {
    localStorage.removeItem('userUID')
    return next({ name: 'LoginPage' })
  }

  const snap = await getDoc(doc(db, 'users', user.uid))
  const role = snap.exists() ? snap.data().role : null

  if (to.meta.requiresGestorOrAdmin) {
    if (role === 'gestor' || role === 'admin') {
      return next()
    } else {
      return next({ name: 'PendingValidation' })
    }
  }

  next()
})

export default router
