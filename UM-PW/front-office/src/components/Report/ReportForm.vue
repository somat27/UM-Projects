<template>
  <section
    class="container mt-6 fade-in"
    style="margin-top: 150px; margin-bottom: 50px"
  >
    <div class="card shadow p-4 slide-up">
      <h1 class="text-center pulse" style="color: #204c6d; font-weight: bold">
        Reportar uma Ocorrência
      </h1>

      <p class="text-center text-muted fade-in-delay">
        Ajude a melhorar a cidade! Preencha os dados abaixo para registrar o
        problema.
      </p>

      <div class="mb-3 fade-in-delay-1">
        <label class="form-label">Categoria</label>
        <select v-model="selectedCategory" class="form-select hover-effect">
          <option value="" disabled selected>Selecione uma categoria</option>
          <option value="roads">Vias e Passeios</option>
          <option value="lights">Iluminação Pública</option>
          <option value="sinals">Sinalização em Falta</option>
        </select>
      </div>

      <div class="mb-3 fade-in-delay-2">
        <h2 class="h5">Localização</h2>
        <p class="text-muted">
          Selecione a localização do incidente (no mapa ou insira o endereço)
        </p>
        <div class="map-container">
          <div id="map" class="border rounded shadow-sm map-fade-in"></div>
        </div>
      </div>

      <div class="mb-3 fade-in-delay-3">
        <label class="form-label">Endereço</label>
        <div class="input-group">
          <input
            v-model="address"
            class="form-control hover-effect"
            placeholder="Digite o endereço do incidente"
            :class="{ filled: address }"
            @keyup.enter="searchAddress"
          />
          <button
            class="btn btn-outline-primary"
            @click="searchAddress"
            :disabled="!address"
          >
            <i class="bi bi-search"></i>
          </button>
        </div>
        <small class="text-muted" v-if="isSearching">
          <i class="bi bi-hourglass-split"></i> Buscando endereço...
        </small>
        <small class="text-success" v-if="lastSearchSuccess">
          <i class="bi bi-geo-alt-fill"></i> Endereço localizado no mapa!
        </small>
        <small class="text-danger" v-if="searchError">
          <i class="bi bi-exclamation-triangle"></i> {{ searchError }}
        </small>
      </div>

      <div class="mb-3 fade-in-delay-4">
        <label class="form-label">Observações</label>
        <textarea
          v-model="observations"
          class="form-control hover-effect"
          placeholder="Descreva o problema (máximo 100 palavras)"
          maxlength="500"
          :class="{ filled: observations }"
        ></textarea>
        <small
          class="text-muted float-end mt-1 character-count"
          v-if="observations"
        >
          {{
            observations.split(" ").filter((word) => word.length > 0).length
          }}/100 palavras
        </small>
      </div>

      <div class="mb-3 fade-in-delay-5">
        <label class="form-label">Anexos</label>
        <div class="file-upload-container">
          <input
            type="file"
            ref="fileInput"
            class="form-control hover-effect file-input"
            @change="handleFileUpload"
            accept="image/*,video/*"
            multiple
            id="file-upload"
          />
          <label for="file-upload" class="file-upload-label">
            <i class="bi bi-cloud-upload"></i> Selecionar Arquivos
          </label>
        </div>
        <transition name="fade">
          <div v-if="uploadedFiles.length" class="mt-2 text-muted file-list">
            <div class="file-preview">
              Arquivos selecionados:
              {{ uploadedFiles.map((file) => file.name).join(", ") }}
            </div>
          </div>
        </transition>
      </div>

      <button
        @click="submitForm"
        class="btn btn-primary w-100 submit-button"
        :disabled="!isFormValid"
        :class="{ 'button-pulse': isFormValid }"
      >
        <i class="bi bi-send-fill"></i> Submeter
      </button>
    </div>
  </section>
</template>

<script>
import { submitOcorrencia } from "@/services/firebase";

