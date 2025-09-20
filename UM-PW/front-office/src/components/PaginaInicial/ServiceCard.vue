<template>
  <article class="service-card">
    <h2 class="card-title">{{ title }}</h2>
    <img
      :src="imageSrc"
      :alt="imageAlt || 'Imagem do serviço'"
      class="card-icon"
    />
    <p class="card-description">{{ description }}</p>
    <button class="card-button">{{ buttonText }}</button>
  </article>
</template>

<script>
export default {
  name: "ServiceCard",
  props: {
    title: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    imageSrc: {
      type: String,
      default: "/default-image.jpg",
    },
    imageAlt: {
      type: String,
      default: "Imagem do serviço",
    },
    buttonText: {
      type: String,
      default: "Reportar",
    },
  },
};
</script>

<style scoped>
.service-card {
  width: 312px;
  padding: 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 20px;
  background-color: #d9d9d9;
  transition: all 0.3s ease;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.service-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  background-color: #e6e6e6;
}

@media (max-width: 640px) {
  .service-card {
    width: 100%;
  }
}

.card-title {
  font-size: 25px;
  font-weight: 700;
  min-height: 68px;
  margin: 0;
  transition: color 0.3s ease;
}

.service-card:hover .card-title {
  color: #204c6d;
}

.card-icon {
  width: 104px;
  height: 104px;
  transition: transform 0.3s ease;
  object-fit: cover;
}

.service-card:hover .card-icon {
  transform: scale(1.1);
}

.card-description {
  font-size: 17px;
  min-height: 64px;
  margin: 0;
}

.card-button {
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  padding: 15px 30px;
  border-radius: 31px;
  border: none;
  cursor: pointer;
  min-width: 238px;
  background-color: #204c6d;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.service-card:hover .card-button {
  background-color: #153a56;
  transform: scale(1.05);
}
</style>
