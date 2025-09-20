<template>

    <AppHeader titulo="Registo"/>

    <div class="flex-linha item-ponta centro margem">
        <button class="flex-linha transparente" @click="goToPaginaIncial">
            <h2><i class="bi bi-arrow-left"></i>   Voltar para menu</h2>
        </button>

        <button class="transparente" @click="limparLocalStorage">
            <h3>Limpar alterações</h3>
        </button>
        
    </div>

    <div class="flex-coluna margem painel" v-if="auditoria.tipo">
        <h1>{{ nomeOcorrencia(auditoria.tipo) }}</h1>


        <div class="flex-linha item-ponta margem-cima centro">
            <h2><i class="bi bi-camera icon"></i> Fotografias</h2>

            <button class="flex-linha transparente centro painel" id="filtro" @click="$refs.inputFicheiro.click()">
                <h3><i class="bi bi-box-arrow-up"></i></h3>
                <h3>Adicionar</h3>
                <input 
                        type="file"
                        ref="inputFicheiro"
                        style="display: none;"
                        @change="carregarImagem" 
                        accept="image/*,video/*"
                    />
            </button>
        </div>

        <div class="painel fundo-cinza pop-up" style="padding: 0;">
            <progress v-if="carregarFicheiro" id="barra-progresso" :value="percentagemUpload" max="100"></progress>
            <PainelImagens :imagens="auditoria.imagemVideo" @removeFicheiro="removeFicheiro"/>
        </div>


        <div class="flex-linha item-ponta margem-cima centro">
            <h2><i class="bi bi-mic icon"></i> Áudio</h2>

            <button 
                class="transparente" 
                @touchstart.prevent="iniciarGravacao" 
                @touchend.prevent="pararGravacao">
                    <i :class="isGravando ? 'bi bi-circle-fill' : 'bi bi-record-circle'" id="gravar"></i>
            </button>
        </div>

        <div class="painel fundo-cinza" style="padding: 0;">
            <PainelAudios :audios="auditoria.audios" @removeAudio="removeAudio"/>
        </div>


        <h2 class="margem-cima">Observações</h2>

        <textarea  
            type="text" 
            v-model="auditoria.descricao"
            placeholder="Adicione notas, observações ou detalhes importantes..." 
            @change="salvarAlteracoesEmLocalStorage"
            class="painel fundo-cinza"
            id="caixa-texto"></textarea>
        

        <button class="flex-linha transparente margem-cima" @click="popUpProfissionais = !popUpProfissionais">
            <h2><i class='bi bi-people icon'></i> Profissionais</h2>
            <PopUpInfo 
                v-if="popUpProfissionais && auditoria.profissionais.length > 0" 
                :dados="this.auditoria.profissionais" 
                :texto="`<i class='bi bi-people icon'></i> Profissionais`" 
                :lista="listaProfissionais" 
                @alteracoes="atualizarListaAlteracaoProfissionais"
                @novoItem="adicionarProfissionalLista"/>
        </button>


        <button class="flex-linha transparente" @click="popUpMateriais = !popUpMateriais">
            <h2><i class='bi bi-file-earmark-text icon'></i> Materiais</h2>
            <PopUpInfo 
                v-if="popUpMateriais && auditoria.materiais.length > 0" 
                :dados="this.auditoria.materiais" :texto="`<i class='bi bi-file-earmark-text icon'></i> Materiais`" 
                :lista="listaMateriais" 
                @alteracoes="atualizarListaAlteracaoMateriais"
                @novoItem="adicionarMaterialLista"/>
        </button>


        <button class="flex-linha transparente centro fundo-azul margem-cima botao-acao" @click="guardarAuditoria">
            <h2><i class="bi bi-save"></i> Guardar Auditoria</h2>
        </button>
    </div>
</template>


