<template>
  <main class="step-guide">
    <div class="guide-header">
      <h1 class="guide-title">Ajuda - Como Reportar uma Ocorrência</h1>
      <div class="guide-progress">
        <div
          v-for="step in 6"
          :key="step"
          class="progress-item"
          :class="{ active: currentStep >= step }"
          @click="scrollToStep(step)"
        >
          {{ step }}
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: progressWidth + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <section class="guide-content" ref="guideContent">
      <Step
        ref="step1"
        :number="1"
        title="Passo 1: Aceder à Plataforma"
        :description="[
          'Abra o site da EyesEverywhere através do seu navegador',
        ]"
        :image="require('@/assets/HelpImages/step1.jpg')"
        stepPosition="right"
      />

      <Step
        ref="step2"
        :number="2"
        title="Passo 2: Criar uma Nova Ocorrência"
        :description="[
          'No ecrã inicial, clique no botão Reportar Incidente',
          'Identifique o tipo de Ocorrência',
        ]"
        :image="require('@/assets/HelpImages/step2.jpg')"
        stepPosition="left"
      />

      <Step
        ref="step3"
        :number="3"
        title="Passo 3: Identificar a localização da mesma"
        :description="[
          'Selecione um ponto no mapa ou digite a morada manualmente',
        ]"
        :image="require('@/assets/HelpImages/step3.jpg')"
        stepPosition="right"
      />

      <Step
        ref="step4"
        :number="4"
        title="Passo 4: Criar uma descrição"
        :description="['Escreva uma breve descrição do problema.']"
        :image="require('@/assets/HelpImages/step4.jpg')"
        stepPosition="left"
      />

      <Step
        ref="step5"
        :number="5"
        title="Passo 5: Submeter imagens ou vídeos"
        :description="[
          'Arraste ou carregue os arquivos de forma a comprovar a sua ocorrência',
        ]"
        :image="require('@/assets/HelpImages/step5.jpg')"
        stepPosition="right"
      />

      <Step
        ref="step6"
        :number="6"
        title="Passo 6: Submeter a Ocorrência"
        :description="[
          'Revise as informações e clique em Reportar.',
          'A ocorrência será enviada para análise pela equipa responsável.',
        ]"
        :image="require('@/assets/HelpImages/step6.jpg')"
        stepPosition="left"
      />
    </section>
  </main>
</template>

<script>
import Step from "./HelpSteps.vue";

export default {
  name: "StepGuide",
  components: {
    Step,
  },
  data() {
    return {
      currentStep: 1,
      scrolling: false,
      progressWidth: 16.66,
    };
  },
  mounted() {
    window.addEventListener("scroll", this.handleScroll);
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
  },
  methods: {
    handleScroll() {
      if (this.scrolling) return;

      for (let i = 1; i <= 6; i++) {
        const stepRef = this.$refs[`step${i}`];
        if (stepRef && stepRef.$el) {
          const rect = stepRef.$el.getBoundingClientRect();

          if (
            rect.top <= window.innerHeight * 0.5 &&
            rect.bottom >= window.innerHeight * 0.3
          ) {
            this.currentStep = i;
            this.progressWidth = i * 16.66;
            break;
          }
        }
      }
    },
    scrollToStep(step) {
      if (this.$refs[`step${step}`]) {
        this.scrolling = true;
        this.currentStep = step;
        this.progressWidth = step * 16.66;

        this.$refs[`step${step}`].$el.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });

        setTimeout(() => {
          this.scrolling = false;
        }, 1000);
      }
    },
    scrollToNext() {
      if (this.currentStep < 6) {
        this.scrollToStep(this.currentStep + 1);
      }
    },
    scrollToPrev() {
      if (this.currentStep > 1) {
        this.scrollToStep(this.currentStep - 1);
      }
    },
  },
};
</script>

<style scoped>
.step-guide {
  padding: 53px 179px;
  flex-grow: 1;
  margin-top: 75px;
}

.guide-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 20px 0;
  backdrop-filter: blur(5px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.guide-title {
  color: #204c6d;
  font-size: 50px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 20px;
}

.guide-progress {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  padding: 0 20px;
}

.progress-item {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #d9d9d9;
  color: #666;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.progress-item.active {
  background-color: #204c6d;
  color: white;
  transform: scale(1.1);
}

.progress-bar {
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: #d9d9d9;
  transform: translateY(-50%);
  z-index: 1;
}

.progress-fill {
  height: 100%;
  background-color: #204c6d;
  transition: width 0.5s ease;
}

.guide-content {
  padding: 58px 0;
  border-radius: 8px;
  background-color: #d9d9d9;
  margin-top: 30px;
  position: relative;
}

.guide-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding: 0 38px;
}

.nav-button {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #204c6d;
  background-color: transparent;
  color: #204c6d;
}

.nav-button:hover:not(:disabled) {
  background-color: rgba(32, 76, 109, 0.1);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 991px) {
  .step-guide {
    padding: 32px;
  }

  .guide-content {
    padding: 32px 16px;
  }

  .guide-title {
    font-size: 38px;
  }

  .progress-item {
    width: 30px;
    height: 30px;
    font-size: 14px;
  }
}

@media (max-width: 640px) {
  .guide-title {
    font-size: 32px;
  }

  .guide-progress {
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }

  .progress-bar {
    display: none;
  }

  .nav-button {
    padding: 10px 16px;
    font-size: 14px;
  }
}
</style>