export default {
  name: "ReportForm",
  props: {
    defaultCategory: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      map: null,
      geocoder: null,
      selectedCategory: this.defaultCategory,
      address: "",
      observations: "",
      uploadedFiles: [],
      userLocation: null,
      mapInitialized: false,
      isSubmitting: false,
      isSearching: false,
      lastSearchSuccess: false,
      searchError: null,
      google: null,
    };
  },
  computed: {
    isFormValid() {
      return this.selectedCategory && this.address && this.userLocation;
    },
    googleMapsApiUrl() {
      // Removida a biblioteca marker, utilizando apenas places
      return `https://maps.googleapis.com/maps/api/js?key=${process.env.VUE_APP_API_KEY}&libraries=places&callback=initGoogleCallback`;
    },
  },
  mounted() {
    window.initGoogleCallback = this.initMapAfterLoad;

    // efeito suave
    setTimeout(() => {
      this.loadGoogleMapsAPI();
    }, 300);
  },
  methods: {
    loadGoogleMapsAPI() {
      if (typeof window !== "undefined" && !window.google) {
        const script = document.createElement("script");
        script.src = this.googleMapsApiUrl;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
      } else if (window.google && !this.mapInitialized) {
        this.initMapAfterLoad();
      }
    },
    initMapAfterLoad() {
      if (window.google) {
        this.google = window.google;
        this.initMap();
      }
    },
    initMap() {
      if (
        typeof window !== "undefined" &&
        document.getElementById("map") &&
        !this.mapInitialized &&
        this.google
      ) {
        // Coordenadas iniciais
        const cord_inicial = { lat: 41.442726, lng: -8.291696 };

        this.map = new this.google.maps.Map(document.getElementById("map"), {
          center: cord_inicial,
          zoom: 13,
          mapTypeControl: true,
          streetViewControl: false,
          fullscreenControl: true,
          zoomControl: true,
        });

        this.geocoder = new this.google.maps.Geocoder();

        this.map.addListener("click", (e) => {
          this.onMapClick(e);
        });

        setTimeout(() => {
          this.map.setZoom(14);
        }, 500);

        this.mapInitialized = true;
      }
    },
    onMapClick(e) {
      const lat = e.latLng.lat();
      const lng = e.latLng.lng();



      this.reverseGeocode(lat, lng);
    },

    removeMapMarker() {
      if (this.marker) {
        this.marker.setMap(null);
        this.marker = null;
      }
    },

    async searchAddress() {
      if (!this.address) return;

      this.isSearching = true;
      this.lastSearchSuccess = false;
      this.searchError = null;

      try {
        const result = await this.geocodeAddress(this.address);

        if (result) {
          this.updateMapMarker(result.lat, result.lng);
          this.lastSearchSuccess = true;

          const addressInput = document.querySelector(
            'input[v-model="address"]'
          );
          if (addressInput) {
            addressInput.classList.add("success-input");
            setTimeout(() => {
              addressInput.classList.remove("success-input");
            }, 1500);
          }
        } else {
          this.searchError =
            "Endereço não encontrado, tente ser mais específico";
        }
      } catch (error) {
        console.error("Erro ao buscar endereço:", error);
        this.searchError = "Erro ao buscar o endereço. Tente novamente.";
      } finally {
        this.isSearching = false;
      }
    },

    async geocodeAddress(address) {
      return new Promise((resolve) => {
        if (!this.geocoder) {
          resolve(null);
          return;
        }

        // Adicionar 'Portugal' ao final da pesquisa para melhorar a precisão
        const searchQuery = `${address}, Portugal`;

        this.geocoder.geocode({ address: searchQuery }, (results, status) => {
          if (status === "OK" && results && results.length > 0) {
            const location = results[0].geometry.location;
            resolve({
              lat: location.lat(),
              lng: location.lng(),
              displayName: results[0].formatted_address,
            });
          } else {
            resolve(null);
          }
        });
      });
    },

    async reverseGeocode(lat, lng) {
      try {
        if (!this.geocoder) return;

        this.isSearching = true;

        const latlng = { lat, lng };

        this.geocoder.geocode({ location: latlng }, (results, status) => {
          if (status === "OK" && results && results.length > 0) {
            const addressComponents = results[0].address_components;

            const countryComponent = addressComponents.find(comp =>
              comp.types.includes("country")
            );

            if (countryComponent && countryComponent.long_name === "Portugal") {
              this.address = results[0].formatted_address;
              this.lastSearchSuccess = true;

              // ✅ Só atualiza o marcador se for em Portugal
              this.updateMapMarker(lat, lng);
            } else {
              this.address = "";
              this.lastSearchSuccess = false;

              // ❌ Remove marcador se estiver fora de Portugal
              this.removeMapMarker();
            }

          } else {
            this.address = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
            this.lastSearchSuccess = false;
            this.removeMapMarker();
          }

          this.isSearching = false;
        });
      } catch (error) {
        console.error("Erro na geocodificação reversa:", error);
        this.address = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        this.isSearching = false;
        this.lastSearchSuccess = false;
        this.removeMapMarker();
      }
    },



    updateMapMarker(lat, lng) {
      if (!this.google || !this.map) return;

      if (this.marker) {
        this.marker.setMap(null);
        this.marker = null;
      }

      try {
        const markerOptions = {
          position: { lat, lng },
          map: this.map,
          title: "Localização selecionada",
        };

        if (process.env.VUE_APP_MARKER_ICON) {
          markerOptions.icon = {
            url: process.env.VUE_APP_MARKER_ICON,
            scaledSize: new this.google.maps.Size(40, 40),
            origin: new this.google.maps.Point(0, 0),
            anchor: new this.google.maps.Point(20, 40),
          };
        }

        this.marker = new this.google.maps.Marker(markerOptions);

        this.map.setCenter({ lat, lng });
        this.map.setZoom(16);

        this.userLocation = { lat, lng };

        console.log("Novo marcador padrão criado em:", lat, lng);
      } catch (error) {
        console.error("Erro ao criar marcador:", error);
        alert(
          "Erro ao criar o marcador. Verifique o console para mais detalhes."
        );
      }
    },
    handleFileUpload(event) {
      const newFiles = Array.from(event.target.files);

      const validTypes = ["image/", "video/"];
      const filteredFiles = newFiles.filter((file) =>
        validTypes.some((type) => file.type.startsWith(type))
      );

      filteredFiles.forEach((file) => {
        const alreadyExists = this.uploadedFiles.some(
          (f) => f.name === file.name && f.size === file.size
        );
        if (!alreadyExists) {
          this.uploadedFiles.push(file);
        }
      });

      event.target.value = "";
    },
    async submitForm() {
      if (!this.isFormValid) {
        this.showValidationAnimation();
        return;
      }

      this.isSubmitting = true;

      const button = document.querySelector(".submit-button");
      button.classList.add("success-submit");
      button.innerHTML = '<i class="bi bi-hourglass-split"></i> Enviando...';

      const formData = {
        selectedCategory: this.selectedCategory,
        address: this.address,
        observations: this.observations,
        userLocation: this.userLocation,
        files: this.uploadedFiles,
      };
      console.log(formData.files);

      try {
        const result = await submitOcorrencia(formData);

        if (result.success) {
          console.log("Ocorrência enviada com sucesso! ID:", result.id);

          button.innerHTML =
            '<i class="bi bi-check-lg"></i> Enviado com Sucesso!';

          setTimeout(() => {
            this.$router.push("/");
          }, 1500); // 1.5 seg
        } else {
          throw new Error(result.error || "Erro ao enviar ocorrência");
        }
      } catch (error) {
        console.error("Erro ao processar formulário:", error);

        button.classList.remove("success-submit");
        button.classList.add("error-submit");
        button.innerHTML =
          '<i class="bi bi-exclamation-triangle"></i> Erro no envio!';

        setTimeout(() => {
          button.classList.remove("error-submit");
          button.innerHTML = '<i class="bi bi-send-fill"></i> Submeter';
          this.isSubmitting = false;
        }, 3000);
      }
    },
    showValidationAnimation() {
      const invalidFields = document.querySelectorAll(
        "select:invalid, input:invalid"
      );
      invalidFields.forEach((field) => {
        field.classList.add("shake-animation");
        setTimeout(() => {
          field.classList.remove("shake-animation");
        }, 500);
      });
    },
    resetForm() {
      this.selectedCategory = "";
      this.address = "";
      this.observations = "";
      this.uploadedFiles = [];
      this.userLocation = null;
      this.lastSearchSuccess = false;
      this.searchError = null;

      // Reset do botão
      const button = document.querySelector(".submit-button");
      button.classList.remove("success-submit");
      button.innerHTML = '<i class="bi bi-send-fill"></i> Submeter';

      // Limpa os marcadores do mapa
      if (this.marker) {
        this.marker.setMap(null);
        this.marker = null;
      }
    },
  },

  beforeUnmount() {
    if (window.initGoogleCallback) {
      delete window.initGoogleCallback;
    }

    if (this.marker) {
      this.marker.setMap(null);
      this.marker = null;
    }
  },
};
</script>

