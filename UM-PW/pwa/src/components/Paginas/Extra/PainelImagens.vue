<template>
    <div class="flex-linha centro" v-if="imagens && imagens.length !== 0" style="position: relative;">
        <button class="transparente botao-imagem" id="esquerda" @click="imagemAnterior" v-if="imagens.length > 1">
            <i class="bi bi-chevron-compact-left"></i>
        </button>

        <img v-if="imagens[imagemAtual] && imagens[imagemAtual].tipo.startsWith('image/')" :src="imagens[imagemAtual].url" class="imagem" />
        
        <video v-else-if="imagens[imagemAtual] && imagens[imagemAtual].tipo.startsWith('video/')" :src="imagens[imagemAtual].url" controls class="imagem"></video>

        <button class="transparente" id="remover" @click="removeFicheiro"><i class="bi bi-trash-fill"></i></button>

        <button class="transparente botao-imagem" id="direita" @click="imagemSeguinte" v-if="imagens.length > 1">
            <i class="bi bi-chevron-compact-right"></i>
        </button>
    </div>
</template>


<script>
    export default {
        name: "PainelImagens",
        props: {
            imagens: {
                type: Array,
                required: true,
                default: () => []
            }
        },
        data() {
            return {
                imagemAtual: 0,
            };
        },
        methods: {
            imagemAnterior() {
                this.imagemAtual = (this.imagemAtual + 1) % this.imagens.length;
            },
            imagemSeguinte() {
                this.imagemAtual = (this.imagemAtual - 1 + this.imagens.length) % this.imagens.length;
            },
            removeFicheiro() {
                const index = this.imagemAtual;
                if (this.imagens.length === 1) {
                    this.imagemAtual = 0;
                } else if (this.imagemAtual >= this.imagens.length - 1) {
                    this.imagemAtual = this.imagens.length - 2;
                }
                this.$emit("removeFicheiro", index);
            }
        }
    }
</script>


<style>
    .imagem {
        height: 20vh;
        width: 100%;
        border-radius: 15px;

        object-fit: cover;
    }

    .botao-imagem {
        position: absolute;
        height: 20vh;
    }

    #esquerda {
        left: -5vw;
    }

    #direita {
        right: -5vw;
    }

    #remover {
        position: absolute;
        top: 0;
        right: 0;
        background-color: #f5f5f54b;
        border-radius: 5px;
    }
</style>