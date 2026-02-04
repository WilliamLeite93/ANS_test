<template>
  <div style="max-width: 1100px; margin: 0 auto; padding: 20px; font-family: sans-serif; color: #333;">
    <header style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #42b983; margin-bottom: 20px; padding-bottom: 10px;">
      <div>
        <h1 style="margin: 0;">📊 Sistema ANS Financeiro</h1>
      </div>
      <nav>
        <button @click="irPara('tabela')" :style="estiloBotao(abaAtiva === 'tabela' || abaAtiva === 'detalhes')">📋 Operadoras</button>
        <button @click="irPara('graficos')" :style="estiloBotao(abaAtiva === 'graficos')">📈 Ver Gráficos</button>
      </nav>
    </header>

    <main v-if="abaAtiva === 'tabela'">
      <section>
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 20px;">
          <h2>Lista de Operadoras</h2>
          <div style="display: flex; gap: 5px;">
            <input v-model="busca" @keyup.enter="novaBusca" placeholder="Nome ou CNPJ..." 
                   style="padding: 10px; width: 280px; border-radius: 4px; border: 1px solid #42b983; outline: none;">
            <button @click="novaBusca" style="padding: 10px 20px; background: #42b983; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Buscar</button>
          </div>
        </div>

        <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <thead>
            <tr style="background: #42b983; color: white;">
              <th style="padding: 15px; text-align: left;">Razão Social</th>
              <th style="padding: 15px; text-align: left;">CNPJ</th>
              <th style="padding: 15px; text-align: center;">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in operadoras" :key="item.cnpj" style="border-bottom: 1px solid #eee;">
              <td style="padding: 12px;">{{ item.raz }}</td>
              <td style="padding: 12px;">{{ item.cnpj }}</td>
              <td style="padding: 12px; text-align: center;">
                <button @click="verDetalhes(item)" style="padding: 5px 10px; cursor: pointer; background: #35495e; color: white; border: none; border-radius: 4px;">Ver Detalhes</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div style="margin-top: 25px; display: flex; justify-content: center; align-items: center; gap: 15px;">
          
          <button @click="mudarPagina(1)" :disabled="operadoras.length < 15" :style="{ ...estiloPaginacao(operadoras.length < 15), color: '#000' }">Anterior ⬅️</button>
          <span style="font-weight: bold;">Página {{ paginaAtual }}</span>
          <button @click="mudarPagina(1)" :disabled="operadoras.length < 15" :style="{ ...estiloPaginacao(operadoras.length < 15), color: '#000' }">Próxima ➡️</button>

        </div>
      </section>
    </main>

    <main v-if="abaAtiva === 'detalhes'">
      <button @click="abaAtiva = 'tabela'" style="margin-bottom: 20px; cursor: pointer; background: none; border: 1px solid #666; padding: 5px 10px; border-radius: 4px;">⬅️ Voltar para Lista</button>
      
      <section v-if="selecionada" style="background: #f9f9f9; padding: 25px; border-radius: 8px; border: 1px solid #ddd;">
        <h2 style="color: #42b983;">{{ selecionada.raz }}</h2>
        <p><strong>CNPJ:</strong> {{ selecionada.cnpj }} | <strong>UF:</strong> {{ selecionada.uf || 'N/A' }}</p>
        
        <h3 style="margin-top: 30px; border-top: 1px solid #ccc; padding-top: 20px;">📜 Histórico de Despesas (Conta 411)</h3>
        
        <div v-if="carregandoDetalhes" style="padding: 20px; text-align: center;">⏳ Buscando histórico financeiro...</div>
        
        <div v-else-if="historico.length === 0" style="padding: 20px; color: #666;">
          Nenhum histórico de despesas encontrado para esta operadora nos últimos trimestres.
        </div>

        <table v-else style="width: 100%; border-collapse: collapse; margin-top: 10px; background: white;">
          <thead>
            <tr style="background: #eee;">
              <th style="padding: 10px; text-align: left;">Período (Ano/Trimestre)</th>
              <th style="padding: 10px; text-align: right;">Valor da Despesa</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(h, index) in historico || []" :key="index" style="border-bottom: 1px solid #eee;">
              <td style="padding: 10px;">{{ h.ano }} / {{ h.tri }}º Trimestre</td>
              <td style="padding: 10px; text-align: right; font-weight: bold; color: #d9534f;">
                R$ {{ h.valor ? h.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '0,00' }}
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>

    <main v-if="abaAtiva === 'graficos'">
      <div v-if="!estatisticas" style="text-align: center; padding: 50px;">Carregando dados analíticos...</div>
      <div v-else style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
        <section style="background: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
          <h3 style="text-align: center; margin-bottom: 20px;">Top 5 Operadoras (Despesa Total)</h3>
          <div style="height: 250px; display: flex; align-items: flex-end; gap: 10px;">
            <div v-for="op in estatisticas.top_5_operadoras" :key="op.raz" 
                 style="background: #42b983; flex: 1; border-radius: 4px 4px 0 0; position: relative;"
                 :title="op.raz"
                 :style="{ height: (op.total / estatisticas.top_5_operadoras[0].total * 100) + '%' }">
            </div>
          </div>
          <div style="display: flex; gap: 10px; margin-top: 10px;">
            <div v-for="op in estatisticas.top_5_operadoras" :key="op.raz" 
                 style="flex: 1; font-size: 8px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              {{ op.raz }}
            </div>
          </div>
        </section>

        <section style="background: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
          <h3 style="text-align: center; margin-bottom: 20px;">Distribuição de Despesas por UF</h3>
          <div style="height: 250px; display: flex; align-items: flex-end; gap: 5px;">
            <div v-for="uf in estatisticas.distribuicao_uf.slice(0, 10)" :key="uf.uf" 
                 style="background: #35495e; flex: 1; border-radius: 4px 4px 0 0; position: relative;"
                 :style="{ height: (uf.total / estatisticas.distribuicao_uf[0].total * 100) + '%' }">
              <div style="position: absolute; top: -20px; width: 100%; text-align: center; font-size: 10px; font-weight: bold;">{{ uf.uf }}</div>
            </div>
          </div>
          <p style="text-align: center; font-size: 11px; margin-top: 15px; color: #666;">Top 10 estados com maiores despesas</p>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