<style scoped>
.body {
  background-color: rgba(255, 255, 255, 1);
  display: flex;
  width: 100%;
  padding: 120px 80px 91px;
  flex-direction: column;
  align-items: center;
  font-family: Inter, -apple-system, Roboto, Helvetica, sans-serif;
}

/* Animações gerais */
.fade-in {
  animation: fadeIn 0.8s ease-in-out;
}

.fade-in-delay {
  animation: fadeIn 0.8s ease-in-out 0.2s forwards;
  opacity: 0;
}

.fade-in-delay-1 {
  animation: fadeIn 0.8s ease-in-out 0.3s forwards;
  opacity: 0;
}

.fade-in-delay-2 {
  animation: fadeIn 0.8s ease-in-out 0.4s forwards;
  opacity: 0;
}

.fade-in-delay-3 {
  animation: fadeIn 0.8s ease-in-out 0.5s forwards;
  opacity: 0;
}

.fade-in-delay-4 {
  animation: fadeIn 0.8s ease-in-out 0.6s forwards;
  opacity: 0;
}

.fade-in-delay-5 {
  animation: fadeIn 0.8s ease-in-out 0.7s forwards;
  opacity: 0;
}

.slide-up {
  animation: slideUp 0.6s ease-out;
}

.map-fade-in {
  animation: fadeIn 1s ease-in-out 0.5s forwards;
  opacity: 0.5;
}

