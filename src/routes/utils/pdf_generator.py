from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
)
import os


def generate_report_pdf(report_data) -> bytes:

    def fl_to_real(value: float, symbol: bool = False) -> str:
        """
        Formata um float para o padrão de moeda brasileira.
        
        Args:
            value (float): Valor a ser formatado
            symbol (bool): Se True, adiciona o símbolo R$
        
        Returns:
            str: Valor formatado no padrão brasileiro
        """
        # Formatar com duas casas decimais
        formatted = f"{value:.2f}"
        
        # Separar parte inteira e decimal
        integer_part, decimal_part = formatted.split('.')
        
        # Adicionar separador de milhares (ponto)
        if len(integer_part) > 3:
            # Inverter string para adicionar pontos a cada 3 dígitos
            reversed_int = integer_part[::-1]
            grouped = [reversed_int[i:i+3] for i in range(0, len(reversed_int), 3)]
            integer_part = '.'.join(grouped)[::-1]
        
        # Juntar com vírgula como separador decimal
        result = f"{integer_part},{decimal_part}"
        
        # Adicionar símbolo se necessário
        if symbol:
            result = f"R$ {result}"
        
        return result

    def calcula_espaco_contato(n_linhas):
        altura_pagina = 29.7 * cm
        margem_superior = 1 * cm
        margem_inferior = 2 * cm
        tam_linhas_dados = n_linhas * 0.63 * cm
        tam_linha_total = 0.63 * cm
        espaco_antes_data = 0.6 * cm
        tam_data = 0.35 * cm
        tam_contato = 2 * cm
        tam_coringa = 0.9 * cm

        espaco_ocupado = (margem_superior + tam_linhas_dados + 
                        tam_linha_total + espaco_antes_data + tam_data + 
                        tam_contato + margem_inferior + tam_coringa)
        
        espaco_necessario = altura_pagina - espaco_ocupado
        
        return max(espaco_necessario, 0.5 * cm)


    def calcula_espaco_contato_pg1(n_linhas):
        altura_pagina = 29.7 * cm
        margem_superior = 1 * cm
        margem_inferior = 2 * cm
        tam_linhas_dados = n_linhas * 0.63 * cm
        tam_coringa = 11.1 * cm

        espaco_ocupado = (margem_superior + tam_linhas_dados + 
                        margem_inferior + tam_coringa)

        espaco_necessario = altura_pagina - espaco_ocupado
        
        return max(espaco_necessario, 0.5 * cm)


    def inserir_cabecalho():
        cabecalho = [['Nº', 'Data', 'Nome Cliente', 'Tipo Serviço', 'Valor (R$)']]
        tab_cabecalho = Table(cabecalho, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(cabecalho))]) # Soma precisa ser 17
        tab_cabecalho.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#cccccc')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))

        conteudo.append(tab_cabecalho)


    def inserir_linha_final():
        dados_fim = [['TOTAL', '', '', '', fl_to_real(total_valores, symbol=True)]]
        tab_fim = Table(dados_fim, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(dados_fim))]) # Soma precisa ser 17
        tab_fim.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('SPAN', (0, -1), (3, -1)),  # Mescla da coluna 0 até a 3 na última linha
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ]))
        
        conteudo.append(tab_fim)


    def fechamento_data():
        conteudo.append(Spacer(1, 0.6*cm))

        meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 
                'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        data_atual = datetime.now()
        final_data = f"Pereira Barreto, {data_atual.day:02d} de {meses[data_atual.month - 1]} de {data_atual.year}."
        
        conteudo.append(Paragraph(final_data, ParagraphStyle(name='texto', fontSize=10, alignment=2)))


    def inserir_contato(espaco_contato):
        conteudo.append(Spacer(1, espaco_contato))
        texto_info = '''
        <b>Bar-Beer Baltazar</b><br/>
        <b>Email:</b> baltazar@baltazar.com<br/>
        <b>Telefone/WhatsApp:</b> (18) 99662-3429<br/>
        <b>Local:</b> Rua Ciro Maia, nº 1433 - Pereira Barreto/SP<br/>
        <b>Atendimento:</b> SEG a SEX 9:30 às 19:30 | Sáb. 9:30 às 16:00
        '''
        
        linha = HRFlowable(width="100%", thickness=0.5, lineCap='round', color=colors.grey, spaceBefore=1, spaceAfter=5)
        
        conteudo.append(linha)
        conteudo.append(Paragraph(texto_info, ParagraphStyle(name='texto_info', fontSize=9, alignment=0, leftIndent=0)))


    def inserir_continua():
        continua = '<i>(continua)</i>'
        conteudo.append(Paragraph(continua, ParagraphStyle(name='cont', fontSize=10, alignment=2, spaceBefore=1*cm)))


    colaborador = report_data.get('name')
    periodo = report_data.get('period')
    dados_servicos = report_data.get('appointments', [])
    
    total_servicos = len(dados_servicos)

    if total_servicos > 0:
        total_valores = sum([linha[3] for linha in dados_servicos])
        dados_servicos = [
            [i+1, servico[0], servico[1], servico[2], fl_to_real(servico[3], symbol=False)]
            for i, servico in enumerate(dados_servicos)
        ]

    # Criando PDF em buffer de memória
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=1*cm, bottomMargin=2*cm,
                            title='Relatório de Serviços - Bar-Beer Baltazar',
                            author='Bar-Beer Baltazar',
                            subject=f'Relatório de Serviços - {colaborador} - {periodo}',
                            creator='TimeMate',
                            keywords='relatório, serviços, barbearia')

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1, fontSize=14, spaceAfter=10))

    conteudo = []

    logo_image = os.path.join(os.path.dirname(__file__), 'logo.png')
    logo = Image(logo_image, width=6*cm, height=3*cm)

    # Cabeçalho com logotipo
    conteudo.append(logo)
    conteudo.append(Spacer(1, 12))
    conteudo.append(Paragraph('<b>RELATÓRIO DE SERVIÇOS</b>', styles['Center']))
    conteudo.append(Spacer(1, 12))

    # Informações do relatório
    conteudo.append(Paragraph(f'<b>colaborador:</b> {colaborador}', ParagraphStyle(name='colaborador', fontSize=11, spaceAfter=1)))
    conteudo.append(Paragraph(f'<b>Período:</b> {periodo}', ParagraphStyle(name='periodo', fontSize=10, spaceAfter=15)))
   
    # Relatório em branco
    if total_servicos == 0:
        conteudo.append(Paragraph('<i>Nenhum serviço realizado no período.</i>', ParagraphStyle(name='nenhum', fontSize=10, alignment=0, spaceBefore=2*cm, spaceAfter=1*cm)))
        fechamento_data()
        inserir_contato(13.9*cm)

    # Relatório com até 23 serviços
    if total_servicos < 24 and total_servicos != 0:

        inserir_cabecalho()

        dados_meio = []

        for linha in dados_servicos:
            dados_meio.append(linha)

        tab_meio = Table(dados_meio, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(dados_meio))]) # Soma precisa ser 17
        tab_meio.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))

        conteudo.append(tab_meio)
        
        inserir_linha_final()
        fechamento_data()
        esp = calcula_espaco_contato_pg1(total_servicos)
        inserir_contato(esp)

    # Relatório com 24 serviços
    if total_servicos == 24:
        inserir_cabecalho()
        
        # Primeira iteração: 23 elementos
        dados_meio = []
        for linha in dados_servicos[0:23]:
            dados_meio.append(linha)

        tab_meio = Table(dados_meio, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(dados_meio))]) # Soma precisa ser 17
        tab_meio.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        conteudo.append(tab_meio)
        inserir_continua()
        conteudo.append(PageBreak())
        
        # Segunda iteração: 1 elemento
        dados_meio = []
        dados_meio.append(dados_servicos[23])

        tab_meio = Table(dados_meio, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(dados_meio))]) # Soma precisa ser 17
        tab_meio.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        conteudo.append(tab_meio)
        
        inserir_linha_final()
        fechamento_data()
        inserir_contato(21.6*cm)

    # Relatório com valores entre 24 e 30 serviços
    if 30 > total_servicos > 24:
        linhas_sobrando = total_servicos % 24
        qtd_paginas = total_servicos // 24
        
        inserir_cabecalho()
        cont = 0
        while cont <= qtd_paginas:
            dados_meio = []

            inicio = cont * 24
            if cont == qtd_paginas:
                fim = inicio + linhas_sobrando
            else:
                fim = inicio + 24

            for linha in dados_servicos[inicio:fim]:
                dados_meio.append(linha)

            tab_meio = Table(dados_meio, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(dados_meio))]) # Soma precisa ser 17
            tab_meio.setStyle(TableStyle([
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ]))

            conteudo.append(tab_meio)

            if cont < qtd_paginas:
                inserir_continua()
                conteudo.append(PageBreak())

            cont += 1
        
        inserir_linha_final()
        esp = calcula_espaco_contato(linhas_sobrando-1)
        inserir_contato(esp)

    # Relatório com 30 ou mais serviços
    if total_servicos >= 30:
        inserir_cabecalho()
        
        # Página 1: 28 elementos
        dados_meio = []
        for linha in dados_servicos[0:28]:
            dados_meio.append(linha)

        tab_meio = Table(dados_meio, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(dados_meio))])
        tab_meio.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        conteudo.append(tab_meio)
        inserir_continua()
        conteudo.append(PageBreak())
        
        # Calcula toda a distribuição antes de começar
        elementos_restantes = total_servicos - 28
        
        # Função para calcular distribuição
        def calcular_distribuicao(elementos):
            # Se <= 34: uma página (cabe contato)
            # Se 35-41: corta no 34, resto (1-7) vai para próxima (cabe contato)
            # Se > 41: páginas de 41 até sobrar menos de 41, aí aplica as regras acima
            
            distribuicao = []
            restantes = elementos
            
            # Enquanto tiver mais de 41, faz páginas de 41
            while restantes > 39:
                distribuicao.append(39)
                restantes -= 39
            
            # Agora restantes <= 41
            if restantes <= 34:
                # Cabe tudo numa página com contato
                distribuicao.append(restantes)

            # restantes entre 35-41
            else:
                # Corta no 34, resto (1-7) vai para próxima
                distribuicao.append(34)
                distribuicao.append(restantes - 34)
            
            return distribuicao
        
        # Calcular distribuição
        distribuicao = calcular_distribuicao(elementos_restantes)
        
        # Aplicar a distribuição
        inicio = 28
        for i, elementos_nesta_pagina in enumerate(distribuicao):
            dados_meio = []
            fim = inicio + elementos_nesta_pagina
            
            for linha in dados_servicos[inicio:fim]:
                dados_meio.append(linha)
            
            tab_meio = Table(dados_meio, colWidths=[1*cm, 2.5*cm, 7*cm, 4*cm, 2.5*cm], rowHeights=[0.63*cm for i in range(len(dados_meio))])
            tab_meio.setStyle(TableStyle([
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ]))
            conteudo.append(tab_meio)
            
            inicio = fim
            
            # Se não é a última página, adiciona quebra de página
            if i < len(distribuicao) - 1:
                inserir_continua()
                conteudo.append(PageBreak())
        
        # Adicionar linha final, data e contato na última página
        inserir_linha_final()
        fechamento_data()
        
        ultima_pagina_elementos = distribuicao[-1] if distribuicao else 0
        esp = calcula_espaco_contato(ultima_pagina_elementos)
        inserir_contato(esp)

    doc.build(conteudo)
    
    buffer.seek(0)

    return buffer.getvalue()