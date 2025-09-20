<template>
  <footer class="site-footer">
    <div class="footer-links animate-fade-in">
      <h3 class="footer-heading">Links Uteis</h3>
      <a href="/sobre-nos" class="footer-link">Sobre nós</a>
      <a href="/help" class="footer-link">Ajuda</a>
      <a href="/feedback" class="footer-link">Avaliação</a>
    </div>

    <div class="footer-social animate-fade-in">
      <h3 class="footer-heading">Social</h3>
      <a href="/social" class="footer-link">Instagram</a>
      <a href="/social" class="footer-link">Twitter</a>
      <a href="/social" class="footer-link">Tik Tok</a>
    </div>

    <div class="footer-contact animate-fade-in">
      <h3 class="footer-heading">Contactos</h3>
      <p class="contact-info">+351 912345678</p>
      <p class="contact-info">geral@eyeseverywhere.pt</p>
    </div>

    <div class="footer-branding animate-fade-in">
      <img
        src="https://cdn.builder.io/api/v1/image/assets/TEMP/12cdb61c2b96a6ec0b1752be2b759512b3b11795"
        alt="Footer logo"
        class="footer-logo"
      />
      <p class="copyright">C2025 All Rights Reseverd</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: "AppFooter",
  mounted() {
    const elements = document.querySelectorAll(".animate-fade-in");

    elements.forEach((element, index) => {
      setTimeout(() => {
        element.classList.add("visible");
      }, 150 * index);
    });
  },
};
</script>

<style scoped>
.site-footer {
  padding: 1% 1% 1% 8%;
  display: flex;
  justify-content: space-between;
  color: #fff;
  background-color: #a2a2a2;
  overflow: hidden;
}

@media (max-width: 640px) {
  .site-footer {
    flex-direction: column;
    gap: 30px;
    padding: 30px;
  }
}

.footer-links,
.footer-social,
.footer-contact {
  font-family: "Open Sans", sans-serif;
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.footer-heading {
  font-size: 160%;
  margin: 0 0 11px 0;
  font-weight: bold;
  position: relative;
}

.footer-heading:after {
  content: "";
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -2px;
  left: 0;
  background-color: #fff;
  transition: width 0.5s ease;
}

.animate-fade-in:hover .footer-heading:after {
  width: 50%;
}

.footer-link,
.contact-info {
  font-size: 80%;
  text-decoration: none;
  color: #fff;
  margin: 0;
  transition: transform 0.3s ease, color 0.3s ease;
  position: relative;
  display: inline-block;
}

.footer-link:hover {
  transform: translateX(5px);
}

.footer-link:before {
  content: "";
  position: absolute;
  width: 0;
  height: 1px;
  bottom: -2px;
  left: 0;
  background-color: #fff;
  visibility: hidden;
  transition: all 0.3s ease-in-out;
}

.footer-link:hover:before {
  visibility: visible;
  width: 100%;
}

.footer-branding {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 13px;
}

@media (max-width: 640px) {
  .footer-branding {
    align-items: center;
  }
}

.footer-logo {
  width: 323px;
  height: 52px;
  transition: transform 0.5s ease;
}

.footer-branding:hover .footer-logo {
  transform: scale(1.03);
}

.copyright {
  font-family: "Open Sans", sans-serif;
  font-size: 80%;
  margin: 0;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.footer-branding:hover .copyright {
  opacity: 1;
}

/* Animação de entrada */
.animate-fade-in {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.animate-fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