.pulse {
  animation: pulse 1s ease-in-out;
}

/* Efeitos para interação */
.hover-effect {
  transition: all 0.3s ease;
  border: 1px solid rgba(32, 76, 109, 0.3);
}

.hover-effect:hover {
  border-color: rgba(32, 76, 109, 0.8);
  box-shadow: 0 0 5px rgba(32, 76, 109, 0.2);
  transform: translateY(-2px);
}

.hover-effect:focus {
  border-color: rgb(32, 76, 109);
  box-shadow: 0 0 8px rgba(32, 76, 109, 0.4);
  transform: translateY(-2px);
}

.filled {
  border-left: 3px solid rgb(32, 76, 109);
  transition: border-left 0.3s ease;
}

/* Upload de arquivos estilizado */
.file-upload-container {
  position: relative;
  overflow: hidden;
}

.file-input {
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.file-upload-label {
  display: block;
  padding: 12px;
  background-color: #f0f8ff;
  color: rgba(32, 76, 109, 1);
  text-align: center;
  border: 1px dashed rgba(32, 76, 109, 0.5);
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.file-upload-label:hover {
  background-color: rgba(32, 76, 109, 0.1);
  border-color: rgba(32, 76, 109, 0.8);
}

.file-preview {
  animation: fadeIn 0.5s ease-in-out;
}

/* Animação do botão de submissão */
.submit-button {
  transition: all 0.3s ease;
  background-color: rgba(32, 76, 109, 1);
  transform-origin: center;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(32, 76, 109, 0.3);
}

.button-pulse {
  animation: buttonPulse 2s infinite;
}

.success-submit {
  background-color: #28a745 !important;
  transform: scale(1.05);
}

.error-submit {
  background-color: #dc3545 !important;
}

/* Novo estilo para indicar sucesso na busca de endereço */
.success-input {
  border-color: #28a745 !important;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
  animation: successPulse 1s;
}

@keyframes successPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(40, 167, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(40, 167, 69, 0);
  }
}

.shake-animation {
  animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
  border-color: #dc3545 !important;
}

/* Contador de caracteres */
.character-count {
  transition: all 0.3s ease;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.03);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes buttonPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(32, 76, 109, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(32, 76, 109, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(32, 76, 109, 0);
  }
}

@keyframes shake {
  10%,
  90% {
    transform: translate3d(-1px, 0, 0);
  }
  20%,
  80% {
    transform: translate3d(2px, 0, 0);
  }
  30%,
  50%,
  70% {
    transform: translate3d(-2px, 0, 0);
  }
  40%,
  60% {
    transform: translate3d(2px, 0, 0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.map-container {
  max-width: 90%;
  margin: 0 auto;
  padding: 20px;
  transition: all 0.3s ease;
}

#map {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

#map:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* Responsividade */
@media (max-width: 768px) {
  .map-container {
    max-width: 95%;
    padding: 10px;
  }

  #map {
    height: 300px;
  }

  .fade-in-delay-1,
  .fade-in-delay-2,
  .fade-in-delay-3,
  .fade-in-delay-4,
  .fade-in-delay-5 {
    animation-delay: 0.2s;
  }
}

@media (max-width: 768px) {
  .body {
    padding: 100px 20px 60px;
  }
}
</style>
