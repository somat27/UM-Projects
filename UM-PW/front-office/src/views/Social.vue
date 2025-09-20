<template>
    <main class="page-container">
      <Header />
      <Social />
      <Footer />
    </main>
  </template>
  
  <script>
  import Header from "@/layouts/Header.vue";
  import Footer from "@/layouts/Footer.vue";
  import Social from "@/components/Social/SocialConstruction.vue";
  
  export default {
    name: "AboutUS",
    components: {
      Header,
      Social,
      Footer,
    },
  };
  </script>
  
  <style scoped>
  .page-container {
    width: 100%;
    min-height: 100vh;
    background-color: #fff;
    display: flex;
    flex-direction: column;
  }
  </style>
  