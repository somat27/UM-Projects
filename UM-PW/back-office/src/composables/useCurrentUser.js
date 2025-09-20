import { ref, onUnmounted } from 'vue';
import { auth, db } from '@/firebase';
import { doc, onSnapshot } from 'firebase/firestore';
import { onAuthStateChanged } from 'firebase/auth';

// singleton reactivo
export const currentUser = ref(null);

export function useCurrentUser() {
  const stopAuth = onAuthStateChanged(auth, (usr) => {
    if (!usr) {
      currentUser.value = null;
      return;
    }
    const refDoc = doc(db, 'users', usr.uid);
    const stopSnap = onSnapshot(refDoc, (snap) => {
      currentUser.value = snap.exists() ? snap.data() : null;
    });
    onUnmounted(stopSnap);
  });
  onUnmounted(stopAuth);
  return { currentUser };
}
