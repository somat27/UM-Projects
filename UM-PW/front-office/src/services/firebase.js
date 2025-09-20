// services/firebase.js
import { initializeApp } from "firebase/app";
import {
  getFirestore,
  collection,
  addDoc,
  updateDoc,
  doc,
  getDocs,
  getDoc,
  serverTimestamp,
  query,
  where,
} from "firebase/firestore";

import uploadToCloudinary from "./cloudinary";

// Configuração do Firebase
const firebaseConfig = {
  apiKey: "AIzaSyDfrWf9cajeBe7BVT7PWT5nBOWj7gPDBiw",
  authDomain: "pw-g201.firebaseapp.com",
  projectId: "pw-g201",
  storageBucket: "pw-g201.firebasestorage.app",
  messagingSenderId: "858778948795",
  appId: "1:858778948795:web:8bb0688f9713fec265c59e",
  measurementId: "G-JWNEDZWNTX",
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export async function submitOcorrencia(formData) {
  try {
    const ocorrenciaData = {
      dataSubmissao: serverTimestamp(),
      descricao: formData.observations || "",
      endereco: formData.address || "",
      imagemVideo: [],
      status: "Pendente",
      tipoOcorrencia: formData.selectedCategory || "",
      coordenadas: formData.userLocation
        ? {
            latitude: formData.userLocation.lat,
            longitude: formData.userLocation.lng,
          }
        : { latitude: 0, longitude: 0 },
    };

    const docRef = await addDoc(collection(db, "ocorrencias"), ocorrenciaData);
    console.log("Ocorrência registrada com ID:", docRef.id);

    // Se houver arquivos, faz o upload para o Cloudinary
    if (formData.files && formData.files.length > 0) {
      const uploadPromises = formData.files.map((file) =>
        uploadToCloudinary(file)
      ); // Faz upload de todas as imagens

      const fileUrls = await Promise.all(uploadPromises); // Aguarda todos os uploads serem concluídos

      // Atualiza o Firestore com o array de URLs das imagens
      await updateDoc(doc(db, "ocorrencias", docRef.id), {
        imagemVideo: fileUrls.filter((url) => url !== null), // Filtra URLs inválidas
      });

      console.log("Imagens salvas no Firestore:", fileUrls);
    }

    return { success: true, id: docRef.id };
  } catch (error) {
    console.error("Erro ao registrar ocorrência:", error);
    return { success: false, error: error.message };
  }
}

export async function getOcorrencias() {
  try {
    const querySnapshot = await getDocs(collection(db, "ocorrencias"));
    const ocorrencias = [];

    querySnapshot.forEach((doc) => {
      const data = doc.data();
      if (data.dataSubmissao) {
        data.dataSubmissao = data.dataSubmissao.toDate();
      }
      ocorrencias.push({
        id: doc.id,
        ...data,
      });
    });

    return ocorrencias;
  } catch (error) {
    console.error("Erro ao buscar ocorrências:", error);
    return [];
  }
}

export async function getEstatisticas() {
  try {
    const estatisticas = {
      ocorrenciasResolvidas: 0,
      auditoriasRealizadas: 0,
      tempoMedioResolucao: 0,
      mediaAvaliacoes: 0,
    };

    try {
      const ocorrenciasResolvidasQuery = query(
        collection(db, "ocorrencias"),
        where("status", "==", "Resolvido")
      );
      const resolvidasSnapshot = await getDocs(ocorrenciasResolvidasQuery);
      estatisticas.ocorrenciasResolvidas = resolvidasSnapshot.size;
    } catch (err) {
      estatisticas.ocorrenciasResolvidas = 0;
    }

    const auditoriasRef = collection(db, "auditorias");
    const auditoriasSnapshot = await getDocs(auditoriasRef);
    estatisticas.auditoriasRealizadas = auditoriasSnapshot.size;

    let totalOcorrencias = 0;
    let totalTempoResolucao = 0;

    for (const docAuditoria of auditoriasSnapshot.docs) {
      try {
        const auditoria = docAuditoria.data();
        const auditoriaId = docAuditoria.id;

        if (!auditoria.dataFim) {
          continue;
        }

        let dataFim;
        if (
          auditoria.dataFim.toDate &&
          typeof auditoria.dataFim.toDate === "function"
        ) {
          dataFim = auditoria.dataFim.toDate();
        } else if (auditoria.dataFim instanceof Date) {
          dataFim = auditoria.dataFim;
        } else if (
          typeof auditoria.dataFim === "number" ||
          typeof auditoria.dataFim === "string"
        ) {
          dataFim = new Date(auditoria.dataFim);
        } else {
          continue;
        }

        if (!dataFim || isNaN(dataFim.getTime())) {
          continue;
        }

        const ocorrenciaSnap = await getDoc(
          doc(db, "ocorrencias", auditoriaId)
        );

        if (!ocorrenciaSnap.exists()) {
          continue;
        }

        const ocorrencia = ocorrenciaSnap.data();

        // Verifica se a ocorrência está resolvida
        if (ocorrencia.status !== "Resolvido") {
          continue;
        }

        // Verifica se dataSubmissao existe
        if (!ocorrencia.dataSubmissao) {
          continue;
        }

        let dataSubmissao;
        if (
          ocorrencia.dataSubmissao.toDate &&
          typeof ocorrencia.dataSubmissao.toDate === "function"
        ) {
          dataSubmissao = ocorrencia.dataSubmissao.toDate();
        } else if (ocorrencia.dataSubmissao instanceof Date) {
          dataSubmissao = ocorrencia.dataSubmissao;
        } else if (
          typeof ocorrencia.dataSubmissao === "number" ||
          typeof ocorrencia.dataSubmissao === "string"
        ) {
          dataSubmissao = new Date(ocorrencia.dataSubmissao);
        } else {
          continue;
        }

        if (!dataSubmissao || isNaN(dataSubmissao.getTime())) {
          continue;
        }

        const diffMs = dataFim.getTime() - dataSubmissao.getTime();

        // Converte para dias
        const diffDias = diffMs / (1000 * 60 * 60 * 24);

        if (isNaN(diffDias) || diffDias < 0) {
          continue;
        }

        totalTempoResolucao += diffDias;
        totalOcorrencias++;
      } catch (err) {
        throw Error;
      }
    }

    // Calcula o tempo médio de resolução
    if (totalOcorrencias > 0) {
      estatisticas.tempoMedioResolucao = Math.round(
        totalTempoResolucao / totalOcorrencias
      );
    } else {
      estatisticas.tempoMedioResolucao = 0;
    }

    // Cálculo da média de avaliações
    try {
      const feedbacksRef = collection(db, "feedback");
      const feedbacksSnapshot = await getDocs(feedbacksRef);

      let totalRating = 0;
      let totalFeedbacks = 0;

      feedbacksSnapshot.forEach((doc) => {
        const feedback = doc.data();
        const avaliacao = Number(feedback.avaliacao);
        if (!isNaN(avaliacao)) {
          totalRating += avaliacao;
          totalFeedbacks++;
        }
      });

      estatisticas.mediaAvaliacoes =
        totalFeedbacks > 0 ? Math.round(totalRating / totalFeedbacks) : 0;
    } catch (err) {
      estatisticas.mediaAvaliacoes = 0;
    }

    return estatisticas;
  } catch (error) {
    return {
      ocorrenciasResolvidas: 0,
      auditoriasRealizadas: 0,
      tempoMedioResolucao: 0,
      mediaAvaliacoes: 0,
      error: error.message,
    };
  }
}

export const saveFeedback = async (feedbackData) => {
  try {
    // Adiciona timestamp do servidor e formata os dados
    const dataToSave = {
      avaliacao: feedbackData.rating,
      comentario: feedbackData.feedback,
      data: serverTimestamp(),
    };

    const feedbackRef = collection(db, "feedback");
    const docRef = await addDoc(feedbackRef, dataToSave);

    console.log("Feedback salvo com sucesso com ID:", docRef.id);
    return docRef;
  } catch (error) {
    console.error("Erro ao salvar feedback:", error);
    throw error;
  }
};
