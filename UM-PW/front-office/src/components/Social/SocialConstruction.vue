<template>
  <div class="mini-aviso">
    <div class="conteudo">
      <div class="alerta-icon">🚧</div>
      <h1>Redes Sociais em Preparação!</h1>
      <p class="mensagem">Estamos a acertar os últimos pormenores. Até lá, fale connosco:</p>
      
      <div class="contactos-mini">
        <a class="contacto-link">📩 geral@eyeseverywhere.pt</a>
        <a class="contacto-link">📲 +351 912 345 678</a>
      </div>

      <div class="progresso-mini">
        <div class="barra" :style="{width: '75%'}"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mini-aviso {
  background: #D9D9D9;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.conteudo {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  max-width: 1000px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 2px solid #204C6D;
}

h1 {
  color: #204C6D;
  font-size: 1.4rem;
  margin: 0.8rem 0;
}

.mensagem {
  color: #000000;
  font-size: 0.9rem;
  line-height: 1.3;
  margin: 0.5rem 0 1rem;
}

.contactos-mini {
  display: grid;
  gap: 0.6rem;
  margin: 1rem 0;
}

.contacto-link {
  color: #204C6D;
  text-decoration: none;
  font-weight: 500;
  padding: 0.4rem;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.progresso-mini {
  background: #D9D9D9;
  height: 6px;
  border-radius: 3px;
  margin: 1rem auto;
  overflow: hidden;
}

.barra {
  background: #204C6D;
  height: 100%;
  transition: width 0.5s ease;
}

.alerta-icon {
  font-size: 2rem;
  animation: pulsar 1.8s infinite;
}

@keyframes pulsar {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@media (max-width: 480px) {
  .conteudo {
    padding: 1rem;
  }
  
  h1 {
    font-size: 1.2rem;
  }
}
</style>