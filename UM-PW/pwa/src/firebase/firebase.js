// Import the functions you need from the SDKs you need
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

import { initializeApp } from "firebase/app";
import { getFirestore, doc, setDoc, getDoc } from "firebase/firestore";
import { getAuth } from "firebase/auth";
  import {
    signInWithPopup,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    GoogleAuthProvider,
    signOut
  } from "firebase/auth";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyDfrWf9cajeBe7BVT7PWT5nBOWj7gPDBiw",
    authDomain: "pw-g201.firebaseapp.com",
    projectId: "pw-g201",
    storageBucket: "pw-g201.firebasestorage.app",
    messagingSenderId: "858778948795",
    appId: "1:858778948795:web:8bb0688f9713fec265c59e",
    measurementId: "G-JWNEDZWNTX"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

const db = getFirestore(app);
const auth = getAuth(app);

export { db, auth };



import axios from "axios";

const CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/do5hfydb2/upload";
const UPLOAD_PRESET = "EyesEveryWhere";

export async function uploadToCloudinary(file, onUploadProgress = null) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("upload_preset", UPLOAD_PRESET);

  try {
      const response = await axios.post(CLOUDINARY_URL, formData, {
          onUploadProgress,
      });

      return response.data.secure_url;
  } catch (error) {
      console.error("Erro ao enviar para Cloudinary:", error);
      return null;
  }
}

export const googleProvider = new GoogleAuthProvider();
export const logout = () => signOut(auth);

// Registo com email/password (mantém role "usuario")
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
  
  // Login com email/password
  export const loginWithEmail = (email, password) =>
    signInWithEmailAndPassword(auth, email, password);
  
  // Login com Google (cria user em users se não existir)
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