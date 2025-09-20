<template>
    <div class="flex-linha centro" v-if="audios && audios.length !== 0" style="position: relative;">
        <button class="transparente botao-audio" id="esquerda" @click="audioAnterior" v-if="audios.length > 1">
            <i class="bi bi-chevron-compact-left"></i>
        </button>

        <audio :src="audios[audioAtual]" controls id="audio"></audio>

        <button class="transparente" @click="removeAudio"><i class="bi bi-trash-fill"></i></button>

        <button class="transparente botao-audio" id="direita" @click="audioSeguinte" v-if="audios.length > 1">
            <i class="bi bi-chevron-compact-right"></i>
        </button>
    </div>
</template>


<script>
    export default {
        name: "PainelAudios",
        props: {
            audios: {
                type: Array,
                required: true
            }
        },
        data() {
            return {
                audioAtual: 0,
            }
        },
        methods: {
            audioAnterior() {
                this.audioAtual = (this.audioAtual + 1) % this.audios.length;
            },
            audioSeguinte() {
                this.audioAtual = (this.audioAtual - 1 + this.audios.length) % this.audios.length;
            },
            removeAudio() {
                this.$emit("removeAudio", this.audioAtual);
            }
        }
    }
</script>


<style>
    #audio {
        width: 100%;
        border-radius: 15px;

        object-fit: cover;
    }

    .botao-audio {
        position: absolute;
        height: 5vh;
    }
</style>