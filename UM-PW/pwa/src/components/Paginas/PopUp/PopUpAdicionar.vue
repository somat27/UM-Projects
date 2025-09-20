<template>
    <div id="popup">
        <div v-for="(item, index) in itemsDisponiveis" :key="index">
                <button class="transparente" @click="this.$emit('fechaFiltro', item);"><h3>{{ item.nome }}</h3></button>
        </div>
    </div>
</template>


<script>
    export default {
        name: "PopUpAdicionar",
        props: {
            itemsDisponiveis: {
                type: Array,
                required: true
            }
        }
    };
</script>


<style scoped>
    #popup {
        position: absolute;
        width: 100%;
        padding: 1vh 1vw;

        background-color: #F1F5F9;

        border: 1px solid #e6eaf0;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);

        max-height: 20vh;
        overflow-y: auto;

        text-align: left;

        z-index: 30;
    }
</style>