import api from './services/api';

export default {
  data() {
    return {
      abaAtiva: 'tabela',
      operadoras: [],
      estatisticas: null,
      busca: '',
      paginaAtual: 1,
      selecionada: null,
      historico: [],
      carregandoDetalhes: false
    }
  },
  methods: {
    irPara(aba) { this.abaAtiva = aba; },
    estiloBotao(ativo) {
      return {
        padding: '10px 20px', marginLeft: '10px', cursor: 'pointer', borderRadius: '4px', border: 'none',
        fontWeight: 'bold', backgroundColor: ativo ? '#42b983' : '#eee', color: ativo ? 'white' : '#333'
      }
    },
    estiloPaginacao(desativado) {
      return {
        padding: '8px 15px', cursor: desativado ? 'not-allowed' : 'pointer', borderRadius: '4px',
        border: '1px solid #ccc', backgroundColor: desativado ? '#f5f5f5' : 'white', opacity: desativado ? 0.5 : 1
      }
    },
    async buscarOperadoras() {
      try {
        const resp = await api.get('/operadoras', { params: { busca: this.busca, page: this.paginaAtual, limit: 15 } });
        this.operadoras = resp.data.data;
      } catch (err) { console.error("Erro na API de operadoras:", err); }
    },
    async verDetalhes(op) {
      this.selecionada = op;
      this.abaAtiva = 'detalhes';
      this.carregandoDetalhes = true;
      this.historico = []; 
      
      try {
        
        const url = `/operadoras/${op.cnpj}/despesas`;
        const resp = await api.get(url);
        this.historico = resp.data.historico || [];
      } catch (err) {
        console.error("Erro ao buscar histórico da operadora:", err);
        this.historico = [];
      } finally {
        this.carregandoDetalhes = false;
      }
    },
    novaBusca() { 
      this.paginaAtual = 1; 
      this.buscarOperadoras(); 
    },
    mudarPagina(direcao) { 
      this.paginaAtual += direcao; 
      this.buscarOperadoras(); 
    },
    async carregarEstatisticas() {
      try {
        const resp = await api.get('/estatisticas');
        this.estatisticas = resp.data;
      } catch (err) { console.error("Erro ao carregar estatísticas:", err); }
    }
  },
  mounted() {
    this.buscarOperadoras();
    this.carregarEstatisticas();
  }
}
</script>