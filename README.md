# TERA AI

Aplicativo para Windows em Python com interface em HTML/CSS (design moderno e tecnológico), focado em programação, hardware, mobile, iOS e informática.

## Recursos

- Tarefas por área técnica
- Memória de aprendizados (anotações salvas)
- Execução de comandos com log no banco
- Banco SQLite persistente
- Exportação do banco
- Sincronização para GitHub via botão/API

## Estrutura

- `main.py`: backend Python (Flask + SQLite)
- `templates/index.html`: interface
- `static/style.css`: tema visual tecnológico
- `static/app.js`: interações do frontend

## Fonte Angels

Para usar a fonte solicitada:

1. Baixe a fonte **Angels** no Dafont.
2. Coloque o arquivo em: `static/fonts/Angels.ttf`

Observação: o repositório traz `static/fonts/README.txt` indicando o local da fonte.

## Rodar localmente

```bash
python -m pip install -r requirements.txt
python main.py
```

O app abre no navegador local automaticamente.

## Gerar executável (.exe)

```bat
build_exe.bat
```

Saída:

`dist\Tera\Tera.exe`
