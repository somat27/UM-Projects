<template>
  <article class="stat-card">
    <img :src="imageSrc" :alt="iconAlt" class="stat-icon" />
    <h3 class="stat-value">{{ displayValue }}</h3>
    <p class="stat-description">{{ description }}</p>
  </article>
</template>

<script>
export default {
  name: "StatCard",
  props: {
    imageSrc: {
      type: String,
      default: "/default-image.jpg",
    },
    iconAlt: {
      type: String,
      required: true,
    },
    value: {
      type: [String, Number],
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      displayValue: "0",
      animationStarted: false,
    };
  },
  methods: {
    animateValue() {
      const finalValue = parseInt(this.value) || 0;
      const duration = 2000; // 2 seg
      const startTime = Date.now();

      const updateValue = () => {
        const currentTime = Date.now();
        const elapsedTime = currentTime - startTime;

        if (elapsedTime < duration) {
          const currentValue = Math.floor(
            (elapsedTime / duration) * finalValue
          );
          this.displayValue = currentValue.toString();
          requestAnimationFrame(updateValue);
        } else {
          this.displayValue = this.value;
        }
      };

      updateValue();
    },
    checkVisibility() {
      if (!this.animationStarted) {
        const element = this.$el;
        const position = element.getBoundingClientRect();

        if (position.top < window.innerHeight && position.bottom >= 0) {
          this.animationStarted = true;
          this.animateValue();
        }
      }
    },
  },
  mounted() {
    window.addEventListener("scroll", this.checkVisibility);
    this.checkVisibility();
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.checkVisibility);
  },
  watch: {
    value() {
      this.animationStarted = false;
      this.checkVisibility();
    },
  },
};
</script>

<style scoped>
.stat-card {
  height: 200px;
  display: flex;
  align-items: center;
  position: relative;
  background-color: #d9d9d9;
  transition: all 0.3s ease;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.stat-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  transition: all 0.6s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  background-color: #e6e6e6;
}

.stat-card:hover::before {
  left: 100%;
}

@media (max-width: 991px) {
  .stat-card {
    width: 100%;
  }
}

.stat-icon {
  width: 151px;
  height: 151px;
  margin-left: 31px;
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.05) rotate(5deg);
}

.stat-value {
  font-size: 50px;
  font-weight: 700;
  position: absolute;
  right: 25px;
  top: 49px;
  margin: 0;
  transition: all 0.3s ease;
  color: #204c6d;
}

.stat-card:hover .stat-value {
  transform: scale(1.1);
  color: #153a56;
}

.stat-description {
  font-size: 20px;
  font-weight: 700;
  position: absolute;
  right: 25px;
  top: 121px;
  text-align: center;
  max-width: 411px;
  margin: 0;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-description {
  font-weight: 800;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card {
  animation: fadeIn 0.5s ease-out;
}
</style>
