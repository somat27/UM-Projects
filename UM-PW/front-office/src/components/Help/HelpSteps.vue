<template>
  <article class="step-container" ref="stepContainer">
    <div v-if="stepPosition === 'left'" class="step-content">
      <div class="step-number-container" v-html="stepNumberSvg"></div>
      <div class="step-info">
        <h3 class="step-title">{{ title }}</h3>
        <p
          v-for="(line, index) in descriptionLines"
          :key="index"
          class="step-description"
        >
          {{ line }}
        </p>
      </div>
      <img v-if="image" :src="image" alt="" class="step-image" />
    </div>

    <div
      v-else-if="stepPosition === 'right'"
      class="step-content"
      :class="'right-position'"
    >
      <!-- Agora a imagem grande aparece antes do texto -->
      <img v-if="image" :src="image" alt="" class="step-image" />

      <div class="step-info">
        <h3 class="step-title">{{ title }}</h3>
        <p
          v-for="(line, index) in descriptionLines"
          :key="index"
          class="step-description"
        >
          {{ line }}
        </p>
      </div>

      <div class="step-number-container" v-html="stepNumberSvg"></div>
    </div>

    <div v-else class="step-content">
      <div class="step-number-container" v-html="stepNumberSvg"></div>
      <div class="step-info">
        <h3 class="step-title">{{ title }}</h3>
        <p
          v-for="(line, index) in descriptionLines"
          :key="index"
          class="step-description"
        >
          {{ line }}
        </p>
      </div>
      <img
        v-if="smallImage"
        :src="smallImage"
        alt=""
        class="step-image-small"
      />
    </div>

    <!-- Progresso visual para conectar os steps -->
    <div v-if="number < 6" class="step-progress"></div>
  </article>
</template>

<script>
export default {
  name: "HelpSteps",
  props: {
    number: {
      type: Number,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    description: {
      type: [String, Array],
      required: true,
    },
    image: {
      type: String,
      default: null,
    },
    smallImage: {
      type: String,
      default: null,
    },
    stepPosition: {
      type: String,
      default: "left",
      validator: (value) => ["left", "right", "center"].includes(value),
    },
  },
  data() {
    return {
      isVisible: false,
    };
  },
  mounted() {
    window.addEventListener("scroll", this.checkVisibility);
    this.checkVisibility();
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.checkVisibility);
  },
  methods: {
    checkVisibility() {
      if (this.$refs.stepContainer) {
        const rect = this.$refs.stepContainer.getBoundingClientRect();
        const isVisible =
          rect.top < window.innerHeight - 100 && rect.bottom >= 0;

        if (isVisible && !this.isVisible) {
          this.isVisible = true;
          this.$refs.stepContainer.classList.add("step-visible");
        }
      }
    },
  },
  computed: {
    descriptionLines() {
      return Array.isArray(this.description)
        ? this.description
        : [this.description];
    },
    stepNumberSvg() {
      return `<svg width="70" height="70" viewBox="0 0 70 70" fill="none" xmlns="http://www.w3.org/2000/svg" class="step-number">
        <circle cx="35" cy="35" r="35" fill="#204C6D"></circle>
        <text fill="white" xml:space="preserve" style="white-space: pre" font-family="Inter" font-size="30" font-weight="bold" letter-spacing="0em"><tspan x="${
          this.number > 9 ? "24" : "27"
        }" y="46">${this.number}</tspan></text>
      </svg>`;
    },
  },
};
</script>

<style scoped>
.step-container {
  margin-bottom: 60px;
  position: relative;
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.step-visible {
  opacity: 1;
  transform: translateY(0);
}

.step-content {
  display: flex;
  align-items: center;
  padding: 0 38px;
  position: relative;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.step-content:hover {
  background-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
}

.step-info {
  margin-left: 34px;
  flex-grow: 1;
  padding: 20px 0;
}

.step-title {
  color: #204c6d;
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 8px;
  transition: color 0.3s ease;
}

.step-content:hover .step-title {
  color: #153a56;
}

.step-description {
  color: #000;
  font-size: 20px;
  font-weight: 700;
  margin-top: 8px;
  transition: all 0.3s ease;
}

.step-content:hover .step-description {
  color: #333;
}

.step-image {
  width: 90px;
  height: 90px;
  object-fit: contain;
  margin-left: auto;
  margin-right: auto;
  transition: transform 0.3s ease;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.step-content:hover .step-image {
  transform: scale(1.1);
}

.step-image-small {
  width: 81px;
  height: 79px;
  object-fit: contain;
  transition: transform 0.3s ease;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.step-content:hover .step-image-small {
  transform: scale(1.1);
}

.step-number-container {
  transition: transform 0.3s ease;
}

.step-content:hover .step-number-container {
  transform: rotate(10deg) scale(1.05);
}

/* Linha de progresso conectando os passos */
.step-progress {
  position: absolute;
  left: 35px;
  bottom: -60px;
  width: 4px;
  height: 60px;
  background: linear-gradient(to bottom, #204c6d, #79a8c9);
  z-index: 1;
}

.step-content.right-position .step-info {
  text-align: right;
  margin-right: 30px;
}

.step-content.right-position .step-number-container {
  margin-left: auto;
}

.step-content.right-position .step-image {
  margin-left: 0;
  margin-right: auto;
}

@media (max-width: 991px) {
  .step-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 20px;
  }

  .step-info {
    margin: 16px 0;
  }

  .step-image,
  .step-image-small {
    margin: 16px 0;
  }

  .step-progress {
    left: 50%;
    transform: translateX(-50%);
  }
}

@media (max-width: 640px) {
  .step-title {
    font-size: 24px;
  }

  .step-description {
    font-size: 16px;
  }
}

/* Animação para o número pulsar */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.step-content:hover :deep(.step-number) circle {
  animation: pulse 1s infinite;
  transform-origin: center;
}
</style>
