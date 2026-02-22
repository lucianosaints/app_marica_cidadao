import React, { useState } from 'react';

const FormularioZeladoria = () => {
  // 1. Estados para armazenar os dados do formulário
  const [descricao, setDescricao] = useState('');
  const [categoria, setCategoria] = useState(''); 
  const [foto, setFoto] = useState(null);
  const [localizacao, setLocalizacao] = useState({ lat: null, lng: null });
  const [statusEnvio, setStatusEnvio] = useState('');

  // 2. Função para capturar a localização GPS do celular/navegador
  const capturarLocalizacao = () => {
    setStatusEnvio('Buscando localização...');
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocalizacao({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
          setStatusEnvio('Localização capturada com sucesso!');
        },
        (error) => {
          console.error("Erro no GPS:", error);
          setStatusEnvio('Erro: Por favor, permita o acesso à localização.');
        }
      );
    } else {
      setStatusEnvio('Geolocalização não suportada neste dispositivo.');
    }
  };

  // 3. Função principal para montar e enviar os dados
  const handleSubmit = async (e) => {
    e.preventDefault(); // Evita que a página recarregue

    if (!localizacao.lat || !foto) {
      setStatusEnvio('Por favor, tire uma foto e capture a localização.');
      return;
    }

    setStatusEnvio('Enviando relato para a prefeitura...');

    // Criando o objeto FormData (Essencial para enviar arquivos)
    const formData = new FormData();
    formData.append('descricao', descricao);
    formData.append('categoria', categoria); // ID da categoria no banco (ex: 1 para Buraco)
    
    // Convertendo explicitamente as coordenadas para que o serializador consiga interpretar como float
    formData.append('latitude', parseFloat(localizacao.lat));
    formData.append('longitude', parseFloat(localizacao.lng));
    
    formData.append('foto_problema', foto); // Anexando o arquivo da imagem

    try {
      // URL da sua API. Quando for subir para produção, substitua pelo domínio do servidor.
      const resposta = await fetch('http://localhost:8000/api/relatos/', {
        method: 'POST',
        headers: {
          // ATENÇÃO: O 'Content-Type' não deve ser setado aqui ao enviar FormData
          // 'Authorization': `Token ${tokenUsuarioLogado}` // Descomente para enviar token de autenticação
        },
        body: formData,
      });

      if (resposta.ok) {
        setStatusEnvio('Sucesso! O problema foi relatado à prefeitura.');
        // Limpando os campos após envio
        setDescricao('');
        setFoto(null);
      } else {
        setStatusEnvio('Erro ao enviar. Verifique os dados e tente novamente.');
      }
    } catch (erro) {
      console.error("Erro na requisição:", erro);
      setStatusEnvio('Erro de conexão com o servidor.');
    }
  };

  return (
    <div className="formulario-container">
      <h2>Relatar Problema na Cidade</h2>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Selecione o Problema:</label>
          <select value={categoria} onChange={(e) => setCategoria(e.target.value)} required>
            <option value="">Selecione...</option>
            <option value="1">Buraco na Via</option>
            <option value="2">Lâmpada Queimada</option>
            <option value="3">Foco de Dengue</option>
          </select>
        </div>

        <div>
          <label>Descrição do Problema:</label>
          <textarea 
            value={descricao} 
            onChange={(e) => setDescricao(e.target.value)} 
            placeholder="Descreva os detalhes para ajudar a equipe..."
            required 
          />
        </div>

        <div>
          <label>Foto do Local:</label>
          {/* O accept="image/*" abre a câmera automaticamente em dispositivos móveis */}
          <input 
            type="file" 
            accept="image/*" 
            onChange={(e) => setFoto(e.target.files[0])} 
            required 
          />
        </div>

        <div>
           <button type="button" onClick={capturarLocalizacao}>
            📍 Pegar Minha Localização Atual
          </button>
          {localizacao.lat && <p>GPS Capturado: {localizacao.lat}, {localizacao.lng}</p>}
        </div>

        <button type="submit">Enviar Relato</button>
      </form>

      {statusEnvio && <p className="status-mensagem">{statusEnvio}</p>}
    </div>
  );
};

export default FormularioZeladoria;
