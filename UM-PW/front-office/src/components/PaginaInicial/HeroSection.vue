<template>
  <section class="hero-section" ref="heroSection" @mousemove="handleParallax">
    <!-- Elementos de fundo interativos -->
    <div class="city-silhouette"></div>
    <div class="particle-container">
      <div
        v-for="n in 20"
        :key="`particle-${n}`"
        class="particle"
        :style="getRandomParticleStyle()"
      ></div>
    </div>

    <div
      class="reveal-mask"
      :style="{ transform: `scale(${revealScale})` }"
    ></div>

    <div class="hero-content">
      <h1 class="hero-title">{{ titleText }}</h1>

      <Transition name="clip-reveal" appear>
        <p class="hero-description">
          Reporte problemas urbanos e acompanhe a resolução em tempo real
        </p>
      </Transition>

      <div
        class="button-container"
        @click="activateRipple"
        @mousemove="moveButtonLight"
      >
        <div
          class="button-light"
          :style="{ left: buttonLightX + 'px', top: buttonLightY + 'px' }"
        ></div>
        <button class="cta-button" @click="goToReportPage">
          <span class="button-text">Reportar Incidente</span>
          <span class="button-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M5 12h14"></path>
              <path d="m12 5 7 7-7 7"></path>
            </svg>
          </span>
        </button>
        <div
          v-for="(ripple, index) in ripples"
          :key="`ripple-${index}`"
          class="ripple"
          :style="{
            left: ripple.x + 'px',
            top: ripple.y + 'px',
            animationPlayState: ripple.active ? 'running' : 'paused',
          }"
        ></div>
      </div>
    </div>

    <!-- Indicador de scroll -->
    <div class="scroll-indicator">
      <div class="scroll-dot"></div>
    </div>
  </section>
</template>

<script>
import heroBackground from "@/assets/PaginaInicial/HeroImage.jpg";

export default {
  name: "HeroSection",
  data() {
    return {
      heroBackground,
      titleText: "Ajude a melhorar a nossa cidade!",
      mouseX: 0,
      mouseY: 0,
      buttonLightX: 50,
      buttonLightY: 50,
      ripples: [],
      revealScale: 0,
      isLoaded: false,
    };
  },
  computed: {
    titleChars() {
      return this.titleText.split("");
    },
  },
  mounted() {
    window.addEventListener("scroll", this.handleScroll);
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
  },
  methods: {
    handleParallax(e) {
      const rect = this.$refs.heroSection.getBoundingClientRect();
      this.mouseX = (e.clientX - rect.left) / rect.width;
      this.mouseY = (e.clientY - rect.top) / rect.height;
    },
    getRandomParticleStyle() {
      const size = Math.floor(Math.random() * 10) + 5;
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      const duration = Math.random() * 20 + 10;
      const delay = Math.random() * 5;

      return {
        width: `${size}px`,
        height: `${size}px`,
        left: `${x}%`,
        top: `${y}%`,
        animationDuration: `${duration}s`,
        animationDelay: `${delay}s`,
        opacity: Math.random() * 0.5 + 0.1,
      };
    },
    moveButtonLight(e) {
      const button = e.currentTarget;
      const rect = button.getBoundingClientRect();
      this.buttonLightX = e.clientX - rect.left;
      this.buttonLightY = e.clientY - rect.top;
    },
    activateRipple(e) {
      const button = e.currentTarget;
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Criar nova ondulação
      const newRipple = {
        x,
        y,
        active: true,
        id: Date.now(),
      };

      this.ripples.push(newRipple);

      // Remover ondulação após a animação
      setTimeout(() => {
        this.ripples = this.ripples.filter((r) => r.id !== newRipple.id);
      }, 2000);
    },
    handleScroll() {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;
      const opacity = 1 - Math.min(scrollTop / 200, 1);

      if (this.$refs.heroSection) {
        this.$refs.heroSection.style.opacity = opacity;
        this.$refs.heroSection.style.transform = `translateY(${
          scrollTop * 0.5
        }px)`;
      }
    },
    goToReportPage() {
      this.$router.push("/report");
    },
  },
};
</script>

<style scoped>
.hero-section {
  height: 800px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  overflow: hidden;
  transition: opacity 0.5s ease, transform 0.2s ease;
  padding-top: 75px;
}

.hero-section::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("@/assets/PaginaInicial/HeroImage.jpg");
  background-size: cover;
  background-position: center;
  opacity: 0.7;
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 4;
}

.reveal-mask {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 150vw;
  height: 150vh;
  background: radial-gradient(circle, transparent 30%, rgba(0, 0, 0, 0.9) 70%);
  transform: translate(-50%, -50%) scale(0);
  z-index: 3;
  transition: transform 1.8s cubic-bezier(0.19, 1, 0.22, 1);
  pointer-events: none;
}

.hero-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  position: relative;
  z-index: 4;
}

.hero-title {
  color: #204c6d;
  font-size: 90px;
  text-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
  max-width: 1000px;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  animation: titleReveal 1.5s ease-out forwards;
}

@keyframes titleReveal {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-description {
  color: #fff;
  font-size: 30px;
  backdrop-filter: blur(2px);
  background-color: rgba(32, 76, 109, 0.3);
  padding: 12px 24px;
  border-radius: 10px;
  margin: 0;
  position: relative;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.button-container {
  position: relative;
  margin-top: 20px;
  overflow: hidden;
  border-radius: 50px;
  z-index: 5;
}

.cta-button {
  color: #fff;
  font-size: 40px;
  padding: 16px 40px;
  border-radius: 50px;
  border: none;
  cursor: pointer;
  backdrop-filter: blur(2px);
  min-width: 484px;
  background-color: #204c6d;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  position: relative;
  z-index: 6;
  overflow: hidden;
  transition: transform 0.4s cubic-bezier(0.19, 1, 0.22, 1);
}

.cta-button:hover {
  transform: translateY(-4px);
}

.cta-button:active {
  transform: translateY(2px);
}

.button-text {
  position: relative;
  z-index: 7;
}

.button-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: bounceRight 2s ease-in-out infinite;
}

@keyframes bounceRight {
  0%,
  100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(6px);
  }
}

.button-light {
  position: absolute;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.8) 0%,
    rgba(255, 255, 255, 0) 70%
  );
  transform: translate(-50%, -50%);
  pointer-events: none;
  opacity: 0;
  z-index: 5;
  transition: opacity 0.3s ease;
}

.button-container:hover .button-light {
  opacity: 0.5;
}

.ripple {
  position: absolute;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(0);
  animation: rippleEffect 2s cubic-bezier(0.19, 1, 0.22, 1) forwards;
  pointer-events: none;
  z-index: 4;
}

@keyframes rippleEffect {
  0% {
    width: 0;
    height: 0;
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(0);
  }
  100% {
    width: 500px;
    height: 500px;
    opacity: 0;
    transform: translate(-50%, -50%) scale(1);
  }
}

/* Indicador de scroll */
.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 50px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 15px;
  display: flex;
  justify-content: center;
  padding-top: 6px;
  z-index: 5;
}

.scroll-dot {
  width: 8px;
  height: 8px;
  background-color: white;
  border-radius: 50%;
  animation: scrollAnim 2s ease-in-out infinite;
}

@keyframes scrollAnim {
  0%,
  100% {
    transform: translateY(0);
    opacity: 1;
  }
  50% {
    transform: translateY(20px);
    opacity: 0.2;
  }
}
</style>
