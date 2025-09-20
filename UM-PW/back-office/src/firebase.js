import { initializeApp } from "firebase/app";
import {
  collection,
  getFirestore,
  doc,
  setDoc,
  getDoc,
  getDocs,
  query,
  where,
  updateDoc,
  deleteDoc
} from "firebase/firestore";
import {
  getAuth,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  signOut
} from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDfrWf9cajeBe7BVT7PWT5nBOWj7gPDBiw",
  authDomain: "pw-g201.firebaseapp.com",
  projectId: "pw-g201",
  storageBucket: "pw-g201.firebasestorage.app",
  messagingSenderId: "858778948795",
  appId: "1:858778948795:web:8bb0688f9713fec265c59e",
  measurementId: "G-JWNEDZWNTX",
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();
export const logout = () => signOut(auth);

export const registerWithEmail = async (email, password, displayName) => {
  const { user } = await createUserWithEmailAndPassword(auth, email, password);
  await setDoc(doc(db, "users", user.uid), {
    uid: user.uid,
    displayName,
    email,
    photoURL: null,
    role: "usuario",
  });
  return user;
};

export const loginWithEmail = (email, password) =>
  signInWithEmailAndPassword(auth, email, password);

export const loginWithGoogle = async () => {
  const { user } = await signInWithPopup(auth, googleProvider);
  const ref = doc(db, "users", user.uid);
  if (!(await getDoc(ref)).exists()) {
    await setDoc(ref, {
      uid: user.uid,
      displayName: user.displayName,
      email: user.email,
      photoURL: user.photoURL,
      role: "usuario",
    });
  }
  return user;
};

export const updateUserRole = async (uid, newRole) => {
  await updateDoc(doc(db, "users", uid), { role: newRole });
};

export const addPeritoProfile = async (uid, peritoData) => {
  try {
    await setDoc(doc(db, "peritos", uid), {
      uid,
      ...peritoData
    });
  } catch (error) {
    console.error("Erro ao adicionar perfil de perito:", error);
    throw error;
  }
};

export const getActivePeritos = async () => {
  try {
    const usersRef = collection(db, "users");
    const q = query(usersRef, where("role", "==", "perito"));
    const userSnaps = await getDocs(q);
    const peritos = await Promise.all(
      userSnaps.docs.map(async uDoc => {
        const uid = uDoc.id;
        const peritoSnap = await getDoc(doc(db, "peritos", uid));
        return peritoSnap.exists() ? { uid, ...peritoSnap.data() } : null;
      })
    );
    return peritos.filter(p => p);
  } catch (error) {
    console.error("Erro ao buscar peritos ativos:", error);
    throw error;
  }
};

export const getPeritosWithoutProfile = async () => {
  try {
    const usersRef = collection(db, "users");
    const q = query(usersRef, where("role", "==", "perito"));
    const userSnaps = await getDocs(q);
    const missing = await Promise.all(
      userSnaps.docs.map(async uDoc => {
        const uid = uDoc.id;
        const peritoSnap = await getDoc(doc(db, "peritos", uid));
        if (!peritoSnap.exists()) {
          return { uid, ...uDoc.data() };
        }
        return null;
      })
    );
    return missing.filter(p => p);
  } catch (error) {
    console.error("Erro ao buscar peritos sem perfil:", error);
    throw error;
  }
};

export const getPeritosWithProfile = getActivePeritos;

export const updatePeritoProfile = async (uid, updates) => {
  await updateDoc(doc(db, "peritos", uid), updates);
};

export const deletePeritoProfile = async (uid) => {
  await deleteDoc(doc(db, "peritos", uid));
};

export default {
  registerWithEmail,
  loginWithEmail,
  loginWithGoogle,
  logout,
  updateUserRole,
  addPeritoProfile,
  getActivePeritos,
  getPeritosWithoutProfile,
  getPeritosWithProfile,
  updatePeritoProfile,
  deletePeritoProfile
};
