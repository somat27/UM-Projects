<template>
  <main class="platform-rating">
    <div class="rating-header">
      <h1 class="rating-title">Avalie a Plataforma EyesEverywhere</h1>
      <p class="rating-subtitle">
        A sua opinião é importante para melhorarmos continuamente.
      </p>
    </div>

    <div class="rating-container">
      <div class="rating-form">
        <div class="rating-slider-container">
          <label for="rating-slider">Avaliação ({{ rating }}%)</label>
          <input
            type="range"
            id="rating-slider"
            class="rating-slider"
            v-model="rating"
            min="0"
            max="100"
            step="1"
          />
          <div class="rating-labels">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        <div class="feedback-container">
          <label for="feedback-text">Deixe o seu comentário:</label>
          <textarea
            id="feedback-text"
            class="feedback-textarea"
            v-model="feedback"
            placeholder="Partilhe a sua experiência com a plataforma..."
            rows="5"
          ></textarea>
        </div>

        <button
          class="submit-button"
          @click="submitFeedback"
          :disabled="submitting"
          :class="{ success: submitSuccess, error: submitError }"
        >
          {{ buttonText }}
        </button>
      </div>
    </div>
  </main>
</template>

<script>
import { saveFeedback } from "@/services/firebase";

export default {
  name: "PlatformRating",
  data() {
    return {
      rating: 50,
      feedback: "",
      submitting: false,
      submitSuccess: false,
      submitError: false,
      buttonText: "Submeter Avaliação",
    };
  },
  methods: {
    async submitFeedback() {
      if (this.submitting) return;
      this.submitting = true;
      this.buttonText = "A enviar...";

      const feedbackData = {
        rating: this.rating,
        feedback: this.feedback,
      };

      try {
        await saveFeedback(feedbackData);
        this.handleSubmitSuccess();
      } catch (error) {
        console.error("Erro ao submeter feedback:", error);
        this.handleSubmitError();
      }
    },

    handleSubmitSuccess() {
      this.submitSuccess = true;
      this.buttonText = "Avaliação Submetida com Sucesso!";

      setTimeout(() => {
        this.$router.push("/");
      }, 2000);
    },

    handleSubmitError() {
      this.submitting = false;
      this.submitError = true;
      this.buttonText = "Erro na submissão. Tente novamente.";

      setTimeout(() => {
        this.submitError = false;
        this.buttonText = "Submeter Avaliação";
      }, 3000);
    },
  },
};
</script>

<style scoped>
.platform-rating {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
  margin-top: 75px;
}

.rating-header {
  text-align: center;
  margin-bottom: 40px;
}

.rating-title {
  color: #204c6d;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
}

.rating-subtitle {
  color: #555;
  font-size: 16px;
}

.rating-container {
  background-color: #f5f5f5;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rating-slider-container {
  margin-bottom: 25px;
}

.rating-slider-container label {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
  color: #204c6d;
}

.rating-slider {
  width: 100%;
  height: 8px;
  background: #d9d9d9;
  border-radius: 4px;
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.rating-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: #204c6d;
  border-radius: 50%;
  cursor: pointer;
}

.rating-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 14px;
  color: #666;
}

.feedback-container {
  margin-bottom: 25px;
}

.feedback-container label {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
  color: #204c6d;
}

.feedback-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.feedback-textarea:focus {
  outline: none;
  border-color: #204c6d;
}

.submit-button {
  background-color: #204c6d;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.submit-button:hover:not(:disabled) {
  background-color: #183a54;
}

.submit-button:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

.submit-button.success {
  background-color: #4caf50;
}

.submit-button.error {
  background-color: #f44336;
}

@media (max-width: 640px) {
  .platform-rating {
    padding: 20px;
  }

  .rating-title {
    font-size: 24px;
  }

  .rating-container {
    padding: 20px;
  }
}
</style>