<script>
    import { doc, getDoc, collection, getDocs, updateDoc } from 'firebase/firestore';
    import { db, uploadToCloudinary } from '@/firebase/firebase.js';
    import AppHeader from '../AppHeader.vue';
    import PainelImagens from './Extra/PainelImagens.vue';
    import PainelAudios from './Extra/PainelAudios.vue';
    import PopUpInfo from './PopUp/PopUpInfo.vue';

    export default {
        name: "RegistoAuditoria",
        components: {
            AppHeader,
            PainelImagens,
            PainelAudios,
            PopUpInfo,
        },
        data() {
            return {
                auditoria: {},
                listaProfissionais: [],
                listaMateriais: [],

                mediaRecorder: null,
                chunks: [],
                isGravando: false,

                popUpProfissionais: false,
                popUpMateriais: false,

                carregarFicheiro: false,
                percentagemUpload: 0,

                listaAlteracaoProfissionais: [],
                listaAlteracaoMateriais: [],
            }
        },
        async mounted() {
            const id = this.$route.params.id;

            const auditorias = JSON.parse(localStorage.getItem('previaAuditoria')) || {};
            const materiais = JSON.parse(localStorage.getItem('previaMaterial')) || {};
            const profissionais = JSON.parse(localStorage.getItem('previaProfissionais')) || {};
            const materiaisAlterados = JSON.parse(localStorage.getItem('previaMaterialAlterado')) || {};
            const profissionaisAlterados = JSON.parse(localStorage.getItem('previaProfissionaisAlterado')) || {};

            if (auditorias[id] && auditorias[id].tipo) {
                this.auditoria = auditorias[id];
                this.listaMateriais = materiais[id] || [];
                this.listaProfissionais = profissionais[id] || [];
                this.listaAlteracaoMateriais = materiaisAlterados[id] || [];
                this.listaAlteracaoProfissionais = profissionaisAlterados[id] || [];
            }
            else {
                const docSnap = await getDoc(doc(db, "auditorias", id));
                if (docSnap.exists()) {

                    const dados = docSnap.data();
                    this.auditoria = { 
                        id: docSnap.id, 
                        ...dados,
                        imagemVideo: dados.imagemVideo || [],
                        audios: dados.audios || [],
                        profissionais: dados.profissionais || [],
                        materiais: dados.materiais || []
                    };


                    const querySnapshotProfissionais = await getDocs(collection(db, "profissionais"));
                    this.listaProfissionais = querySnapshotProfissionais.docs.map(doc => ({
                        id: doc.id,
                        ...doc.data()
                    }));

                    const querySnapshotMateriais = await getDocs(collection(db, "materiais"));
                    this.listaMateriais = querySnapshotMateriais.docs.map(doc => ({
                        id: doc.id,
                        ...doc.data()
                    }));

                } else {
                    this.auditoria = {};
                }
            }
        },
        methods: {
            goToPaginaIncial() {
                this.$router.push("/ListaAuditorias");
            },
            async carregarImagem(event) {
                const file = event.target.files[0];
                if (file) {
                    this.carregarFicheiro = true;
                    this.percentagemUpload = 0;

                    const url = await uploadToCloudinary(file, (e) => {
                        const percent = Math.round((e.loaded * 100) / e.total);
                        this.percentagemUpload = percent;
                        console.log("Progresso:", percent);
                    });
                    const tipo = file.type;

                    this.auditoria.imagemVideo.push({
                        url: url,
                        tipo: tipo
                    });

                    this.salvarAlteracoesEmLocalStorage()

                    this.carregarFicheiro = false;
                    this.percentagemUpload = 0;
                }
            },
            async guardarAuditoria() {
                this.limparAlteracoesDeLocalStorage()
                try {
                    // Primeiro, busque os valores atualizados na Firebase para profissionais e materiais
                    const querySnapshotProfissionais = await getDocs(collection(db, "profissionais"));
                    const profissionaisAtualizados = querySnapshotProfissionais.docs.map(doc => ({
                        id: doc.id,
                        ...doc.data()
                    }));

                    const querySnapshotMateriais = await getDocs(collection(db, "materiais"));
                    const materiaisAtualizados = querySnapshotMateriais.docs.map(doc => ({
                        id: doc.id,
                        ...doc.data()
                    }));

                    // Verifique se as quantidades nas listas de alterações são possíveis de serem retiradas
                    const profissionaisValidados = this.listaAlteracaoProfissionais.every(alteracao => {
                        const profissional = profissionaisAtualizados.find(p => p.nome === alteracao.nome);
                        return profissional && profissional.quantidade >= -alteracao.quantidade;
                    });

                    const materiaisValidados = this.listaAlteracaoMateriais.every(alteracao => {
                        const material = materiaisAtualizados.find(m => m.nome === alteracao.nome);
                        return material && material.quantidade >= -alteracao.quantidade;
                    });

                    // Se todas as quantidades forem válidas, atualize a Firebase e guarde a auditoria
                    if (profissionaisValidados && materiaisValidados) {
                        // Atualizar a quantidade dos profissionais na Firebase
                        for (const alteracao of this.listaAlteracaoProfissionais) {
                            const profissional = profissionaisAtualizados.find(p => p.nome === alteracao.nome);
                            if (profissional) {
                                await updateDoc(doc(db, "profissionais", profissional.id), {
                                    quantidade: profissional.quantidade + alteracao.quantidade
                                });
                            }
                        }

                        // Atualizar a quantidade dos materiais na Firebase
                        for (const alteracao of this.listaAlteracaoMateriais) {
                            const material = materiaisAtualizados.find(m => m.nome === alteracao.nome);
                            if (material) {
                                await updateDoc(doc(db, "materiais", material.id), {
                                    quantidade: material.quantidade + alteracao.quantidade
                                });
                            }
                        }

                        // Agora, guarde a auditoria
                        this.auditoria.status = "Pendente";
                        const auditoriaId = this.$route.params.id;
                        await updateDoc(doc(db, "auditorias", auditoriaId), {
                                audios: this.auditoria.audios,
                                imagemVideo: this.auditoria.imagemVideo,
                                materiais: this.auditoria.materiais,
                                profissionais: this.auditoria.profissionais,
                                descricao: this.auditoria.descricao,
                                status: this.auditoria.status,
                        });
                        console.log("Dados da auditoria salvos com sucesso!");

                        // Redirecionar para a página de informações da auditoria
                        this.$router.push({
                            name: "InfoAuditoria",
                            params: { id: this.auditoria.id }
                        });

                    } else {
                        // Se alguma quantidade não for válida, avise o usuário
                        alert("Não há quantidade suficiente para realizar a alteração.");
                    }
                } catch (error) {
                    console.error("Erro ao salvar os dados:", error);
                }
            },
            removeAudio(index) {
                this.auditoria.audios.splice(index, 1);
                this.salvarAlteracoesEmLocalStorage()
            },
            removeFicheiro(index) {
                this.auditoria.imagemVideo.splice(index, 1);
                this.salvarAlteracoesEmLocalStorage()
            },
            async iniciarGravacao() {
                try {
                    // Ativa o estado de gravação
                    this.isGravando = true;

                    // Solicita acesso ao microfone
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

                    this.mediaRecorder = new MediaRecorder(stream);
                    this.chunks = [];

                    this.mediaRecorder.ondataavailable = (e) => {
                        if (e.data.size > 0) {
                            this.chunks.push(e.data);
                        }
                    };

                    this.mediaRecorder.onstop = async () => {
                        const blob = new Blob(this.chunks, { type: 'audio/webm' });
                        const file = new File([blob], "gravacao.webm", { type: "audio/webm" });
                        const url = await uploadToCloudinary(file);

                        this.auditoria.audios.push(url);

                        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());

                        // Finaliza o estado de gravação
                        this.isGravando = false;
                    };

                    this.mediaRecorder.start();
                } catch (error) {
                    console.error('Erro ao iniciar gravação:', error);
                    this.isGravando = false;
                }
            },
            pararGravacao() {
                if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
                    this.mediaRecorder.stop();
                    this.salvarAlteracoesEmLocalStorage()
                }
            },
            atualizarListaAlteracaoProfissionais(dados) {
                const elemento = dados.elemento;
                const quantidade = dados.quantidade;

                const itemAuditoria = this.auditoria.profissionais.find(item => item.nome === elemento.nome);
                if (itemAuditoria) {
                    itemAuditoria.presente = false
                    if (itemAuditoria.quantidade === 0) {
                        this.auditoria.profissionais = this.auditoria.profissionais.filter(i => i.nome !== elemento.nome);
                    }
                }

                const item = this.listaAlteracaoProfissionais.find(item => item.nome === elemento.nome)
                if(item) {
                    item.quantidade += quantidade

                    if (item.quantidade === 0) {
                        this.listaAlteracaoProfissionais = this.listaAlteracaoProfissionais.filter(i => i.nome !== elemento.nome);
                    }
                }
                else {
                    this.listaAlteracaoProfissionais.push({
                        "nome": elemento.nome,
                        "quantidade": quantidade,
                    })
                }
                this.salvarAlteracoesEmLocalStorage()
            },
            atualizarListaAlteracaoMateriais(dados) {
                const elemento = dados.elemento;
                const quantidade = dados.quantidade;

                const itemAuditoria = this.auditoria.materiais.find(item => item.nome === elemento.nome);
                if (itemAuditoria) {
                    itemAuditoria.presente = false
                    if (itemAuditoria.quantidade === 0) {
                        this.auditoria.materiais = this.auditoria.materiais.filter(i => i.nome !== elemento.nome);}
                }

                const item = this.listaAlteracaoMateriais.find(item => item.nome === elemento.nome)
                if(item) {
                    item.quantidade += quantidade

                    if (item.quantidade === 0) {
                        this.listaAlteracaoMateriais = this.listaAlteracaoMateriais.filter(i => i.nome !== elemento.nome);
                    }
                }
                else {
                    this.listaAlteracaoMateriais.push({
                        "nome": elemento.nome,
                        "quantidade": quantidade,
                    })
                }
                this.salvarAlteracoesEmLocalStorage()
            },
            salvarAlteracoesEmLocalStorage() {
                localStorage.setItem('previaAuditoria', JSON.stringify({[this.auditoria.id]: this.auditoria}));

                localStorage.setItem('previaMaterialAlterado', JSON.stringify({[this.auditoria.id]: this.listaAlteracaoMateriais}));
                
                localStorage.setItem('previaProfissionaisAlterado', JSON.stringify({[this.auditoria.id]: this.listaAlteracaoProfissionais}));

                localStorage.setItem('previaMaterial', JSON.stringify({[this.auditoria.id]: this.listaMateriais}));
                
                localStorage.setItem('previaProfissionais', JSON.stringify({[this.auditoria.id]: this.listaProfissionais}));
            },

            limparAlteracoesDeLocalStorage() {

                localStorage.setItem('previaAuditoria', JSON.stringify({[this.auditoria.id]: {}}));

                localStorage.setItem('previaMaterialAlterado', JSON.stringify({[this.auditoria.id]: {}}));

                localStorage.setItem('previaProfissionaisAlterado', JSON.stringify({[this.auditoria.id]: {}}));

                localStorage.setItem('previaMaterial', JSON.stringify({[this.auditoria.id]: {}}));

                localStorage.setItem('previaProfissionais', JSON.stringify({[this.auditoria.id]: {}}));
            },
            nomeOcorrencia(valor) {
                switch(valor) {
                    case "lights": return "Iluminação Pública"
                    case "sinals": return "Sinalização em Falta"
                    case "roads": return "Vias e Passeios"
                }
            },
            limparLocalStorage() {
                this.limparAlteracoesDeLocalStorage()
                window.location.reload();
            },
            adicionarProfissionalLista(item) {
                this.auditoria.profissionais.push(item)
            },
            adicionarMaterialLista(item) {
                this.auditoria.materiais.push(item)
            }
        }
    }
</script>


<style>
    #caixa-texto {
        height: 11.5vh;

        padding: 1vh;
        font-size: 14px;
    }

    #gravar {
        color: red;
    }

    #barra-progresso {
        position: absolute;
        z-index: 5;
        top: -1vh;
        left: 0;
        width: 100%;
    }
</style>