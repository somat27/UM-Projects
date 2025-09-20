const CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/do5hfydb2/upload";
const UPLOAD_PRESET = "EyesEveryWhere";

async function uploadToCloudinary(file) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("upload_preset", UPLOAD_PRESET);

  try {
    const response = await fetch(CLOUDINARY_URL, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Erro no upload: ${response.statusText}`);
    }

    const data = await response.json();
    return data.secure_url; // Retorna a URL do arquivo no Cloudinary
  } catch (error) {
    console.error("Erro ao enviar para Cloudinary:", error);
    return null;
  }
}

export default uploadToCloudinary;
