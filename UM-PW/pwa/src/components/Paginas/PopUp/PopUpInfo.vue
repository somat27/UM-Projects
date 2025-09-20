<template>
    <div v-if="dados" class="fundo centro">
        <div class="fundo-cinza painel flex-coluna popup" @click.stop>

            <h1 v-html="texto"/>

            <div v-for="(elemento, index) in dados" :key="index" class="flex-linha item-ponta centro">
                <h2>{{ elemento.nome }}</h2>

                <div class="flex-linha painel painel-ajustado centro">

                    <button class="transparente" @click="removeQuantidade(elemento)"><h1>-</h1></button>

                    <h2>{{ elemento.quantidade }}</h2>
                    
                    <button class="transparente" @click="adicionaQuantidade(elemento)"><h1>+</h1></button>
                </div>
            </div>
            <div class="pop-up">
                <div class="flex-linha item-ponta">
                    <div></div>
                    <button class="flex-linha centro" id="filtro" @click="adicionaEstado = !adicionaEstado">
                        <h2>Adicionar</h2>
                    </button>
                </div>
                

                <PopUpAdicionar v-if="adicionaEstado" :itemsDisponiveis="getItensDisponiveis()" @fechaFiltro="fechaFiltro"/>
            </div>
        </div>
    </div>
</template>


<script>
    import PopUpAdicionar from './PopUpAdicionar.vue'
    export default {
        name: "PopUpInfo",
        components: {
            PopUpAdicionar
        },
        data() {
            return {
                adicionaEstado: false,
                listaAlteracao: [],
                item: {}
            }
        },
        props: {
            dados: {
                type: Array,
                required: true
            },
            texto: {
                type: String,
                required: true
            },
            lista: {
                type: Array,
                required: true
            }
        },
        methods: {
            adicionaQuantidade(elemento) {
                const item = this.lista.find(item => item.nome === elemento.nome)
                if (item && item.quantidade > 0) {
                    elemento.quantidade++
                    item.quantidade--
                    this.$emit('alteracoes', {elemento ,"quantidade": -1})
                }
            },
            removeQuantidade(elemento) {
                const item = this.lista.find(item => item.nome === elemento.nome)
                if (item && elemento.quantidade > 0) {
                    elemento.quantidade--
                    item.quantidade++
                    this.$emit('alteracoes', {elemento ,"quantidade": 1})
                }
            },
            fechaFiltro(novoItem) {
                this.item = {
                    nome: novoItem.nome,
                    presente: false,
                    quantidade: 0
                }
                this.$emit('novoItem', this.item)
                this.adicionaEstado = false;
                this.adicionaQuantidade(this.item)
            },
            getItensDisponiveis() {
                const nomesSelecionados = this.dados.map(item => item.nome);
                return this.lista.filter(item => !nomesSelecionados.includes(item.nome));
            },
        },
    }
</script>


<style scoped>
    .popup {
        width: 90vw;
    }

    .painel-ajustado {
        height: 5vh;
        width: 25vw;
        padding: 1vh;

        justify-content: space-evenly;
    }
</style>